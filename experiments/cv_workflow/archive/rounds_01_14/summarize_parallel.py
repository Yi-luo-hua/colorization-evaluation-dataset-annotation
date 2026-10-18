"""Concurrency wall-clock and file-contract comparison; AI agreement is not accuracy."""
from collections import Counter
from pathlib import Path
from workflow import OUTPUT,read_json,write_json,verify_sources,validate_reviews


def inventory(name):
    p=OUTPUT/name;m=verify_sources(p);result=read_json(p/'agy_calls/parallel/result.json')
    v=read_json(p/'visual_reviews.json');validate_reviews(m,v,strict=True)
    calls=result['worker_calls'];rows=v['reviews'];conversations=[r['conversation_id'] for r in calls]
    if len(conversations)!=len(set(conversations)):raise ValueError('Concurrent jobs must have independent conversations')
    return {'run':name,'samples':len(rows),'wall_seconds':result['elapsed_seconds'],'jobs':result['jobs'],
        'workers':result['workers'],'sheets_per_job':result['sheets_per_job'],
        'peak_active_runner_processes':result['peak_active_runner_processes'],
        'failed_jobs':0,'unresolved_samples':sum(r['decision']=='uncertain' for r in rows),
        'call_elapsed_seconds':[r['elapsed_seconds'] for r in calls],
        'agy_pids':[r.get('agy_pid') for r in calls],'conversation_ids':conversations,
        'usage':result['usage'],'defect_counts':dict(Counter(d['id'] for r in rows for d in r['defects'])),
        'A_samples':[r['sample_key'] for r in rows if any(d['id']=='A' for d in r['defects'])],
        'BF_only_samples':[r['sample_key'] for r in rows if r.get('review_scope')=='reference_free_BF_only']}


def main():
    names=['parallel2_12_round11_20261013','parallel4_6_round11_20261013',
           'parallel2_12_fresh48_round11_20261013','parallel4_12_fresh48_round11_20261013']
    rows=[inventory(name) for name in names]
    a,b=[OUTPUT/name for name in names[-2:]]
    jobs=lambda p:[read_json(c/'manifest.json') for c in sorted((p/'parts').iterdir())]
    key=lambda m:[(r['sample_key'],r['source_sample_key'],r['gt_sha256'],r['model_sha256'],r['metrics'],r['cv_flags']) for r in m['records']]
    aj,bj=jobs(a),jobs(b)
    if [key(m) for m in aj]!=[key(m) for m in bj]:raise ValueError('Fresh comparison must keep job contents and order identical')
    if [[s['sha256'] for s in m['sheets']] for m in aj]!=[[s['sha256'] for s in m['sheets']] for m in bj]:
        raise ValueError('Fresh comparison must use the same PNG bytes per job')
    ar=read_json(a/'visual_reviews.json')['reviews'];br={r['sample_key']:r for r in read_json(b/'visual_reviews.json')['reviews']}
    categories=lambda r:sorted({d['id'] for d in r['defects']})
    differences=[{'sample_key':r['sample_key'],'two_workers':r,'four_workers':br[r['sample_key']]}
                 for r in ar if categories(r)!=categories(br[r['sample_key']]) or r.get('review_scope')!=br[r['sample_key']].get('review_scope')]
    out=OUTPUT/'parallel_summary_round11_20261013';out.mkdir()
    write_json(out/'results.json',{'reference_is_AI_not_human':True,'runs':rows,
        'matched_fixed_job_size_fresh48':True,'fresh48_four_over_two_speedup':rows[2]['wall_seconds']/rows[3]['wall_seconds'],
        'matched24_two_over_serial_speedup':243.6/rows[0]['wall_seconds'],
        'serial_24_call_sum_seconds':243.6,'timing':'Concurrent values include scheduler join/import/export; serial comparison is recorded sum of two calls, excludes Codex idle gaps'})
    write_json(out/'quality_differences.json',{'matched_category_set_and_scope':len(ar)-len(differences),'samples':len(ar),
               'not_human_accuracy':True,'differences':differences,
               'board_observations':{'S037':'Four-worker A overclassification: visible skin and vivid yellow-green remain; raw annotations preserved.',
                                     'S044':'Two-worker BF-only over-exclusion: GT has brown cat fur and window reference; raw annotations preserved.'}})
    print([(r['run'],r['samples'],r['wall_seconds']) for r in rows])
    print(out/'results.json')


if __name__=='__main__':main()
