"""Ablation, integration check and measured overhead for the frozen D experiment."""
import copy
import time
from pathlib import Path
import cv2
import numpy as np
import engine
import optimize
from workflow import read_json, write_json
from experiment_d_groups import ROOT


def main():
    cv2.setNumThreads(1)
    out=ROOT/'cv_d_color_groups_20261012'; rows=read_json(out/'real_records.json')
    comparisons={}
    for part in ['development','holdout','all']:
        group=[r for r in rows if not r['a_target'] and (part=='all' or r['partition']==part)]
        comparisons[part]={
            'v4':optimize.confusion(group,[r['baseline_d'] for r in group],'d_target'),
            'scalar_gain_only':optimize.confusion(group,[r['baseline_d'] and r['metrics']['scalar_gain']>=0.2 for r in group],'d_target'),
            'selected_groups':optimize.confusion(group,[r['group_prediction'] for r in group],'d_target')}
    config=read_json(Path(__file__).with_name('config.json')); baseline=copy.deepcopy(config)
    baseline['global_models']['d'].pop('color_groups')
    manifest=read_json(ROOT/'real_boundary_full_fast_20261012/manifest.json')
    inputs=[]
    for r in manifest['records']:
        gt=engine.read_rgb(engine.ROOT/r['gt_path'],config['analysis_max_side'])
        gen=engine.read_rgb(engine.ROOT/r['model_path'],config['analysis_max_side'])
        if gt.shape!=gen.shape: gen=cv2.resize(gen,(gt.shape[1],gt.shape[0]),interpolation=cv2.INTER_AREA)
        inputs.append((r['sample_key'],engine.lab(gt),engine.lab(gen)))
    expected={r['sample_key']:r['group_prediction'] for r in rows}
    differences=[];times={'v4':[],'v5':[]}
    for repeat in range(3):
        for key,gt,gen in inputs:
            for name,cfg in ([('v4',baseline),('v5',config)] if repeat%2==0 else [('v5',config),('v4',baseline)]):
                started=time.perf_counter();_,flags,_=engine.measure(gt,gen,cfg)
                times[name].append((time.perf_counter()-started)*1000)
                if name=='v5' and repeat==0 and flags['d_candidate']!=expected[key]: differences.append(key)
    result={'real_weak_reference_ablation':comparisons,
            'active_engine_differences_from_frozen_experiment':differences,
            'numerical_measurement_mean_ms':{k:float(np.mean(v)) for k,v in times.items()},
            'profiling_samples':len(inputs),'profiling_repeats':3,
            'overhead_excludes_image_IO_ROI_rendering_and_model_calls':True}
    write_json(out/'deployment_check.json',result);print(result,flush=True)


if __name__=='__main__':main()
