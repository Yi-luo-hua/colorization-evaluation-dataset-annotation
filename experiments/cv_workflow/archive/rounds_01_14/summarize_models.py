"""Summarize frozen runs and bootstrap by source GT, not correlated interventions."""
from pathlib import Path

import numpy as np

import engine
from workflow import read_json,write_json


def main():
    root=engine.ROOT/'LS_lcad_reviewer/intermediate/experiments'
    stress=root/'cv_models_stress_20261012'
    rows=read_json(stress/'records.json')
    roi=read_json(root/'cv_regions_confirm_20261012/records.json')
    ids=sorted({r['image_id'] for r in rows})
    assert set(ids)=={r['image_id'] for r in roi}
    counts=[];overlaps=[]
    for image_id in ids:
        group=[r for r in rows if r['image_id']==image_id]
        vector=[]
        for target,prediction,selected in [('a_target','a_prediction',group),
                                           ('d_target','d_prediction',[r for r in group if not r['a_target']])]:
            vector.extend([sum(r[target] and r[prediction] for r in selected),
                           sum(not r[target] and r[prediction] for r in selected),
                           sum(r[target] and not r[prediction] for r in selected)])
        counts.append(vector)
        overlaps.append([np.mean([r[k] for r in roi if r['image_id']==image_id])
                         for k in ['baseline_iou','primary_iou']])
    counts=np.array(counts);overlaps=np.array(overlaps)
    rng=np.random.default_rng(20261012);values=[]
    for _ in range(1000):
        index=rng.integers(0,len(ids),len(ids));total=counts[index].sum(0);metrics=[]
        for tp,fp,fn in [total[:3],total[3:]]:
            metrics.extend([tp/(tp+fp),tp/(tp+fn),2*tp/(2*tp+fp+fn)])
        metrics.extend(overlaps[index].mean(0));values.append(metrics)
    names=['a_precision','a_recall','a_f1','d_precision','d_recall','d_f1','roi_baseline_mean_iou','roi_primary_mean_iou']
    summary={'source_gt_count':len(ids),'bootstrap_replicates':1000,'bootstrap_unit':'GT image ID',
             'warning':'Synthetic interventions only; ROI and global confirmation share the same 48 GT images.',
             'intervals_95_percent':{k:np.percentile(np.array(values)[:,i],[2.5,97.5]).tolist() for i,k in enumerate(names)}}
    write_json(stress/'cluster_bootstrap.json',summary)
    for entry in read_json(stress/'source_verification.json'):
        assert engine.sha256(engine.ROOT/entry['matching_source'])==entry['sha256'],entry
    print(summary)
    print('PASS: all recorded source snapshots match their run manifests')


if __name__=='__main__':main()
