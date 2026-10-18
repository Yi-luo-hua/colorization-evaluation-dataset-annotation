"""Round 16: fresh train/test GT, one short positional grounding instruction."""
import argparse
import hashlib
import shutil
import time
from datetime import datetime
from pathlib import Path

import cv2

import engine
import compact_harness
from select_boundaries import prior_sources
from run_harness_trial import prepare_trial
from workflow import BASE,OUTPUT,read_json,write_json,utc,prepare,verify_sources


def build(args):
    out=OUTPUT/args.run_id;out.mkdir();cfg=read_json(Path(__file__).with_name('config.json'))
    settings=read_json(Path(__file__).with_name('object_round16_config.json'))
    profiles_path=OUTPUT/'gt_quality_all_splits_20261013/profiles.json'
    profiles=read_json(profiles_path)['records'];registry=read_json(engine.ROOT/cfg['gt_reference']['exclude_manifest'])
    blocked={(r['split'],r['image_id']) for r in registry['excluded_GT']+registry.get('unresolved',[])}
    seen=prior_sources();sources=[];batches=[]
    for split in settings['splits']:
        pool=[r for r in profiles if r['split']==split and (split,r['image_id']) not in blocked and r['image_id'] not in seen]
        used=set();selected=[]
        for stratum in settings['strata']:
            def ranking(r):
                if stratum=='diverse_palette':return r['curve_residual']
                if stratum=='low_chroma':return -r['mean_chroma']
                if stratum=='concentrated_palette':return r['hue_concentration']
                return hashlib.sha256(f"{settings['seed']}:{split}:{r['image_id']}".encode()).hexdigest()
            ranked=sorted((r for r in pool if r['image_id'] not in used),key=ranking,reverse=True)
            for row in ranked[:settings['GT_per_stratum']]:
                used.add(row['image_id']);selected.append({**row,'stratum':stratum})
        samples=[]
        for model in ['lcad','unicolor']:
            task_path=next((BASE/'tasks_pool'/split).glob(f'*{model}*.json'));tasks=read_json(task_path)
            mapping={Path(task['data']['original_record']['image_id']).stem:i for i,task in enumerate(tasks,1)}
            samples.extend({'model':model,'task_idx':mapping[r['image_id']],'sample_key':f"{split}/{model}/{r['image_id']}"} for r in selected)
        selection_path=out/f'{split}_selection.json';write_json(selection_path,{'split':split,'samples':samples})
        baseline=OUTPUT/f'{args.run_id}_{split}_baseline24'
        prepare(argparse.Namespace(run_id=baseline.name,model='both',split=split,start=1,end=1,selection=selection_path),cfg)
        trial=OUTPUT/f'{args.run_id}_{split}_position24';prepare_trial(baseline,trial,'compact')
        manifest=read_json(trial/'manifest.json');request=read_json(trial/'review_request.json')
        for config in [manifest['configuration'],request]:config['visual_harness']['object_color_rule']=settings['object_color_rule']
        write_json(trial/'manifest.json',manifest);write_json(trial/'review_request.json',request)
        for directory in [baseline,trial]:
            (directory/'prompt_preview.txt').write_text(compact_harness.build_prompt(read_json(directory/'review_request.json'),directory/'reviews_gemini.json'),encoding='utf-8')
        assert [s['sha256'] for s in verify_sources(baseline)['sheets']]==[s['sha256'] for s in verify_sources(trial)['sheets']]
        sources.extend(selected);batches.extend([str(baseline),str(trial)])
    shutil.copy2(Path(__file__),out/'object_diagnostic_source.py');shutil.copy2(Path(__file__).with_name('object_round16_config.json'),out/'settings.json')
    write_json(out/'experiment.json',{'created_at':utc(),'state':'visual_pending','configuration':cfg,'settings':settings,
                 'GT_sources':sources,'batches':batches,'prior_defect_diagnostic_GT_count':len(seen),
                 'GT_profiles_sha256':engine.sha256(profiles_path),'excluded_GT_sha256':engine.sha256(engine.ROOT/cfg['gt_reference']['exclude_manifest']),
                 'fresh_for_CV_defect_diagnostics':True,'GT_gate_may_have_seen_sources':True,
                 'purpose':'Diagnostic coverage, not representative prevalence/accuracy; no human golden labels.'})
    print(f'Ready: {len(sources)} GT / {2*len(sources)} real model pairs, two conditions',flush=True)


def analyze(args):
    out=OUTPUT/args.run_id;experiment=read_json(out/'experiment.json');conditions={};changes=[]
    for split in experiment['settings']['splits']:
        pairs=[]
        for condition in ['baseline','position']:
            directory=OUTPUT/f'{args.run_id}_{split}_{condition}24';manifest=verify_sources(directory)
            reviews={r['sample_key']:r for r in read_json(directory/'visual_reviews.json')['reviews']}
            timing=read_json(directory/'agy_calls/parallel/result.json');counts={k:0 for k in ['A','B','C','D','E1','E2','F']}
            for review in reviews.values():
                for code in {d['id'] for d in review['defects']}:counts[code]+=1
            conditions[f'{split}_{condition}']={'pairs':len(reviews),'category_counts':counts,
                    'GT_excluded':[k for k,r in reviews.items() if r['decision']=='excluded_GT'],
                    'uncertain':[k for k,r in reviews.items() if r['decision']=='uncertain'],
                    'no_defects':sum(r['decision']=='no_defects' for r in reviews.values()),
                    'elapsed_seconds':None if 'recovery only' in timing.get('timing','') else timing['elapsed_seconds'],
                    'timing_note':timing.get('timing',''),'usage':timing['usage'],'calls':timing['jobs'],'output_state':timing['state']}
            pairs.append((manifest,reviews))
        a,b=pairs;assert [s['sha256'] for s in a[0]['sheets']]==[s['sha256'] for s in b[0]['sheets']]
        for record in a[0]['records']:
            key=record['sample_key'];one=a[1][key];two=b[1][key]
            changes.append({'split':split,'sample_key':key,'source_sample_key':record['source_sample_key'],
                'sheet':record['sheet'],'baseline':one,'position':two,
                'category_scope_changed':one['decision']!=two['decision'] or {d['id'] for d in one['defects']}!={d['id'] for d in two['defects']}})
    write_json(out/'summary.json',{'conditions':conditions,'category_scope_changes':sum(r['category_scope_changed'] for r in changes),
              'default_changed':False,'warning':'Label count/agreement is not accuracy. Grounding must be checked against visible GT.'})
    write_json(out/'paired_observations.json',changes);experiment['state']='visual_complete_grounding_diagnosis_pending';write_json(out/'experiment.json',experiment)
    print(conditions,flush=True)


def recover(args):
    """Recover validated native files after host export failure; rerun only the null job."""
    from agy_runner import load_completed_file
    from run_sheet_workers import finish_batch
    from workflow import export_candidate
    root=OUTPUT/args.run_id;recovered=[]
    for condition in ['baseline','position']:
        batch=OUTPUT/f'{args.run_id}_test_{condition}24';results=[]
        initial=batch/'agy_calls/parallel/result.json'
        if not (initial.with_name('result_initial.json')).exists():shutil.copy2(initial,initial.with_name('result_initial.json'))
        for child in sorted((batch/'parts').glob('job_*')):
            directory=OUTPUT/f'{args.run_id}_retry_test_baseline_job001' if condition=='baseline' and child.name=='job_001' else child
            calls=next(directory.glob('agy_calls/*/stdout.json')).parent
            envelope=read_json(calls/'stdout.json');manifest=verify_sources(directory)
            load_completed_file(manifest,directory/'reviews_gemini.json',envelope)
            result_path=calls/'result.json'
            if result_path.exists() and read_json(result_path).get('state')!='model_call_incomplete':
                result=read_json(result_path)
            else:
                export_candidate(argparse.Namespace(batch=directory))
                timing=read_json(child/'worker_timing.json');launch=read_json(calls/'launch.json')
                result={'state':'observations_saved_without_source_scores','elapsed_seconds':round(timing['end_offset_seconds']-timing['start_offset_seconds'],2),
                        'model':manifest['configuration']['external_reviewer']['model'],'usage':envelope['usage'],
                        'agy_pid':launch['agy_pid'],'conversation_id':envelope['conversation_id'],
                        'postprocessing_recovered':True,'initial_worker_exit_code':timing['exit_code'],'native_status':envelope['status']}
                write_json(calls/'result_after_metadata_fix.json',result);recovered.append(str(child))
            if directory!=child:
                old_launch=read_json(next(child.glob('agy_calls/*/launch.json')));new_launch=read_json(calls/'launch.json')
                offset=(datetime.fromisoformat(new_launch['started_at'])-datetime.fromisoformat(old_launch['started_at'])).total_seconds()
                result['scheduler_timing']={'runner_pid':None,'agy_pid':result['agy_pid'],'start_offset_seconds':offset,
                                           'end_offset_seconds':offset+result['elapsed_seconds'],'exit_code':0,'phase':'retry; offset relative to original child launch'}
            else:result['scheduler_timing']=read_json(child/'worker_timing.json')
            results.append((directory,result))
        # Recovery wall is deliberately separate from initial shared queue wall and the retry call.
        completed=finish_batch(batch,verify_sources(batch),results,[],time.monotonic(),16,2,2)
        completed['timing']='offline merge/metadata recovery only; original call wall in result_initial.json; retry recorded separately'
        write_json(initial,completed)
    write_json(root/'recovery.json',{'created_at':utc(),'native_files_recovered_without_new_AI_calls':recovered,
                 'retry_batch':str(OUTPUT/f'{args.run_id}_retry_test_baseline_job001'),'original_model_files_unchanged':True,
                 'source_scores_not_invented':True})
    print('Test labels recovered; legacy candidate deferred because source scores/model/timestamps are absent.',flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['build','analyze','recover']);p.add_argument('--run-id',required=True);args=p.parse_args()
    cv2.setNumThreads(1)
    {'build':build,'analyze':analyze,'recover':recover}[args.stage](args)


if __name__=='__main__':main()
