"""Compare whole-board layouts while requiring identical sources and CV values."""
import argparse
from collections import Counter
from pathlib import Path

from workflow import read_json,write_json,verify_sources


def summarize(baseline,trial):
    bm,tm=[verify_sources(p) for p in [baseline,trial]]
    pairs=[(r['sample_key'],r['source_sample_key'],r['gt_sha256'],r['model_sha256'],r['metrics'],r['cv_flags']) for r in bm['records']]
    other=[(r['sample_key'],r['source_sample_key'],r['gt_sha256'],r['model_sha256'],r['metrics'],r['cv_flags']) for r in tm['records']]
    if pairs!=other:raise ValueError('Layout trial requires identical ordered source pairs and CV records')
    reviews=[{r['sample_key']:r for r in read_json(p/'visual_reviews.json')['reviews']} for p in [baseline,trial]]
    calls=[read_json(next(p.glob('agy_calls/*/result.json'))) for p in [baseline,trial]]
    codes=lambda r:{d['id'] for d in r['defects']}
    result={'reference_is_AI_not_human':True,'same_source_hashes_order_and_CV':True,
        'models':[r['model'] for r in calls],'elapsed_seconds':[r['elapsed_seconds'] for r in calls],
        'speed_ratio_baseline_over_trial':calls[0]['elapsed_seconds']/calls[1]['elapsed_seconds'],
        'samples':len(reviews[0]),'sheet_sizes':[[r['size'] for r in m['sheets']] for m in [bm,tm]],
        'label_set_agreement':sum(codes(reviews[0][k])==codes(reviews[1][k]) for k in reviews[0]),
        'defect_counts':[dict(Counter(d['id'] for r in rv.values() for d in r['defects'])) for rv in reviews],
        'decisions':[dict(Counter(r['decision'] for r in rv.values())) for rv in reviews],
        'usage':[c['usage'] for c in calls],
        'changes':[{'sample_key':k,'baseline':reviews[0][k]['defects'],'trial':reviews[1][k]['defects']}
            for k in reviews[0] if reviews[0][k]['defects']!=reviews[1][k]['defects']]}
    write_json(trial/f'layout_comparison_{baseline.name}.json',result)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--trial',type=Path,required=True)
    args=p.parse_args();result=summarize(args.baseline,args.trial)
    print({k:v for k,v in result.items() if k!='changes'})
    for row in result['changes']:print(row)


if __name__=='__main__':main()
