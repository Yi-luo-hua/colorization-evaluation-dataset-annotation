"""Fourth experiment: A structure, D gain explanations, and numerical ROI coverage.

Develop on previously used GT. Evaluate once on new GT-source holdout.
No external AI calls, real semantic labels, severity calibration, or automatic promotion.
"""
import argparse
import csv
import hashlib
import importlib.util
import itertools
import json
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

import engine
import global_models as gm
import region_models as rm
from workflow import read_json,write_json,utc

SPEC=importlib.util.spec_from_file_location('baseline_cv3',Path(__file__).with_name('baselines')/'engine_v3.py')
BASELINE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASELINE)


def confusion(rows,predictions,label):
    y=np.array([r[label] for r in rows],dtype=bool);p=np.array(predictions,dtype=bool)
    tp,fp,fn,tn=[int(m.sum()) for m in [y&p,~y&p,y&~p,~y&~p]]
    return {'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':tp/(tp+fp) if tp+fp else 0,
            'recall':tp/(tp+fn) if tp+fn else 0,'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0}


def choose(rows,search,label,predictor):
    development=[r for r in rows if r['partition']=='development'];trials=[]
    for values in itertools.product(*search.values()):
        p=dict(zip(search,values));score=confusion(development,[predictor(r,p) for r in development],label)
        trials.append({'parameters':p,'development':score})
    trials.sort(key=lambda t:(t['development']['f1'],-t['development']['fp']),reverse=True)
    return trials[0]['parameters'],trials[:10]


def strong_bbox(c,area):
    h,w=c.shape;bh=max(2,round(h*np.sqrt(area)));bw=max(2,round(w*np.sqrt(area)))
    score=cv2.boxFilter(c,-1,(bw,bh),normalize=True,borderType=cv2.BORDER_REFLECT)
    score[:bh//2]=-1;score[h-(bh+1)//2:]=-1;score[:,:bw//2]=-1;score[:,w-(bw+1)//2:]=-1
    y,x=np.unravel_index(np.argmax(score),score.shape);x1=max(0,min(w-bw,x-bw//2));y1=max(0,min(h-bh,y-bh//2))
    return x1,y1,x1+bw,y1+bh


def bbox_iou(a,b):
    x1,y1=max(a[0],b[0]),max(a[1],b[1]);x2,y2=min(a[2],b[2]),min(a[3],b[3]);overlap=max(0,x2-x1)*max(0,y2-y1)
    union=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-overlap
    return overlap/union if union else 0


def alterations(gt,cfg):
    # Import the v3 intervention generator, with its configuration snapshot.
    import evaluate
    yield from evaluate.interventions(gt,cfg)
    base=engine.rgb(gt).astype(np.float32)/255
    for i,gains in enumerate(OPT['linear_white_balance_gains']):
        modified=gm.to_srgb(np.clip(gm.to_linear(base)*np.array(gains),0,1))
        yield f'linear_wb_{i}',engine.lab(np.rint(modified*255).astype(np.uint8)),False,True,1
    for gain in OPT['exposure_gains']:
        yield f'exposure_{gain:g}',engine.lab(np.rint(np.clip(base*gain,0,1)*255).astype(np.uint8)),False,False,1
    for area in OPT['partial_gray_retained_areas']:
        box=strong_bbox(engine.chroma(gt),area);x1,y1,x2,y2=box;x=gt.copy();x[...,1:]=0;x[y1:y2,x1:x2]=gt[y1:y2,x1:x2]
        yield f'partial_gray_keep_{area:g}',x,False,False,(x2-x1)*(y2-y1)/(gt.shape[0]*gt.shape[1])
    _,data=cv2.imencode('.jpg',cv2.cvtColor(engine.rgb(gt),cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,OPT['jpeg_quality']])
    yield 'jpeg_control',engine.lab(cv2.cvtColor(cv2.imdecode(data,cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)),False,False,0


def roi_trial(gt_rgb,kind,area,jpeg=False):
    gt=engine.lab(gt_rgb);box=strong_bbox(engine.chroma(gt),area);x1,y1,x2,y2=box;changed=gt.copy()
    if kind=='hue_change':changed[y1:y2,x1:x2,1]=-gt[y1:y2,x1:x2,2];changed[y1:y2,x1:x2,2]=gt[y1:y2,x1:x2,1]
    else:changed[y1:y2,x1:x2,1:]*=(1.6 if kind=='chroma_gain' else 0.5)
    generated=engine.rgb(changed)
    if jpeg:
        _,data=cv2.imencode('.jpg',cv2.cvtColor(generated,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,OPT['jpeg_quality']])
        generated=cv2.cvtColor(cv2.imdecode(data,cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)
    return generated,[x1/gt.shape[1],y1/gt.shape[0],x2/gt.shape[1],y2/gt.shape[0]]


def source_records(item):
    image_id,part,stratum=item;path=engine.ROOT/CONFIG['datasets']['val']/'image'/f'{image_id}.jpg'
    rgb=engine.read_rgb(path,CONFIG['analysis_max_side']);gt=engine.lab(rgb);rows=[];roi_rows=[]
    for name,x,a,d,area in alterations(gt,EVAL):
        gen=engine.lab(engine.rgb(x));metrics,flags,_=BASELINE.measure(gt,gen,CONFIG)
        rows.append({'image_id':image_id,'partition':part,'stratum':stratum,'intervention':name,'a_target':a,'d_target':d,
                     'area_fraction':area,'baseline_a':flags['a_candidate'],'baseline_d':flags['d_candidate'],'metrics':metrics,
                     'models':gm.measure(gt,gen,OPT['features'])})
    original=engine.read_rgb(path,max(OPT['region_resolutions']))
    region_parameters=[dict(zip(OPT['localization_search'],values)) for values in itertools.product(*OPT['localization_search'].values())]
    for kind in ['chroma_gain','chroma_loss','hue_change']:
        for area in OPT['small_region_areas']:
            for jpeg in ([False,True] if area==0.01 else [False]):
                generated,box=roi_trial(original,kind,area,jpeg)
                for resolution in OPT['region_resolutions']:
                    h,w=original.shape[:2];ratio=min(1,resolution/max(h,w));size=(round(w*ratio),round(h*ratio))
                    rg=cv2.resize(original,size,interpolation=cv2.INTER_AREA);rm_=cv2.resize(generated,size,interpolation=cv2.INTER_AREA)
                    _,_,maps=BASELINE.measure(engine.lab(rg),engine.lab(rm_),CONFIG)
                    signal=maps['hue_component'] if kind=='hue_change' else np.maximum(maps['signed_dc']*(1 if kind=='chroma_gain' else -1),0)
                    x1,y1,x2,y2=box;crop=signal[int(y1*size[1]):max(int(y1*size[1])+1,int(y2*size[1])),int(x1*size[0]):max(int(x1*size[0])+1,int(x2*size[0]))]
                    effective=float(np.mean(crop>=CONFIG['regions']['quantile_signal_floor']))
                    old=BASELINE.regions(maps,CONFIG);old_iou=max([bbox_iou(r['bbox_normalized'],box) for r in old if r['kind']==kind],default=0)
                    trials=[]
                    for p in region_parameters:
                        regions=rm.regions(maps,p);best=max([bbox_iou(r['bbox_normalized'],box) for r in regions if r['kind']==kind],default=0)
                        trials.append({'parameters':p,'best_iou':best})
                    roi_rows.append({'image_id':image_id,'partition':part,'kind':kind,'area':area,'jpeg':jpeg,'resolution':resolution,
                                     'target_bbox':box,'effective_signal_fraction':effective,'baseline_best_iou':old_iou,'trials':trials})
    return rows,roi_rows


def roi_summary(rows,p):
    eligible=[r for r in rows if r['effective_signal_fraction']>=OPT['minimum_effective_signal_fraction']]
    values=[next(t['best_iou'] for t in r['trials'] if t['parameters']==p) for r in eligible]
    old=[r['baseline_best_iou'] for r in eligible]
    return {'cases':len(rows),'eligible_cases':len(eligible),'baseline_mean_iou':float(np.mean(old)) if old else 0,
            'candidate_mean_iou':float(np.mean(values)) if values else 0,
            'baseline_recall_iou25':float(np.mean(np.array(old)>=0.25)) if old else 0,
            'candidate_recall_iou25':float(np.mean(np.array(values)>=0.25)) if values else 0,
            'baseline_recall_iou50':float(np.mean(np.array(old)>=0.5)) if old else 0,
            'candidate_recall_iou50':float(np.mean(np.array(values)>=0.5)) if values else 0}


def cluster_bootstrap(rows,predictor,label):
    ids=sorted({r['image_id'] for r in rows});counts=[]
    for i in ids:
        group=[r for r in rows if r['image_id']==i];m=confusion(group,[predictor(r) for r in group],label);counts.append([m[k] for k in ['tp','fp','fn','tn']])
    rng=np.random.default_rng(OPT['seed']);values=[];counts=np.array(counts)
    for _ in range(OPT['bootstrap_replicates']):
        tp,fp,fn,tn=counts[rng.integers(0,len(ids),len(ids))].sum(0);values.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return {'source_images':len(ids),'f1_95_interval':np.percentile(values,[2.5,97.5]).tolist()}


def main():
    global OPT,CONFIG,EVAL
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='cv_models_v4_20261012');args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.run_id):raise ValueError('Invalid run ID')
    cv2.setNumThreads(1);OPT=read_json(Path(__file__).with_name('optimization_config.json'))
    root=engine.ROOT/'LS_lcad_reviewer/intermediate';old=root/'audits/cv_workflow_experiment_20261012_01';prior=root/'experiments/cv_geometry_v3_20261012'
    previous=read_json(prior/'manifest.json');CONFIG=previous['configuration'];EVAL=previous['evaluation_configuration']
    seen={i for i,_,_ in read_json(old/'v2_manifest.json')['samples']}|{i for i,_,_ in previous['samples']}
    for manifest in (root/'experiments').glob('*/manifest.json'):
        data=read_json(manifest)
        if data.get('schema_version')=='cv_handoff_v1':seen.update(r['sample_key'].split('/')[-1] for r in data['records'])
    with (old/'gt_profiles.csv').open(encoding='utf-8-sig') as f:profiles=list(csv.DictReader(f))
    cuts=read_json(old/'synthetic_sample_manifest.json')['gt_chroma_stratum_boundaries'];samples=[]
    for s in range(3):
        for part,n in [('development',OPT['development_per_stratum']),('holdout',OPT['holdout_per_stratum'])]:
            pool=[r for r in profiles if r['split']=='val' and int(np.searchsorted(cuts,float(r['mean_c'])))==s and
                  (r['image_id'] in seen if part=='development' else r['partition']=='holdout' and r['image_id'] not in seen)]
            pool.sort(key=lambda r:hashlib.sha256(f'{OPT["seed"]}:v4:{r["image_id"]}'.encode()).hexdigest())
            samples.extend((r['image_id'],part,s) for r in pool[:n])
    assert len({i for i,p,_ in samples if p=='holdout'})==48 and not ({i for i,p,_ in samples if p=='holdout'}&seen)
    out=root/'experiments'/args.run_id
    if out.exists():raise ValueError('Run exists; use another run ID')
    out.mkdir(parents=True);write_json(out/'manifest.json',{'created_at':utc(),'samples':samples,'prior_gt_excluded':sorted(seen),
                'configuration':CONFIG,'optimization_configuration':OPT,'test_split_used':False,
                'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(gm.__file__),Path(rm.__file__),Path(BASELINE.__file__),Path(__file__).with_name('optimization_config.json')]}})
    rows=[];roi=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,(a,b) in enumerate(pool.map(source_records,samples),1):
            rows.extend(a);roi.extend(b)
            if i%6==0:print(f'Global/ROI source images: {i}/{len(samples)}',flush=True)
    write_json(out/'records.json',rows);write_json(out/'region_records.json',roi)
    pa,ta=choose(rows,OPT['a_search'],'a_target',gm.predict_a)
    drows=[r for r in rows if not r['a_target']];pd,td=choose(drows,OPT['d_search'],'d_target',gm.predict_d)
    region_parameters=[t['parameters'] for t in roi[0]['trials']];dev_roi=[r for r in roi if r['partition']=='development']
    rt=[{'parameters':p,'development':roi_summary(dev_roi,p)} for p in region_parameters]
    rt.sort(key=lambda r:r['development']['candidate_mean_iou'],reverse=True);pr=rt[0]['parameters']
    hold=[r for r in rows if r['partition']=='holdout'];dh=[r for r in hold if not r['a_target']]
    ah=[gm.predict_a(r,pa) for r in hold];dp=[gm.predict_d(r,pd) for r in hold]
    results={'production_ready':False,'source_images':len(samples),'global_cases':len(rows),'localization_cases':len(roi),
             'A':{'parameters':pa,'baseline':confusion(hold,[r['baseline_a'] for r in hold],'a_target'),'candidate':confusion(hold,ah,'a_target'),'trials':ta},
             'D':{'parameters':pd,'baseline':confusion(dh,[r['baseline_d'] for r in dh],'d_target'),
                  'strict_pixel_baseline':confusion(dh,[r['baseline_d'] and r['metrics']['active_pixel_coverage']>=0.95 for r in dh],'d_target'),
                  'candidate':confusion(dh,[gm.predict_d(r,pd) for r in dh],'d_target'),'trials':td},
             'regions':{'parameters':pr,'development_trials':rt,'holdout':roi_summary([r for r in roi if r['partition']=='holdout'],pr)},
             'cascade':{'D_after_A':confusion(hold,[d and not a for a,d in zip(ah,dp)],'d_target'),
                        'true_D_routed_to_A':sum(a and r['d_target'] for r,a in zip(hold,ah))}}
    for label,predictor in [('A',lambda r:gm.predict_a(r,pa)),('D',lambda r:gm.predict_d(r,pd))]:
        group=hold if label=='A' else dh;target=label.lower()+'_target'
        results[label]['by_intervention']={n:confusion([r for r in group if r['intervention']==n],[predictor(r) for r in group if r['intervention']==n],target) for n in sorted({r['intervention'] for r in group})}
        results[label]['cluster_bootstrap']=cluster_bootstrap(group,predictor,target)
    results['regions']['by_condition']={f'{kind}/{resolution}/jpeg={jpeg}':roi_summary([r for r in roi if r['partition']=='holdout' and r['kind']==kind and r['resolution']==resolution and r['jpeg']==jpeg],pr)
                                      for kind in ['chroma_gain','chroma_loss','hue_change'] for resolution in OPT['region_resolutions'] for jpeg in [False,True]}
    write_json(out/'results.json',results)
    candidate={**CONFIG,'version':'cv_workflow_candidate_4','global_models':{'features':OPT['features'],'a':pa,'d':pd},
               'regions':{**pr,'max_side':512}}
    write_json(out/'config_candidate.json',candidate)
    # Candidate remains separate. Integration is decided after inspecting holdout failures.
    print(json.dumps({k:{x:y for x,y in v.items() if x in ['baseline','candidate','parameters','holdout']} for k,v in results.items() if k in ['A','D','regions']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
