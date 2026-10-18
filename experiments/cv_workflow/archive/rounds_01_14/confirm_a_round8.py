"""Select the smallest residual cutoff on cached controls, freeze, confirm on new GT."""
import csv
import argparse
import hashlib
import itertools
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

import engine
import global_models as gm
import optimize
from experiment_d_groups import stress_changes
from select_boundaries import prior_sources
from workflow import OUTPUT,read_json,write_json,utc


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='cv_a_confirm_round8_20261012')
    parser.add_argument('--config',type=Path,default=Path(__file__).with_name('baselines')/'config_v6_round8.json')
    parser.add_argument('--joint-scale-search',action='store_true');args=parser.parse_args()
    cv2.setNumThreads(1);started=time.perf_counter()
    cfg=read_json(args.config)
    old=OUTPUT/'cv_models_stress_20261012'
    cached=read_json(old/'records.json');params=cfg['global_models']['a']
    development_sources=[old/'records.json']
    if args.joint_scale_search:
        # The first confirmation is now development data; never call it an untouched holdout.
        development_sources.append(OUTPUT/'cv_a_confirm_round8_20261012/records.json')
        cached+=read_json(development_sources[-1])
    trials=[]
    combinations=(itertools.product([2,3,4],[0.5,1,2],[0.5,1,2]) if args.joint_scale_search
                  else ((c,params['scale_competition']['maximum_intercept'],params['scale_competition']['maximum_residual']) for c in [2,3,4,5,6]))
    for cutoff,intercept,residual in combinations:
        p={**params,'maximum_model_curve_residual':cutoff,'scale_competition':{**params['scale_competition'],
            'maximum_intercept':intercept,'maximum_residual':residual}}
        trials.append({'parameters':p,'A':optimize.confusion(cached,[gm.predict_a(r,p) for r in cached],'a_target')})
    winner=min(trials,key=lambda t:(t['A']['fp']+t['A']['fn'],t['parameters']['maximum_model_curve_residual'],
        t['parameters']['scale_competition']['maximum_residual'],t['parameters']['scale_competition']['maximum_intercept']))
    frozen=winner['parameters']
    initial=OUTPUT.parent/'audits/cv_workflow_experiment_20261012_01'
    cuts=read_json(initial/'synthetic_sample_manifest.json')['gt_chroma_stratum_boundaries']
    with (initial/'gt_profiles.csv').open(encoding='utf-8-sig') as f:profiles=list(csv.DictReader(f))
    seen=prior_sources();samples=[]
    for stratum in range(3):
        pool=[r for r in profiles if r['split']=='val' and r['image_id'] not in seen and
              int(np.searchsorted(cuts,float(r['mean_c'])))==stratum]
        pool.sort(key=lambda r:hashlib.sha256(f'20261012:A-round8-confirm:{r["image_id"]}'.encode()).hexdigest())
        samples.extend((r['image_id'],stratum) for r in pool[:8])
    out=OUTPUT/args.run_id;out.mkdir()
    (out/'confirm_a_round8_source.py').write_bytes(Path(__file__).read_bytes())
    write_json(out/'manifest.json',{'created_at':utc(),'samples':samples,'configuration':cfg,
        'frozen_A_parameters':frozen,'development_search':trials,
        'development_records_sha256':{str(p.relative_to(engine.ROOT)):engine.sha256(p) for p in development_sources},
        'excluded_prior_GT_ids':sorted(seen),'holdout_parameter_search':False,'test_split_used':False,
        'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(gm.__file__),Path(engine.__file__)]}})
    optimize.OPT=read_json(OUTPUT/'cv_models_v4_20261012/manifest.json')['optimization_configuration']
    eval_cfg=read_json(OUTPUT/'cv_geometry_v3_20261012/manifest.json')['evaluation_configuration']

    def trial(item):
        stem,stratum=item
        gt=engine.lab(engine.read_rgb(engine.ROOT/cfg['datasets']['val']/'image'/f'{stem}.jpg',cfg['analysis_max_side']))
        changes=list(stress_changes(gt,eval_cfg))
        rng=np.random.default_rng(int(stem))
        for sigma in [0.5,1.0,2.0]:
            x=gt.copy();x[...,1:]=rng.normal(0,sigma,x[...,1:].shape)
            changes.append((f'gray_noise_{sigma:g}',x,True,False,1))
        for scale in [0.05,0.1]:
            x=gt.copy();x[...,1:]*=scale
            changes.append((f'faithful_fade_{scale:g}',x,False,False,1))
        x=gt.copy();x[...,1:]=x[...,1:]*0.1+rng.normal(0,0.5,x[...,1:].shape)
        changes.append(('faithful_fade_0.1_noise_0.5',x,False,False,1))
        rows=[]
        for name,x,a,d,area in changes:
            m,f,_=engine.measure(gt,engine.lab(engine.rgb(x)),cfg)
            # Reconstruct the pre-model A vote, rather than feeding final A back into itself.
            base=cfg['a']
            baseline=((m['mean_c_model']<=base['maximum_mean_chroma'] and m['chroma_ratio']<=base['maximum_chroma_ratio']) or
                      (m['centered_spread_model']<=base['maximum_centered_spread'] and m['spread_ratio']<=base['maximum_spread_ratio']))
            r={'image_id':stem,'stratum':stratum,'intervention':name,'a_target':a,'baseline_a':bool(baseline),
               'metrics':m,'models':m['global_models'],'old_A':f['a_candidate']}
            r['candidate_A']=gm.predict_a(r,frozen);rows.append(r)
        return rows

    rows=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,batch in enumerate(pool.map(trial,samples),1):
            rows.extend(batch)
            if i%8==0:print(f'A holdout GT: {i}/24',flush=True)
    write_json(out/'records.json',rows)
    result={'GT_sources':len(samples),'cases':len(rows),'frozen_A_parameters':frozen,
        'old_A':optimize.confusion(rows,[r['old_A'] for r in rows],'a_target'),
        'candidate_A':optimize.confusion(rows,[r['candidate_A'] for r in rows],'a_target'),
        'by_intervention':{name:{'old_A':optimize.confusion([r for r in rows if r['intervention']==name],[r['old_A'] for r in rows if r['intervention']==name],'a_target'),
            'candidate_A':optimize.confusion([r for r in rows if r['intervention']==name],[r['candidate_A'] for r in rows if r['intervention']==name],'a_target')}
            for name in sorted({r['intervention'] for r in rows})},'wall_seconds':time.perf_counter()-started}
    write_json(out/'results.json',result)
    print({k:v for k,v in result.items() if k!='by_intervention'},flush=True)


if __name__=='__main__':main()
