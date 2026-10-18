"""Full retained-GT colour reference and real visual-pair heatmap scale.

Reuse frozen GT/A decisions; no labels, thresholds for semantic defects, or AI calls.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time

import cv2
import numpy as np

import engine
from workflow import OUTPUT,align,model_image,read_json,write_json,utc


def describe(values):
    return {'count':len(values),'min':float(min(values)),'max':float(max(values)),
            **{f'p{q}':float(np.percentile(values,q)) for q in [1,5,20,25,50,75,90,95,98,99]}}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    cfg_path=Path(__file__).with_name('config.json');cfg=read_json(cfg_path)
    gate_path=engine.ROOT/cfg['gt_filter']['exclude_manifest'];gate=read_json(gate_path)
    blocked={(r['split'],r['image_id']) for r in gate['excluded_GT']+gate.get('unresolved',[])}
    profiles_path=gate_path.parent/'profiles.json'
    jobs=[r for r in read_json(profiles_path)['records'] if (r['split'],r['image_id']) not in blocked]
    a_path=engine.ROOT/cfg['a']['confirmed_manifest']
    fixed_a={r['source_sample_key'] for r in read_json(a_path)['records'] if r['GT_eligible']}
    assert len({(r['split'],r['image_id']) for r in jobs})==len(jobs)==14228
    out=OUTPUT/args.run_id;out.mkdir()
    (out/'config_before.json').write_bytes(cfg_path.read_bytes())
    write_json(out/'manifest.json',{'created_at':utc(),'state':'statistics_running',
        'GT_count':len(jobs),'analysis_max_side':cfg['analysis_max_side'],'configuration':cfg,
        'source_sha256':{str(p.relative_to(engine.ROOT)):engine.sha256(p) for p in [gate_path,profiles_path,a_path,cfg_path,Path(__file__),Path(engine.__file__)]},
        'GT_qualification_reused':True,'A_decisions_reused':True,'new_native_calls':0})
    cv2.setNumThreads(1);started=time.monotonic()
    def measure(row):
        gp=engine.ROOT/row['gt_path'];gt_hash=engine.sha256(gp)
        if gt_hash!=row['gt_sha256']:raise ValueError(f'Frozen GT source changed: {gp}')
        gt=engine.read_rgb(gp,cfg['analysis_max_side']);gt_lab=engine.lab(gt);cg=engine.chroma(gt_lab)
        reference={'split':row['split'],'image_id':row['image_id'],'gt_path':row['gt_path'],'gt_sha256':gt_hash,
                   'GT_low_chroma_p20':float(np.percentile(cg,20)),
                   'GT_mean_chroma':float(cg.mean()),'GT_chroma_p95':float(np.percentile(cg,95)),
                   'analysis_size':[gt.shape[1],gt.shape[0]]}
        pairs=[]
        for model in ['lcad','unicolor']:
            key=f"{row['split']}/{model}/{row['image_id']}"
            if key in fixed_a:continue
            mp=model_image(engine.ROOT/cfg['datasets'][row['split']]/'model'/model,row['image_id'])
            generated=align(gt,engine.read_rgb(mp,cfg['analysis_max_side']))
            cm=engine.chroma(engine.lab(generated))
            pairs.append({'sample_key':key,'split':row['split'],'model':model,
                          'model_path':str(mp.relative_to(engine.ROOT)),'model_sha256':engine.sha256(mp),
                          'absolute_delta_chroma_p95':float(np.percentile(np.abs(cm-cg),95))})
        return reference,pairs
    refs=[];pairs=[]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i,(ref,pp) in enumerate(pool.map(measure,jobs),1):
            refs.append(ref);pairs.extend(pp)
            if i%1000==0:print(f'Full retained GT statistics: {i}/{len(jobs)}; visual pairs {len(pairs)}',flush=True)
    assert len(pairs)==28302 and len({r['sample_key'] for r in pairs})==len(pairs)
    reference=float(np.median([r['GT_low_chroma_p20'] for r in refs]))
    maximum=float(np.percentile([r['absolute_delta_chroma_p95'] for r in pairs],95))
    gt_stats={'GT':len(refs),'low_chroma_percentile':20,'reference_low_chroma':reference,
        'aggregation':'median of per-GT C* p20; each retained GT once; not a perceptual threshold',
        'analysis_max_side':cfg['analysis_max_side'],
        'distribution':describe([r['GT_low_chroma_p20'] for r in refs]),
        'by_split':{s:describe([r['GT_low_chroma_p20'] for r in refs if r['split']==s]) for s in cfg['datasets']},
        'rows':refs}
    heat_stats={'visual_pairs':len(pairs),'fixed_A_pairs_skipped':len(fixed_a),'display_maximum':maximum,
        'aggregation':'P95 across each real visual pair absolute delta C* P95; all GT-eligible non-A pairs',
        'analysis_max_side':cfg['analysis_max_side'],'not_semantic_threshold':True,
        'distribution':describe([r['absolute_delta_chroma_p95'] for r in pairs]),
        'by_split':{s:describe([r['absolute_delta_chroma_p95'] for r in pairs if r['split']==s]) for s in cfg['datasets']},
        'by_model':{m:describe([r['absolute_delta_chroma_p95'] for r in pairs if r['model']==m]) for m in ['lcad','unicolor']}}
    write_json(out/'GT_chroma_reference.json',gt_stats)
    write_json(out/'visual_pair_chroma_statistics.json',heat_stats)
    write_json(out/'visual_pair_records.json',pairs)
    summary={'created_at':utc(),'state':'full_statistics_complete_not_applied','valid_GT':len(refs),
        'excluded_GT_reused':len(blocked),'GT_counted_once':True,'visual_pairs':len(pairs),'fixed_A_not_processed':len(fixed_a),
        'reference_low_chroma_old':cfg['color_evidence']['reference_low_chroma'],'reference_low_chroma_new':reference,
        'display_maximum_old':cfg['display']['maximum'],'display_maximum_new':maximum,
        'by_split_GT':{s:gt_stats['by_split'][s]['count'] for s in cfg['datasets']},
        'by_split_visual_pairs':{s:heat_stats['by_split'][s]['count'] for s in cfg['datasets']},
        'analysis_max_side':cfg['analysis_max_side'],'elapsed_seconds':round(time.monotonic()-started,2),
        'new_native_calls':0,'labels_or_GT_decisions_modified':False}
    write_json(out/'summary.json',summary)
    manifest=read_json(out/'manifest.json');manifest['state']='statistics_complete';write_json(out/'manifest.json',manifest)
    print(summary,flush=True)


if __name__=='__main__':main()
