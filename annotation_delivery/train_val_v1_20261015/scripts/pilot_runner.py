"""Run the authorized 384-image pilot with fixed-role, reusable agy sessions."""
import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import threading
import time
from collections import deque, Counter
from concurrent.futures import ThreadPoolExecutor

from prepare import PROJECT, ROOT, read, write, lines, sha, SIX, FOUR
from prepare_packets import render
from review_contract import validate_file
from secondary_review import POLICY, prepare_secondary_files


def now():
    return datetime.now(timezone.utc).isoformat()


def failure_kind(text):
    if re.search(r'User location is not supported|PERMISSION_DENIED|UNAUTHENTICATED', text, re.I):
        return 'provider_access_rejected'
    if re.search(r'quota|resource.exhausted|额度|配额|insufficient.credit', text, re.I):
        return 'quota_or_resource_exhausted'
    if re.search(r'connection.reset|connection.refused|unexpected EOF|no such host|dial tcp|proxyconnect|TLS handshake|network error|broken pipe|socket error|网络|连接中断', text, re.I):
        return 'network_error'
    if re.search(r'HTTP.?50[234]|service unavailable|bad gateway', text, re.I):
        return 'service_unavailable'
    return None


class Pilot:
    def __init__(self, directory, resume=False):
        self.directory = directory
        self.cfg = read(PROJECT / 'config.json')
        self.cv = read(ROOT / self.cfg['source_config'])
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.processes = {}
        self.stopped = False
        self.stop_reason = None
        self.queues = {'initial_rgb': deque(), 'secondary_chroma': deque()}
        self.inventory = {r['source_sample_key']: r for r in lines(PROJECT / self.cfg['preparation']['inventory'] / 'inventory.jsonl')}
        if resume:
            state = read(directory / 'checkpoint.json')
            if state.get('secondary_merge_policy') != self.cfg['stages']['secondary_chroma']['merge']:
                raise ValueError('Old full-replacement checkpoint is retired; prepare a new item-review run from the original baseline')
            self.jobs = state['jobs']
            self.workers = state['workers']
            self.started_at = state['started_at']
            for job in self.jobs.values():
                if job['state'] in ['running', 'ready', 'retry_pending']:
                    job['state'] = 'ready'
        else:
            directory.mkdir(parents=True)
            index = read(PROJECT / self.cfg['preparation']['starter'] / 'starter_index.json')
            if index['annotation_contract'] != self.cfg['annotation_contract'] or len(index['packets']) != 16:
                raise ValueError('Expected current 16-packet pilot starter set')
            all_jobs = {r['job_id']: r for r in lines(PROJECT / self.cfg['preparation']['inventory'] / 'queue.jsonl')}
            self.jobs = {}
            for number, packet in enumerate(index['packets'], 1):
                source = all_jobs[packet['job_id']]
                identifier = f'T{number:04d}'
                self.jobs[identifier] = {'task_id': identifier, 'stage': packet['stage'], 'state': 'ready',
                                         'source_sample_keys': source['source_sample_keys'], 'accepted': {}, 'pending': {},
                                         'attempts': [], 'depends_on': None}
                if packet['stage'] == 'initial_rgb':
                    child = f'T{number + 16:04d}'
                    self.jobs[child] = {'task_id': child, 'stage': 'secondary_chroma', 'state': 'waiting_initial',
                                       'source_sample_keys': source['source_sample_keys'], 'accepted': {}, 'pending': {},
                                       'attempts': [], 'depends_on': identifier}
            unique = {k for j in self.jobs.values() for k in j['source_sample_keys']}
            if len(unique) != 384:
                raise ValueError('Pilot must contain exactly 384 unique source identities')
            self.workers = {f'W{i:02d}': {'role': 'initial_rgb' if i <= 8 else 'secondary_chroma',
                                         'conversation_id': None, 'rounds': 0, 'conversation_history': []} for i in range(1, 17)}
            self.started_at = now()
            write(directory / 'authorization.json', {'authorized_at': self.started_at,
                'user_request': '做好准备，先试标一小批24x16=384，然后导出流式包到label studio，让我检测',
                'scope': 'exactly_384_unique_train_val_samples_no_full_dataset_continuation',
                'model': self.cfg['model'], 'global_concurrency': 16,
                'quota_gate': 'direct user instruction authorizes this pilot; stop on any actual quota error',
                'session_tail_exception': 'Small pilot may end before 4 rounds; no padding with extra samples'})
            for file in [Path(__file__), Path(__file__).with_name('review_contract.py')]:
                (directory / file.name).write_bytes(file.read_bytes())
        for identifier, job in self.jobs.items():
            if job['state'] == 'waiting_initial' and self.jobs[job['depends_on']]['state'] == 'completed':
                job['state'] = 'ready'
            if job['state'] in ['ready', 'retry_pending']:
                self.queues[job['stage']].append(identifier)
        self.checkpoint()

    def checkpoint(self):
        with self.lock:
            secondary = [j for j in self.jobs.values() if j['stage'] == 'secondary_chroma']
            final_count = sum(len(j['accepted']) for j in secondary)
            write(self.directory / 'checkpoint.json', {'annotation_contract': self.cfg['annotation_contract'],
                  'secondary_merge_policy': self.cfg['stages']['secondary_chroma']['merge'],
                  'started_at': self.started_at, 'updated_at': now(), 'state': 'stopped' if self.stopped else 'running',
                  'stop_reason': self.stop_reason, 'target_unique_samples': 384, 'final_completed': final_count,
                  'initial_completed': sum(len(j['accepted']) for j in self.jobs.values() if j['stage'] == 'initial_rgb'),
                  'active_calls': len(self.processes), 'jobs': self.jobs, 'workers': self.workers,
                  'job_states': dict(Counter(j['state'] for j in self.jobs.values()))})

    def stop(self, reason):
        with self.condition:
            if self.stopped:
                return
            self.stopped, self.stop_reason = True, reason
            active = list(self.processes.values())
            self.checkpoint()
            self.condition.notify_all()
        print('GLOBAL STOP: ' + reason, flush=True)
        for process in active:
            if process.poll() is None:
                subprocess.run(['taskkill.exe', '/PID', str(process.pid), '/T', '/F'], capture_output=True,
                               creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def materialize(self, job):
        remaining = [k for k in job['source_sample_keys'] if k not in job['accepted']]
        directory = self.directory / 'tasks' / job['task_id'] / f'attempt_{len(job["attempts"]) + 1:02d}'
        directory.mkdir(parents=True)
        (directory / 'sheets').mkdir()
        rows = [copy.deepcopy(self.inventory[k]) for k in remaining]
        if job['depends_on']:
            parent = self.jobs[job['depends_on']]
            for row in rows:
                row['baseline'] = {'source': {'kind': 'new_initial_NR_review', 'task_id': parent['task_id']},
                                   'defects': parent['accepted'][row['source_sample_key']]['defects']}
        sheets = render(rows, job['stage'], directory / 'sheets', self.cfg, self.cv)
        mapping = {f'S{i:03d}': r for i, r in enumerate(rows, 1)}
        packet_id = f'{job["task_id"]}-a{len(job["attempts"]) + 1:02d}'
        target = directory / 'reviews_gemini.json'
        request = {'annotation_contract': self.cfg['annotation_contract'], 'stage': job['stage'], 'packet_id': packet_id,
                   'checked_categories': FOUR if job['stage'] == 'initial_rgb' else SIX, 'sheets': sheets}
        write(target, {'schema_version': 'delivery_review_compact_v2', **{k: request[k] for k in ['annotation_contract', 'stage', 'packet_id']},
                       'reviews': {key: None for key in mapping}})
        prior = None
        if job['stage'] == 'secondary_chroma':
            prior = directory / 'prior_reviews.json'
            write(prior, {'schema_version': 'delivery_anonymous_prior_v2',
                         'status': 'new_initial_labels_for_secondary_review' if job['depends_on'] else 'unverified_legacy_labels_full_NR_review_required',
                         'reviews': {key: [{k: d[k] for k in ['id', 'severity', 'object', 'description'] if k in d}
                                           for d in row['baseline']['defects'] if d.get('id') in SIX] for key, row in mapping.items()}})
            if self.cfg['stages']['secondary_chroma']['merge'] == POLICY:
                prepare_secondary_files(directory, request, mapping)
        listing = '\n'.join(s['path'] + ': ' + ', '.join(s['sample_keys']) for s in sheets)
        current = (f'本轮packet_id={packet_id}，stage={job["stage"]}，契约={self.cfg["annotation_contract"]}。\n'
                   f'本轮只处理{len(rows)}个S编号，指定结果文件：{target.resolve()}\n'
                   + (f'匿名审核底稿：{prior.resolve()}，先读原标签及P编号，再逐图核对。\n' if prior else '')
                   + '本轮看板，每张只读一次：\n' + listing + '\n只修改指定结果文件，保存后只回复“文件已保存”。')
        role = (PROJECT / f'prompts/{job["stage"]}.md').read_text(encoding='utf-8')
        full = (PROJECT / 'prompts/session.md').read_text(encoding='utf-8') + '\n' + role + '\n' + current
        continuation = '继续固定角色，新一轮S编号与上轮无关。按各类独立分级，描述为自然句，不含GT比较／对象等级标题。\n' + role + '\n' + current
        write(directory / 'request.json', request)
        write(directory / 'manifest_private.json', {'sample_mapping': mapping, 'host_only': True})
        return directory, request, mapping, full, continuation

    def run_one(self, worker_id, task_id):
        worker, job = self.workers[worker_id], self.jobs[task_id]
        directory, request, mapping, full, continuation = self.materialize(job)
        if worker['rounds'] >= 8:
            worker['conversation_history'].append(worker['conversation_id'])
            worker['conversation_id'], worker['rounds'] = None, 0
        prompt = continuation if worker['conversation_id'] else full
        (directory / 'prompt.txt').write_text(prompt, encoding='utf-8')
        agy = Path.home() / 'AppData/Local/agy/bin/agy.exe'
        command = [str(agy), '-p', prompt, '--model', self.cfg['model'], '--mode', 'accept-edits',
                   '--dangerously-skip-permissions', '--output-format', 'json', '--print-timeout', '600s',
                   '--log-file', str(directory / 'client.log')]
        resumed_id = worker['conversation_id']
        if resumed_id:
            command += ['--conversation', resumed_id]
        call = {'path': str(directory), 'worker_id': worker_id, 'started_at': now(), 'resumed_conversation_id': resumed_id}
        envelope, error, stdout, stderr = {}, None, b'', b''
        process = None
        started = time.monotonic()
        with self.condition:
            if self.stopped:
                job['state'] = 'ready'
                return False
            process = subprocess.Popen(command, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            self.processes[worker_id] = process
            call['pid'] = process.pid
            job['attempts'].append(call)
            worker['rounds'] += 1
            write(directory / 'launch.json', call)
            self.checkpoint()
        print(f'{worker_id} {task_id}: started, {len(mapping)} samples, resume={bool(resumed_id)}', flush=True)
        try:
            stdout, stderr = process.communicate(timeout=620)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill.exe', '/PID', str(process.pid), '/T', '/F'], capture_output=True,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            stdout, stderr = process.communicate()
            error = 'call_timeout'
        (directory / 'stdout.json').write_bytes(stdout)
        (directory / 'stderr.txt').write_bytes(stderr)
        try:
            envelope = json.loads(stdout.decode('utf-8-sig'))
        except (ValueError, UnicodeError):
            error = error or 'native_result_not_json'
        accepted, pending, raw = {}, {}, {}
        try:
            raw = read(directory / 'reviews_gemini.json')
            accepted, pending = validate_file(raw, request, mapping)
        except (ValueError, KeyError, TypeError) as exc:
            error = str(exc)
            pending = {r['source_sample_key']: error for r in mapping.values()}
        native_text = str(envelope.get('error', '')) + '\n' + stderr.decode('utf-8', errors='replace')
        if not accepted:
            native_text += '\n' + str(envelope.get('response', ''))
        kind = failure_kind(native_text) if envelope.get('status') != 'SUCCESS' else None
        conversation_id = envelope.get('conversation_id')
        session_error = None
        if conversation_id:
            if resumed_id and conversation_id != resumed_id:
                session_error = 'returned_conversation_id_mismatch'
            else:
                worker['conversation_id'] = conversation_id
        elif accepted:
            session_error = 'completed_file_but_missing_conversation_id'
        with self.condition:
            self.processes.pop(worker_id, None)
            call.update(finished_at=now(), elapsed_seconds=round(time.monotonic() - started, 2),
                        native_status=envelope.get('status'), native_error=envelope.get('error'),
                        conversation_id=conversation_id, usage=envelope.get('usage') or {}, error=error,
                        accepted_samples=len(accepted), pending_samples=len(pending), session_error=session_error)
            for identity, defects in accepted.items():
                job['accepted'][identity] = {'defects': defects, 'provenance': {'model': self.cfg['model'],
                    'conversation_id': conversation_id, 'worker_id': worker_id, 'call_path': str(directory),
                    'received_at': call['finished_at'], 'stage': job['stage'],
                    'native_status': call['native_status'], 'native_error': call['native_error']}}
                if request.get('secondary_merge_policy') == POLICY:
                    sample = next(k for k,r in mapping.items() if r['source_sample_key']==identity)
                    job['accepted'][identity].update(category_checks=raw['category_checks'][sample],
                        baseline_review=raw['reviews'][sample], secondary_merge_policy=POLICY)
                    job['accepted'][identity]['provenance']['prompt_revision'] = request['prompt_revision']
            job['pending'] = pending
            complete = len(job['accepted']) == len(job['source_sample_keys'])
            job['state'] = 'completed' if complete else 'retry_pending' if len(job['attempts']) < job.get('maximum_attempts',3) else 'needs_attention'
            if complete and job['stage'] == 'initial_rgb':
                for child_id, child in self.jobs.items():
                    if child['depends_on'] == task_id:
                        child['state'] = 'ready'
                        self.queues['secondary_chroma'].append(child_id)
            elif not complete and job['state'] == 'retry_pending' and not self.stopped and not kind and not session_error:
                self.queues[job['stage']].append(task_id)
            write(directory / 'result.json', call)
            write(directory / 'accepted.json', {'accepted': accepted, 'pending': pending})
            self.checkpoint()
            self.condition.notify_all()
        print(f'{worker_id} {task_id}: {len(job["accepted"])}/{len(job["source_sample_keys"])} accepted, {call["native_status"]}, {call["elapsed_seconds"]}s', flush=True)
        if kind or session_error:
            self.stop(kind or session_error)
        return complete

    def worker(self, worker_id):
        role = self.workers[worker_id]['role']
        while True:
            with self.condition:
                while not self.stopped and not self.queues[role]:
                    unfinished_initial = any(j['stage'] == 'initial_rgb' and j['state'] in ['ready', 'running', 'retry_pending'] for j in self.jobs.values())
                    running_same = any(j['stage'] == role and j['state'] == 'running' for j in self.jobs.values())
                    if not running_same and (role == 'initial_rgb' or not unfinished_initial):
                        return
                    self.condition.wait(timeout=5)
                if self.stopped:
                    return
                task_id = self.queues[role].popleft()
                self.jobs[task_id]['state'] = 'running'
                self.checkpoint()
            try:
                self.run_one(worker_id, task_id)
            except Exception as exc:
                with self.condition:
                    self.jobs[task_id]['state'] = 'needs_attention'
                    self.jobs[task_id]['host_error'] = repr(exc)
                    self.condition.notify_all()
                self.stop('host_error: ' + str(exc))
                return

    def run(self):
        # First actual secondary packet is part of the 384, not a separate probe.
        secondary_queue = self.queues['secondary_chroma']
        gate = next((k for k in secondary_queue if self.jobs[k]['attempts']), None) or next(iter(secondary_queue), None)
        if gate and not any(j['accepted'] for j in self.jobs.values()):
            self.queues['secondary_chroma'].remove(gate)
            self.jobs[gate]['state'] = 'running'
            if not self.run_one('W09', gate):
                self.stop('first_real_packet_incomplete')
        if not self.stopped:
            with ThreadPoolExecutor(max_workers=16) as pool:
                futures = [pool.submit(self.worker, worker_id) for worker_id in self.workers]
                for future in futures:
                    future.result()
        self.checkpoint()
        final = {identity: {**value, 'source_sample_key': identity, 'checked_categories': SIX,
                           'inspection_complete': True, 'annotation_contract': self.cfg['annotation_contract']}
                 for job in self.jobs.values() if job['stage'] == 'secondary_chroma' for identity, value in job['accepted'].items()}
        write(self.directory / 'visual_reviews.json', {'annotation_contract': self.cfg['annotation_contract'],
              'target_samples': 384, 'completed_samples': len(final), 'reviews': list(final.values()),
              'experiment_annotations_used': 0, 'complete': len(final) == 384})
        print(f'PILOT FINAL: {len(final)}/384 complete; stopped={self.stopped}; reason={self.stop_reason}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=PROJECT / 'runtime/pilot_384_20261015_01')
    parser.add_argument('--execute-authorized-pilot', action='store_true', required=True)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    pilot = Pilot(args.run.resolve(), args.resume)
    try:
        pilot.run()
    except KeyboardInterrupt:
        pilot.stop('user_interrupt')
        pilot.checkpoint()
