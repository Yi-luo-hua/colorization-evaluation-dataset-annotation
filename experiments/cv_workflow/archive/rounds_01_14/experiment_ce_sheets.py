"""Matched 12-sample display trial: signed chroma alone versus chroma + hue.

No old labels enter either prompt; no numerical thresholds are fitted to AI labels.
"""
import argparse
import copy
import time
from pathlib import Path
import cv2
from workflow import OUTPUT,read_json,write_json,utc,prepare,render
import engine


def main():
    cv2.setNumThreads(1);out=OUTPUT/'ce_display_round7_20261012';out.mkdir()
    config=read_json(Path(__file__).with_name('config.json'))
    source=OUTPUT/'real_boundary_cv5_file_20261012'
    manifest=read_json(source/'manifest.json')
    # Preselected clothing, frisbee/grass, tennis, foliage, neutral-plate cases.
    keys=[f'S{i:03d}' for i in [3,4,5,6,10,12,21,22,23,24,28,30]]
    records=[r for r in manifest['records'] if r['sample_key'] in keys]
    selection={'split':'val','samples':[{'model':r['model'],'task_idx':r['task_idx'],'sample_key':r['source_sample_key']} for r in records]}
    write_json(out/'selection.json',selection)
    base=OUTPUT/'ce_signed_12_20261012';started=time.perf_counter()
    prepare(argparse.Namespace(model='both',split='val',start=1,end=12,selection=out/'selection.json',run_id=base.name),config)
    base_seconds=time.perf_counter()-started
    from run_harness_trial import prepare_trial
    trial=OUTPUT/'ce_chroma_hue_12_20261012';tm=prepare_trial(base,trial,'compact')
    tm['configuration']['display']['mode']='chroma_hue'
    started=time.perf_counter();tm['sheets']=render(tm['records'],trial,tm['configuration']);dual_seconds=time.perf_counter()-started
    write_json(trial/'manifest.json',tm)
    request=read_json(trial/'review_request.json');request['display']=tm['configuration']['display'];write_json(trial/'review_request.json',request)
    for r in tm['records']:
        r['source_sha256_verified']=engine.sha256(engine.ROOT/r['gt_path'])==r['gt_sha256'] and engine.sha256(engine.ROOT/r['model_path'])==r['model_sha256']
    # Label-free targeted signal inventory, rather than declaring semantic C/E truth.
    inventory=[]
    for r in tm['records']:
        gt=engine.read_rgb(engine.ROOT/r['gt_path'],config['analysis_max_side']);gen=engine.read_rgb(engine.ROOT/r['model_path'],config['analysis_max_side'])
        if gt.shape!=gen.shape:gen=cv2.resize(gen,(gt.shape[1],gt.shape[0]),interpolation=cv2.INTER_LINEAR)
        import numpy as np
        maps=engine.difference_maps(engine.lab(gt),engine.lab(gen));quiet=np.abs(maps['signed_dc'])<=config['display']['deadzone']
        inventory.append({'sample_key':r['sample_key'],'hue_only_pixel_fraction':float(np.mean(quiet & (maps['hue_component']>config['display']['deadzone']))),
                          'hue_p95':float(np.percentile(maps['hue_component'],95)),
                          'signed_chroma_abs_p95':float(np.percentile(np.abs(maps['signed_dc']),95))})
    write_json(out/'manifest.json',{'created_at':utc(),'samples':len(records),'GT_clusters':len(records)//2,
               'baseline':base.name,'trial':trial.name,'sample_source_mapping':[{k:r[k] for k in ['sample_key','source_sample_key']} for r in tm['records']],
               'matched_images_and_CV':True,'changed_surface':'third panel + matching legend',
               'signal_inventory':inventory,'baseline_prepare_seconds':base_seconds,'dual_render_seconds':dual_seconds,
               'known_label_reference_used':False,'selection_is_targeted_not_representative':True,
               'source_sha256':{p.name:engine.sha256(p) for p in [Path(__file__),Path(engine.__file__),Path(__file__).with_name('workflow.py'),Path(__file__).with_name('compact_harness.py')]}})
    print(f'Prepared matched 12 samples / 2 sheets each: {base.name}, {trial.name}')


if __name__=='__main__':main()
