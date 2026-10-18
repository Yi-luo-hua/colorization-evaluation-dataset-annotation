"""Fixed-rule confirmation on fresh GT: severe E2, exposure, partial gains, tint colors."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np

import engine
import global_models as gm
import optimize
from workflow import read_json,write_json,utc


def main():
    cv2.setNumThreads(1);root=engine.ROOT/'LS_lcad_reviewer/intermediate/experiments'
    config=read_json(Path(__file__).with_name('config.json'));optimize.CONFIG=config
    optimize.OPT=read_json(root/'cv_models_v4_20261012/manifest.json')['optimization_configuration']
    eval_cfg=read_json(root/'cv_geometry_v3_20261012/manifest.json')['evaluation_configuration']
    samples=read_json(root/'cv_regions_confirm_20261012/manifest.json')['samples']
    out=root/'cv_models_stress_20261012'
    if out.exists():raise ValueError('Stress run exists')
    out.mkdir(parents=True);write_json(out/'manifest.json',{'created_at':utc(),'samples':samples,'configuration':config,
                 'parameter_search':False,'same_new_GT_as_region_confirmation':True,'test_split_used':False,
                 'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(gm.__file__),Path(engine.__file__)]}})

    def trial(image_id):
        rgb=engine.read_rgb(engine.ROOT/config['datasets']['val']/'image'/f'{image_id}.jpg',config['analysis_max_side']);gt=engine.lab(rgb)
        changes=list(optimize.alterations(gt,eval_cfg))
        for a,b in [(20,-15),(1,1)]:
            x=gt.copy();x[...,1]=a;x[...,2]=b;changes.append((f'tint_{a}_{b}',x,True,False,1))
        x=gt.copy();x[...,1:]*=0.1;changes.append(('severe_desaturation_0.1',x,False,False,1))
        base=engine.rgb(gt).astype(np.float32)/255
        for domain in ['encoded','linear']:
            for i,gains in enumerate([[1.15,1,0.85],[0.85,1,1.15]]):
                transformed=np.clip((base if domain=='encoded' else gm.to_linear(base))*np.array(gains),0,1)
                if domain=='linear':transformed=gm.to_srgb(transformed)
                full=engine.lab(np.rint(transformed*255).astype(np.uint8))
                expected=np.linalg.norm(full[...,1:]-gt[...,1:],axis=-1);box=optimize.strong_bbox(expected,0.1)
                x1,y1,x2,y2=box;full[y1:y2,x1:x2]=gt[y1:y2,x1:x2]
                changes.append((f'partial_{domain}_gain90_{i}',full,False,False,0.9))
        rows=[]
        for name,x,a,d,area in changes:
            gen=engine.lab(engine.rgb(x));m,f,_=optimize.BASELINE.measure(gt,gen,config)
            row={'image_id':image_id,'intervention':name,'a_target':a,'d_target':d,'baseline_a':f['a_candidate'],'baseline_d':f['d_candidate'],
                 'metrics':m,'models':gm.measure(gt,gen,config['global_models']['features'])}
            row['a_prediction']=gm.predict_a(row,config['global_models']['a']);row['d_prediction']=gm.predict_d(row,config['global_models']['d']);rows.append(row)
        return rows

    rows=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,batch in enumerate(pool.map(trial,samples),1):
            rows.extend(batch)
            if i%8==0:print(f'Fresh model stress sources: {i}/48',flush=True)
    write_json(out/'records.json',rows)
    d=[r for r in rows if not r['a_target']]
    result={'production_ready':False,'source_images':48,'cases':len(rows),
            'A':optimize.confusion(rows,[r['a_prediction'] for r in rows],'a_target'),
            'D':optimize.confusion(d,[r['d_prediction'] for r in d],'d_target'),
            'baseline_A':optimize.confusion(rows,[r['baseline_a'] for r in rows],'a_target'),
            'baseline_D':optimize.confusion(d,[r['baseline_d'] for r in d],'d_target'),
            'by_intervention':{n:{'A':optimize.confusion([r for r in rows if r['intervention']==n],[r['a_prediction'] for r in rows if r['intervention']==n],'a_target'),
                                  'D':optimize.confusion([r for r in rows if r['intervention']==n],[r['d_prediction'] for r in rows if r['intervention']==n],'d_target')} for n in sorted({r['intervention'] for r in rows})},
            'cascade_D':optimize.confusion(rows,[r['d_prediction'] and not r['a_prediction'] for r in rows],'d_target'),
            'true_D_routed_to_A':sum(r['a_prediction'] and r['d_target'] for r in rows)}
    write_json(out/'results.json',result);print({k:v for k,v in result.items() if k!='by_intervention'},flush=True)


if __name__=='__main__':main()
