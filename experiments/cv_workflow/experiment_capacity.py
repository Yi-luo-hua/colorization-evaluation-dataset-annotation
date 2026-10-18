"""Matched-board task-capacity pilot. Controls are not production annotations."""
import argparse
import copy
import json
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

import engine
import workflow as wf
from run_harness_trial import prepare_trial
from select_boundaries import prior_sources

PREFIX='capacity_round19_balanced'
SETUP=wf.OUTPUT/f'{PREFIX}_setup_20261013'
SOURCE=wf.OUTPUT/f'{PREFIX}_source96_20261013'
CAPACITIES=[2,4,8,12,16]


def prepare():
    cfg=wf.read_json(Path(__file__).with_name('config.json'))
    cfg=copy.deepcopy(cfg);cfg['sheet']['show_model_name']=False
    registry=wf.read_json(engine.ROOT/cfg['gt_filter']['exclude_manifest'])
    blocked={r['image_id'] for r in registry['excluded_GT'] if r['split']=='val'}
    seen=prior_sources()
    pools={model:next((wf.BASE/'tasks_pool/val').glob(f'*{model}*.json')) for model in ['lcad','unicolor']}
    tasks={model:wf.read_json(path) for model,path in pools.items()}
    indices={model:{Path(t['data']['original_record']['image_id']).stem:i for i,t in enumerate(rows,1)} for model,rows in tasks.items()}
    eligible=sorted(set(indices['lcad']) & set(indices['unicolor'])-blocked-seen)
    chosen=np.random.default_rng(191013).choice(eligible,36,replace=False).tolist()
    selection={'split':'val','samples':[{'model':model,'task_idx':indices[model][stem],
        'sample_key':f'val/{model}/{stem}'} for stem in chosen for model in ['lcad','unicolor']]}
    wf.write_json(SETUP/'selection.json',selection)
    wf.write_json(SETUP/'experimental_config.json',cfg)
    real_name=f'{PREFIX}_real72_20261013'
    wf.prepare(argparse.Namespace(run_id=real_name,model='both',split='val',start=1,end=1,selection=SETUP/'selection.json'),cfg)
    parent=wf.verify_sources(wf.OUTPUT/real_name)
    SOURCE.mkdir();(SOURCE/'sheets').mkdir();(SOURCE/'controls').mkdir()
    source_records=copy.deepcopy(parent['records'])
    # Interleave models rather than keeping every LCAD before every UniColor.
    by_identity={r['source_sample_key']:r for r in source_records}
    real=[by_identity[f'val/{model}/{stem}'] for stem in chosen for model in ['lcad','unicolor']]
    controls=[]
    for i,stem in enumerate(chosen[:6]):
        origin=by_identity[f'val/lcad/{stem}'];rgb=engine.read_rgb(engine.ROOT/origin['gt_path'])
        neutral=np.repeat(cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY)[...,None],3,axis=-1)
        tinted=np.clip(neutral.astype(np.int16)+[18,2,-12],0,255).astype(np.uint8)
        faded=np.rint(neutral*0.8+rgb*0.2).astype(np.uint8)
        partial=neutral.copy();h,w=neutral.shape[:2];partial[:h//2,:w//2]=rgb[:h//2,:w//2]
        # A visible colour island is guaranteed; not required to match GT.
        partial[max(0,h//8):max(2,h//4),max(0,w//8):max(2,w//4)]=[170,70,100]
        for kind,pixels in [('gray',neutral),('tint',tinted),('fading',faded),('local',partial)]:
            path=SOURCE/'controls'/f'G{i+1:02d}_{kind}.png'
            ok,data=cv2.imencode('.png',cv2.cvtColor(pixels,cv2.COLOR_RGB2BGR));assert ok;data.tofile(path)
            gt_small=engine.read_rgb(engine.ROOT/origin['gt_path'],cfg['analysis_max_side'])
            gen_small=wf.align(gt_small,engine.resize_rgb(pixels,cfg['analysis_max_side']))
            metrics,flags,_=engine.measure(engine.lab(gt_small),engine.lab(gen_small),cfg,generated_rgb=pixels)
            region_side=cfg['regions']['max_side'];gt_region=engine.read_rgb(engine.ROOT/origin['gt_path'],region_side)
            gen_region=wf.align(gt_region,engine.resize_rgb(pixels,region_side))
            maps=engine.difference_maps(engine.lab(gt_region),engine.lab(gen_region))
            record=copy.deepcopy(origin)
            record.update(source_sample_key=f'val/control/{stem}_{kind}',model='control',
                model_path=str(path.relative_to(engine.ROOT)),model_sha256=engine.sha256(path),
                metrics=metrics,cv_flags=flags,region_candidates=engine.regions(maps,cfg),
                original_record={'image_id':f'control/G{i+1:02d}_{kind}.png','file_path':str(path.relative_to(engine.ROOT)),
                    'source_dataset':'controlled_intervention','role':'control','gpt_score':None},
                source_task_data={'source_kind':'controlled_intervention'},
                experiment_control={'kind':kind,'expected_A':kind=='gray','GT_origin':stem})
            controls.append(record)
    # Controls evenly spaced through task beginnings, middles and ends.
    records=[];real_iter=iter(real);control_iter=iter(controls)
    for i in range(96):records.append(next(control_iter) if i%4==1 else next(real_iter))
    for i,r in enumerate(records,1):r['sample_key']=f'S{i:03d}'
    manifest=copy.deepcopy(parent);manifest.update(created_at=wf.utc(),records=records,
        sheets=wf.render(records,SOURCE,cfg),state='awaiting_external_visual_review',configuration=cfg,
        experiment={'real_samples':72,'controlled_samples':24,'fresh_GT':36,'labels_not_copied':True,
                     'controlled_metadata':'Unscored synthetic outputs; no source rating/model/time invented.'})
    manifest['source_code_sha256']['experiment_capacity.py']=engine.sha256(Path(__file__))
    wf.write_json(SOURCE/'manifest.json',manifest);wf.write_handoff(SOURCE,manifest)
    for capacity in CAPACITIES:
        destination=wf.OUTPUT/f'{PREFIX}_s{capacity:02d}_96_20261013'
        prepare_trial(SOURCE,destination,'compact')
    wf.write_json(SETUP/'experiment.json',{'created_at':wf.utc(),'state':'prepared','source':str(SOURCE),
        'capacities':CAPACITIES,'samples_per_condition':96,'conditions':5,'unique_inputs':96,
        'real_inputs':72,'controlled_inputs':24,'fresh_GT':36,'workers_limit':16,'timeout':300,
        'condition_order':CAPACITIES,'same_board_hashes':True,'A_targets_hidden_from_model':True,
        'timing':'Each capacity runs separately; within-condition jobs roll. Initial job counts differ; not steady-state throughput.'})
    print('Prepared matched 16 boards / 96 inputs, 5 independent empty conditions.',flush=True)


def run():
    state=wf.read_json(SETUP/'experiment.json');state['state']='running';wf.write_json(SETUP/'experiment.json',state)
    for capacity in CAPACITIES:
        batch=wf.OUTPUT/f'{PREFIX}_s{capacity:02d}_96_20261013'
        if (batch/'parts').exists():raise ValueError('Existing attempt retained; use retry for incomplete parts, never overwrite.')
        state['active_capacity']=capacity;wf.write_json(SETUP/'experiment.json',state)
        print(f'Capacity {capacity}: starting independent condition',flush=True)
        command=[sys.executable,str(Path(__file__).with_name('run_sheet_workers.py')),'--batch',str(batch),
                 '--workers','16','--sheets-per-job',str(capacity),'--no-combined-export']
        started=time.monotonic()
        with (SETUP/f'capacity_{capacity:02d}_runner.txt').open('w',encoding='utf-8') as log:
            process=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT)
        state.setdefault('runs',[]).append({'capacity':capacity,'exit_code':process.returncode,
            'condition_process_wall_seconds':round(time.monotonic()-started,2)})
        wf.write_json(SETUP/'experiment.json',state)
        print(f'Capacity {capacity}: exit {process.returncode}; results retained',flush=True)
        analyse()
        if process.returncode:
            errors=' '.join(p.read_text(encoding='utf-8') for p in batch.glob('parts/job_*/agy_calls/*/result.json'))
            if 'User location is not supported' in errors:
                state['state']='service_unavailable';wf.write_json(SETUP/'experiment.json',state);return
    state['state']='initial_conditions_complete';state.pop('active_capacity',None);wf.write_json(SETUP/'experiment.json',state)
    analyse()


def analyse():
    reference=wf.read_json(SOURCE/'manifest.json');control={r['sample_key']:r['experiment_control'] for r in reference['records'] if 'experiment_control' in r}
    conditions=[]
    for capacity in CAPACITIES:
        batch=wf.OUTPUT/f'{PREFIX}_s{capacity:02d}_96_20261013'
        observations={};jobs=[]
        for child in sorted(batch.glob('parts/job_*')):
            manifest=wf.read_json(child/'manifest.json');files=sorted(child.glob('agy_calls/*/result.json'))
            result=wf.read_json(files[-1]) if files else {'state':'running_or_not_started'}
            complete=(child/'visual_reviews.json').exists()
            if complete:
                for row in wf.read_json(child/'visual_reviews.json')['reviews']:observations[row['sample_key']]=row
            jobs.append({'job':child.name,'samples':len(manifest['records']),'sheets':len(manifest['sheets']),
                'complete_file':complete,'state':result['state'],'call_seconds':result.get('elapsed_seconds'),
                'usage':result.get('usage'),'error':result.get('error')})
        if not jobs:continue
        errors=[]
        for key,target in control.items():
            if key not in observations:continue
            row=observations[key];has_A=any(d['id']=='A' for d in row['defects'])
            if has_A!=target['expected_A']:errors.append({'sample_key':key,**target,'observed_A':has_A,'defects':row['defects']})
        batch_result=wf.read_json(batch/'agy_calls/parallel/result.json') if (batch/'agy_calls/parallel/result.json').exists() else {}
        full=[j for j in jobs if j['samples']==capacity*6 and j['complete_file']]
        total_seconds=sum(j['call_seconds'] for j in full)
        conditions.append({'capacity':capacity,'jobs':jobs,'complete_samples':len(observations),
            'batch_state':batch_result.get('state'),'batch_wall_seconds':batch_result.get('elapsed_seconds'),
            'peak_active_runners':batch_result.get('peak_active_runner_processes'),
            'full_task_effective_samples_per_native_minute':sum(j['samples'] for j in full)*60/total_seconds if total_seconds else None,
            'controlled_A_mismatches':errors,'controlled_samples_seen':sum(k in observations for k in control),
            'A_positive_detected':sum(control[k]['expected_A'] and any(d['id']=='A' for d in observations[k]['defects']) for k in control if k in observations),
            'uncertain':sum(r['decision']=='uncertain' for r in observations.values()),
            'observation_source':'Actual files, not CLI acknowledgement; diagnostic controls have A-only targets.'})
    wf.write_json(SETUP/'initial_results.json',{'conditions':conditions,'same_unique_inputs':96,
        'timing_warning':'Full-task native sample rate excludes queue waiting; batch wall uses differing actual concurrency. Neither proves production steady-state throughput.',
        'semantic_warning':'A controlled checks are targets. Real label consistency is not accuracy; no artificial C/D/E/F truth.'})
    print('Available:',[(c['capacity'],c['complete_samples'],len(c['controlled_A_mismatches'])) for c in conditions],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','run','analyse']);args=parser.parse_args()
    {'prepare':prepare,'run':run,'analyse':analyse}[args.command]()
