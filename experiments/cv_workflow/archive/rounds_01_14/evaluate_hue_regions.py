"""Check reliable hue navigation without adding images to the default visual stage."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time
import cv2
import numpy as np
import engine
import optimize
import region_models as rm
from workflow import OUTPUT,read_json,write_json,utc


def main():
    started=time.perf_counter();cv2.setNumThreads(1)
    config=read_json(OUTPUT/'ce_signed_12_20261012/manifest.json')['configuration'];settings=config['regions']
    optimize.OPT=read_json(OUTPUT/'cv_models_v4_20261012/manifest.json')['optimization_configuration']
    samples=read_json(OUTPUT/'cv_regions_confirm_20261012/manifest.json')['samples']
    out=OUTPUT/'ce_hue_regions_20261012';out.mkdir()
    write_json(out/'manifest.json',{'created_at':utc(),'samples':samples,'settings':settings,'parameter_search':False,
               'previous_ROI_GT_reused':True,'test_split_used':False,'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(rm.__file__)]}})
    def measure(g,m,jpeg=False):
        maps=engine.difference_maps(g,m)
        raw=rm.anchored_regions(maps,settings,prefer_compact=jpeg)
        weighted=maps['hue_component']*np.sqrt(np.minimum(engine.chroma(g),engine.chroma(m))/(np.maximum(engine.chroma(g),engine.chroma(m))+1e-8))
        reliable=rm.anchored_regions({**maps,'hue_component':weighted},settings,prefer_compact=jpeg)
        return raw,reliable
    def trial(image_id):
        original=engine.read_rgb(engine.ROOT/config['datasets']['val']/'image'/f'{image_id}.jpg',settings['max_side']);rows=[];controls=[]
        for area in optimize.OPT['small_region_areas']:
            for jpeg in ([False,True] if area==.01 else [False]):
                generated,box=optimize.roi_trial(original,'hue_change',area,jpeg)
                for resolution in [256,512]:
                    h,w=original.shape[:2];ratio=min(1,resolution/max(h,w));size=(round(w*ratio),round(h*ratio))
                    g=engine.lab(cv2.resize(original,size,interpolation=cv2.INTER_AREA));m=engine.lab(cv2.resize(generated,size,interpolation=cv2.INTER_AREA))
                    raw,reliable=measure(g,m,jpeg)
                    rows.append({'image_id':image_id,'area':area,'jpeg':jpeg,'resolution':resolution,
                                 'raw_iou':max([optimize.bbox_iou(r['bbox_normalized'],box) for r in raw if r['kind']=='hue_change'],default=0),
                                 'reliable_iou':max([optimize.bbox_iou(r['bbox_normalized'],box) for r in reliable if r['kind']=='hue_change'],default=0)})
        gt=engine.lab(original)
        for name,scale in [('gray',0),('radial_0.1',.1)]:
            x=gt.copy();x[...,1:]*=scale;m=engine.lab(engine.rgb(x));raw,reliable=measure(gt,m)
            controls.append({'image_id':image_id,'control':name,'raw_hue_regions':sum(r['kind']=='hue_change' for r in raw),
                             'reliable_hue_regions':sum(r['kind']=='hue_change' for r in reliable)})
        return rows,controls
    rows=[];controls=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for index,(batch,control) in enumerate(pool.map(trial,samples),1):
            rows.extend(batch);controls.extend(control)
            if index%12==0:print(f'Hue region controls: {index}/48 GT',flush=True)
    result={'GT_sources':len(samples),'ROI_cases':len(rows),'control_cases':len(controls),
            'mean_iou':{key:float(np.mean([r[key] for r in rows])) for key in ['raw_iou','reliable_iou']},
            'recall_iou50':{key:float(np.mean([r[key]>=.5 for r in rows])) for key in ['raw_iou','reliable_iou']},
            'controls_with_hue_region':{name:{key:sum(r[key]>0 for r in controls if r['control']==name) for key in ['raw_hue_regions','reliable_hue_regions']} for name in ['gray','radial_0.1']},
            'by_resolution':{str(res):{key:float(np.mean([r[key] for r in rows if r['resolution']==res])) for key in ['raw_iou','reliable_iou']} for res in [256,512]},
            'wall_seconds':time.perf_counter()-started,'not_semantic_C_E_accuracy':True}
    write_json(out/'records.json',rows);write_json(out/'controls.json',controls);write_json(out/'results.json',result);print(result,flush=True)


if __name__=='__main__':main()
