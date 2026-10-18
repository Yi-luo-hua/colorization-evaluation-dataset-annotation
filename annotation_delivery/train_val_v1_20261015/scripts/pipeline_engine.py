"""One executor for ingestion, fixed-role agy sessions, QA feedback and durable delivery."""
from concurrent.futures import ThreadPoolExecutor
import copy
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid

from prepare import PROJECT, ROOT, FOUR, SIX, read, write, sha, lines
from prepare_packets import render, RENDER_REVISION
from review_contract import validate_file,expand_category_checks
from visual_receipts import read_visual_receipts,path_key
from secondary_review import POLICY, REVISION, baseline_from_mapping, prepare_secondary_files, write_inheritance_guidance
from pipeline_store import Store, OwnerLock, now, pid_alive
from batch_auth import batch_environment, prepare_worker_profile, GUARD
from result_examples import prepare_example,example_instruction
from quota_control import explicit_exhaustion,pause_for_quota,allow_requested_start,cancel_automatic_resume,zero_windows
import pipeline_delivery

DEFAULT_RUN = PROJECT/'runtime/recovery5000_20261016_01'
LEGACY_BATCH = PROJECT/'runtime/batch5000_8sheets_20261016_01'
MANUAL_SESSION_FAULTS = {'location_unsupported','quota_exhausted'}
SESSION_RETRY_LIMIT = 5
SESSION_RETRY_POLICY = 'continue_five_then_pool_v4'
IDENTITY_FAULTS = {'conversation_identity_mismatch','missing_conversation_id'}
CONTEXT_TOKEN_LIMIT = 80000


def latest_context_usage(conversation, started_at, transcript=None):
    """Per-request input includes cached tokens; the CLI envelope is cumulative."""
    source=Path(transcript) if transcript else (
        Path.home()/'.gemini/antigravity-cli/brain'/str(conversation)/'.system_generated/logs/transcript_full.jsonl')
    latest=None
    if not source.exists():return None
    with source.open(encoding='utf-8') as stream:
        for line in stream:
            try:step=json.loads(line)
            except ValueError:continue
            if (step.get('type')!='PLANNER_RESPONSE' or step.get('source')!='MODEL'
                    or step.get('status')!='DONE' or step.get('created_at','')<started_at[:19]):continue
            input_tokens=step.get('input_tokens');cached=step.get('cache_read_tokens',0)
            if type(input_tokens) is not int or type(cached) is not int or input_tokens<0 or cached<0:continue
            latest={'conversation_id':conversation,'tokens':input_tokens+cached,
                'input_tokens':input_tokens,'cache_read_tokens':cached,
                'observed_at':step['created_at'],'step_index':step.get('step_index'),
                'source':'native latest completed request input including cache'}
    return latest


def failure_kind(text):
    if 'auth_browser_blocked' in text:
        return 'auth_browser_blocked'
    if explicit_exhaustion(text):
        return 'quota_exhausted'
    if re.search(r'(?:HTTP|status|code|error)[^\w\n]*429|429\s+Too Many Requests',text,re.I):
        return 'rate_limited'
    if re.search(r'User location is not supported|PERMISSION_DENIED|UNAUTHENTICATED',text,re.I):
        return 'provider_access_rejected'
    if re.search(r'connection.reset|connection.refused|\bEOF\b|wsasend|forcibly closed|no such host|dial tcp|proxyconnect|TLS handshake|network error|broken pipe|socket error|HTTP.?50[234]|service unavailable|bad gateway',text,re.I):
        return 'network_error'
    return None


def terminal_error_lines(text):
    """Only errors emitted by this owned call, excluding prompts and retry/telemetry diagnostics."""
    result=[]
    for line in text.splitlines():
        message=re.sub(r'^[IWEF]\d{4}\s+[^\]]*\]\s*','',line)
        if re.match(r'(?:agent executor error:|generating and executing:|Print mode: run ended with error|'
                r'(?:Error:\s*)?(?:RESOURCE_EXHAUSTED|Individual quota reached|User location is not supported|'
                r'PERMISSION_DENIED|UNAUTHENTICATED)\b)',message):
            result.append(line)
    return result


def live_failure_kind(text):
    """Observe explicit access failures without interrupting a running CLI."""
    for line in terminal_error_lines(text):
        kind=manual_stop_kind(line) or failure_kind(line)
        if kind in {'location_unsupported','quota_exhausted','provider_access_rejected'}:
            return kind
    return None


def native_error_scope(error, conversation, started_at, transcript=None):
    """The CLI envelope can contain the last error of an older conversation turn."""
    source = Path(transcript) if transcript else (
        Path.home()/'.gemini/antigravity-cli/brain'/str(conversation)/'.system_generated/logs/transcript_full.jsonl')
    if not error or not source.exists():
        return {'scope':'unverified'}
    matched = None
    with source.open(encoding='utf-8') as stream:
        for line in stream:
            try:
                step = json.loads(line)
            except ValueError:
                continue
            if step.get('type')=='ERROR_MESSAGE' and step.get('error')==error and step.get('created_at'):
                matched = step['created_at']
    if matched is None:
        return {'scope':'unverified'}
    error_at = datetime.fromisoformat(matched.replace('Z','+00:00'))
    start = datetime.fromisoformat(started_at.replace('Z','+00:00'))
    return {'scope':'historical' if error_at < start.replace(microsecond=0) else 'current_call',
        'error_at':matched,'transcript':str(source)}


def completed_call_error(native, error, complete):
    """Validated output completes the task; an error must not create an empty retry task."""
    if complete and not error and native.get('native_error'):
        stream=re.fullmatch(r'The stream was interrupted\.\s*Please continue the task you were working on\.',
            native['native_error'].strip())
        scope=native.get('native_error_scope',{}).get('scope','unverified')
        native['completion_warning']=('stream_interrupted_after_complete_result' if stream else
            scope+'_envelope_error_after_complete_result')
    if complete and error and error not in IDENTITY_FAULTS:
        stream=re.fullmatch(r'The stream was interrupted\.\s*Please continue the task you were working on\.',
            (native.get('native_error') or '').strip())
        native.update(session_error=None,completion_warning=(
            'stream_interrupted_after_complete_result' if stream else 'native_error_after_complete_result'),
            ignored_session_error=error)
        return None
    return error


def manual_stop_kind(text):
    if failure_kind(text)=='quota_exhausted':
        return 'quota_exhausted'
    if re.search(r'User location is not supported',text,re.I):
        return 'location_unsupported'
    return None


def fingerprint():
    paths = [Path(__file__),Path(__file__).with_name('pipeline_store.py'),Path(__file__).with_name('pipeline_delivery.py'),Path(__file__).with_name('pipeline_credentials.py'),Path(__file__).with_name('review_contract.py'),
        Path(__file__).with_name('result_examples.py'),
        Path(__file__).with_name('quota_control.py'),Path(__file__).with_name('native_quota_monitor.py'),
        Path(__file__).with_name('update_quota_snapshot.py'),
        Path(__file__).with_name('secondary_review.py'),Path(__file__).with_name('visual_receipts.py'),Path(__file__).with_name('prepare_packets.py'),
        Path(__file__).with_name('prepare.py'),Path(__file__).with_name('export_pilot.py'),
        Path(__file__).with_name('batch_auth.py'),GUARD,Path(__file__).parent/'native/browser_guard.go',
        ROOT/'experiments/cv_workflow/engine.py',ROOT/read(PROJECT/'config.json')['source_config'],PROJECT/'config.json',
        ROOT/'AGENTS.md',PROJECT/'AGENTS.md',
        *(PROJECT/'prompts').glob('*.md'),*(PROJECT/'prompts/examples').glob('*.json')]
    return {str(p.relative_to(ROOT)):sha(p) for p in paths}


def snapshot(store):
    # Compatibility artifact. SQLite is authoritative; dashboard never writes this file.
    rows = store.rows()
    data = store.summary()
    data['samples'] = {r['source_sample_key']:r for r in rows}
    write(store.run_dir/'checkpoint.json',data)
    write(store.run_dir/'needs_manual_attention.json',[r for r in rows if r['state']=='needs_manual'])


def return_for_review(store, key, reason, infrastructure=False):
    """Apply an explicit reviewer decision; never infer semantic labels in code."""
    with store.tx() as db:
        found=db.execute('SELECT body FROM samples WHERE key=?',(key,)).fetchone()
        if not found:
            raise ValueError('Sample outside the prepared scope')
        row=json.loads(found[0])
        if row['state']!='completed':
            raise ValueError('Only accepted visual results can be explicitly returned')
        row['returned_result']={k:row.get(k) for k in ['defects','baseline_review','category_checks','provenance']}
        row.update(state='secondary_chroma_ready',stage='secondary_chroma',ready_at=now(),
            defects=None,previous_review=row.get('baseline_review'),last_feedback=reason,
            qa_failures=row.get('qa_failures',0)+(0 if infrastructure else 1),
            failure_count=row.get('failure_count',0) if infrastructure else 1,worker_id=None,
            reviewer_return={'authority':'codex_explicit_review','reason':reason,'created_at':now(),
                'infrastructure':infrastructure})
        Store.put_sample(db,row)
        Store.put_meta(db,'state_updated_at',now())
    store.event('explicit_review_return',source_sample_key=key,reason=reason)


def initialize(store, rows, scope, extra=None):
    with store.tx() as db:
        if db.execute('SELECT count(*) FROM samples').fetchone()[0]:
            raise ValueError('Runtime already contains samples; preserve it and use reconcile/status')
        for row in rows:
            Store.put_sample(db,row)
        values = {'annotation_contract':read(PROJECT/'config.json')['annotation_contract'],
            'prompt_revision':REVISION,'render_revision':RENDER_REVISION,'scope':scope,'phase':'prepared',
            'stopped':True,'stop_reason':'续跑准备完成，尚未启动','owner_pid':None,'heartbeat_at':None,
            'state_updated_at':now(),'maximum_retries':2,'maximum_session_rounds':8,'worker_limit':16,
            'retry_limit':SESSION_RETRY_LIMIT,
            'legacy_source_sha256':sha(ROOT/'LS_lcad_reviewer/exports/reviewed_1_10000_clean.json'),
            'code_fingerprint':fingerprint(),'preflight':{'ready':False,'images_verified':False}}
        values.update(extra or {})
        for k,v in values.items():
            Store.put_meta(db,k,v)
    for i in range(1,17):
        store.worker(f'W{i:02d}',{'worker_id':f'W{i:02d}','role':'secondary_chroma','status':'idle',
            'conversation_id':None,'rounds':0,'pid':None,'current_task':None,'history':[]})


def migrate_batch(run_dir=DEFAULT_RUN, batch_dir=LEGACY_BATCH):
    """Read/revalidate legacy files; never alter them or recover JSON by guessing labels."""
    store = Store(run_dir)
    if store.rows():
        raise ValueError('Recovery runtime already prepared; use check/reconcile, never overwrite it')
    batch_dir = Path(batch_dir).resolve()
    manifest = read(batch_dir/'batch_manifest.json')
    source_hash = sha(ROOT/'LS_lcad_reviewer/exports/reviewed_1_10000_clean.json')
    inventory = {r['source_sample_key']:r for r in lines(PROJECT/'data/preparation_02/inventory.jsonl')}
    frozen_a = {r['source_sample_key'] for r in read(PROJECT/'data/preparation_02/fixed_A_final.json')['reviews']}
    old_checkpoint = read(PROJECT/'runtime/autonomous_pipeline_v1/checkpoint.json')
    old_completed = {k for k,v in old_checkpoint['samples'].items() if v['state']=='completed'}
    source_files, rows, rejected = {},[],[]
    counts = Counter()
    for job in manifest['packets']:
        directory = Path(job['dir'])
        mapping = read(directory/'manifest_private.json')['sample_mapping']
        request = read(directory/'request.json')
        accepted,pending,raw = {},{},{}
        parse_error = None
        try:
            raw = read(directory/'reviews_gemini.json')
            accepted,pending = validate_file(raw,request,mapping)
        except (ValueError,KeyError,TypeError) as exc:
            parse_error = str(exc)
            pending = {r['source_sample_key']:'原结果文件无效：'+parse_error for r in mapping.values()}
            counts['invalid_file_samples'] += len(mapping)
        if not isinstance(raw,dict):
            raw = {}
        for name in ['request.json','manifest_private.json','prior_reviews.json','reviews_gemini.json','prompt.txt']:
            path = directory/name
            if path.exists():
                source_files[str(path)] = sha(path)
                saved = store.run_dir/'legacy_inputs'/job['packet_id']/name
                saved.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(path,saved)
        for index,(local,record) in enumerate(mapping.items()):
            key = record['source_sample_key']
            canonical = inventory[key]
            if key in frozen_a or record['baseline']['source']['sha256']!=source_hash:
                raise ValueError('Frozen A or untrusted legacy baseline in secondary batch: '+key)
            for field in ['gt_path','model_path','gt_sha256','model_sha256','baseline']:
                if record[field]!=canonical[field]:
                    raise ValueError('Manifest no longer matches reviewed inventory: '+key+' / '+field)
            baseline = baseline_from_mapping({local:record})[local]
            if request['secondary_baseline'][local]!=baseline:
                raise ValueError('Secondary baseline mismatch: '+key)
            value = raw.get('reviews',{}).get(local)
            ok = key in accepted
            feedback = pending.get(key)
            qa_bad = bool(not ok and (parse_error or value is not None))
            row = {'source_sample_key':key,'sample_key':local,'record':copy.deepcopy(record),
                'stage':'secondary_chroma','state':'completed' if ok else 'secondary_chroma_ready',
                'group_id':job['packet_id']+f'-{index//24:02d}',
                'ready_at':now(),'legacy_packet':job['packet_id'],'legacy_result':str(directory/'reviews_gemini.json'),
                'baseline':baseline,'attempt_count':0,'qa_failures':int(qa_bad),'failure_count':int(qa_bad),
                'last_feedback':feedback,'defects':accepted.get(key),'worker_id':None,
                'baseline_review':value if ok else None,
                'category_checks':raw.get('category_checks',{}).get(local) if ok else None,
                'previous_review':value if not ok and isinstance(value,dict) else None,
                'provenance':{'model':'gemini-3.8-flash-high','source':'legacy_revalidated',
                    'result_path':str(directory/'reviews_gemini.json'),
                    'result_sha256':source_files.get(str(directory/'reviews_gemini.json')),
                    'legacy_conversation_id':None,'accepted_at':now()} if ok else None}
            rows.append(row)
            if ok:
                counts['completed'] += 1
                counts['recovered_unaggregated'] += key not in old_completed
            else:
                counts['returned_qa' if qa_bad else 'unwritten_pending'] += 1
                if key in old_completed:
                    counts['returned_previously_completed'] += 1
                rejected.append({'source_sample_key':key,'reason':feedback,'had_result':qa_bad,
                    'previously_completed':key in old_completed,'legacy_packet':job['packet_id']})
    keys = {r['source_sample_key'] for r in rows}
    if len(keys)!=len(rows) or len(rows)!=manifest['total_samples']:
        raise ValueError('Batch identity coverage mismatch')
    initialize(store,rows,{'batch_dir':str(batch_dir),'target':len(rows),'new_unique_coverage':0},
        {'legacy_source_files':source_files})
    write(store.run_dir/'reconciliation.json',{'counts':dict(counts),'samples':len(rows),
        'original_files_preserved':True,'semantic_labels_rewritten':False,'model_calls':0})
    write(store.run_dir/'returned_samples.json',rejected)
    for name in ['session.md','secondary_chroma.md','initial_rgb.md']:
        target = store.run_dir/'prompts'/name
        target.parent.mkdir(exist_ok=True)
        shutil.copy2(PROJECT/'prompts'/name,target)
    pipeline_delivery.export(store)
    snapshot(store)
    return store


def load_inventory(run_dir, inventory_dir):
    """Explicit all-scope ingestion; fixed human A bypasses rendering and model dispatch."""
    directory = Path(inventory_dir)
    if directory.resolve()!=(PROJECT/'data/preparation_02').resolve():
        raise ValueError('Only the active preparation_02 inventory may enter this workflow')
    inventory = lines(directory/'inventory.jsonl')
    fixed = {r['source_sample_key']:r for r in read(directory/'fixed_A_final.json')['reviews']}
    rows = []
    for i,record in enumerate(inventory):
        key = record['source_sample_key']
        if record['split'] not in ['train','val'] or record['model'] not in ['lcad','unicolor']:
            raise ValueError('Unexpected training/validation scope: '+key)
        human = fixed.get(key)
        stage = 'secondary_chroma' if record.get('baseline') else 'initial_rgb'
        rows.append({'source_sample_key':key,'sample_key':f'S{i%24+1:03d}','record':record,
            'stage':stage,'state':'fixed_a' if human else stage+'_ready','group_id':f'{stage}-{i//24:06d}',
            'ready_at':now(),'attempt_count':0,'qa_failures':0,'failure_count':0,'last_feedback':None,
            'baseline':baseline_from_mapping({'S':record})['S'] if record.get('baseline') else None,
            'defects':human['defects'] if human else None,'provenance':human['provenance'] if human else None})
    store = Store(run_dir)
    initialize(store,rows,{'inventory':str(directory.resolve()),'target':len(rows)})
    for name in ['session.md','secondary_chroma.md','initial_rgb.md']:
        target = store.run_dir/'prompts'/name; target.parent.mkdir(exist_ok=True)
        shutil.copy2(PROJECT/'prompts'/name,target)
    pipeline_delivery.export(store); snapshot(store)
    return store


def preflight(store, verify_images=False):
    meta = store.meta()
    if meta.get('code_fingerprint')!=fingerprint():
        raise ValueError('Implementation/prompt/config changed since preparation; reconcile in a new run')
    if meta['legacy_source_sha256']!=sha(ROOT/'LS_lcad_reviewer/exports/reviewed_1_10000_clean.json'):
        raise ValueError('Designated reviewed baseline changed')
    rows = store.rows()
    if not rows or len({r['source_sample_key'] for r in rows})!=len(rows):
        raise ValueError('Missing or duplicate prepared scope')
    if any(r['state'].endswith('_running') for r in rows):
        raise ValueError('Interrupted claims must be reconciled before dispatch')
    checked = set()
    if verify_images:
        for i,row in enumerate(rows,1):
            for path_field,hash_field in [('gt_path','gt_sha256'),('model_path','model_sha256')]:
                record = row['record']; path = ROOT/record[path_field]
                if str(path) not in checked:
                    if sha(path)!=record[hash_field]:
                        raise ValueError('Image changed: '+row['source_sample_key'])
                    checked.add(str(path))
            if i%1000==0:
                print(f'Preflight image hashes: {i}/{len(rows)}',flush=True)
    report = {'ready':True,'checked_at':now(),'samples':len(rows),
        'images_verified':verify_images or meta.get('preflight',{}).get('images_verified',False),
        'unique_images_checked':len(checked) if verify_images else meta.get('preflight',{}).get('unique_images_checked',0),
        'model_calls':0,'semantic_accuracy_verified':False}
    store.update_meta(preflight=report)
    write(store.run_dir/'preflight.json',report)
    return report


def recover_interrupted(store, worker_id=None):
    rows = [r for r in store.rows() if r['state'].endswith('_running')
        and (worker_id is None or r.get('worker_id')==worker_id)]
    workers = {key:w for key,w in store.summary()['workers'].items()
        if worker_id is None or key==worker_id}
    for worker in workers.values():
        if pid_alive(worker.get('pid')):
            raise RuntimeError('Previous annotation process is still alive; refusing duplicate dispatch')
    groups = {}
    for row in rows:
        groups.setdefault(row.get('last_attempt'),[]).append(row)
    recovered = 0
    for directory,claimed in groups.items():
        path = Path(directory) if directory else None
        if path and (path/'request.json').exists() and (path/'manifest_private.json').exists():
            request = read(path/'request.json')
            mapping = read(path/'manifest_private.json')['sample_mapping']
            native = read(path/'native_result.json') if (path/'native_result.json').exists() else (
                read(path/'launch.json') if (path/'launch.json').exists() else {'started':False})
            if pid_alive(native.get('pid')):
                raise RuntimeError('Interrupted attempt still has a live process; reconcile after it exits')
            Executor(store).accept(claimed,path,request,mapping,native,interrupted=True)
            recovered += len(claimed)
        else:
            with store.tx() as db:
                for row in claimed:
                    row.update(state=row['stage']+'_ready',worker_id=None,last_feedback='未启动的中断任务已回池')
                    Store.put_sample(db,row)
    for key,worker in workers.items():
        worker.update(status=('awaiting_continue' if worker.get('pending_resume') else
            'session_blocked' if worker.get('status')=='session_blocked' else 'idle'),pid=None,current_task=None)
        store.worker(key,worker)
    store.event('interruption_reconciled',worker_id=worker_id,claimed=len(rows),harvested_attempt_rows=recovered)


def validate_initial(raw, request, mapping):
    # Initial completion covers B/C/D/F only, with the same observation/description checks.
    return validate_file(raw,request,mapping)


class Executor:
    RETRY_DELAY_SECONDS=20
    def __init__(self, store, workers=16, process_factory=subprocess.Popen, model=None, maximum_batches=None, sample_scope=None, continue_blocked=False, resume_workers=None, auto_resume_pending=False, resume_retry_offsets=None):
        self.store = store
        if workers<1 or workers>16:
            raise ValueError('Shared concurrency must be 1..16')
        self.worker_limit = workers
        self.process_factory = process_factory
        self.cfg = read(PROJECT/'config.json')
        if model:
            self.cfg['model'] = model
        if maximum_batches is not None and (maximum_batches<1 or workers!=1):
            raise ValueError('A limited trial requires one worker and a positive batch count')
        self.maximum_batches = maximum_batches
        self.sample_scope = sample_scope
        self.continue_blocked = continue_blocked
        self.resume_workers=set(resume_workers or [])
        self.auto_resume_pending=auto_resume_pending
        self.resume_retry_offsets=resume_retry_offsets or {}
        self.worker_workspace = Path(os.environ.get('LOCALAPPDATA',str(Path.home())))/'MCLAnnotation/worker_context_v5'
        self.worker_profile = self.worker_workspace.parent/'worker_profile_v1'
        self.cv = read(ROOT/self.cfg['source_config'])
        self.stopped = threading.Event()
        self.process_lock = threading.RLock()
        self.processes = {}
        self.reason = None
        self.dirty = threading.Event()

    def terminate(self, proc):
        if proc.poll() is not None:
            return
        if os.name=='nt':
            subprocess.run(['taskkill.exe','/PID',str(proc.pid),'/T','/F'],capture_output=True,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        else:
            proc.terminate()

    def stop(self, reason):
        with self.process_lock:
            if reason in ['user_pause','user_interrupt']:
                cancel_automatic_resume(self.store)
            if not self.stopped.is_set():
                self.reason = reason
                self.stopped.set()
                self.store.update_meta(phase='pausing',stopped=True,stop_reason=reason,state_updated_at=now())
                self.store.event('stop_requested',reason=reason)
            for proc in list(self.processes.values()):
                self.terminate(proc)

    def reset_session(self, worker, reason, directory=None):
        """Retire only this conversation; two fresh-session retries, then isolate its lane."""
        conversation = worker.get('conversation_id')
        if conversation:
            worker.setdefault('history',[]).append(conversation)
        failures = worker.get('consecutive_session_failures',0)+1
        blocked = failures>2
        worker.update(conversation_id=None,rounds=0,pid=None,current_task=None,
            status='session_blocked' if blocked else 'idle',
            consecutive_session_failures=failures,last_session_error=reason)
        self.store.worker(worker['worker_id'],worker)
        self.store.event('session_isolated' if blocked else 'session_restart',
            worker_id=worker['worker_id'],reason=reason,retired_conversation_id=conversation,
            consecutive_failures=failures,attempt=str(directory) if directory else None)

    def materialize(self, worker, rows):
        stage = rows[0]['stage']
        attempt_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+worker['worker_id']+'_'+uuid.uuid4().hex[:8]
        directory = self.store.run_dir/'attempts'/attempt_id
        (directory/'sheets').mkdir(parents=True)
        records = [copy.deepcopy(r['record']) for r in rows]
        sheets = render(records,stage,directory/'sheets',self.cfg,self.cv)
        assert len(sheets)<=4
        mapping = {f'S{i:03d}':r for i,r in enumerate(records,1)}
        request = {'annotation_contract':self.cfg['annotation_contract'],'stage':stage,'packet_id':attempt_id,
            'prompt_revision':REVISION,'render_revision':RENDER_REVISION,'candidate_overlays':False,
            'compact_transport':'explicit_checks_v1','require_visual_receipts':True,
            'checked_categories':SIX if stage=='secondary_chroma' else FOUR,'sheets':sheets,
            'result_file':str((directory/'reviews_gemini.json').resolve())}
        if stage=='secondary_chroma':
            prepare_secondary_files(directory,request,mapping)
        else:
            write(directory/'reviews_gemini.json',{'schema_version':'delivery_review_compact_v2',
                **{k:request[k] for k in ['annotation_contract','stage','packet_id']},
                'prompt_revision':request['prompt_revision'],
                'reviews':{key:None for key in mapping},'category_checks':{key:None for key in mapping}})
        feedback = {local:{'reason':r.get('last_feedback'),'previous_review':r.get('previous_review')}
            for local,r in zip(mapping,rows) if r.get('last_feedback')}
        write(directory/'retry_feedback.json',feedback)
        write(directory/'manifest_private.json',{'sample_mapping':mapping,'host_only':True})
        request['allowed_read_files'] = [s['path'] for s in sheets]+[str((directory/'retry_feedback.json').resolve())]
        if stage=='secondary_chroma':
            request['allowed_read_files'].append(str((directory/'prior_reviews.json').resolve()))
        prepare_example(directory,request)
        write(directory/'request.json',request)
        role = (self.store.run_dir/'prompts'/f'{stage}.md').read_text(encoding='utf-8')
        common = (self.store.run_dir/'prompts/session.md').read_text(encoding='utf-8')
        signature=hashlib.sha256((common+'\n'+role).encode('utf-8')).hexdigest()
        same_rules=worker.get('conversation_id') and worker.get('context_signature')==signature
        worker['context_signature']=signature
        listing = '\n'.join(s['path']+': '+', '.join(s['sample_keys']) for s in sheets)
        prompt = (('继续同一固定角色会话。本轮S编号重新对应。保留本会话规则及紧凑传输格式。\n' if same_rules else common+'\n'+role+'\n')+
            f'\npacket_id={attempt_id}。只修改{request["result_file"]}。\n'
            +example_instruction(request)
            +(f'先读取匿名原底稿：{(directory/"prior_reviews.json").resolve()}\n' if stage=='secondary_chroma' else '')+
            f'读取逐样本打回反馈：{(directory/"retry_feedback.json").resolve()}。这是未通过的历史尝试，只供定向纠正，不替换原底稿。\n'
            '本轮只标下面S编号，每张看板只读一次，不查manifest或源图，不执行命令：\n'+listing+
            '\n对打回原因逐项纠正；仍须按本阶段规则完整检查。保存后仅回复“文件已保存”。')
        (directory/'prompt.txt').write_text(prompt,encoding='utf-8')
        return directory,request,mapping,prompt

    def accept(self, rows, directory, request, mapping, native, interrupted=False):
        raw,accepted,pending = {},{},{}
        try:
            raw = read(directory/'reviews_gemini.json')
            accepted,pending = (validate_file if request['stage']=='secondary_chroma' else validate_initial)(raw,request,mapping)
            if request.get('require_visual_receipts'):
                proof=read_visual_receipts(native.get('conversation_id'),request['sheets'])
                native['visual_receipts']=proof
                missing={path_key(p) for p in proof['missing']}
                for sheet in request['sheets']:
                    if path_key(sheet['path']) in missing:
                        for local in sheet['sample_keys']:
                            identity=mapping[local]['source_sample_key']
                            accepted.pop(identity,None)
                            pending[identity]='missing successful visual read receipt: '+Path(sheet['path']).name
        except (ValueError,KeyError,TypeError) as exc:
            pending = {r['source_sample_key']:'结果文件/契约无效：'+str(exc) for r in mapping.values()}
        if native.get('session_error') in IDENTITY_FAULTS:
            accepted={}
            pending={r['source_sample_key']:native['session_error'] for r in mapping.values()}
        if not isinstance(raw,dict):
            raw = {}
        previous = {r['source_sample_key']:r for r in rows}
        maximum_failures = self.store.meta()['maximum_retries']+1
        with self.store.tx() as db:
            for local,record in mapping.items():
                key = record['source_sample_key']
                if key not in previous:
                    continue
                row = previous[key]
                row.update(worker_id=None,ready_at=now())
                row['attempt_count'] = row.get('attempt_count',0)+int(native.get('started',False))
                row['last_attempt'] = str(directory)
                if key in accepted:
                    row['failure_count'] = 0
                    row['last_feedback'] = None
                    row['previous_review'] = None
                    if request['stage']=='initial_rgb':
                        row['initial_defects'] = accepted[key]
                        row['initial_provenance'] = native
                        row['record']['baseline'] = {'source':{'kind':'new_initial_NR_review','attempt':str(directory)},'defects':accepted[key]}
                        row['stage'] = 'secondary_chroma'
                        row['state'] = 'secondary_chroma_ready'
                        row['baseline'] = baseline_from_mapping({'S':row['record']})['S']
                    else:
                        checks=expand_category_checks(accepted[key],raw['category_checks'][local],request['checked_categories'],
                            request.get('compact_transport')=='explicit_checks_v1')
                        row.update(state='completed',defects=accepted[key],baseline_review=raw['reviews'][local],
                            category_checks=checks,provenance={**native,'accepted_at':now(),
                                'result_path':str(directory/'reviews_gemini.json'),
                                'result_sha256':sha(directory/'reviews_gemini.json')})
                else:
                    row['state'] = request['stage']+'_ready'
                    row['last_feedback'] = pending[key]
                    row['previous_review'] = raw.get('reviews',{}).get(local) if isinstance(raw.get('reviews'),dict) else None
                    if not interrupted:
                        row['failure_count'] = row.get('failure_count',0)+1
                        row['qa_failures'] = row.get('qa_failures',0)+1
                        if row['failure_count']>=maximum_failures:
                            row['state'] = 'needs_manual'
                Store.put_sample(db,row)
            Store.put_meta(db,'state_updated_at',now())
        write(directory/'acceptance.json',{'accepted_keys':list(accepted),'pending':pending,
            'interrupted':interrupted,'validated_with_full_contract':request['stage']=='secondary_chroma'})
        self.dirty.set()
        return len(set(accepted)&set(previous)),len(set(pending)&set(previous))

    def _execute_agy(self, worker, directory, command, log_file, stdout_file, stderr_file, resumed_conv, stage):
        native = {'model':self.cfg['model'],'worker_id':worker['worker_id'],'stage':stage,
            'resumed_conversation_id':resumed_conv,'started_at':now(),'started':False}
        session_error = None
        observed_error = None
        auth_marker=log_file.with_suffix('.auth_blocked.json')
        with stdout_file.open('wb') as stdout, stderr_file.open('wb') as stderr:
            with self.process_lock:
                quota_meta=self.store.meta()
                if zero_windows(quota_meta.get('quota_snapshot') or {}):
                    pause_for_quota(self.store,quota_meta['quota_snapshot'],'before_native_dispatch',force=True)
                if self.store.meta().get('quota_guard',{}).get('waiting_for_recovery'):
                    self.stop('quota_exhausted')
                if self.stopped.is_set():
                    return native, 'stopped', None
                self.worker_workspace.mkdir(parents=True,exist_ok=True)
                (self.worker_workspace/'AGENTS.md').write_text(
                    '只执行本轮明确提供的图像标注任务，以首轮及固定角色提示为准。只读取本轮列出的PNG、格式示例、结果骨架、匿名底稿和反馈；'
                    '只写指定结果文件，不遍历目录、不读源图或源码、不执行命令、不调用外部服务。'
                    '每张看板一次，后续补写利用当前会话已看过的上下文。保存后只回复文件已保存。',encoding='utf-8')
                settings=self.worker_workspace/'.agents'
                settings.mkdir(exist_ok=True)
                write(settings/'mcp_config.json',{'mcpServers':{}})
                prepare_worker_profile(self.worker_profile)
                child_env=batch_environment(auth_marker,self.worker_profile)
                proc = self.process_factory(command,cwd=self.worker_workspace,stdout=stdout,stderr=stderr,
                    env=child_env,
                    creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                self.processes[worker['worker_id']] = proc
                native.update(started=True,pid=proc.pid)
                worker.update(status='running',pid=proc.pid,current_task=directory.name,started_at=native['started_at'])
                worker['context_rotation_eligible']=False
                self.store.worker(worker['worker_id'],worker)
            log_offset=0
            log_fragment=''
            while proc.poll() is None:
                if self.stopped.is_set():
                    self.terminate(proc)
                if auth_marker.exists():
                    session_error='auth_browser_blocked'
                    observed_error='auth_browser_blocked'
                    self.terminate(proc)
                if log_file.exists():
                    with log_file.open('rb') as stream:
                        stream.seek(log_offset)
                        text = log_fragment+stream.read().decode('utf-8',errors='replace')
                        log_offset=stream.tell()
                        log_fragment=text.rsplit('\n',1)[-1]
                        kind = live_failure_kind(text)
                    if not worker.get('conversation_id'):
                        m_conv = re.search(r'(?:Created conversation|conversation=)([0-9a-f-]{36})', text)
                        if m_conv:
                            worker['conversation_id'] = m_conv.group(1)
                            self.store.worker(worker['worker_id'], worker)
                    if kind:
                        observed_error=kind
                    quota_lines=[line for line in terminal_error_lines(text) if explicit_exhaustion(line)]
                    if quota_lines:
                        pause_for_quota(self.store,{'native_error':quota_lines[-1],'log_file':str(log_file)},
                            'native terminal quota error')
                        self.stop('quota_exhausted')
                time.sleep(0.2)
            proc.wait()
        with self.process_lock:
            self.processes.pop(worker['worker_id'],None)
        envelope = {}
        try:
            envelope = read(stdout_file)
        except (ValueError,TypeError):
            pass
        conversation = envelope.get('conversation_id') or resumed_conv or worker.get('conversation_id')
        error_scope = native_error_scope(envelope.get('error'),conversation,native['started_at'])
        client_text=log_file.read_text(encoding='utf-8',errors='replace') if log_file.exists() else ''
        current_lines=terminal_error_lines(client_text)+terminal_error_lines(
            stderr_file.read_text(encoding='utf-8',errors='replace'))
        raw_error=str(envelope.get('error') or '')
        matching=[line for line in current_lines if raw_error and raw_error in line]
        if matching:
            error_scope={'scope':'current_call','source':'owned native terminal log',
                'log_file':str(log_file),'error_line':matching[-1]}
        native['native_error_scope'] = error_scope
        # The envelope is conversation-wide. An unknown timestamp is never proof of a new fault.
        text='\n'.join(current_lines)
        if error_scope['scope']=='current_call':text+='\n'+raw_error
        native['current_error_evidence']=current_lines[-3:]
        native['effective_error']=text.strip() or None
        kind = failure_kind(text)
        if explicit_exhaustion(text):
            pause_for_quota(self.store,{'native_error':text},'native quota error')
            self.stop('quota_exhausted')
        if auth_marker.exists():
            session_error='auth_browser_blocked'
            native['auth_browser_guard']={'blocked':True,'marker':str(auth_marker)}
            kind='auth_browser_blocked'
        stop_kind=manual_stop_kind(text)
        if stop_kind:
            session_error=stop_kind
        elif kind:
            session_error = kind
        logged_conversation = None
        if not envelope.get('conversation_id') and not resumed_conv and log_file.exists():
            sent = re.search(r'(?m)^I\d{4} [^\n]*conversation_manager\.go:\d+\] Forwarding user message to conversation ([0-9a-f-]{36}) \(',
                log_file.read_text(encoding='utf-8',errors='replace'))
            if sent:
                logged_conversation = sent.group(1)
        conversation = envelope.get('conversation_id') or resumed_conv or logged_conversation or worker.get('conversation_id')
        if resumed_conv and conversation and conversation!=resumed_conv:
            session_error = 'conversation_identity_mismatch'
            native['reported_conversation_id']=conversation
            conversation=resumed_conv
        elif not conversation:
            session_error = 'missing_conversation_id'
        if not self.stopped.is_set() and (proc.returncode!=0 or (
                envelope.get('status')=='ERROR' and (error_scope['scope']=='current_call' or not raw_error))):
            session_error = session_error or 'native_call_failed'
        native.update(finished_at=now(),returncode=proc.returncode,native_status=envelope.get('status'),
            native_error=envelope.get('error'),conversation_id=conversation,usage=envelope.get('usage',{}),
            session_error=session_error,observed_transient_error=observed_error)
        if conversation and session_error not in IDENTITY_FAULTS:
            context=latest_context_usage(conversation,native['started_at'])
            if context:
                native['context_usage']=context
                worker['context_usage']=context
                self.store.worker(worker['worker_id'],worker)
        if logged_conversation:
            native['conversation_id_source']='owned native log, forwarded user message'
        usage=envelope.get('usage')
        if usage and session_error not in IDENTITY_FAULTS:
            previous=worker.get('last_usage',{}) if worker.get('usage_conversation_id')==conversation else {}
            native['incremental_usage']={key:max(0,value-previous.get(key,0)) for key,value in usage.items()}
            # Error envelopes may report zero; keep the cumulative high-water mark.
            worker.update(last_usage={key:max(value,previous.get(key,0)) for key,value in usage.items()},
                usage_conversation_id=conversation)
            self.store.worker(worker['worker_id'],worker)
        return native, session_error, conversation

    def _call_native(self, worker, directory, command, log_file, stdout_file, stderr_file, resumed_conv, stage):
        try:
            return self._execute_agy(worker,directory,command,log_file,stdout_file,stderr_file,resumed_conv,stage)
        except OSError as exc:
            reason=failure_kind(str(exc)) or 'native_launch_error'
            conversation=resumed_conv or worker.get('conversation_id')
            return {'model':self.cfg['model'],'worker_id':worker['worker_id'],'stage':stage,
                'started':False,'native_status':'ERROR','native_error':str(exc),
                'session_error':reason,'conversation_id':conversation,'finished_at':now()},reason,conversation

    def wait_for_retry(self,worker,index,reason):
        worker['continue_retry']={'attempt':index,'limit':SESSION_RETRY_LIMIT,'reason':reason or 'incomplete_result',
            'next_at':(datetime.now(timezone.utc)+timedelta(seconds=self.RETRY_DELAY_SECONDS)).isoformat(),
            'interval_seconds':self.RETRY_DELAY_SECONDS}
        worker.update(status='retry_wait',pid=None,retry_count=index)
        self.store.worker(worker['worker_id'],worker)
        return not self.stopped.wait(self.RETRY_DELAY_SECONDS)

    def run_one(self, worker, rows, resume_attempt=None, retry_offset=0):
        if not retry_offset:
            worker.pop('continue_retry',None)
            worker['retry_count']=0
        call_tag=''
        if resume_attempt:
            directory=Path(resume_attempt['attempt'])
            request=read(directory/'request.json')
            mapping=read(directory/'manifest_private.json')['sample_mapping']
            if request['stage']=='secondary_chroma':
                write_inheritance_guidance(directory,request)
            prepare_example(directory,request)
            write(directory/'request.json',request)
            call_tag='_manual_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')+'_'+uuid.uuid4().hex[:6]
            prompt=('继续。接续当前会话的原任务，仅补写尚未完成项，保留已通过项。'
                '成功读过的看板不要重读；未成功读取的看板必须各读一次再标注。'
                '重新查看原prior_reviews.json的逐P inherit_allowed；false时按格式示例显式填写object、description，禁止inherit。'
                +example_instruction(request)
                +f'先读{directory / "continuation_feedback.json"}，只写{request["result_file"]}。')
            worker['conversation_id']=resume_attempt['conversation_id']
            if not worker['conversation_id']:
                prompt=((self.store.run_dir/'prompts/session.md').read_text(encoding='utf-8')+'\n'+
                    (self.store.run_dir/'prompts'/f'{request["stage"]}.md').read_text(encoding='utf-8')+'\n'+
                    (directory/'prompt.txt').read_text(encoding='utf-8')+'\n'+prompt)
        else:
            directory,request,mapping,prompt = self.materialize(worker,rows)
        with self.store.tx() as db:
            for row in rows:
                row['last_attempt'] = str(directory)
                Store.put_sample(db,row)
        resumed = worker.get('conversation_id')
        agy = Path.home()/'AppData/Local/agy/bin/agy.exe'
        base_cmd = [str(agy),'--model',self.cfg['model'],'--mode','accept-edits',
            '--dangerously-skip-permissions','--output-format','json','--print-timeout','0']

        cmd0 = base_cmd + ['-p',prompt,'--log-file',str(directory/f'client{call_tag}.log')]
        if resumed:
            cmd0 += ['--conversation',resumed]
        write(directory/f'launch{call_tag}.json',{'model':self.cfg['model'],'worker_id':worker['worker_id'],
            'stage':request['stage'],'resumed_conversation_id':resumed,'started_at':now()})

        if retry_offset:
            if not self.wait_for_retry(worker,retry_offset,resume_attempt['reason']):
                return
            self.store.event('session_continue_retry',worker_id=worker['worker_id'],conversation_id=resumed,
                retry_index=retry_offset,reason=resume_attempt['reason'],attempt=str(directory))
        native, session_error, conversation = self._call_native(
            worker, directory, cmd0, directory/f'client{call_tag}.log', directory/f'stdout{call_tag}.json',
            directory/f'stderr{call_tag}.txt', resumed, request['stage'])
        if resume_attempt and not conversation:
            conversation=resumed
            native['conversation_id']=conversation

        frozen = read(directory/'accepted_partial.json') if (directory/'accepted_partial.json').exists() else {}
        def result_progress():
            if native.get('session_error') in IDENTITY_FAULTS:
                return False,{r['source_sample_key']:native['session_error'] for r in mapping.values()}
            try:
                raw = read(directory/'reviews_gemini.json')
                for local,value in frozen.items():
                    raw['reviews'][local],raw['category_checks'][local] = copy.deepcopy(value)
                accepted, pending = (validate_file if request['stage']=='secondary_chroma' else validate_initial)(raw,request,mapping)
                if request.get('require_visual_receipts'):
                    proof=read_visual_receipts(conversation,request['sheets'])
                    native['visual_receipts']=proof
                    missing={path_key(p) for p in proof['missing']}
                    for sheet in request['sheets']:
                        if path_key(sheet['path']) in missing:
                            for local in sheet['sample_keys']:
                                identity=mapping[local]['source_sample_key']
                                accepted.pop(identity,None)
                                pending[identity]='missing successful visual read receipt: '+Path(sheet['path']).name
                for local,record in mapping.items():
                    if record['source_sample_key'] in accepted:
                        frozen[local] = copy.deepcopy((raw['reviews'][local],raw['category_checks'][local]))
                if frozen:
                    write(directory/'reviews_gemini.json',raw)
                    write(directory/'accepted_partial.json',frozen)
                return len(accepted)==len(mapping),pending
            except Exception as exc:
                expected={'schema_version':'delivery_secondary_review_delta_v1' if request['stage']=='secondary_chroma'
                    else 'delivery_review_compact_v2',
                    **{key:request[key] for key in ['annotation_contract','stage','packet_id','prompt_revision']}}
                return False,{'file':f'结果校验未通过：{exc}。顶层必须保留：'
                    +json.dumps(expected,ensure_ascii=False)
                    +'。保留已完成项，只修复指出的字段、文件语法及未完成项，不重新读图。'}

        # A fault episode gets five same-conversation continuations; success resets the next episode.
        continue_retries = retry_offset
        complete,pending = result_progress()
        session_error=completed_call_error(native,session_error,complete)
        if not self.stopped.is_set() and (session_error or not complete):
            target_conv = conversation or resumed
            if target_conv:
                for retry_i in range(retry_offset+1, SESSION_RETRY_LIMIT+1):
                    if self.stopped.is_set():
                        break
                    if not self.wait_for_retry(worker,retry_i,session_error):
                        break
                    continue_retries += 1
                    self.store.event('session_continue_retry', worker_id=worker['worker_id'],
                        conversation_id=target_conv, retry_index=retry_i, reason=session_error,
                        attempt=str(directory))
                    feedback_file=directory/'continuation_feedback.json'
                    anonymous_pending={local:pending[record['source_sample_key']] for local,record in mapping.items()
                        if record['source_sample_key'] in pending}
                    if 'file' in pending:anonymous_pending['file']=pending['file']
                    unread=native.get('visual_receipts',{}).get('missing',[])
                    write(feedback_file,{'packet_id':request['packet_id'],'pending':anonymous_pending,
                        'accepted_sample_keys':list(frozen),'result_file':request['result_file'],
                        'format_example_file':request['format_example_file'],'unread_sheets':unread})
                    reminder=('继续。仅补写本轮未完成项或修复结果JSON，保留已通过项。'
                        '已成功读过的看板不要重读；反馈列出的unread_sheets尚未成功读取，必须各读一次再标注，不能凭底稿猜标签。'
                        f'本轮packet_id={request["packet_id"]}，只写{request["result_file"]}。'
                        +example_instruction(request)
                        +f'先读定向反馈{feedback_file.resolve()}。')
                    retry_cmd = base_cmd + ['-p',reminder,'--log-file',str(directory/f'client{call_tag}_retry{retry_i}.log'),
                        '--conversation',target_conv]
                    retry_native, retry_err, retry_conv = self._call_native(
                        worker, directory, retry_cmd, directory/f'client{call_tag}_retry{retry_i}.log',
                        directory/f'stdout{call_tag}_retry{retry_i}.json', directory/f'stderr{call_tag}_retry{retry_i}.txt',
                        target_conv, request['stage'])
                    if retry_conv:
                        target_conv = retry_conv
                        conversation = retry_conv
                    write(directory/f'native_result{call_tag}_retry{retry_i}.json', retry_native)
                    session_error = retry_err
                    any_started=bool(native.get('started') or retry_native.get('started'))
                    native=copy.deepcopy(retry_native)
                    native['started']=any_started
                    complete,pending = result_progress()
                    session_error=completed_call_error(native,session_error,complete)
                    if complete and not session_error:
                        break

        if not complete:
            if native.get('visual_receipts',{}).get('missing'):
                session_error=session_error or 'unread_visual_input'
            try:
                raw=read(directory/'reviews_gemini.json')
                if all(value is None for value in raw.get('reviews',{}).values()):
                    session_error=session_error or 'incomplete_result'
            except (ValueError,TypeError):
                if frozen:
                    shutil.copy2(directory/'reviews_gemini.json',directory/'invalid_final_result.json')
                    raw={'schema_version':'delivery_secondary_review_delta_v1' if request['stage']=='secondary_chroma' else 'delivery_review_compact_v2',
                        **{k:request[k] for k in ['annotation_contract','stage','packet_id','prompt_revision']},
                        'reviews':{key:None for key in mapping},'category_checks':{key:None for key in mapping}}
                    for key,value in frozen.items():raw['reviews'][key],raw['category_checks'][key]=value
                    write(directory/'reviews_gemini.json',raw)

        native['continue_retries'] = continue_retries
        native['packet_id']=directory.name
        if call_tag:
            write(directory/f'native_result{call_tag}.json',native)
        write(directory/'native_result.json',native)
        pause_reason=(session_error or 'incomplete_result') if not self.stopped.is_set() and (session_error or not complete) else None
        preserve_packet=bool(pause_reason or (self.stopped.is_set() and (resume_attempt or conversation))) and not complete
        if preserve_packet:
            # Reserve before accept releases rows to ready; healthy lanes must never steal this packet.
            worker['pending_resume']={'attempt':str(directory),'conversation_id':conversation,
                'keys':[r['source_sample_key'] for r in rows],
                'reason':pause_reason or self.reason,'stopped_at':now()}
            self.store.worker(worker['worker_id'],worker)
        self.accept(rows,directory,request,mapping,native,self.stopped.is_set() or bool(pause_reason))
        worker.pop('pending_resume',None)
        if preserve_packet:
            keys=[r['source_sample_key'] for r in rows if r['state']==request['stage']+'_ready']
            if keys:
                worker['pending_resume']={'attempt':str(directory),'conversation_id':conversation,'keys':keys,
                    'reason':pause_reason or self.reason,'stopped_at':now()}
                feedback_file=directory/'continuation_feedback.json'
                write(feedback_file,{'packet_id':request['packet_id'],'pending':{
                    local:pending.get(record['source_sample_key'],pending.get('file','仅补写未完成项')) for local,record in mapping.items()
                    if record['source_sample_key'] in keys},'accepted_sample_keys':list(frozen),
                    'result_file':request['result_file'],'format_example_file':request['format_example_file'],
                    'unread_sheets':native.get('visual_receipts',{}).get('missing',[])})
        if pause_reason and not worker.get('pending_resume') and pause_reason not in {'conversation_identity_mismatch','missing_conversation_id'}:
            # QA-exhausted rows belong to the sample review queue, never a zero-item session retry.
            worker['last_task_warning']=pause_reason
            pause_reason=None
        worker.update(status=('awaiting_continue' if worker.get('pending_resume') else 'session_blocked') if pause_reason else 'idle',pid=None,current_task=None,conversation_id=conversation,
            rounds=self.store.productive_rounds(conversation))
        worker.pop('continue_retry',None)
        if pause_reason:
            worker['retry_count']=continue_retries
            if worker.get('pending_resume'):
                worker['pending_resume']['continue_retries']=continue_retries
                worker['pending_resume']['retry_limit']=SESSION_RETRY_LIMIT
            worker['last_session_error']=pause_reason
            self.store.worker(worker['worker_id'],worker)
            self.store.event('session_paused',worker_id=worker['worker_id'],reason=pause_reason,
                conversation_id=conversation,attempt=str(directory),unfinished=len(worker.get('pending_resume',{}).get('keys',[])))
        else:
            worker['retry_count']=0
            worker['context_rotation_eligible']=bool(complete and not self.stopped.is_set())
            if not self.stopped.is_set():
                worker.update(consecutive_session_failures=0,last_session_error=None)
            self.store.worker(worker['worker_id'],worker)

    def release_completed_resume(self,worker):
        """Repair old zero-item holds only after revalidating their original packet and receipts."""
        pending=worker.get('pending_resume')
        if (not pending or pending.get('keys') or not pending.get('conversation_id')
                or pending.get('reason') in {'conversation_identity_mismatch','missing_conversation_id'}):
            return False
        directory=Path(pending['attempt'])
        try:
            request=read(directory/'request.json')
            mapping=read(directory/'manifest_private.json')['sample_mapping']
            accepted,_=(validate_file if request['stage']=='secondary_chroma' else validate_initial)(
                read(directory/'reviews_gemini.json'),request,mapping)
        except (OSError,ValueError,KeyError,TypeError):
            return False
        if len(accepted)!=len(mapping):
            return False
        if request.get('require_visual_receipts') and read_visual_receipts(pending['conversation_id'],request['sheets'])['missing']:
            return False
        worker['last_task_warning']=pending.get('reason')
        worker.pop('pending_resume')
        worker.pop('continue_retry',None)
        worker.update(status='idle',last_session_error=None,pid=None,current_task=None,retry_count=0)
        self.store.worker(worker['worker_id'],worker)
        self.store.event('completed_packet_released',worker_id=worker['worker_id'],
            conversation_id=pending['conversation_id'],attempt=str(directory),previous_error=pending.get('reason'))
        return True

    def rotate_large_completed_context(self,worker):
        context=worker.get('context_usage') or {}
        conversation=worker.get('conversation_id')
        if (not conversation or worker.get('pending_resume') or not worker.get('context_rotation_eligible')
                or context.get('conversation_id')!=conversation or context.get('tokens',0)<CONTEXT_TOKEN_LIMIT):
            return False
        worker.setdefault('history',[]).append(conversation)
        worker['last_context_rotation']={'conversation_id':conversation,'tokens':context['tokens'],
            'threshold':CONTEXT_TOKEN_LIMIT,'at':now(),'reason':'completed_task_context_limit'}
        worker.update(conversation_id=None,rounds=0,context_rotation_eligible=False)
        worker.pop('context_usage',None)
        worker.pop('context_signature',None)
        self.store.worker(worker['worker_id'],worker)
        self.store.event('completed_session_context_rotated',worker_id=worker['worker_id'],
            conversation_id=conversation,tokens=context['tokens'],threshold=CONTEXT_TOKEN_LIMIT)
        return True

    def worker_loop(self, worker_id, continue_pending=False):
        worker = self.store.worker(worker_id)
        self.release_completed_resume(worker)
        worker['rounds']=self.store.productive_rounds(worker.get('conversation_id'))
        allow_continue=continue_pending or self.continue_blocked or worker_id in self.resume_workers or self.auto_resume_pending
        if worker.get('pending_resume') and not allow_continue:
            return
        if worker.get('status')=='session_blocked':
            return
        if worker.get('model')!=self.cfg['model'] and worker.get('conversation_id'):
            worker.setdefault('history',[]).append(worker['conversation_id'])
            worker.update(conversation_id=None,rounds=0)
        worker['model']=self.cfg['model']
        batches=0
        # Dead process IDs are never reused; only explicit known conversation identities may be reused.
        worker.update(status='idle',pid=None,current_task=None,consecutive_session_failures=0)
        while not self.stopped.is_set():
            if self.store.meta().get('dispatch_hold',{}).get('active'):
                break
            if self.maximum_batches is not None and batches>=self.maximum_batches:
                break
            resume_attempt=None
            if worker.get('pending_resume'):
                if not allow_continue:
                    break
                resume_attempt=copy.deepcopy(worker['pending_resume'])
                rows=self.store.claim_resume(worker)
                allow_continue=False
            elif self.rotate_large_completed_context(worker):
                pass
            elif worker.get('rounds',0)>=8:
                worker.setdefault('history',[]).append(worker.get('conversation_id'))
                worker.update(conversation_id=None,rounds=0)
            if not resume_attempt:
                rows = self.store.claim(worker['role'],worker_id,prefer_full=self.maximum_batches is not None,allowed_keys=self.sample_scope)
            if not rows and self.store.meta().get('dispatch_hold',{}).get('active'):
                break
            if not rows and not resume_attempt:
                other = 'initial_rgb' if worker['role']=='secondary_chroma' else 'secondary_chroma'
                rows = self.store.claim(other,worker_id,prefer_full=self.maximum_batches is not None,allowed_keys=self.sample_scope)
                if rows:
                    worker.setdefault('history',[]).append(worker.get('conversation_id'))
                    worker.update(role=other,conversation_id=None,rounds=0)
            if not rows and not resume_attempt:
                if self.store.meta().get('dispatch_hold',{}).get('active'):
                    break
                state = self.store.summary()['stats']
                if state['running']==0:
                    break
                time.sleep(0.5)
                continue
            try:
                batches+=1
                self.run_one(worker,rows,resume_attempt=resume_attempt,
                    retry_offset=self.resume_retry_offsets.pop(worker_id,
                        1 if self.auto_resume_pending and not continue_pending and not self.continue_blocked else 0) if resume_attempt else 0)
            except Exception as exc:
                self.store.event('host_error',worker=worker_id,error=str(exc))
                with self.process_lock:
                    proc = self.processes.pop(worker_id,None)
                    if proc:
                        self.terminate(proc)
                        proc.wait()
                worker.update(pid=None,current_task=None)
                pause_reason=manual_stop_kind(str(exc)) or failure_kind(str(exc)) or 'host_error: '+str(exc)
                worker.update(status='awaiting_continue',last_session_error=pause_reason,
                    pending_resume={'attempt':rows[0].get('last_attempt'),
                        'conversation_id':worker.get('conversation_id'),'keys':[r['source_sample_key'] for r in rows],
                        'reason':pause_reason,'stopped_at':now()})
                self.store.worker(worker_id,worker)
                recover_interrupted(self.store,worker_id)
                self.store.event('session_paused',worker_id=worker_id,reason=pause_reason)
            if worker.get('pending_resume') or worker.get('status') in ['session_blocked','awaiting_continue']:
                break
            if worker.get('consecutive_session_failures'):
                self.stopped.wait(1)
        worker.update(status=('awaiting_continue' if worker.get('pending_resume') else
            'session_blocked' if worker.get('status')=='session_blocked' else 'idle'),pid=None,current_task=None)
        self.store.worker(worker_id,worker)

    def run(self, authorized=False):
        if not authorized:
            raise ValueError('Actual model calls require --execute-authorized-run')
        with OwnerLock(self.store.run_dir), OwnerLock(PROJECT/'runtime'):
            recover_interrupted(self.store)
            preflight(self.store,verify_images=not self.store.meta().get('preflight',{}).get('images_verified'))
            if not allow_requested_start(self.store):
                return
            with self.store.tx() as db:
                if not db.execute("SELECT 1 FROM commands WHERE action='drain' AND status='pending'").fetchone():
                    Store.put_meta(db,'dispatch_hold',{'active':False})
            self.store.update_meta(phase='running',stopped=False,stop_reason=None,owner_pid=os.getpid(),
                heartbeat_at=now(),worker_limit=self.worker_limit,active_model=self.cfg['model'],
                dispatch_control={'version':1,'owner_pid':os.getpid()},
                session_fault_policy=SESSION_RETRY_POLICY,retry_limit=SESSION_RETRY_LIMIT,
                limited_run={'maximum_batches':self.maximum_batches,'model':self.cfg['model']})
            self.store.update_meta(context_rotation_policy={'enabled':True,'input_token_limit':CONTEXT_TOKEN_LIMIT,
                'measurement':'latest native request input_tokens + cache_read_tokens',
                'rotate_only_after_complete':True,'maximum_rounds_fallback':8})
            for command in self.store.pending_commands():
                if command['action']=='start':
                    self.store.ack(command['id'],detail='执行器已接收，真实调度启动')
                elif command['action'] in ['stop','quota-stop']:
                    self.stop('quota_exhausted' if command['action']=='quota-stop' else 'user_pause')
                    self.store.ack(command['id'],detail='开跑前已收到停止指令，未派发')
                elif command['action']=='drain':
                    self.store.update_meta(phase='draining')
                    self.store.ack(command['id'],detail='已停止派发；等待已领取任务自然结束并保存')
            watching = threading.Event()
            def watch():
                try:
                    while not watching.is_set():
                        self.store.update_meta(heartbeat_at=now())
                        for command in self.store.pending_commands():
                            if command['action'] in ['stop','quota-stop']:
                                self.stop('quota_exhausted' if command['action']=='quota-stop' else 'user_pause')
                                self.store.ack(command['id'],detail='停止派发并终止本批在途调用；正在核对实际文件')
                            elif command['action']=='drain':
                                if not self.stopped.is_set():
                                    self.store.update_meta(phase='draining')
                                self.store.event('dispatch_drain_requested',command_id=command['id'])
                                self.store.ack(command['id'],detail='已停止派发；当前任务含必要补试自然结束后暂停')
                        watching.wait(0.5)
                except Exception as exc:
                    self.stop('control_watch_error: '+str(exc))
            watcher = threading.Thread(target=watch,daemon=True)
            watcher.start()
            pool = ThreadPoolExecutor(max_workers=self.worker_limit)
            try:
                futures = {f'W{i+1:02d}':pool.submit(self.worker_loop,f'W{i+1:02d}') for i in range(self.worker_limit)}
                while True:
                    for command in self.store.pending_commands():
                        if command['action']!='continue-blocked' or self.stopped.is_set():
                            continue
                        if self.store.meta().get('dispatch_hold',{}).get('active'):
                            self.store.ack(command['id'],'failed','正在等待在途结束，未启动中断会话')
                            continue
                        resumed=[]
                        for worker_id,worker in self.store.summary()['workers'].items():
                            future=futures.get(worker_id)
                            if worker.get('pending_resume') and (future is None or future.done()):
                                futures[worker_id]=pool.submit(self.worker_loop,worker_id,True)
                                resumed.append(worker_id)
                        if resumed:
                            self.store.ack(command['id'],detail='原会话手动续接：'+','.join(resumed)+'；其他路保持运行')
                        elif not any(w.get('pending_resume') for w in self.store.summary()['workers'].values()):
                            self.store.ack(command['id'],detail='当前没有待继续的会话')
                    if self.dirty.is_set():
                        self.dirty.clear()
                        pipeline_delivery.export(self.store)
                        snapshot(self.store)
                    if all(f.done() for f in futures.values()):
                        break
                    time.sleep(0.5)
                for f in futures.values():
                    f.result()
            except KeyboardInterrupt:
                self.stop('user_interrupt')
            except Exception:
                self.stop('coordinator_error')
                raise
            finally:
                pool.shutdown(wait=True)
                recover_interrupted(self.store)
                watching.set(); watcher.join()
                self.store.update_meta(heartbeat_at=now())
                counts = self.store.summary()['stats']
                waiting=any(w.get('pending_resume') for w in self.store.summary()['workers'].values())
                phase = ('paused' if self.reason in ['user_pause','user_interrupt'] else 'blocked') if self.stopped.is_set() else (
                    'completed' if counts['program_validated']==counts['total'] else 'needs_attention')
                if self.reason=='quota_exhausted':phase='quota_waiting'
                if not self.stopped.is_set() and self.store.meta().get('dispatch_hold',{}).get('active'):
                    phase='paused'
                    self.reason='user_drain'
                for command in self.store.pending_commands():
                    if command['action']=='quota-stop':
                        self.store.ack(command['id'],detail='额度耗尽，全部会话已停止并保留原任务')
                    elif command['action']=='drain':
                        self.store.ack(command['id'],detail='在途任务已结束，结果与断点已保存')
                self.store.update_meta(phase=phase,stopped=True,stop_reason=self.reason or ('sessions_paused' if waiting else None),
                    owner_pid=None,heartbeat_at=now(),state_updated_at=now())
                pipeline_delivery.export(self.store)
                snapshot(self.store)
                print(json.dumps({k:v for k,v in self.store.summary().items() if k in ['phase','stats','stop_reason','active_calls']},ensure_ascii=False),flush=True)
