"""Offline generated-image A suspects; frozen GT eligibility, no semantic labels."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
import numpy as np

import engine
import generated_color
from workflow import BASE,OUTPUT,model_image,read_json,write_json,utc


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run-id',required=True)
    p.add_argument('--splits',nargs='+',choices=['train','val','test'],default=['train','val','test'])
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--include-excluded',action='store_true',help='Screen excluded-source generated images too; never re-admit them for annotation')
    p.add_argument('--reuse-screen',type=Path,help='Reuse matching recorded RGB measurements; only decode additional source images')
    p.add_argument('--config',type=Path,default=Path(__file__).with_name('config.json'))
    a=p.parse_args();cfg=read_json(a.config)
    if cfg['a'].get('screening_enabled',True) is False:
        raise SystemExit('A screening stopped by user; reuse the frozen human A list.')
    out=OUTPUT/a.run_id;out.mkdir()
    gate_path=engine.ROOT/cfg['gt_filter']['exclude_manifest']
    gate=read_json(gate_path);blocked={(r['split'],r['image_id']) for r in gate['excluded_GT']+gate.get('unresolved',[])}
    jobs=[];sources={str(gate_path.relative_to(engine.ROOT)):engine.sha256(gate_path)}
    for split in a.splits:
        for model in ['lcad','unicolor']:
            pool=next((BASE/'tasks_pool'/split).glob(f'*{model}*.json'))
            sources[str(pool.relative_to(engine.ROOT))]=engine.sha256(pool)
            for index,task in enumerate(read_json(pool),1):
                stem=Path(task['data']['original_record']['image_id']).stem
                if a.include_excluded or (split,stem) not in blocked:jobs.append((split,model,index,stem))
    previous={}
    if a.reuse_screen:
        prior=read_json(a.reuse_screen/'manifest.json')
        if prior['source_task_sha256']!=sources:
            raise ValueError('Reuse screen source task identities differ')
        previous={r['sample_key']:r for r in read_json(a.reuse_screen/'records.json')}
    write_json(out/'manifest.json',{'created_at':utc(),'state':'offline_A_screen','configuration':cfg,
        'splits':a.splits,'samples':len(jobs),'source_task_sha256':sources,'no_new_GT_qualification':True,
        'include_excluded':a.include_excluded,'reuse_screen':str(a.reuse_screen) if a.reuse_screen else None,
        'source_code_sha256':{x.name:engine.sha256(x) for x in [Path(__file__),Path(generated_color.__file__)]},
        'no_AI_calls':True,'no_final_A_labels':True})
    cv2.setNumThreads(1)
    def measure(job):
        split,model,index,stem=job
        key=f'{split}/{model}/{stem}';eligible=(split,stem) not in blocked
        if key in previous:
            old=previous[key];color=old['generated_color'];hist=np.array(color['rgb_channel_spread_histogram'])
            coloured=int(hist[cfg['a']['maximum_gray_channel_spread']+1:].sum());fraction=coloured/color['pixels'];gray=1-fraction
            color={**color,'colored_pixel_count':coloured,'colored_pixel_fraction':fraction,'gray_pixel_fraction':gray,
                   'gray_channel_tolerance':cfg['a']['maximum_gray_channel_spread'],
                   'minimum_gray_pixel_fraction':cfg['a']['minimum_gray_pixel_fraction'],
                   'grayscale_candidate':gray>=cfg['a']['minimum_gray_pixel_fraction']}
            return {**old,'generated_color':color,'GT_eligible':eligible,'measurement_reused':True}
        path=model_image(engine.ROOT/cfg['datasets'][split]/'model'/model,stem)
        image=engine.read_rgb(path)
        return {'sample_key':key,'split':split,'model':model,'task_idx':index,'GT_eligible':eligible,'measurement_reused':False,
            'model_path':str(path.relative_to(engine.ROOT)),'generated_color':generated_color.measure(image,cfg['a'],include_histogram=True)}
    rows=[]
    with ThreadPoolExecutor(max_workers=a.workers) as pool:
        for i,row in enumerate(pool.map(measure,jobs),1):
            rows.append(row)
            if i%1000==0:print(f'A offline screen: {i}/{len(jobs)}',flush=True)
    suspects=[r for r in rows if r['generated_color']['grayscale_candidate']]
    write_json(out/'records.json',rows);write_json(out/'candidates.json',suspects)
    for split in a.splits:
        selected=[{'model':r['model'],'task_idx':r['task_idx'],'sample_key':r['sample_key']} for r in suspects if r['split']==split and r['GT_eligible']]
        if selected:write_json(out/f'selection_{split}.json',{'split':split,'samples':selected})
    write_json(out/'summary.json',{'created_at':utc(),'samples':len(rows),'A_suspects':len(suspects),
        'strict_grayscale_images':sum(r['generated_color']['strict_grayscale'] for r in rows),
        'GT_eligible_samples':sum(r['GT_eligible'] for r in rows),
        'excluded_source_samples':sum(not r['GT_eligible'] for r in rows),
        'measurements_reused':sum(r['measurement_reused'] for r in rows),
        'newly_decoded_images':sum(not r['measurement_reused'] for r in rows),
        'by_split':{s:{'samples':sum(r['split']==s for r in rows),'suspects':sum(r['split']==s for r in suspects)} for s in a.splits},
        'pixel_channel_tolerance':cfg['a']['maximum_gray_channel_spread'],
        'minimum_gray_pixel_fraction':cfg['a']['minimum_gray_pixel_fraction'],
        'thresholds_provisional':True,'visual_confirmation_pending':True,'new_native_calls':0})
    print(f'Finished: {len(suspects)} A suspects / {len(rows)} real generated images',flush=True)


if __name__=='__main__':main()
