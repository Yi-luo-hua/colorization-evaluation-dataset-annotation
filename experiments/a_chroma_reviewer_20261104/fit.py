"""Fit exactly two threshold parameters, without selecting on validation labels."""
from datetime import datetime, timezone
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def confusion(rows,thresholds):
    tp=fp=fn=tn=0
    for r in rows:
        predicted = r['mean_C']<=thresholds['mean_C_max'] and r['var_ab']<=thresholds['var_ab_max']
        actual = r['label']=='A'
        tp += predicted and actual; fp += predicted and not actual
        fn += not predicted and actual; tn += not predicted and not actual
    n = len(rows)
    return {'n':n,'TP':tp,'FP':fp,'FN':fn,'TN':tn,
        'precision':tp/(tp+fp) if tp+fp else None,
        'recall':tp/(tp+fn) if tp+fn else None,
        'balanced_accuracy':(tp/(tp+fn)+tn/(tn+fp))/2 if tp+fn and tn+fp else None}


def seed_rows():
    path = ROOT/'experiments/human_standard_600_20261102/local/A_calibration_20261104/chroma_features.json'
    d = json.loads(path.read_text(encoding='utf-8'))
    return [{'id':'seed-'+str(r['review_index']),'mean_C':r['features']['mean_C'],
        'var_ab':r['features']['var_a_plus_var_b'],'label':'A' if r['human_A'] else 'not_A'} for r in d['records']]


def optimize(rows):
    # Candidate boundaries are observed training values, not arbitrary hard-coded cutoffs.
    means = np.unique([0.]+[r['mean_C'] for r in rows])
    variances = np.unique([0.]+[r['var_ab'] for r in rows])
    pos = np.zeros((len(means),len(variances)),dtype=np.int64)
    neg = np.zeros_like(pos)
    for r in rows:
        target = pos if r['label']=='A' else neg
        target[np.searchsorted(means,r['mean_C']),np.searchsorted(variances,r['var_ab'])] += 1
    positives,negatives = int(pos.sum()),int(neg.sum())
    if not positives or not negatives:
        raise ValueError('需要A与非A两类确定标注')
    tp = pos.cumsum(0).cumsum(1)
    fp = neg.cumsum(0).cumsum(1)
    # Integer form of balanced accuracy; tie-break by fewer false positives,
    # then fewer false negatives, then the tighter threshold rectangle.
    score = tp*negatives+(negatives-fp)*positives
    a,b = np.where(score==score.max())
    chosen = min(zip(a,b),key=lambda ij:(int(fp[ij]),positives-int(tp[ij]),int(ij[0]+ij[1]),int(ij[0])))
    return {'mean_C_max':float(means[chosen[0]]),'var_ab_max':float(variances[chosen[1]])}


def fit_model(manifest,labels,revision):
    new = [{**r,'label':labels[r['id']]['label']} for r in manifest['records']
        if labels.get(r['id'],{}).get('label') in ['A','not_A']]
    training = seed_rows()+[r for r in new if r['partition']=='training']
    validation = [r for r in new if r['partition']=='validation']
    pending = sum(r['id'] not in labels for r in manifest['records'])
    unsure = sum(labels.get(r['id'],{}).get('label')=='unsure' for r in manifest['records'])
    base = {'created_at':datetime.now(timezone.utc).isoformat(),'label_revision':revision,
        'function':'A = (mean_C <= mean_C_max) and (var_ab <= var_ab_max)',
        'feature_definition':manifest['feature_definition'],'new_definite_labels':len(new),
        'new_A':sum(r['label']=='A' for r in new),'new_not_A':sum(r['label']=='not_A' for r in new),
        'pending':pending,'unsure_excluded_from_fit':unsure,
        'source':'187 fixed human-reviewed development anchors plus new human judgments',
        'validation_policy':'New candidates grouped by GT SHA-256, preassigned 80/20; validation labels never used for threshold selection.',
        'scope':'Enriched candidate calibration pool; metrics do not estimate full-dataset prevalence or independent workflow performance.'}
    if not new:
        return {**base,'status':'awaiting_human_labels','thresholds':None}
    thresholds = optimize(training)
    complete = pending==0 and base['new_A']>0 and base['new_not_A']>0
    return {**base,'status':'review_round_complete' if complete else 'provisional',
        'thresholds':thresholds,'training':confusion(training,thresholds),
        'validation':confusion(validation,thresholds),
        'training_ids':[r['id'] for r in training],'validation_ids':[r['id'] for r in validation],
        'decision_python':'def is_A(mean_C, var_ab):\n    return mean_C <= '+repr(thresholds['mean_C_max'])+' and var_ab <= '+repr(thresholds['var_ab_max'])+'\n'}
