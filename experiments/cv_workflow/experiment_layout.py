"""Round21:3/6/8 rows per sheet at24 samples/job, same frozen CV and order."""
import argparse
import copy
import shutil
import subprocess
import sys
import time
from pathlib import Path
from collections import Counter

import engine
import workflow as wf
from summarize_capacity import inspect

SETUP=wf.OUTPUT/'layout_round21_setup_20261013'
SOURCE=wf.OUTPUT/'capacity_round20_fixed_source192_20261013'
ORDER=[6,3,8]
WORKERS=8
SAMPLES_PER_JOB=24


def batch(groups):return wf.OUTPUT/f'layout_round21_g{groups:02d}_192_20261013'


def prepare():
    parent=wf.verify_sources(SOURCE)
    for groups in ORDER:
        out=batch(groups);out.mkdir();(out/'sheets').mkdir()
        m=copy.deepcopy(parent);cfg=m['configuration']
        cfg['sheet']['groups_per_sheet']=groups;cfg['visual_harness']['spatial_hint']=False
        if groups==6:
            for s in m['sheets']:shutil.copy2(SOURCE/s['path'],out/s['path'])
        else:m['sheets']=wf.render(m['records'],out,cfg)
        m.update(created_at=wf.utc(),state='awaiting_external_visual_review',
                 experiment={'round':21,'unique_inputs':192,'real_samples':168,'controls':24,'inherited_GT':84,'new_GT':0,
                             'parent_source':str(SOURCE),'same_sample_order_and_CV':True,'only_changed_factor':'groups per sheet',
                             'samples_per_job':SAMPLES_PER_JOB,'sheets_per_job':SAMPLES_PER_JOB//groups,'workers':WORKERS})
        for name in ['workflow.py','compact_harness.py','review_boundaries.py','agy_runner.py',Path(__file__).name]:
            m['source_code_sha256'][name]=engine.sha256(Path(__file__).with_name(name))
        wf.write_json(out/'manifest.json',m);wf.write_handoff(out,m)
        request=wf.read_json(out/'review_request.json')
        assert len(request['samples'])==192 and request['sheet_groups']==groups
        assert [r['sample_key'] for r in m['records']]==[r['sample_key'] for r in parent['records']]
        assert [r['metrics'] for r in m['records']]==[r['metrics'] for r in parent['records']]
    wf.write_json(SETUP/'experiment.json',{'created_at':wf.utc(),'state':'prepared','order':ORDER,'workers':WORKERS,'samples_per_job':24,
         'jobs_per_condition':8,'unique_inputs':192,'successful_observation_target':576,'new_GT':0,'inherited_GT':84,'timeout':300,
         'source':str(SOURCE),'image_box':[500,320],'card_height':430,'width':1560,
         'timing':'Conditions separate; same8 simultaneous jobs,24 samples per job;6 first then3 then8,order is a limitation.',
         'source_labels_copied':False,'numeric_CV_changed':False,'default_config_changed':False})
    print('Prepared3 conditions x192 inputs;64/32/24 sheets;8 jobs each.',flush=True)


def run():
    state=wf.read_json(SETUP/'experiment.json');state['state']='running';wf.write_json(SETUP/'experiment.json',state)
    for groups in ORDER:
        out=batch(groups);state['active_groups']=groups;wf.write_json(SETUP/'experiment.json',state)
        print(f'Groups{groups}: starting',flush=True)
        command=[sys.executable,str(Path(__file__).with_name('run_sheet_workers.py')),'--batch',str(out),
                 '--workers',str(WORKERS),'--sheets-per-job',str(SAMPLES_PER_JOB//groups),'--no-combined-export']
        started=time.monotonic()
        with (SETUP/f'g{groups:02d}_runner.txt').open('w',encoding='utf-8') as log:process=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        state.setdefault('runs',[]).append({'groups':groups,'exit_code':process.returncode,'process_wall_seconds':round(time.monotonic()-started,2)})
        wf.write_json(SETUP/'experiment.json',state);analyse();print(f'Groups{groups}: finished exit{process.returncode}',flush=True)
        if process.returncode:
            errors=' '.join(p.read_text(encoding='utf-8') for p in out.glob('parts/job_*/agy_calls/*/result.json'))
            if 'User location is not supported' in errors:
                state['state']='service_unavailable';wf.write_json(SETUP/'experiment.json',state);return
    state['state']='initial_conditions_complete';state.pop('active_groups',None);wf.write_json(SETUP/'experiment.json',state);analyse()


def analyse():
    conditions=[];baseline=None
    for groups in ORDER:
        out=batch(groups)
        if not (out/'parts').exists():continue
        m,rows,jobs,positions=inspect(out)
        initial_attempt=None;attempt_out=out
        retry=wf.OUTPUT/'layout_round21_g06_retry192_20261013'
        if groups==6 and (retry/'parts').exists():
            initial_attempt={'batch':str(out),'rows':len(rows),'jobs':jobs,'timing':wf.read_json(out/'agy_calls/parallel/result.json')}
            m,rows,jobs,positions=inspect(retry);attempt_out=retry
        record_map={r['sample_key']:r for r in m['records']}
        for position in positions:position['sheet_row']=record_map[position['sample_key']]['sheet_row']
        row_stats=[]
        for number in range(1,groups+1):
            pp=[p for p in positions if p['sheet_row']==number];rr=[p for p in pp if not p['control'] and p['inspected_file_entry']]
            row_stats.append({'sheet_row':number,'samples':len(pp),'file_entries':sum(p['inspected_file_entry'] for p in pp),'controls':sum(bool(p['control']) for p in pp),'real_seen':len(rr),'real_empty':sum(p['categories']==[] for p in rr),'real_defect_items':sum(len(p['defects']) for p in rr)})
        real={r['sample_key'] for r in m['records'] if 'experiment_control' not in r}
        controls=[p for p in positions if p['control'] and p['inspected_file_entry']]
        path=attempt_out/'agy_calls/parallel/result.json';timing=wf.read_json(path) if path.exists() else {}
        changes=[]
        if baseline is not None:
            for k,r in rows.items():
                if k not in baseline or k not in real:continue
                before=baseline[k]['defects'];after=r['defects']
                if before!=after:changes.append({'sample_key':k,'baseline_defects':before,'current_defects':after,
                                                'category_changed':{d['id'] for d in before}!={d['id'] for d in after}})
        conditions.append({'groups':groups,'initial_attempt':initial_attempt,'actual_attempt':str(attempt_out),'samples_per_job':24,'sheets_per_job':24//groups,'actual_file_rows':len(rows),
            'resolved_rows':sum(p['resolved'] for p in positions),'jobs':jobs,'timing':timing,
            'A_positive_seen':sum(p['control']['expected_A'] for p in controls),
            'A_positive_hits':sum(p['control']['expected_A'] and 'A' in p['categories'] for p in controls),
            'colored_false_A':sum(not p['control']['expected_A'] and 'A' in p['categories'] for p in controls),
            'A_mismatches':[p for p in controls if p['A_target_mismatch']],
            'failure_inclusive_active_seconds':(initial_attempt['timing']['elapsed_seconds'] if initial_attempt else 0)+timing.get('elapsed_seconds',0),'real_file_rows':sum(k in rows for k in real),'real_empty':sum(rows[k]['decision']=='no_defects' for k in real if k in rows),
            'real_category_items':dict(Counter(d['id'] for k in real if k in rows for d in rows[k]['defects'])),
            'category_changes_from_g6':changes,'positions':positions,'within_sheet_rows':row_stats})
        if groups==6:baseline=rows
    wf.write_json(SETUP/'paired_results.json',{'created_at':wf.utc(),'conditions':conditions,'unique_inputs':192,'new_GT':0,
         'interpretation':'Actual files only. A controls are known targets; real consistency/counts are not accuracy. Raw PNG row pixels unchanged; model-side resizing is not observable.',
         'read_counts':None,'read_count_note':'CLI does not provide reliable per-board read traces.'})
    print([(c['groups'],c['resolved_rows'],c['A_positive_hits'],c['colored_false_A'],c['timing'].get('elapsed_seconds')) for c in conditions],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','run','analyse']);args=p.parse_args()
    {'prepare':prepare,'run':run,'analyse':analyse}[args.command]()
