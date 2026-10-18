"""Fixed counters for speed trials. AI-to-AI agreement is not accuracy."""
import argparse
from collections import Counter
from pathlib import Path
from workflow import read_json,write_json


def summarize(baseline,trial,allow_display_change=False):
    bm,tm=[read_json(p/'manifest.json') for p in [baseline,trial]]
    same_sheets=[s['sha256'] for s in bm['sheets']]==[s['sha256'] for s in tm['sheets']]
    same_samples=[r['source_sample_key'] for r in bm['records']]==[r['source_sample_key'] for r in tm['records']]
    matched_source_hashes=[(r['gt_sha256'],r['model_sha256']) for r in bm['records']]==[(r['gt_sha256'],r['model_sha256']) for r in tm['records']]
    if not same_samples or not matched_source_hashes:raise ValueError('Comparison requires identical sample order and source images')
    same_main_panels=None
    if not same_sheets:
        if not allow_display_change:raise ValueError('Prompt comparison requires identical sheets')
        from PIL import Image
        import numpy as np
        third_left=18+2*(bm['configuration']['sheet']['image_box_width']+15)
        same_main_panels=all(np.array_equal(np.asarray(Image.open(baseline/b['path']))[:,:third_left],
                                           np.asarray(Image.open(trial/t['path']))[:,:third_left]) for b,t in zip(bm['sheets'],tm['sheets']))
        if not same_main_panels:raise ValueError('GT/generated panels or telemetry changed, not only helper display')
    b={r['sample_key']:r for r in read_json(baseline/'visual_reviews.json')['reviews']}
    t={r['sample_key']:r for r in read_json(trial/'visual_reviews.json')['reviews']}
    def codes(r):return {d['id'] for d in r['defects']}
    changes=[{'sample_key':k,'baseline':b[k]['defects'],'trial':t[k]['defects'],
              'removed_ids':sorted(codes(b[k])-codes(t[k])),'added_ids':sorted(codes(t[k])-codes(b[k]))}
             for k in b if codes(b[k])!=codes(t[k])]
    reference={(k,c) for k,r in b.items() for c in codes(r)};found={(k,c) for k,r in t.items() for c in codes(r)}
    major={(k,d['id']) for k,r in b.items() for d in r['defects'] if d['severity'] in ['L2','L3'] or d['id']=='A'}
    calls=[read_json(next(p.glob('agy_calls/*/result.json'))) for p in [baseline,trial]]
    result={'reference_is_AI_not_human':True,'same_sheet_hashes':same_sheets,'same_sample_order':same_samples,
            'same_source_hashes':matched_source_hashes,'same_GT_generated_panels_and_telemetry':same_main_panels,
            'models':[c['model'] for c in calls], 'samples':len(b),
            'elapsed_seconds':[c['elapsed_seconds'] for c in calls],
            'speedup':calls[0]['elapsed_seconds']/calls[1]['elapsed_seconds'],
            'label_set_agreement_count':sum(codes(b[k])==codes(t[k]) for k in b),
            'reference_label_pairs':len(reference),'retained_reference_label_pairs':len(reference&found),
            'reference_major_label_pairs':len(major),'retained_reference_major_label_pairs':len(major&found),
            'A_sample_agreement':all(('A' in codes(b[k]))==('A' in codes(t[k])) for k in b),
            'entity_defect_counts':[sum(len(r['defects']) for r in data.values()) for data in [b,t]],
            'decisions':[dict(Counter(r['decision'] for r in data.values())) for data in [b,t]],
            'defect_counts':[dict(Counter(d['id'] for r in data.values() for d in r['defects'])) for data in [b,t]],
            'usage':[c['usage'] for c in calls],
            'prompt_characters':[c.get('prompt_characters') or sum(len(file.read_text(encoding='utf-8')) for file in p.rglob('prompt.txt')) for p,c in zip([baseline,trial],calls)],
            'changes':changes}
    write_json(trial/f'harness_comparison_{baseline.name}.json',result)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--trial',type=Path,required=True)
    p.add_argument('--allow-display-change',action='store_true')
    args=p.parse_args();result=summarize(args.baseline,args.trial,args.allow_display_change)
    print({k:v for k,v in result.items() if k!='changes'})
    for r in result['changes']:print(r)


if __name__=='__main__':main()
