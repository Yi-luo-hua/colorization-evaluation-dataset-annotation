"""Rerun exactly the 48 rejected pilot finals using detailed prompts and one reused session."""
import argparse
from collections import Counter, deque
import copy
import shutil
import threading
from pathlib import Path

from prepare import PROJECT, read, write, sha, SIX
from pilot_runner import Pilot, now, failure_kind

REVISION = 'NR_detail_20261015_03'
SOURCE = PROJECT / 'runtime/pilot_384_20261015_01'
RUN = PROJECT / 'runtime/rerun48_detail_20261015_01'


class DetailRerun(Pilot):
    def __init__(self, directory, resume=False):
        self.directory = directory
        self.cfg = read(PROJECT / 'config.json')
        if self.cfg['stages']['secondary_chroma']['merge'] != 'replace_final_defect_list':
            raise ValueError('Retired free-relabel runner; use the corrected item-review workflow and original baseline')
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.processes = {}
        self.stopped, self.stop_reason = False, None
        self.queues = {'initial_rgb':deque(), 'secondary_chroma':deque()}
        self.inventory = {}
        if resume:
            state = read(directory / 'checkpoint.json')
            if state.get('stop_reason') == 'provider_access_rejected' and not read(directory/'authorization.json').get('provider_access_restored_confirmed'):
                raise ValueError('Provider location/access error unresolved; confirm access restored before resuming')
            self.jobs, self.workers, self.started_at = state['jobs'], state['workers'], state['started_at']
            for job in self.jobs.values():
                if job['state'] in ['running', 'ready', 'retry_pending', 'needs_attention'] and len(job['accepted']) < len(job['source_sample_keys']):
                    job['state'] = 'ready'
        else:
            if (directory / 'checkpoint.json').exists():
                raise ValueError('Existing rerun checkpoint; use --resume')
            authorization = read(directory / 'authorization.json')
            if authorization['quota_recovery_confirmation'] != '已恢复，按新版提示重跑这48条':
                raise ValueError('Quota recovery confirmation required')
            finals = read(SOURCE / 'visual_reviews.json')['reviews']
            selected = {r['source_sample_key'] for r in finals}
            assert len(selected) == 48
            previous = read(SOURCE / 'checkpoint.json')
            self.jobs = {}
            for number, source_id in enumerate(['T0009', 'T0011'], 1):
                original = previous['jobs'][source_id]
                source_packet = next(a['path'] for a in reversed(original['attempts']) if a.get('accepted_samples') == 24)
                identifier = f'R{number:04d}'
                self.jobs[identifier] = {'task_id':identifier, 'stage':'secondary_chroma', 'state':'ready',
                    'source_sample_keys':original['source_sample_keys'], 'accepted':{}, 'pending':{},
                    'attempts':[], 'depends_on':None, 'source_packet':source_packet, 'source_task_id':source_id}
            assert {k for j in self.jobs.values() for k in j['source_sample_keys']} == selected
            self.workers = {'W01':{'role':'secondary_chroma','conversation_id':None,'rounds':0,'conversation_history':[]}}
            self.started_at = now()
            (directory / 'prompts').mkdir()
            for name in ['session.md', 'secondary_chroma.md']:
                shutil.copy2(PROJECT / 'prompts' / name, directory / 'prompts' / name)
            write(directory / 'source_snapshot.json', {'source_run':str(SOURCE), 'source_reviews_sha256':sha(SOURCE / 'visual_reviews.json'),
                'prompt_revision':REVISION, 'prompt_hashes':{f.name:sha(f) for f in (directory/'prompts').glob('*.md')},
                'target_unique_samples':48, 'session_plan':'one fixed-role session, two rounds of 24; no padding',
                'boards':'exact copies of original 8 boards; no layout or CV change',
                'baseline':'original designated legacy reviewed file, not the rejected 48 model outputs'})
        for identifier, job in self.jobs.items():
            mapping = read(Path(job['source_packet']) / 'manifest_private.json')['sample_mapping']
            self.inventory.update({row['source_sample_key']:row for row in mapping.values()})
            if job['state'] in ['ready', 'retry_pending']:
                self.queues['secondary_chroma'].append(identifier)
        self.checkpoint()

    def checkpoint(self):
        with self.lock:
            completed = sum(len(j['accepted']) for j in self.jobs.values())
            state = 'stopped' if self.stopped else 'completed' if completed == 48 else 'running'
            write(self.directory / 'checkpoint.json', {'annotation_contract':self.cfg['annotation_contract'],
                'prompt_revision':REVISION, 'started_at':self.started_at,'updated_at':now(),'state':state,
                'stop_reason':self.stop_reason,'target_unique_samples':48,'final_completed':completed,
                'active_calls':len(self.processes),'jobs':self.jobs,'workers':self.workers,
                'job_states':dict(Counter(j['state'] for j in self.jobs.values())), 'new_unique_coverage':0})

    def materialize(self, job):
        remaining = [k for k in job['source_sample_keys'] if k not in job['accepted']]
        source = Path(job['source_packet'])
        original_mapping = read(source / 'manifest_private.json')['sample_mapping']
        # Original S numbers and full boards remain fixed on retries; completed rows are kept unchanged.
        mapping = {key:row for key,row in original_mapping.items() if row['source_sample_key'] in remaining}
        destination = self.directory / 'tasks' / job['task_id'] / f'attempt_{len(job["attempts"])+1:02d}'
        (destination / 'sheets').mkdir(parents=True)
        sheets = []
        for sheet in read(source / 'request.json')['sheets']:
            if not set(sheet['sample_keys']) & set(mapping):
                continue
            target = destination / 'sheets' / Path(sheet['path']).name
            shutil.copy2(sheet['path'], target)
            assert sha(target) == sheet['sha256']
            sheets.append({**sheet,'path':str(target.resolve())})
        prior = read(source / 'prior_reviews.json')
        prior['reviews'] = {key:prior['reviews'][key] for key in mapping}
        write(destination / 'prior_reviews.json', prior)
        packet_id = f'{job["task_id"]}-a{len(job["attempts"])+1:02d}'
        request = {'annotation_contract':self.cfg['annotation_contract'],'stage':'secondary_chroma',
            'packet_id':packet_id,'checked_categories':SIX,'sheets':sheets,'prompt_revision':REVISION}
        write(destination / 'request.json', request)
        write(destination / 'manifest_private.json', {'sample_mapping':mapping,'host_only':True})
        output = destination / 'reviews_gemini.json'
        write(output, {'schema_version':'delivery_review_compact_v2',
            **{k:request[k] for k in ['annotation_contract','stage','packet_id','prompt_revision']},
            'reviews':{key:None for key in mapping},'category_checks':{key:None for key in mapping}})
        common = (self.directory/'prompts/session.md').read_text(encoding='utf-8')
        role = (self.directory/'prompts/secondary_chroma.md').read_text(encoding='utf-8')
        listing = '\n'.join(s['path'] + ': ' + ', '.join(k for k in s['sample_keys'] if k in mapping) for s in sheets)
        current = (f'本轮packet_id={packet_id}，stage=secondary_chroma，契约={self.cfg["annotation_contract"]}。\n'
            f'本轮只处理这些S编号：{", ".join(mapping)}。看板其他编号不是本轮任务。\n'
            f'只修改结果文件：{output.resolve()}\n匿名旧标签：{(destination/"prior_reviews.json").resolve()}\n'
            '本轮指定看板（每张读一次）：\n' + listing + '\n'
            'reviews逐图详细填写所有成立的缺陷；category_checks逐图列齐六类status/evidence。'
            '无缺陷须六类逐项确认，不以空列表草率结束。保存后只回复“文件已保存”。')
        full = common + '\n' + role + '\n' + current
        continuation = ('继续固定二次角色，沿用NR_detail_20261015_03完整规则。每图详细检查六类，清晰L1也保留；'
            '多类别／多对象可共存，发现一项后继续检查。极其谨慎输出无缺陷，按本轮图重新判断。\n'
            + role + '\n' + current)
        return destination, request, mapping, full, continuation

    def run_one(self, worker_id, task_id):
        complete = super().run_one(worker_id, task_id)
        job = self.jobs[task_id]
        if job['attempts']:
            path = Path(job['attempts'][-1]['path'])
            raw = read(path / 'reviews_gemini.json')
            mapping = read(path / 'manifest_private.json')['sample_mapping']
            for key, row in mapping.items():
                identity = row['source_sample_key']
                if identity in job['accepted']:
                    job['accepted'][identity]['category_checks'] = raw['category_checks'][key]
                    job['accepted'][identity]['provenance']['prompt_revision'] = REVISION
            self.checkpoint()
        return complete

    def run(self):
        self.worker('W01')
        if any(j['state']=='needs_attention' for j in self.jobs.values()) and not self.stopped:
            latest_errors = [a.get('native_error','') for j in self.jobs.values() for a in j['attempts'][-1:]]
            if any(failure_kind(str(e)) == 'provider_access_rejected' for e in latest_errors):
                self.stop('provider_access_rejected')
        self.checkpoint()
        final = [{**value,'source_sample_key':identity,'checked_categories':SIX,'inspection_complete':True,
                  'annotation_contract':self.cfg['annotation_contract'],'prompt_revision':REVISION}
            for job in self.jobs.values() for identity,value in job['accepted'].items()]
        write(self.directory/'visual_reviews.json', {'annotation_contract':self.cfg['annotation_contract'],
            'prompt_revision':REVISION,'target_samples':48,'completed_samples':len(final),'complete':len(final)==48,
            'new_unique_coverage':0,'experiment_annotations_used':0,'reviews':final})
        previous = {r['source_sample_key']:r for r in read(SOURCE/'visual_reviews.json')['reviews']}
        write(self.directory/'comparison.json', {'source_run':str(SOURCE),'target_unique_samples':48,
            'completed_samples':len(final),'new_unique_coverage':0,
            'before_count_distribution':dict(Counter(len(r['defects']) for r in previous.values())),
            'after_count_distribution':dict(Counter(len(r['defects']) for r in final)),
            'before_categories':dict(Counter(d['id'] for r in previous.values() for d in r['defects'])),
            'after_categories':dict(Counter(d['id'] for r in final for d in r['defects'])),
            'matched_before_count_distribution':dict(Counter(len(previous[r['source_sample_key']]['defects']) for r in final)),
            'matched_before_total_defects':sum(len(previous[r['source_sample_key']]['defects']) for r in final),
            'records':[{'source_sample_key':r['source_sample_key'],'before':previous[r['source_sample_key']]['defects'],
                        'after':r['defects']} for r in final]})
        print(f'DETAIL RERUN: {len(final)}/48, stopped={self.stopped}, reason={self.stop_reason}',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-authorized-rerun',action='store_true',required=True)
    parser.add_argument('--resume',action='store_true')
    args = parser.parse_args()
    runner = DetailRerun(RUN,args.resume)
    try:
        runner.run()
    except KeyboardInterrupt:
        runner.stop('user_interrupt')
        runner.checkpoint()
