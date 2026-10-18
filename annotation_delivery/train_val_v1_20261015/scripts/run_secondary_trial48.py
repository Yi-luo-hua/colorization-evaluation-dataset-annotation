"""Run the corrected 48-sample secondary trial with explicit baseline-item review."""
import argparse
from collections import Counter, deque
import shutil
import threading
from pathlib import Path

from prepare import PROJECT, ROOT, SIX, read, write, sha
from pilot_runner import Pilot, now
from secondary_review import POLICY, REVISION, prepare_secondary_files
from prepare_packets import RENDER_REVISION

PACKETS = PROJECT/read(PROJECT/'ACTIVE_PREPARATION.json')['corrected_packets']
RUN = PROJECT/'runtime/secondary_review_trial48_no_overlay_20261015_01'


class SecondaryTrial(Pilot):
    def __init__(self, resume=False):
        self.directory = RUN
        self.cfg = read(PROJECT/'config.json')
        assert self.cfg['stages']['secondary_chroma']['merge'] == POLICY
        for identifier in ['T0009','T0011']:
            request = read(PACKETS/identifier/'request.json')
            assert request.get('render_revision') == RENDER_REVISION and request.get('candidate_overlays') is False
        self.lock = threading.RLock()
        self.condition = threading.Condition(self.lock)
        self.processes = {}
        self.stopped, self.stop_reason = False, None
        self.queues = {'initial_rgb':deque(), 'secondary_chroma':deque()}
        if resume:
            state = read(RUN/'checkpoint.json')
            if state['stop_reason']:
                raise ValueError('Stopped service requires a new explicit recovery authorization; no automatic resume')
            self.jobs, self.workers, self.started_at = state['jobs'],state['workers'],state['started_at']
            for job in self.jobs.values():
                if job['state'] in ['running','retry_pending']:
                    job['state'] = 'ready'
        else:
            RUN.mkdir()
            self.started_at = now()
            self.jobs = {}
            for number, identifier in enumerate(['T0009','T0011'],1):
                mapping = read(PACKETS/identifier/'manifest_private.json')['sample_mapping']
                task = f'Q{number:04d}'
                self.jobs[task] = {'task_id':task,'stage':'secondary_chroma','state':'ready',
                    'source_packet':str((PACKETS/identifier).resolve()),
                    'source_sample_keys':[r['source_sample_key'] for r in mapping.values()],
                    'accepted':{},'pending':{},'attempts':[],'depends_on':None}
            assert len({k for j in self.jobs.values() for k in j['source_sample_keys']}) == 48
            self.workers = {'W01':{'role':'secondary_chroma','conversation_id':None,'rounds':0,'conversation_history':[]}}
            (RUN/'prompts').mkdir()
            for name in ['session.md','secondary_chroma.md']:
                shutil.copy2(PROJECT/'prompts'/name,RUN/'prompts'/name)
            write(RUN/'authorization.json',{'user_request':'再次测试试运行，然后给我看','authorized_at':self.started_at,
                'scope':'same48_corrected_secondary_review_only','service_gate':'explicit user request authorizes this trial; stop immediately if actual access/quota/network failure recurs',
                'new_unique_coverage':0,'model':self.cfg['model'],'prompt_revision':REVISION})
            write(RUN/'source_snapshot.json',{'prompt_revision':REVISION,'secondary_merge_policy':POLICY,
                'original_reviewed_source_sha256':sha(ROOT/self.cfg['sources']['legacy_reviewed']),
                'same48_as_preceding_trial':True,'original_BCDF_items':77,
                'prompt_hashes':{p.name:sha(p) for p in (RUN/'prompts').glob('*.md')}})
            for name in ['run_secondary_trial48.py','secondary_review.py','review_contract.py','pilot_runner.py']:
                shutil.copy2(PROJECT/'scripts'/name,RUN/name)
        for key, job in self.jobs.items():
            if job['state'] in ['ready','retry_pending']:
                self.queues['secondary_chroma'].append(key)
        self.checkpoint()

    def checkpoint(self):
        with self.lock:
            count = sum(len(j['accepted']) for j in self.jobs.values())
            write(RUN/'checkpoint.json',{'annotation_contract':self.cfg['annotation_contract'],
                'prompt_revision':REVISION,'secondary_merge_policy':POLICY,'started_at':self.started_at,'updated_at':now(),
                'state':'stopped' if self.stopped else 'completed' if count==48 else 'running',
                'stop_reason':self.stop_reason,'active_calls':len(self.processes),'target_unique_samples':48,
                'final_completed':count,'new_unique_coverage':0,'jobs':self.jobs,'workers':self.workers,
                'job_states':dict(Counter(j['state'] for j in self.jobs.values()))})

    def materialize(self, job):
        source = Path(job['source_packet'])
        remaining = set(job['source_sample_keys']) - set(job['accepted'])
        mapping = {key:row for key,row in read(source/'manifest_private.json')['sample_mapping'].items()
                   if row['source_sample_key'] in remaining}
        destination = RUN/'tasks'/job['task_id']/f'attempt_{len(job["attempts"])+1:02d}'
        (destination/'sheets').mkdir(parents=True)
        request = read(source/'request.json')
        request['packet_id'] = f'{job["task_id"]}-a{len(job["attempts"])+1:02d}'
        sheets = []
        for sheet in request['sheets']:
            if not set(sheet['sample_keys']) & set(mapping):
                continue
            target = destination/'sheets'/Path(sheet['path']).name
            shutil.copy2(sheet['path'],target)
            assert sha(target) == sheet['sha256']
            sheets.append({**sheet,'path':str(target.resolve())})
        request['sheets'] = sheets
        prepare_secondary_files(destination,request,mapping)
        write(destination/'request.json',request)
        write(destination/'manifest_private.json',{'sample_mapping':mapping,'host_only':True})
        common = (RUN/'prompts/session.md').read_text(encoding='utf-8')
        role = (RUN/'prompts/secondary_chroma.md').read_text(encoding='utf-8')
        current = (f'packet_id={request["packet_id"]}，annotation_contract={request["annotation_contract"]}，stage=secondary_chroma。\n'
            f'本轮仅处理S编号：{", ".join(mapping)}。\n'
            f'先读取匿名审核底稿：{(destination/"prior_reviews.json").resolve()}\n'
            f'只修改结果文件：{(destination/"reviews_gemini.json").resolve()}\n'
            '指定看板，每张一次：\n'+'\n'.join(s['path']+': '+', '.join(k for k in s['sample_keys'] if k in mapping) for s in sheets)+'\n'
            '重点详细重标E1/E2；原B/C/D/F逐P编号审核、默认保留，只改明确错误并写理由。'
            '输出增量审核对象，不能用六类自由重标数组覆盖原标签。保存后只回复“文件已保存”。')
        full = common+'\n'+role+'\n'+current
        continuation = '继续固定二次角色，沿用NR_secondary_preserve_20261015_04，S编号按本轮重新对应。\n'+role+'\n'+current
        return destination,request,mapping,full,continuation

    def run(self):
        self.worker('W01')
        self.checkpoint()
        final = [{**value,'source_sample_key':identity,'checked_categories':SIX,'inspection_complete':True,
                  'annotation_contract':self.cfg['annotation_contract'],'prompt_revision':REVISION}
                 for job in self.jobs.values() for identity,value in job['accepted'].items()]
        write(RUN/'visual_reviews.json',{'annotation_contract':self.cfg['annotation_contract'],'prompt_revision':REVISION,
            'secondary_merge_policy':POLICY,'target_samples':48,'completed_samples':len(final),'complete':len(final)==48,
            'new_unique_coverage':0,'experiment_annotations_used':0,'reviews':final})
        audit = Counter(d['action'] for r in final for d in r['baseline_review']['other_decisions'].values())
        write(RUN/'review_summary.json',{'samples':len(final),'target_samples':48,'complete':len(final)==48,
            'original_BCDF_items_target':77,'review_actions':dict(audit),
            'new_saturation_items':sum(len(r['baseline_review']['saturation_defects']) for r in final),
            'new_other_items':sum(len(r['baseline_review']['other_additions']) for r in final),
            'final_categories':dict(Counter(d['id'] for r in final for d in r['defects'])),
            'semantic_accuracy_verified':False,'stop_reason':self.stop_reason})
        print(f'SECONDARY TRIAL: {len(final)}/48; stop={self.stop_reason}',flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-authorized-trial',action='store_true',required=True)
    parser.add_argument('--resume',action='store_true')
    args = parser.parse_args()
    trial = SecondaryTrial(args.resume)
    try:
        trial.run()
    except KeyboardInterrupt:
        trial.stop('user_interrupt')
        trial.checkpoint()
