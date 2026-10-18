"""Single ab-distance panel against signed chroma; frozen pixels and blind reviews."""
import argparse
import copy
import subprocess
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import engine
import compact_harness
from workflow import OUTPUT,read_json,write_json,render,verify_sources,validate_reviews,utc
from run_harness_trial import prepare_trial

PREFIX='ab_heatmap_round13'


def prepare():
    cv2.setNumThreads(1)
    anchor=OUTPUT/'round10_base24_20261013';fresh=OUTPUT/f'{PREFIX}_fresh72_source_20261013'
    sources=[(verify_sources(p),read_json(p/'review_request.json')) for p in [anchor,fresh]]
    cfg=read_json(Path(__file__).with_name('config.json'))
    def numerical(config):
        result=copy.deepcopy(config);result['visual_harness'].pop('parallel_scheduler',None);return result
    if any(numerical(m['configuration'])!=numerical(cfg) for m,_ in sources):raise ValueError('Freeze the same CV8 thresholds in both sources')
    records=[];public={};task_hashes={}
    for manifest,request in sources:
        lookup={r['sample_key']:r for r in request['samples']}
        for r in manifest['records']:
            records.append(copy.deepcopy(r));public[r['source_sample_key']]=copy.deepcopy(lookup[r['sample_key']])
        task_hashes.update(manifest['source_task_sha256'])
    if len({r['source_sample_key'] for r in records})!=96:raise ValueError('Expected 96 distinct model/image pairs')
    baseline=OUTPUT/f'{PREFIX}_signed96_20261013';bm=prepare_trial(fresh,baseline,'compact')
    bm['records']=records;bm['configuration']=cfg;bm['source_task_sha256']=task_hashes
    for index,r in enumerate(records,1):r['sample_key']=f'S{index:03d}'
    bm['sheets']=render(records,baseline,cfg)
    request=read_json(baseline/'review_request.json');request['samples']=[]
    for r in records:
        row=public[r['source_sample_key']];row.update(sample_key=r['sample_key'],sheet=r['sheet'],sheet_row=r['sheet_row'])
        request['samples'].append(row)
    request['display']=cfg['display'];request['visual_harness']=cfg['visual_harness']
    request['low_chroma_GT_candidates']=[r['sample_key'] for r in records if r['metrics']['mean_c_gt']<=cfg['gt_reference']['low_chroma_mean_candidate']]
    write_json(baseline/'manifest.json',bm);write_json(baseline/'review_request.json',request)
    write_json(baseline/'review_template.json',compact_harness.template(request))
    trial=OUTPUT/f'{PREFIX}_turbo96_20261013';tm=prepare_trial(baseline,trial,'compact')
    tm['configuration']['display']['mode']='ab_distance_turbo';tm['sheets']=render(tm['records'],trial,tm['configuration'])
    write_json(trial/'manifest.json',tm)
    request=read_json(trial/'review_request.json');request['display']=tm['configuration']['display'];write_json(trial/'review_request.json',request)
    from review_boundaries import write_start_instructions
    for run,m in [(baseline,bm),(trial,tm)]:write_start_instructions(run,m)
    out=OUTPUT/f'{PREFIX}_setup_20261013';out.mkdir()
    left=18+2*515
    for b,t in zip(bm['sheets'],tm['sheets']):
        if not np.array_equal(np.asarray(Image.open(baseline/b['path']))[:,:left],np.asarray(Image.open(trial/t['path']))[:,:left]):
            raise ValueError('GT/generated panels and telemetry must match pixel-for-pixel')
    write_json(out/'manifest.json',{'created_at':utc(),'samples_per_condition':96,'anchor_samples':24,'fresh_samples':72,
        'baseline':baseline.name,'trial':trial.name,'same_GT_generated_panels_and_telemetry':True,
        'same_CV_metrics_and_rules':True,'changed_surface':'third panel and matching legend only',
        'display_scale':'existing shared deadzone/maximum/gamma; no per-image scaling or fitting to labels',
        'source_sample_mapping':[{k:r[k] for k in ['sample_key','source_sample_key']} for r in records],
        'no_old_labels_provided':True,'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(__file__).with_name('workflow.py'),Path(__file__).with_name('compact_harness.py')]}})
    for name in ['engine.py','workflow.py','compact_harness.py']:(out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    (out/'experiment_source.py').write_bytes(Path(__file__).read_bytes())
    print('PASS 96 paired samples; identical GT/generated/telemetry pixels:',baseline,trial)


def retry(attempt):
    if attempt<2:raise ValueError('Retry attempts start at 2; preserve the failed first attempt')
    original=OUTPUT/f'{PREFIX}_setup_20261013';setup=copy.deepcopy(read_json(original/'manifest.json'))
    out=OUTPUT/f'{PREFIX}_attempt{attempt:02d}_20261013';out.mkdir()
    for key in ['baseline','trial']:
        source=OUTPUT/setup[key];destination=OUTPUT/f'{source.name}_attempt{attempt:02d}'
        prepare_trial(source,destination,'compact');setup[key]=destination.name
    setup.update(created_at=utc(),retry_of=str(original),no_old_model_outputs_copied=True)
    write_json(out/'manifest.json',setup);(out/'experiment_source.py').write_bytes(Path(__file__).read_bytes())
    return out


def prepare_orange():
    cv2.setNumThreads(1);source=OUTPUT/f'{PREFIX}_signed96_20261013'
    baseline=OUTPUT/f'{PREFIX}_orange_control96_20261013';bm=prepare_trial(source,baseline,'compact')
    trial=OUTPUT/f'{PREFIX}_orange96_20261013';tm=prepare_trial(source,trial,'compact')
    tm['configuration']['display']['mode']='ab_distance_orange';tm['sheets']=render(tm['records'],trial,tm['configuration'])
    write_json(trial/'manifest.json',tm)
    request=read_json(trial/'review_request.json');request['display']=tm['configuration']['display'];write_json(trial/'review_request.json',request)
    out=OUTPUT/f'{PREFIX}_orange_setup_20261013';out.mkdir()
    setup=read_json(OUTPUT/f'{PREFIX}_setup_20261013/manifest.json')
    setup.update(created_at=utc(),baseline=baseline.name,trial=trial.name,changed_surface='third panel as single-orange ab distance and matching legend')
    left=18+2*(bm['configuration']['sheet']['image_box_width']+15)
    for b,t in zip(bm['sheets'],tm['sheets']):
        if not np.array_equal(np.asarray(Image.open(baseline/b['path']))[:,:left],np.asarray(Image.open(trial/t['path']))[:,:left]):raise ValueError('Main panels changed')
    setup['source_sha256']={p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(__file__).with_name('workflow.py'),Path(__file__).with_name('compact_harness.py')]}
    write_json(out/'manifest.json',setup)
    for name in ['engine.py','workflow.py','compact_harness.py']:(out/name).write_bytes(Path(__file__).with_name(name).read_bytes())
    (out/'experiment_source.py').write_bytes(Path(__file__).read_bytes())
    print(out)


def run_retry(attempt):
    out=retry(attempt);setup=read_json(out/'manifest.json')
    command=[sys.executable,str(Path(__file__).with_name('run_sheet_workers.py')),'--batch',
             str(OUTPUT/setup['baseline']),str(OUTPUT/setup['trial']),'--queue-run-id',f'{PREFIX}_queue_attempt{attempt:02d}_20261013',
             '--workers','16','--sheets-per-job','2','--timeout','300','--no-combined-export']
    subprocess.run(command,check=True)
    summarize(out)


def summarize(out=None):
    out=out or OUTPUT/f'{PREFIX}_setup_20261013';setup=read_json(out/'manifest.json');results=[];reviews=[]
    for key in ['baseline','trial']:
        run=OUTPUT/setup[key];m=verify_sources(run);v=read_json(run/'visual_reviews.json');validate_reviews(m,v,strict=True)
        call=read_json(run/'agy_calls/parallel/result.json');reviews.append({r['sample_key']:r for r in v['reviews']})
        results.append({'run':run.name,'wall_seconds':call['elapsed_seconds'],'call_seconds':[c['elapsed_seconds'] for c in call['worker_calls']],
            'mean_call_seconds':float(np.mean([c['elapsed_seconds'] for c in call['worker_calls']])),
            'usage':call['usage'],'A_samples':[r['sample_key'] for r in v['reviews'] if any(d['id']=='A' for d in r['defects'])],
            'BF_only_samples':[r['sample_key'] for r in v['reviews'] if r.get('review_scope')=='reference_free_BF_only']})
    a,b=reviews;codes=lambda r:sorted({d['id'] for d in r['defects']})
    changes=[{'sample_key':s,'baseline':a[s],'trial':b[s]} for s in a if codes(a[s])!=codes(b[s]) or a[s].get('review_scope')!=b[s].get('review_scope')]
    write_json(out/'results.json',{'reference_is_AI_not_human':True,'matched_panels':True,'runs':results,
        'timing':'both conditions share one 16-process queue; 8 jobs/condition all start together, no duplicate candidate merge',
        'category_and_scope_agreement':96-len(changes),'changes':changes,
        'anchor_reviews':{s:[a[s],b[s]] for s in a if int(s[1:])<=24}})
    print([(r['run'],r['wall_seconds'],r['mean_call_seconds']) for r in results]);print(out/'results.json')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','prepare-orange','summarize','retry']);p.add_argument('--attempt',type=int,default=2)
    p.add_argument('--setup',type=Path);args=p.parse_args()
    if args.command=='prepare':prepare()
    elif args.command=='prepare-orange':prepare_orange()
    elif args.command=='retry':run_retry(args.attempt)
    else:summarize(args.setup)
