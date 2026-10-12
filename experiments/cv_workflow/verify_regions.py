"""Fresh source holdout for anchored region navigation. No parameter search."""
import csv
import hashlib
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

import engine
import region_models as rm
import optimize
from workflow import read_json,write_json,utc


def main():
    cv2.setNumThreads(1);root=engine.ROOT/'LS_lcad_reviewer/intermediate'
    v4=root/'experiments/cv_models_v4_20261012';config=read_json(v4/'config_candidate.json')
    settings=config['regions'];optimize.CONFIG=config;optimize.OPT=read_json(v4/'manifest.json')['optimization_configuration']
    seen=set(read_json(v4/'manifest.json')['prior_gt_excluded']);seen.update(i for i,_,_ in read_json(v4/'manifest.json')['samples'])
    old=root/'audits/cv_workflow_experiment_20261012_01'
    with (old/'gt_profiles.csv').open(encoding='utf-8-sig') as f:profiles=list(csv.DictReader(f))
    cuts=read_json(old/'synthetic_sample_manifest.json')['gt_chroma_stratum_boundaries'];samples=[]
    for s in range(3):
        pool=[r for r in profiles if r['split']=='val' and r['partition']=='holdout' and r['image_id'] not in seen and int(np.searchsorted(cuts,float(r['mean_c'])))==s]
        pool.sort(key=lambda r:hashlib.sha256(f'20261012:roi-confirm:{r["image_id"]}'.encode()).hexdigest())
        samples.extend(r['image_id'] for r in pool[:16])
    assert len(samples)==48 and not set(samples)&seen
    out=root/'experiments/cv_regions_confirm_20261012'
    if out.exists():raise ValueError('Confirmation exists; do not overwrite')
    out.mkdir(parents=True);write_json(out/'manifest.json',{'created_at':utc(),'samples':samples,'excluded_gt_ids':sorted(seen),
                     'settings':settings,'parameter_search':False,'test_split_used':False,
                     'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(rm.__file__)]}})

    def trial(image_id):
        original=engine.read_rgb(engine.ROOT/config['datasets']['val']/'image'/f'{image_id}.jpg',512);rows=[]
        for kind in ['chroma_gain','chroma_loss','hue_change']:
            for area in optimize.OPT['small_region_areas']:
                for jpeg in ([False,True] if area==0.01 else [False]):
                    generated,box=optimize.roi_trial(original,kind,area,jpeg)
                    for resolution in [256,512]:
                        h,w=original.shape[:2];ratio=min(1,resolution/max(h,w));size=(round(w*ratio),round(h*ratio))
                        g=engine.lab(cv2.resize(original,size,interpolation=cv2.INTER_AREA));m=engine.lab(cv2.resize(generated,size,interpolation=cv2.INTER_AREA))
                        cg,cm=engine.chroma(g),engine.chroma(m);dc=cm-cg;ab=np.linalg.norm(m[...,1:]-g[...,1:],axis=-1)
                        maps={'signed_dc':dc,'hue_component':np.sqrt(np.maximum(0,ab**2-dc**2))}
                        old_regions=optimize.BASELINE.regions(maps,config)
                        anchored=rm.anchored_regions(maps,settings,prefer_compact=jpeg)
                        old_iou=max([optimize.bbox_iou(r['bbox_normalized'],box) for r in old_regions if r['kind']==kind],default=0)
                        primary=max([optimize.bbox_iou(r['bbox_normalized'],box) for r in anchored if r['kind']==kind],default=0)
                        alternatives=max([optimize.bbox_iou(r[k],box) for r in anchored if r['kind']==kind for k in ['compact_bbox_normalized','expanded_bbox_normalized']],default=0)
                        rows.append({'image_id':image_id,'kind':kind,'area':area,'jpeg':jpeg,'resolution':resolution,
                                     'baseline_iou':old_iou,'primary_iou':primary,'alternative_iou':alternatives})
        return rows

    rows=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,batch in enumerate(pool.map(trial,samples),1):
            rows.extend(batch)
            if i%8==0:print(f'Fresh ROI sources: {i}/48',flush=True)
    write_json(out/'records.json',rows)
    def summary(group):
        return {'cases':len(group),**{k:{'mean_iou':float(np.mean([r[k] for r in group])),
                                       'recall_iou25':float(np.mean([r[k]>=0.25 for r in group])),
                                       'recall_iou50':float(np.mean([r[k]>=0.5 for r in group]))} for k in ['baseline_iou','primary_iou','alternative_iou']}}
    result={'production_ready':False,'source_images':48,'cases':len(rows),'overall':summary(rows),
            'by_condition':{f'{kind}/{resolution}/jpeg={jpeg}':summary([r for r in rows if r['kind']==kind and r['resolution']==resolution and r['jpeg']==jpeg])
                            for kind in ['chroma_gain','chroma_loss','hue_change'] for resolution in [256,512] for jpeg in [False,True]}}
    write_json(out/'results.json',result);print(result['overall'],flush=True)


if __name__=='__main__':main()
