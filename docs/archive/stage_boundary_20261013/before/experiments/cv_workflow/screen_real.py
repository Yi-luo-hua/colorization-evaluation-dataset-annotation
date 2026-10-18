"""Unlabelled validation screening for a real boundary review cohort."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re

import cv2

import engine
from workflow import BASE,OUTPUT,align,model_image,read_json,write_json,utc


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run-id',required=True);args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+',args.run_id):raise ValueError('Invalid run ID')
    out=OUTPUT/args.run_id
    if out.exists():raise ValueError('Screen already exists; use a new run ID')
    cfg=read_json(Path(__file__).with_name('config.json'));cv2.setNumThreads(1)
    dataset=engine.ROOT/cfg['datasets']['val'];jobs=[];pools={}
    excluded=set()
    if cfg.get('gt_reference',{}).get('exclude_manifest'):
        path=engine.ROOT/cfg['gt_reference']['exclude_manifest'];registry=read_json(path)
        excluded={(r['split'],r['image_id']) for r in registry['excluded_GT']+registry.get('unresolved',[])}
        pools[str(path.relative_to(engine.ROOT))]=engine.sha256(path)
    for model in ['lcad','unicolor']:
        path=next((BASE/'tasks_pool/val').glob(f'*{model}*.json'));pools[str(path.relative_to(engine.ROOT))]=engine.sha256(path)
        for index,task in enumerate(read_json(path),1):
            # Only source identity is read. Historical labels/scores are not measurements.
            stem=Path(task['data']['original_record']['image_id']).stem
            if ('val',stem) in excluded:continue
            jobs.append((model,index,stem))
    out.mkdir(parents=True)
    write_json(out/'manifest.json',{'created_at':utc(),'state':'unlabelled_screening','configuration':cfg,
               'split':'val','test_split_used':False,'source_task_sha256':pools,
               'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(__file__).with_name('global_models.py')]},
               'total_pairs':len(jobs),'historical_labels_used':False})

    def measure(job):
        model,index,stem=job;gp=dataset/'image'/f'{stem}.jpg';mp=model_image(dataset/'model'/model,stem)
        gt=engine.read_rgb(gp,cfg['analysis_max_side']);gen=align(gt,engine.read_rgb(mp,cfg['analysis_max_side']))
        metrics,flags,_=engine.measure(engine.lab(gt),engine.lab(gen),cfg)
        return {'sample_key':f'val/{model}/{stem}','image_id':stem,'model':model,'task_idx':index,
                'gt_sha256':engine.sha256(gp),'model_sha256':engine.sha256(mp),'metrics':metrics,'cv_flags':flags}

    rows=[]
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i,row in enumerate(pool.map(measure,jobs),1):
            rows.append(row)
            if i%120==0:print(f'Unlabelled validation pairs: {i}/{len(jobs)}',flush=True)
    write_json(out/'records.json',rows)
    write_json(out/'summary.json',{'pairs':len(rows),'GT_images':len({r['image_id'] for r in rows}),
               'A_candidates':sum(r['cv_flags']['a_candidate'] for r in rows),
               'D_candidates':sum(r['cv_flags']['d_candidate'] for r in rows),
               'warning':'Counts are numerical candidates, not defect prevalence or accuracy.'})
    print(out,flush=True)


if __name__=='__main__':main()
