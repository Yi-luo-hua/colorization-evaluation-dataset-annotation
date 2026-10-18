"""Verify fixed-job concurrency trials; report speed separately from AI agreement."""
import argparse
from collections import Counter
from pathlib import Path
from workflow import OUTPUT,read_json,write_json,verify_sources,validate_reviews


def inventory(name):
    batch=OUTPUT/name;manifest=verify_sources(batch)
    result=read_json(batch/'agy_calls/parallel/result.json')
    plan=read_json(batch/'parallel_plan.json');calls=result['worker_calls']
    jobs=[];reviews=[]
    for item in plan['jobs']:
        child=batch/item['path'];cm=verify_sources(child)
        request=read_json(child/'review_request.json');template=read_json(child/'review_template.json')
        keys={r['sample_key'] for r in cm['records']}
        if keys!={r['sample_key'] for r in request['samples']} or keys!=set(template['reviews']):
            raise ValueError('Worker input scope mismatch')
        if not set(request.get('low_chroma_GT_candidates',[]))<=keys:raise ValueError('Foreign candidate IDs')
        jobs.append({'records':[(r['sample_key'],r['source_sample_key'],r['gt_sha256'],r['model_sha256'],r['metrics'],r['cv_flags']) for r in cm['records']],
                     'PNG_sha256':[s['sha256'] for s in cm['sheets']]})
        if (child/'visual_reviews.json').exists():
            v=read_json(child/'visual_reviews.json');validate_reviews(cm,v);reviews.extend(v['reviews'])
    if result['state']!='workers_incomplete':
        final=read_json(batch/'visual_reviews.json');validate_reviews(manifest,final,strict=result['state']=='candidate_exported')
        if reviews!=final['reviews']:raise ValueError('Merged file must retain worker reviews exactly')
    ids=[c['conversation_id'] for c in calls]
    if len(ids)!=len(set(ids)) or None in ids:raise ValueError('Worker conversations must be independent')
    gt_ids={Path(r['gt_path']).stem for r in manifest['records']}
    row={'run':name,'state':result['state'],'workers':plan['workers'],'sheets_per_job':plan['sheets_per_job'],
         'expected_samples':len(manifest['records']),'completed_samples':len(reviews),'jobs':len(jobs),
         'failed_jobs':len(result.get('failures',[])),'unresolved_samples':sum(r['decision']=='uncertain' for r in reviews),
         'wall_seconds':result['elapsed_seconds'],'completed_samples_per_minute':round(60*len(reviews)/result['elapsed_seconds'],2),
         'call_seconds':[c['elapsed_seconds'] for c in calls],'conversation_ids':ids,'agy_pids':[c.get('agy_pid') for c in calls],
         'usage':result.get('usage'),'defect_counts':dict(Counter(d['id'] for r in reviews for d in r['defects'])),
         'A_samples':[r['sample_key'] for r in reviews if any(d['id']=='A' for d in r['defects'])],
         'BF_only_samples':[r['sample_key'] for r in reviews if r.get('review_scope')=='reference_free_BF_only']}
    return row,jobs,reviews,gt_ids


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='*',default=[]);p.add_argument('--queues',nargs='*',default=[])
    p.add_argument('--out-id',required=True);args=p.parse_args()
    data=[inventory(name) for name in args.runs];comparisons=[];queues=[];queue_inputs=[]
    for name in args.queues:
        q=read_json(OUTPUT/name/'queue_result.json');plan=read_json(OUTPUT/name/'queue_plan.json')
        members=[inventory(Path(path).name) for path in plan['batches']]
        data.extend(members)
        timings=[read_json(Path(path)/item['path']/'worker_timing.json') for path in plan['batches']
                 for item in read_json(Path(path)/'parallel_plan.json')['jobs']]
        events=[(t['start_offset_seconds'],1) for t in timings]+[(t['end_offset_seconds'],-1) for t in timings]
        active=peak=0
        for _,delta in sorted(events):active+=delta;peak=max(peak,active)
        batch_timings=[[read_json(Path(path)/item['path']/'worker_timing.json') for item in read_json(Path(path)/'parallel_plan.json')['jobs']] for path in plan['batches']]
        crossings=[{'next_batch':Path(plan['batches'][i]).name,
                    'next_first_start':min(t['start_offset_seconds'] for t in batch_timings[i]),
                    'previous_last_end':max(t['end_offset_seconds'] for t in batch_timings[i-1])}
                   for i in range(1,len(batch_timings))]
        queues.append({'run':name,'workers':q['workers'],'samples':q['samples'],'jobs':q['jobs'],'wall_seconds':q['elapsed_seconds'],
                       'completed_samples':sum(m[0]['completed_samples'] for m in members),'failures':q['failures'],
                       'samples_per_minute':round(60*sum(m[0]['completed_samples'] for m in members)/q['elapsed_seconds'],2),
                       'peak_active_runner_processes':peak,'usage':q['usage'],'batch_crossings':crossings,
                       'every_next_batch_started_before_previous_ended':all(c['next_first_start']<c['previous_last_end'] for c in crossings)})
        queue_inputs.append([m[1] for m in members])
    for i,(a,aj,ar,_) in enumerate(data):
        for b,bj,br,_ in data[i+1:]:
            if aj!=bj:continue
            ad={r['sample_key']:r for r in ar};bd={r['sample_key']:r for r in br};common=ad.keys()&bd.keys()
            key=lambda r:(sorted({d['id'] for d in r['defects']}),r.get('review_scope'))
            differences=[{'sample_key':s,'left':ad[s],'right':bd[s]} for s in sorted(common) if key(ad[s])!=key(bd[s])]
            comparisons.append({'left':a['run'],'right':b['run'],'same_jobs_PNG_CV_order':True,
                'left_wall_over_right_wall':a['wall_seconds']/b['wall_seconds'],'common_review_samples':len(common),
                'matched_category_set_and_scope':len(common)-len(differences),'not_human_accuracy':True,'differences':differences})
    out=OUTPUT/args.out_id;out.mkdir()
    write_json(out/'results.json',{'runs':[d[0] for d in data],'comparisons':comparisons,
        'queues':queues,'queue_comparisons':[{'left':queues[i]['run'],'right':queues[j]['run'],
            'same_jobs_PNG_CV_order':True,'left_wall_over_right_wall':queues[i]['wall_seconds']/queues[j]['wall_seconds']}
            for i in range(len(queues)) for j in range(i+1,len(queues)) if queue_inputs[i]==queue_inputs[j]],
        'unique_GT_sources':len(set().union(*(d[3] for d in data))),
        'timing':'scheduler start through worker join/import/validation/export; excludes CV/board/partition preparation',
        'single_measurement_per_condition':True,'reference_is_AI_not_human':True})
    print([(d[0]['run'],d[0]['completed_samples'],d[0]['wall_seconds'],d[0]['failed_jobs']) for d in data])
    print(out/'results.json')


if __name__=='__main__':main()
