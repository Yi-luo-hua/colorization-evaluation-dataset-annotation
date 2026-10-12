"""Broader geometry/direction interventions, fresh GT-source holdout, no real-label claims."""
import csv
import argparse
import hashlib
import json
import re
from pathlib import Path

import cv2
import numpy as np

import engine
from workflow import write_json,read_json,utc


def confusion(rows,prediction):
    y=np.array([r['d_target'] for r in rows]);p=np.asarray(prediction,dtype=bool)
    tp,fp,fn,tn=[int(m.sum()) for m in [y&p,~y&p,y&~p,~y&~p]]
    return {'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':tp/(tp+fp) if tp+fp else 0,'recall':tp/(tp+fn) if tp+fn else 0,'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0}


def interventions(gt,cfg):
    yield 'identity',gt.copy(),False,False,0
    gray=gt.copy();gray[...,1:]=0;yield 'grayscale',gray,True,False,1
    tint=gt.copy();tint[...,1]=6;tint[...,2]=9;yield 'single_tint',tint,True,False,1
    for strength in cfg['global_shift_norms']:
        for angle in cfg['global_shift_angles']:
            x=gt.copy();theta=np.deg2rad(angle);x[...,1:]+=strength*np.array([np.cos(theta),np.sin(theta)])
            yield f'global_{strength:g}_{angle:g}',x,False,True,1
    h,w=gt.shape[:2];yy,xx=np.mgrid[0:h,0:w]
    for area in cfg['local_areas']:
        for shape in ['right_strip','center_ellipse']:
            mask=xx>=round(w*(1-area)) if shape=='right_strip' else ((xx-(w-1)/2)/(w/2))**2+((yy-(h-1)/2)/(h/2))**2<=area*4/np.pi
            x=gt.copy();x[...,1:][mask]+=cfg['local_shift_norm']*np.array([0.8,0.6])
            yield f'local_{shape}_{area:g}',x,False,False,float(mask.mean())
    for scale in cfg['chroma_scales']:
        x=gt.copy();x[...,1:]*=scale;yield f'scale_{scale:g}',x,False,False,1
    for area in cfg['local_hue_areas']:
        x=gt.copy();width=max(1,round(w*area));x[:,:width,1]=-gt[:,:width,2];x[:,:width,2]=gt[:,:width,1]
        yield f'local_hue90_{area:g}',x,False,False,width/w
    x=gt.copy();x[:,:w//2,1:]*=1.6;x[:,w//2:,1:]*=0.5;yield 'mixed_chroma',x,False,False,1
    x=gt.copy();x[...,1:]+=np.array([6.4,4.8]);x[:h//4,:,1:]+=np.array([-18.,15.]);yield 'global_plus_local',x,False,True,1
    # White-balance RGB gain is an out-of-family global intervention, reported separately.
    base=engine.rgb(gt).astype(np.float32)/255
    for i,gains in enumerate(cfg['white_balance_gains']):
        x=engine.lab(np.rint(np.clip(base*np.array(gains),0,1)*255).astype(np.uint8))
        yield f'white_balance_gain_{i}',x,False,True,1


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',default='cv_geometry_v3_20261012');args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.run_id):raise ValueError('run-id must be a single identifier')
    cv2.setNumThreads(1);cfg=read_json(Path(__file__).with_name('config.json'));evalcfg=read_json(Path(__file__).with_name('evaluation_config.json'))
    old=engine.ROOT/'LS_lcad_reviewer/intermediate/audits/cv_workflow_experiment_20261012_01'
    old_manifest=read_json(old/'v2_manifest.json');seen={i for i,_,_ in old_manifest['samples']}
    with (old/'gt_profiles.csv').open(encoding='utf-8-sig') as f:profiles=list(csv.DictReader(f))
    cuts=read_json(old/'synthetic_sample_manifest.json')['gt_chroma_stratum_boundaries'];samples=[]
    for s in range(3):
        for part,count in [('development',evalcfg['development_per_stratum']),('fresh_holdout',evalcfg['fresh_holdout_per_stratum'])]:
            pool=[r for r in profiles if r['split']=='val' and int(np.searchsorted(cuts,float(r['mean_c'])))==s and
                  ((r['image_id'] in seen) if part=='development' else (r['partition']=='holdout' and r['image_id'] not in seen))]
            pool.sort(key=lambda r:hashlib.sha256(f'{evalcfg["seed"]}:v3:{r["image_id"]}'.encode()).hexdigest())
            samples.extend((r['image_id'],part,s) for r in pool[:count])
    fresh={i for i,p,_ in samples if p=='fresh_holdout'}
    assert not fresh&seen and len(fresh)==48
    out=engine.ROOT/'LS_lcad_reviewer/intermediate/experiments'/args.run_id
    if out.exists():raise ValueError('Evaluation run exists; preserve it and use another run ID for a repeat')
    out.mkdir(parents=True);write_json(out/'manifest.json',{'created_at':utc(),'samples':samples,'configuration':cfg,'evaluation_configuration':evalcfg,
                     'fresh_holdout_sources':48,'previously_seen_sources_excluded':len(seen),'test_split_used':False,
                     'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(__file__).with_name('config.json'),Path(__file__).with_name('evaluation_config.json')]}})
    rows=[]
    for j,(image_id,part,s) in enumerate(samples,1):
        rgb=engine.read_rgb(engine.ROOT/cfg['datasets']['val']/'image'/f'{image_id}.jpg',cfg['analysis_max_side']);gt=engine.lab(rgb)
        for name,x,a,d,area in interventions(gt,evalcfg):
            gen=engine.lab(engine.rgb(x));metrics,flags,_=engine.measure(gt,gen,cfg)
            rows.append({'image_id':image_id,'partition':part,'stratum':s,'intervention':name,'a_target':a,'d_target':d,'area_fraction':area,
                         'a_flag':flags['a_candidate'],'d_flag':flags['d_candidate'],'monochrome_review_only':flags['monochrome_review_only'],**metrics})
        if j%12==0:print(f'Geometry/direction sources: {j}/{len(samples)}',flush=True)
    write_json(out/'records.json',rows)
    # Fit the additional pixel coverage on development only; do not promote on its own.
    development=[r for r in rows if r['partition']=='development' and not r['a_target']]
    trials=[{'coverage':x,'development':confusion(development,[r['d_flag'] and r['active_pixel_coverage']>=x for r in development])} for x in evalcfg['pixel_coverage_search']]
    trials.sort(key=lambda r:(r['development']['f1'],-r['development']['fp']),reverse=True);winner=trials[0]['coverage']
    holdout=[r for r in rows if r['partition']=='fresh_holdout' and not r['a_target']]
    result={'production_ready':False,'source_images':len(samples),'cases':len(rows),'pixel_coverage_candidate':winner,'development_trials':trials,
            'v2_rule_fresh_holdout':confusion(holdout,[r['d_flag'] for r in holdout]),
            'v2_plus_pixel_coverage_fresh_holdout':confusion(holdout,[r['d_flag'] and r['active_pixel_coverage']>=winner for r in holdout])}
    result['by_intervention']={n:{'v2':confusion([r for r in holdout if r['intervention']==n],[r['d_flag'] for r in holdout if r['intervention']==n]),
                               'pixel_candidate':confusion([r for r in holdout if r['intervention']==n],[r['d_flag'] and r['active_pixel_coverage']>=winner for r in holdout if r['intervention']==n])} for n in sorted({r['intervention'] for r in holdout})}
    result['A']={'gray_detected':sum(r['a_flag'] for r in rows if r['partition']=='fresh_holdout' and r['intervention']=='grayscale'),
                 'single_tint_detected':sum(r['a_flag'] for r in rows if r['partition']=='fresh_holdout' and r['intervention']=='single_tint'),
                 'false_flags':sum(r['a_flag'] for r in rows if r['partition']=='fresh_holdout' and not r['a_target'])}
    write_json(out/'results.json',result)
    text=['# CV第三轮：方向和几何外推检查','','本轮用新的48张GT留出，不使用真实标签，不测试严重度。扩大方向、局部形状/覆盖，并单列RGB白平衡增益。像素活动覆盖只在24张开发GT上选择。','','| 规则 | 精确率 | 召回率 | F1 | 误报 | 漏报 |','|---|---:|---:|---:|---:|---:|']
    for key in ['v2_rule_fresh_holdout','v2_plus_pixel_coverage_fresh_holdout']:
        m=result[key];text.append(f"| {key} | {m['precision']:.2%} | {m['recall']:.2%} | {m['f1']:.4f} | {m['fp']} | {m['fn']} |")
    text+=['','## 按干预错误','','| 干预 | v2误报/漏报 | 像素覆盖候选误报/漏报 |','|---|---|---|']
    for name,x in result['by_intervention'].items():
        if any(x[k]['fp'] or x[k]['fn'] for k in x):text.append(f"| {name} | {x['v2']['fp']}/{x['v2']['fn']} | {x['pixel_candidate']['fp']}/{x['pixel_candidate']['fn']} |")
    text+=['',f"A保守分支新留出灰阶检出{result['A']['gray_detected']}/48、固定色调检出{result['A']['single_tint_detected']}/48、其他干预误报{result['A']['false_flags']}。色相集中度保留为待复核信息，不直接A熔断。",
           '',f'像素活动覆盖候选阈值={winner}，本轮不自动覆盖活动工作流的参数。高覆盖局部物体与全图偏移、白平衡增益模型均需要真实案例进一步验证。',
           '',f"总计{len(samples)}张GT、{len(rows)}例干预。合成干预类别不是人工语义缺陷真值，不能把本表当实际标注精度。"]
    (out/'report.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['by_intervention','development_trials']},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
