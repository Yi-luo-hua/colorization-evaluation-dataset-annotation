"""Refinement after v1 diagnosis; a new GT-source lockbox prevents holdout reuse.
v1 holdout becomes development data. All v2 parameters fit development only.
"""
import csv
import hashlib
import itertools
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

import experiment_v1 as ex


def extended_metrics(gt, gen, grid):
    row=ex.pair_metrics(gt,gen,grid)
    x=gt[...,1:].reshape(-1,2)[::4];y=gen[...,1:].reshape(-1,2)[::4]
    xm=x.mean(axis=0);ym=y.mean(axis=0)
    gain=float(np.sum((x-xm)*(y-ym))/(np.sum((x-xm)**2)+1e-8))
    intercept=ym-gain*xm
    row['scalar_gain']=gain
    row['scalar_intercept_norm']=float(np.linalg.norm(intercept))
    row['scalar_fit_median_error']=float(np.median(np.linalg.norm(y-gain*x-intercept,axis=1)))
    common=np.array([row['common_da'],row['common_db']])
    row['translation_fit_median_error']=float(np.median(np.linalg.norm(y-x-common,axis=1)))
    norms=[]
    delta=gen[...,1:]-gt[...,1:]
    for block_row in np.array_split(delta,grid,axis=0):
        for block in np.array_split(block_row,grid,axis=1):
            norms.append(float(np.linalg.norm(np.median(block.reshape(-1,2),axis=0))))
    row['cell_norms']=norms
    for name,lab in [('gt',gt),('model',gen)]:
        ab=lab[...,1:].reshape(-1,2)
        row[f'hue_concentration_{name}']=float(np.linalg.norm(ab.sum(axis=0))/(np.linalg.norm(ab,axis=1).sum()+1e-8))
    return row


def d_predict(rows,p):
    base=ex.predict_d(rows,p)
    active=np.mean(np.array([r['cell_norms'] for r in rows])>=p['activity_floor'],axis=1)
    explained=np.array([r['scalar_gain']>0 and r['scalar_intercept_norm']<p['minimum_shift'] and
                         r['scalar_fit_median_error']<p['scale_explanation_ratio']*r['translation_fit_median_error'] for r in rows])
    return base & (active>=p['minimum_active_coverage']) & ~explained


def a_predict(rows,p,base):
    hue=np.array([r['hue_concentration_model'] for r in rows])
    increase=hue-np.array([r['hue_concentration_gt'] for r in rows])
    return ex.predict_a(rows,base) | ((hue>=p['minimum_hue_concentration']) & (increase>=p['minimum_concentration_increase']))


def synthetic(item,cfg):
    image_id,part,stratum=item;rgb,_=ex.read_rgb(ex.DATASET['val']/'image'/f'{image_id}.jpg',cfg['max_side'])
    gt=ex.lab_from_rgb(rgb);rows=[]
    for name,x,a,d,area in ex.interventions(gt,cfg):
        gen=ex.lab_from_rgb(ex.rgb_from_lab(x));dc=ex.chroma(gen)-ex.chroma(gt)
        rows.append({'image_id':image_id,'partition':part,'stratum':stratum,'intervention':name,'a_intervention':a,'d_intervention':d,
                     'area_fraction':area,**extended_metrics(gt,gen,cfg['grid_size']),
                     'hidden_fractions':{str(z):float(np.mean(np.abs(dc)<=z)) for z in V2['display_deadzone_candidates']},
                     'modified_hue_only_dc_p95':float(np.percentile(np.abs(dc[:,:max(1,round(gt.shape[1]*area))]),95)) if name.startswith('local_hue_') else None})
    return rows


def fit(rows,label,search,predict):
    dev=[r for r in rows if r['partition']=='development'];y=[r[label] for r in dev];trials=[]
    for vals in itertools.product(*search.values()):
        p=dict(zip(search,vals));m=ex.confusion(y,predict(dev,p));trials.append({'parameters':p,'development':m})
    trials.sort(key=lambda r:(r['development']['f1'],-r['development']['fp']),reverse=True)
    p=trials[0]['parameters'];results={}
    for part in ['development','lockbox']:
        group=[r for r in rows if r['partition']==part];pred=predict(group,p)
        results[part]=ex.confusion([r[label] for r in group],pred)
        results[part]['by_intervention']={n:ex.confusion([r[label] for r in group if r['intervention']==n],pred[[r['intervention']==n for r in group]]) for n in sorted({r['intervention'] for r in group})}
    return {'parameters':p,'results':results,'top_development_trials':trials[:10]}


def bootstrap(rows,label,prediction):
    ids=sorted({r['image_id'] for r in rows});counts=[]
    for i in ids:
        mask=np.array([r['image_id']==i for r in rows]);m=ex.confusion([r[label] for r in rows if r['image_id']==i],prediction[mask])
        counts.append([m[k] for k in ['tp','fp','fn','tn']])
    counts=np.array(counts);rng=np.random.default_rng(20261012);values=[]
    for _ in range(V2['bootstrap_replicates']):
        tp,fp,fn,tn=counts[rng.integers(0,len(ids),len(ids))].sum(axis=0)
        values.append([2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0,fp/(fp+tn) if fp+tn else 0])
    return {'source_images':len(ids),'replicates':V2['bootstrap_replicates'],'f1_95_interval':np.percentile(np.array(values)[:,0],[2.5,97.5]).tolist(),
            'false_positive_rate_95_interval':np.percentile(np.array(values)[:,1],[2.5,97.5]).tolist()}


def revised_card(gt_rgb,gen_rgb,title,path,display):
    if gen_rgb.shape!=gt_rgb.shape:gen_rgb=cv2.resize(gen_rgb,(gt_rgb.shape[1],gt_rgb.shape[0]))
    gt,gen=ex.lab_from_rgb(gt_rgb),ex.lab_from_rgb(gen_rgb);dc=ex.chroma(gen)-ex.chroma(gt)
    amplitude=np.clip((np.abs(dc)-display['deadzone'])/(display['maximum']-display['deadzone']),0,1)**display['gamma']
    colors=np.where((dc>0)[...,None],np.array([255,45,115]),np.array([35,185,255]))
    heat=np.rint(colors*amplitude[...,None]).astype(np.uint8)
    canvas=Image.new('RGB',(1500,550),(238,240,242));draw=ImageDraw.Draw(canvas)
    draw.text((12,8),title,fill='black',font=ex.font(20))
    draw.text((12,40),f"ΔC*正红负蓝；弱化≤{display['deadzone']:g}，强度上限{display['maximum']:.1f}，γ={display['gamma']:g}；黑色不代表无错色",fill='black',font=ex.font(16))
    for i,(im,label) in enumerate(zip([gt_rgb,gen_rgb,heat],['GT','生成图','双向彩度差'])):
        draw.text((i*500+10,78),label,fill='black',font=ex.font(20));image=Image.fromarray(im);image.thumbnail((484,420))
        canvas.paste(image,(i*500+(500-image.width)//2,120+(420-image.height)//2))
    canvas.save(path)


def main():
    global V2
    cfg=json.loads(Path(__file__).with_name('config_v1.json').read_text(encoding='utf-8'));V2=json.loads(Path(__file__).with_name('config_v2.json').read_text(encoding='utf-8'));cv2.setNumThreads(1)
    out=ex.BASE/'intermediate'/'audits'/cfg['experiment_id'];sheets=ex.BASE/'intermediate'/'inspection_sheets'/cfg['experiment_id']/'v2';sheets.mkdir(exist_ok=True)
    v1=json.loads((out/'candidate_parameters.json').read_text(encoding='utf-8'));sample=json.loads((out/'synthetic_sample_manifest.json').read_text(encoding='utf-8'))
    with (out/'gt_profiles.csv').open(encoding='utf-8-sig') as f:gt=list(csv.DictReader(f))
    seen={r[0] for r in sample['samples']};cuts=np.array(sample['gt_chroma_stratum_boundaries']);samples=[(i,'development',s) for i,_,s in sample['samples']]
    for stratum in range(3):
        pool=[r for r in gt if r['split']=='val' and r['partition']=='holdout' and r['image_id'] not in seen and int(np.searchsorted(cuts,float(r['mean_c'])))==stratum]
        pool.sort(key=lambda r:hashlib.sha256(f'{cfg["seed"]}:lockbox-v2:{r["image_id"]}'.encode()).hexdigest())
        samples.extend((r['image_id'],'lockbox',stratum) for r in pool[:V2['lockbox_per_stratum']])
    assert not (seen & {i for i,p,_ in samples if p=='lockbox'})
    ex.save_json(out/'v2_manifest.json',{'config':V2,'samples':samples,'v1_holdout_used_as_development':True,'lockbox_not_used_for_parameter_search':True,
                'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),Path(__file__).with_name('config_v2.json'),Path(ex.__file__)]}})
    rows=[r for batch in ex.map_parallel(synthetic,samples,cfg,'V2 synthetic sources') for r in batch]
    ex.csv_write(out/'v2_synthetic_metrics.csv',rows)
    drows=[r for r in rows if not r['a_intervention']]
    d=fit(drows,'d_intervention',V2['d_search'],d_predict)
    a=fit(rows,'a_intervention',V2['a_search'],lambda rr,p:a_predict(rr,p,v1['A']['parameters']))
    lock=[r for r in drows if r['partition']=='lockbox'];y=[r['d_intervention'] for r in lock]
    d['lockbox_v1_rule']=ex.confusion(y,ex.predict_d(lock,v1['D']['parameters']))
    d['lockbox_tuned_mean_rule']=ex.confusion(y,ex.predict_mean_shift(lock,v1['D']['tuned_mean_baseline']['parameters']))
    d['lockbox_cluster_bootstrap']=bootstrap(lock,'d_intervention',d_predict(lock,d['parameters']))
    alock=[r for r in rows if r['partition']=='lockbox']
    a['lockbox_v1_rule']=ex.confusion([r['a_intervention'] for r in alock],ex.predict_a(alock,v1['A']['parameters']))
    a['lockbox_cluster_bootstrap']=bootstrap(alock,'a_intervention',a_predict(alock,a['parameters'],v1['A']['parameters']))
    # Low-chroma natural GT identity/JPEG negatives. They do not fit parameters.
    low=sorted([r for r in gt if r['split']=='train'],key=lambda r:float(r['mean_c']))[:V2['boundary_gt_count']];boundary=[]
    for r in low:
        rgb,_=ex.read_rgb(ex.DATASET['train']/'image'/f'{r["image_id"]}.jpg',cfg['max_side']);lab=ex.lab_from_rgb(rgb)
        for name,x,_,_,_ in ex.interventions(lab,cfg):
            if name in ['identity','jpeg_control']:
                boundary.append({'image_id':r['image_id'],'intervention':name,**extended_metrics(lab,ex.lab_from_rgb(ex.rgb_from_lab(x)),cfg['grid_size'])})
    boundary_result={'images':len(low),'cases':len(boundary),'A_false_flags':int(a_predict(boundary,a['parameters'],v1['A']['parameters']).sum()),
                     'D_false_flags':int(d_predict(boundary,d['parameters']).sum()),'gt_mean_chroma_range':[float(low[0]['mean_c']),float(low[-1]['mean_c'])]}
    ex.save_json(out/'v2_low_chroma_boundary_controls.json',{'summary':boundary_result,'records':boundary})
    # Display ablation: changed-pixel evidence retained, not a subjective visual score.
    display_stats={}
    for name in ['global_chroma_scale_0.7','global_chroma_scale_1.3','mixed_chroma_gain_loss','jpeg_control']:
        group=[r for r in rows if r['partition']=='lockbox' and r['intervention']==name]
        display_stats[name]={str(z):ex.quantiles([r['hidden_fractions'][str(z)] for r in group]) for z in V2['display_deadzone_candidates']}
    ex.save_json(out/'display_deadzone_ablation.json',{'warning':'Hidden-pixel fraction; not defect recall. JPEG control is NOT a valid automatic noise bound for all genuine weak color differences.','groups':display_stats})
    # No display parameter selected on lockbox; preview is an explicit candidate.
    display={'deadzone':V2['preview_deadzone'],'maximum':v1['display']['maximum'],'gamma':V2['preview_gamma'],'status':'visual candidate, not validated/frozen'}
    previews=json.loads((out/'preview_manifest.json').read_text(encoding='utf-8'))
    for i,r in enumerate(previews,1):
        g,_=ex.read_rgb(ex.DATASET['val']/'image'/f'{r["image_id"]}.jpg',cfg['preview_max_side']);m,_=ex.read_rgb(ex.model_path(r['image_id'],r['model']),cfg['preview_max_side'])
        revised_card(g,m,f'{r["model"]} / {r["image_id"]}',sheets/f'real_{i:02d}.png',display)
    source=sample['samples'][0][0];g,_=ex.read_rgb(ex.DATASET['val']/'image'/f'{source}.jpg',cfg['preview_max_side']);lab=ex.lab_from_rgb(g)
    for name,x,_,_,_ in ex.interventions(lab,cfg):
        if name in ['identity','local_hue_90_area_0.5','global_shift_16','local_shift_area_0.75','mixed_chroma_gain_loss','grayscale']:
            revised_card(g,ex.rgb_from_lab(x),name,sheets/f'synthetic_{name}.png',display)
    ex.save_json(out/'v2_results.json',{'production_ready':False,'A':a,'D':d,'display':display,'low_chroma_controls':boundary_result,
                                     'source_images':len(samples),'synthetic_cases':len(rows),'lockbox_source_images':len({r['image_id'] for r in alock})})
    print(json.dumps({'A_parameters':a['parameters'],'A_lockbox':{k:v for k,v in a['results']['lockbox'].items() if k!='by_intervention'},
                     'D_parameters':d['parameters'],'D_lockbox':{k:v for k,v in d['results']['lockbox'].items() if k!='by_intervention'},'low_chroma_controls':boundary_result},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
