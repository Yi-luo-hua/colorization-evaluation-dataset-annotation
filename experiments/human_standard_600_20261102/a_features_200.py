"""Explore chroma features using human A labels as fixed calibration targets."""
import json

import cv2
import numpy as np
from PIL import Image

from prepare import HERE, ROOT, sha, write
from summarize_200 import SOURCES


def features(path):
    with Image.open(path) as image:
        rgb = np.asarray(image.convert('RGB'),dtype=np.float32)/255
    lab = cv2.cvtColor(rgb,cv2.COLOR_RGB2LAB)
    ab = lab[:,:,1:]
    chroma = np.linalg.norm(ab,axis=2)
    center = np.median(ab.reshape(-1,2),axis=0)
    residual = np.linalg.norm(ab-center,axis=2)
    h,w = chroma.shape
    tiles = [float(chroma[y*h//4:(y+1)*h//4,x*w//4:(x+1)*w//4].mean()) for y in range(4) for x in range(4)]
    mask = (chroma>10).astype(np.uint8)
    n,_,stats,_ = cv2.connectedComponentsWithStats(mask,connectivity=8)
    q = np.percentile(chroma,[50,95,99])
    var_c = float(np.var(chroma,dtype=np.float64))
    var_ab = float(np.var(ab,axis=(0,1),dtype=np.float64).sum())
    return {'mean_C':float(chroma.mean()),'median_C':float(q[0]),'p95_C':float(q[1]),
        'var_C':var_c,'std_C':float(np.sqrt(var_c)),
        'var_a_plus_var_b':var_ab,'std_ab':float(np.sqrt(var_ab)),
        'p99_C':float(q[2]),'max_C':float(chroma.max()),
        'fraction_C_gt5':float((chroma>5).mean()),'fraction_C_gt10':float(mask.mean()),
        'fraction_C_gt20':float((chroma>20).mean()),
        'max_4x4_tile_mean_C':max(tiles),'largest_component_C_gt10_fraction':float(stats[1:,cv2.CC_STAT_AREA].max()/(h*w)) if n>1 else 0,
        'median_tint_C':float(np.linalg.norm(center)),
        'centered_mean_C':float(residual.mean()),'centered_p95_C':float(np.percentile(residual,95))}


def main():
    rows = []
    for source in SOURCES:
        for r in json.loads(source.read_text(encoding='utf-8'))['reviews']:
            image = ROOT/r['record']['model_path']
            assert sha(image)==r['record']['model_sha256']
            labels = {d['id']:d['severity'] for d in r['defects']}
            generated = features(image)
            gt_path = ROOT/r['record']['gt_path']
            assert sha(gt_path)==r['record']['gt_sha256']
            gt_mean = features(gt_path)['mean_C']
            rows.append({'review_index':r['review_index'],'human_labels':labels,
                'human_A':'A' in labels,'features':generated,'GT_mean_C':gt_mean,
                'mean_C_to_GT_ratio':generated['mean_C']/gt_mean if gt_mean>0 else None})
    positives = [r for r in rows if r['human_A']]
    groups = {'A':positives,'non_A':[r for r in rows if not r['human_A']],
        'non_A_E2':[r for r in rows if not r['human_A'] and 'E2' in r['human_labels']],
        'non_A_E2_L3':[r for r in rows if r['human_labels'].get('E2')=='L3']}
    ranges = {group:{key:{'min':min(r['features'][key] for r in records),
        'median':float(np.median([r['features'][key] for r in records])),
        'max':max(r['features'][key] for r in records)} for key in positives[0]['features']}
        for group,records in groups.items()}
    mean_ceiling = max(r['features']['mean_C'] for r in positives)
    p99_ceiling = max(r['features']['p99_C'] for r in positives)
    mean_overlap = [r['review_index'] for r in rows if not r['human_A'] and r['features']['mean_C']<=mean_ceiling]
    joint_overlap = [r['review_index'] for r in rows if not r['human_A'] and r['features']['mean_C']<=mean_ceiling and r['features']['p99_C']<=p99_ceiling]
    variance_comparisons = {}
    for key in ['var_C','var_a_plus_var_b']:
        ceiling = max(r['features'][key] for r in positives)
        overlap = [r['review_index'] for r in rows if not r['human_A']
            and r['features']['mean_C']<=mean_ceiling and r['features'][key]<=ceiling]
        variance_comparisons[key] = {'positive_maximum':ceiling,
            'non_A_within_mean_and_variance_envelope':overlap,
            'qualifier':'Descriptive fitting on the same 10 positive anchors; not held-out evaluation.'}
    result = {'human_A_authority':'All ten human A decisions are accepted positive anchors; earlier AI rejection suggestions withdrawn.',
        'method':'OpenCV float32 RGB [0,1] to CIELAB; C*=sqrt(a*^2+b*^2). Original generated images and GT are unchanged.',
        'sources':[{'path':str(p),'sha256':sha(p)} for p in SOURCES],
        'counts':{k:len(v) for k,v in groups.items()},'ranges':ranges,
        'mean_plus_variance_descriptive_comparison':variance_comparisons,
        'descriptive_positive_envelope_NOT_VALIDATED_THRESHOLDS':{'max_human_A_mean_C':mean_ceiling,
            'max_human_A_p99_C':p99_ceiling,'non_A_also_below_A_mean_ceiling':mean_overlap,
            'non_A_also_below_both_ceilings':joint_overlap},'records':rows,
        'limits':'Ten positives, selected calibration subset only. Numeric cutoffs and segmentation rules are not validated, and no new workflow or human-label changes are executed.'}
    folder = HERE/'local/A_calibration_20261104'
    folder.mkdir(exist_ok=True)
    write(folder/'chroma_features.json',result)
    print(json.dumps({'counts':result['counts'],'A_features':[{'index':r['review_index'],**r['features']} for r in positives],
        'E2_L3':[r for r in groups['non_A_E2_L3']],
        'A_ranges':ranges['A'],'envelope':result['descriptive_positive_envelope_NOT_VALIDATED_THRESHOLDS'],
        'variance_comparisons':variance_comparisons},ensure_ascii=True))


if __name__=='__main__': main()
