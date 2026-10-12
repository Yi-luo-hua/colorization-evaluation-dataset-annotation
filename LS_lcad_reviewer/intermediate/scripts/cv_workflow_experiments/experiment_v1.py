"""Read-only source experiment: GT priors, legacy-label exploration, controlled CV trials.

All outputs go to intermediate/. No production classifier/export is changed.
Synthetic labels describe interventions, not human semantic defect/severity labels.
"""
import argparse
import csv
import hashlib
import itertools
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'LS_lcad_reviewer'
DATASET = {'train': ROOT / '9_14_10000GT_V1', 'val': ROOT / '10_5_val_V1'}


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


def read_rgb(path, max_side):
    bgr = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if bgr is None:
        raise ValueError(f'Cannot decode {path}')
    h, w = bgr.shape[:2]
    if max(h, w) > max_side:
        scale = max_side / max(h, w)
        bgr = cv2.resize(bgr, (round(w * scale), round(h * scale)), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (w, h)


def lab_from_rgb(rgb):
    return cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)


def model_path(image_id, model):
    directory = DATASET['val'] / 'model' / model
    for extension in ['.png', '.jpg', '.jpeg']:
        path = directory / f'{image_id}{extension}'
        if path.exists():
            return path
    raise FileNotFoundError(f'No model image for {model}/{image_id}')


def rgb_from_lab(lab):
    rgb = cv2.cvtColor(lab.astype(np.float32), cv2.COLOR_LAB2RGB)
    return np.clip(np.rint(rgb * 255), 0, 255).astype(np.uint8)


def quantiles(values):
    a = np.asarray(values, dtype=np.float64)
    return {'n': len(a), 'mean': float(a.mean()), **{f'p{q:g}': float(np.percentile(a, q)) for q in [0, 1, 5, 25, 50, 75, 90, 95, 99, 100]}}


def chroma(lab):
    return np.linalg.norm(lab[..., 1:], axis=-1)


def profile(lab, gray_levels):
    c = chroma(lab)
    center = np.median(lab[..., 1:].reshape(-1, 2), axis=0)
    spread = np.linalg.norm(lab[..., 1:] - center, axis=-1)
    return {
        'mean_c': float(c.mean()), 'p05_c': float(np.percentile(c, 5)),
        'p50_c': float(np.median(c)), 'p95_c': float(np.percentile(c, 95)),
        'centered_spread_p95': float(np.percentile(spread, 95)),
        'mean_l': float(lab[..., 0].mean()), 'mean_a': float(lab[..., 1].mean()),
        'mean_b': float(lab[..., 2].mean()),
        **{f'gray_fraction_c_lt_{x:g}': float(np.mean(c < x)) for x in gray_levels}
    }


def partition(image_id, cfg):
    digest = hashlib.sha256(f'{cfg["seed"]}:{image_id}'.encode()).hexdigest()
    return 'calibration' if int(digest[:8], 16) / 2**32 < cfg['calibration_fraction'] else 'holdout'


def gt_record(item, cfg):
    split, path = item
    rgb, size = read_rgb(path, cfg['max_side'])
    lab = lab_from_rgb(rgb)
    hist = np.histogram(chroma(lab), bins=np.arange(0, 182, 2))[0]
    return {'split': split, 'image_id': path.stem, 'width': size[0], 'height': size[1],
            'partition': partition(path.stem, cfg) if split == 'val' else 'gt_prior',
            **profile(lab, cfg['gt_gray_probe_levels'])}, hist


def pair_metrics(gt, gen, grid_size):
    cg, cm = chroma(gt), chroma(gen)
    delta = gen[..., 1:] - gt[..., 1:]
    dc = cm - cg
    mean_vector = delta.mean(axis=(0, 1))
    vectors = []
    for block_row in np.array_split(delta, grid_size, axis=0):
        for block in np.array_split(block_row, grid_size, axis=1):
            vectors.append(np.median(block.reshape(-1, 2), axis=0))
    vectors = np.asarray(vectors)
    common = np.median(vectors, axis=0)
    norm = float(np.linalg.norm(common))
    distances = np.linalg.norm(vectors - common, axis=1)
    med_g = np.median(gt[..., 1:].reshape(-1, 2), axis=0)
    med_m = np.median(gen[..., 1:].reshape(-1, 2), axis=0)
    spread_g = float(np.percentile(np.linalg.norm(gt[..., 1:] - med_g, axis=-1), 95))
    spread_m = float(np.percentile(np.linalg.norm(gen[..., 1:] - med_m, axis=-1), 95))
    ab_distance = np.linalg.norm(delta, axis=-1)
    hue_component = np.sqrt(np.maximum(0, ab_distance**2 - dc**2))
    weights = np.minimum(cg, cm)
    angle_g = np.arctan2(gt[..., 2], gt[..., 1])
    angle_m = np.arctan2(gen[..., 2], gen[..., 1])
    angle_diff = np.abs(np.arctan2(np.sin(angle_m-angle_g), np.cos(angle_m-angle_g)))
    return {
        'mean_c_gt': float(cg.mean()), 'mean_c_model': float(cm.mean()),
        'chroma_ratio': float(cm.mean() / (cg.mean() + 1e-8)),
        'centered_spread_model': spread_m, 'spread_ratio': spread_m / (spread_g + 1e-8),
        'mean_shift_norm': float(np.linalg.norm(mean_vector)),
        'robust_shift_norm': norm, 'common_da': float(common[0]), 'common_db': float(common[1]),
        'cell_distances': distances.tolist(),
        'dc_p05': float(np.percentile(dc, 5)), 'dc_p95': float(np.percentile(dc, 95)),
        'abs_dc_p95': float(np.percentile(np.abs(dc), 95)),
        'hue_component_p90': float(np.percentile(hue_component, 90)),
        'hue_component_p99': float(np.percentile(hue_component, 99)),
        'hue_component_max': float(hue_component.max()),
        'chroma_weighted_hue_degrees': float(np.sum(angle_diff * weights) / (weights.sum()+1e-8) * 180 / np.pi),
        'raw_ab_p90': float(np.percentile(ab_distance, 90)),
        'residual_ab_p90': float(np.percentile(np.linalg.norm(delta-common, axis=-1), 90))
    }


def real_record(item, cfg):
    image_id, model, part = item
    gt_rgb, gt_size = read_rgb(DATASET['val'] / 'image' / f'{image_id}.jpg', cfg['max_side'])
    gen_rgb, gen_size = read_rgb(model_path(image_id, model), cfg['max_side'])
    resized = gen_rgb.shape != gt_rgb.shape
    if resized:
        gen_rgb = cv2.resize(gen_rgb, (gt_rgb.shape[1], gt_rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
    return {'image_id': image_id, 'model': model, 'partition': part,
            'original_size_mismatch': gt_size != gen_size, 'analysis_resize': resized,
            **pair_metrics(lab_from_rgb(gt_rgb), lab_from_rgb(gen_rgb), cfg['grid_size'])}


def interventions(lab, cfg):
    yield 'identity', lab.copy(), False, False, 0.0
    rgb = rgb_from_lab(lab)
    _, encoded = cv2.imencode('.jpg', cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, cfg['jpeg_quality']])
    decoded = cv2.cvtColor(cv2.imdecode(encoded, cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
    yield 'jpeg_control', lab_from_rgb(decoded), False, False, 0.0
    gray = lab.copy(); gray[..., 1:] = 0
    yield 'grayscale', gray, True, False, 1.0
    tint = lab.copy(); tint[..., 1] = 6; tint[..., 2] = 9
    yield 'single_tint', tint, True, False, 1.0
    for strength in cfg['shift_norms']:
        for sign in [1, -1]:
            x = lab.copy(); x[..., 1:] += sign * strength * np.array([0.8, 0.6])
            yield f'global_shift_{sign*strength:g}', x, False, True, 1.0
    for frac in cfg['local_shift_area_fractions']:
        width = round(lab.shape[1] * frac)
        x = lab.copy(); x[:, :width, 1:] += cfg['local_shift_norm'] * np.array([0.8, 0.6])
        yield f'local_shift_area_{frac:g}', x, False, False, width/lab.shape[1]
    for frac in cfg['local_hue_area_fractions']:
        for deg in cfg['hue_rotation_degrees']:
            x = lab.copy(); width = max(1, round(lab.shape[1]*frac))
            theta = np.deg2rad(deg); a = lab[:, :width, 1]; b = lab[:, :width, 2]
            x[:, :width, 1] = a*np.cos(theta)-b*np.sin(theta)
            x[:, :width, 2] = a*np.sin(theta)+b*np.cos(theta)
            yield f'local_hue_{deg:g}_area_{frac:g}', x, False, False, width/lab.shape[1]
    for scale in cfg['chroma_scales']:
        x = lab.copy(); x[..., 1:] *= scale
        yield f'global_chroma_scale_{scale:g}', x, False, False, 1.0
    x = lab.copy(); width = lab.shape[1] // 2
    x[:, :width, 1:] *= 1.6; x[:, width:, 1:] *= 0.5
    yield 'mixed_chroma_gain_loss', x, False, False, 1.0
    x = lab.copy(); x[..., 1:] += np.array([6.4, 4.8]); x[:lab.shape[0]//4, :, 1:] += np.array([-18., 15.])
    yield 'global_plus_local_shift', x, False, True, 1.0


def synthetic_records(item, cfg):
    image_id, part, stratum = item
    rgb, _ = read_rgb(DATASET['val'] / 'image' / f'{image_id}.jpg', cfg['max_side'])
    lab = lab_from_rgb(rgb)
    rows = []
    for name, modified, a_target, d_target, area in interventions(lab, cfg):
        # RGB roundtrip represents the visible image, including gamut clipping/quantization.
        rendered = lab_from_rgb(rgb_from_lab(modified))
        drift = np.linalg.norm(rendered[..., 1:]-modified[..., 1:], axis=-1)
        rows.append({'image_id': image_id, 'partition': part, 'stratum': stratum,
                     'intervention': name, 'a_intervention': a_target, 'd_intervention': d_target,
                     'area_fraction': area, 'roundtrip_ab_error_p95': float(np.percentile(drift, 95)),
                     **pair_metrics(lab, rendered, cfg['grid_size'])})
    return rows


def confusion(target, prediction):
    y, p = np.asarray(target, dtype=bool), np.asarray(prediction, dtype=bool)
    tp, fp, fn, tn = (int(np.sum(m)) for m in [y&p, ~y&p, y&~p, ~y&~p])
    precision = tp/(tp+fp) if tp+fp else 0
    recall = tp/(tp+fn) if tp+fn else 0
    return {'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn, 'precision': precision, 'recall': recall,
            'f1': 2*precision*recall/(precision+recall) if precision+recall else 0,
            'false_positive_rate': fp/(fp+tn) if fp+tn else 0}


def predict_d(rows, params):
    norm = np.array([r['robust_shift_norm'] for r in rows])
    dist = np.array([r['cell_distances'] for r in rows])
    tol = params['absolute_tolerance'] + params['relative_tolerance']*norm
    cov = np.mean(dist <= tol[:, None], axis=1)
    return (norm >= params['minimum_shift']) & (cov >= params['minimum_coverage'])


def predict_a(rows, params):
    mean = np.array([r['mean_c_model'] for r in rows]); ratio = np.array([r['chroma_ratio'] for r in rows])
    spread = np.array([r['centered_spread_model'] for r in rows]); spread_ratio = np.array([r['spread_ratio'] for r in rows])
    return ((mean <= params['maximum_mean_chroma']) & (ratio <= params['maximum_chroma_ratio'])) | ((spread <= params['maximum_centered_spread']) & (spread_ratio <= params['maximum_spread_ratio']))


def predict_mean_shift(rows, params):
    return np.array([r['mean_shift_norm'] for r in rows]) >= params['minimum_shift']


def fit(rows, label, search, predictor):
    # Only calibration rows fit parameters. Same-source images stay in one partition.
    cal = [r for r in rows if r['partition']=='calibration']
    target = [r[label] for r in cal]
    trials = []
    for values in itertools.product(*search.values()):
        params = dict(zip(search, values)); result = confusion(target, predictor(cal, params))
        trials.append({'parameters': params, 'calibration': result})
    trials.sort(key=lambda x: (x['calibration']['f1'], -x['calibration']['fp']), reverse=True)
    winner = trials[0]['parameters']
    results = {}
    for part in ['calibration', 'holdout']:
        group = [r for r in rows if r['partition']==part]
        pred = predictor(group, winner)
        results[part] = confusion([r[label] for r in group], pred)
        results[part]['by_intervention'] = {name: confusion([r[label] for r in group if r['intervention']==name], pred[[r['intervention']==name for r in group]]) for name in sorted({r['intervention'] for r in group})}
    return {'parameters': winner, 'results': results, 'top_calibration_trials': trials[:10]}


def csv_write(path, rows):
    fields = list(rows[0])
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, list) else v for k,v in row.items()})


def map_parallel(function, items, cfg, title):
    out = []
    with ThreadPoolExecutor(max_workers=cfg['workers']) as pool:
        for i, result in enumerate(pool.map(lambda item: function(item, cfg), items), 1):
            out.append(result)
            if i % 500 == 0 or i==len(items):
                print(f'{title}: {i}/{len(items)}', flush=True)
    return out


def signed_heatmap(gt, gen, deadzone, maximum):
    dc = chroma(gen)-chroma(gt)
    magnitude = np.clip((np.abs(dc)-deadzone)/(maximum-deadzone), 0, 1)
    warm = np.array([255, 45, 115]); cool = np.array([35, 185, 255])
    colors = np.where((dc > 0)[..., None], warm, cool)
    return np.rint(colors*magnitude[..., None]).astype(np.uint8)


def font(size):
    return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', size)


def card(gt_rgb, gen_rgb, title, destination, cfg, display):
    if gen_rgb.shape != gt_rgb.shape:
        gen_rgb = cv2.resize(gen_rgb, (gt_rgb.shape[1],gt_rgb.shape[0]))
    heat = signed_heatmap(lab_from_rgb(gt_rgb),lab_from_rgb(gen_rgb),display['deadzone'],display['maximum'])
    panel_w, panel_h = 500, 420
    canvas = Image.new('RGB',(panel_w*3, panel_h+110),(238,240,242)); draw=ImageDraw.Draw(canvas)
    draw.text((12,8),title,fill='black',font=font(20))
    draw.text((12,40),f"正值红/品红，负值蓝/青；|ΔC*|≤{display['deadzone']:.2f}隐藏，≥{display['maximum']:.1f}封顶；黑色不代表无错色",fill='black',font=font(15))
    for i,(image,label) in enumerate(zip([gt_rgb,gen_rgb,heat],['GT','生成图','双向彩度差 ΔC*'])):
        draw.text((i*panel_w+12,70),label,fill='black',font=font(20))
        im=Image.fromarray(image); im.thumbnail((panel_w-16,panel_h))
        canvas.paste(im,(i*panel_w+(panel_w-im.width)//2,110+(panel_h-im.height)//2))
    canvas.save(destination)


def self_check(cfg):
    lab=np.zeros((32,32,3),np.float32);lab[...,0]=50;lab[...,1]=np.linspace(-20,20,32)[None,:];lab[...,2]=10
    same=pair_metrics(lab,lab,cfg['grid_size']); assert same['raw_ab_p90']==0 and same['abs_dc_p95']==0
    changed=lab.copy();changed[...,1:]+=np.array([6,8])
    metrics=pair_metrics(lab,changed,cfg['grid_size']);assert abs(metrics['robust_shift_norm']-10)<1e-5 and metrics['residual_ab_p90']<1e-5
    changed=lab.copy();changed[...,1]=-lab[...,2];changed[...,2]=lab[...,1]
    metrics=pair_metrics(lab,changed,cfg['grid_size']);assert metrics['abs_dc_p95']<1e-5 and metrics['hue_component_p90']>10
    heat=signed_heatmap(lab,lab,1,20);assert np.count_nonzero(heat)==0
    print('Analytical checks: identity, known global vector, iso-chroma hue rotation, neutral heatmap PASS',flush=True)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,default=Path(__file__).with_name('config_v1.json'));ap.add_argument('--reuse-gt',action='store_true');args=ap.parse_args()
    cfg=json.loads(args.config.read_text(encoding='utf-8'));cv2.setNumThreads(1);self_check(cfg);start=time.time()
    out=BASE/'intermediate'/'audits'/cfg['experiment_id']; sheets=BASE/'intermediate'/'inspection_sheets'/cfg['experiment_id']
    out.mkdir(parents=True,exist_ok=True);sheets.mkdir(parents=True,exist_ok=True)
    source_files=[args.config,Path(__file__),*[p/'labels'/'annotations.json' for p in DATASET.values()],BASE/'exports'/'reviewed_1_10000_clean.json']
    previous=json.loads((out/'manifest.json').read_text(encoding='utf-8')) if args.reuse_gt else None
    if previous:
        assert all(previous['config'][k]==cfg[k] for k in ['max_side','gt_gray_probe_levels','seed','calibration_fraction'])
    manifest={'started_at':datetime.now(timezone.utc).isoformat(),'config':cfg,'opencv':cv2.__version__,'numpy':np.__version__,'reused_gt_profiles':args.reuse_gt,
              'test_split_used':False,'source_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
              'analysis_note':'max-side resize statistics; source GT ID hash defines validation calibration/holdout; synthetic rectangular regions are not object masks'}
    save_json(out/'manifest.json',manifest)
    items=[(split,p) for split,d in DATASET.items() for p in sorted((d/'image').glob('*.jpg'))]
    if args.reuse_gt:
        with (out/'gt_profiles.csv').open(encoding='utf-8-sig',newline='') as f:
            gt=[{k:(v if k in ['split','image_id','partition'] else int(v) if k in ['width','height'] else float(v)) for k,v in row.items()} for row in csv.DictReader(f)]
        assert len(gt)==len(items)
        print(f'Reused {len(gt)} complete GT profiles',flush=True)
    else:
        results=map_parallel(gt_record,items,cfg,'GT profiles');gt=[r[0] for r in results]
        csv_write(out/'gt_profiles.csv',gt)
        numeric=[k for k in gt[0] if k not in ['split','image_id','width','height','partition']]
        gt_summary={s:{k:quantiles([r[k] for r in gt if r['split']==s]) for k in numeric} for s in DATASET}
        hist={s:np.sum([h for (r,h) in results if r['split']==s],axis=0).tolist() for s in DATASET}
        save_json(out/'gt_statistics.json',{'per_image':gt_summary,'pixel_chroma_histogram':{'bin_edges':list(range(0,182,2)),'counts':hist}})
    indexed={(r['split'],r['image_id']):r for r in gt}
    legacy={};labels={}
    for split,d in DATASET.items():
        annotations=json.loads((d/'labels'/'annotations.json').read_text(encoding='utf-8'))['annotations']
        labels.update({(split,a['role'],Path(a['image_id']).stem):a for a in annotations})
        for model in ['lcad','unicolor']:
            group=[a for a in annotations if a['role']==model]; counts={}
            for code in ['A','B','C','D','E1','E2','F','NONE']:
                members=[a for a in group if (not a['defects'] if code=='NONE' else any(x['id']==code for x in a['defects']))]
                priors=[indexed[(split,Path(a['image_id']).stem)]['mean_c'] for a in members]
                counts[code]={'images':len(members),'gt_mean_c':quantiles(priors) if priors else None,
                              'severity_counts':{sev:sum(any(x['id']==code and x['severity']==sev for x in a['defects']) for a in members) for sev in ['','L1','L2','L3']}}
            legacy[f'{split}/{model}']=counts
    save_json(out/'legacy_label_statistics.json',{'warning':'Historical model labels only; not verified defect ground truth and not used to fit CV thresholds','groups':legacy})
    val=[r for r in gt if r['split']=='val']
    real=map_parallel(real_record,[(r['image_id'],m,r['partition']) for r in val for m in ['lcad','unicolor']],cfg,'Validation pairs')
    csv_write(out/'validation_pair_metrics.csv',real)
    groups={}
    for model in ['lcad','unicolor']:
        for code in ['A','B','C','D','E1','E2','F','NONE']:
            members=[r for r in real if r['model']==model and (not labels[('val',model,r['image_id'])]['defects'] if code=='NONE' else any(d['id']==code for d in labels[('val',model,r['image_id'])]['defects']))]
            groups[f'{model}/{code}']={'n':len(members),'metrics':{k:quantiles([r[k] for r in members]) for k in ['mean_c_model','chroma_ratio','mean_shift_norm','robust_shift_norm','abs_dc_p95','hue_component_p90']} if members else {}}
    save_json(out/'legacy_label_metric_associations.json',{'warning':'Exploration, not accuracy evaluation','groups':groups})
    cuts=np.percentile([r['mean_c'] for r in gt if r['split']=='train'],[33.333,66.667])
    samples=[]
    for part in ['calibration','holdout']:
        for stratum in range(3):
            pool=[r for r in val if r['partition']==part and int(np.searchsorted(cuts,r['mean_c']))==stratum]
            pool.sort(key=lambda r:hashlib.sha256(f'{cfg["seed"]}:sample:{r["image_id"]}'.encode()).hexdigest())
            samples.extend((r['image_id'],part,stratum) for r in pool[:cfg['synthetic_per_stratum_partition']])
    assert not ({x[0] for x in samples if x[1]=='calibration'} & {x[0] for x in samples if x[1]=='holdout'})
    save_json(out/'synthetic_sample_manifest.json',{'gt_chroma_stratum_boundaries':cuts.tolist(),'samples':samples})
    synthetic=[r for batch in map_parallel(synthetic_records,samples,cfg,'Synthetic source images') for r in batch]
    csv_write(out/'synthetic_metrics.csv',synthetic)
    a=fit(synthetic,'a_intervention',cfg['a_search'],predict_a)
    # Exclude global color-rendering collapse from D eval: A is a separate terminal route.
    d_rows=[r for r in synthetic if not r['a_intervention']]
    d=fit(d_rows,'d_intervention',cfg['d_search'],predict_d)
    d['tuned_mean_baseline']=fit(d_rows,'d_intervention',{'minimum_shift':cfg['d_search']['minimum_shift']+[18.0,24.0]},predict_mean_shift)
    for part in ['calibration','holdout']:
        rows=[r for r in d_rows if r['partition']==part]
        d['results'][part]['old_mean_threshold_10']=confusion([r['d_intervention'] for r in rows],[r['mean_shift_norm']>=10 for r in rows])
        d['results'][part]['old_mean_threshold_18']=confusion([r['d_intervention'] for r in rows],[r['mean_shift_norm']>=18 for r in rows])
    real_cal=[r for r in real if r['partition']=='calibration']
    noise=[r['abs_dc_p95'] for r in synthetic if r['partition']=='calibration' and r['intervention']=='jpeg_control']
    # Display scale is a visualization parameter, not an E1/E2 defect threshold.
    display_candidates={str(q):float(np.percentile([r['abs_dc_p95'] for r in real_cal],q)) for q in cfg['heatmap_display_quantile_candidates']}
    display={'deadzone':float(np.percentile(noise,95)), 'maximum':display_candidates[str(cfg['selected_display_quantile'])],
             'candidate_maxima':display_candidates,'meaning':'display only; deadzone estimated from synthetic JPEG controls at analysis resolution'}
    save_json(out/'candidate_parameters.json',{'production_ready':False,'A':a,'D':d,'display':display})
    disagreements=[]
    d_pred=predict_d(real,d['parameters']);a_pred=predict_a(real,a['parameters'])
    for row,pd,pa in zip(real,d_pred,a_pred):
        row['candidate_d']=bool(pd);row['candidate_a']=bool(pa)
        if (row['mean_shift_norm']>=10)!=bool(pd):disagreements.append(row)
    save_json(out/'real_candidate_flags.json',{'warning':'CV experimental flags only; no labels modified','candidate_a':int(a_pred.sum()),'candidate_d':int(d_pred.sum()),'d_disagreement_with_old_10':len(disagreements),'records':real})
    # Twelve real examples, diverse mechanisms. No legacy labels are shown to the viewer.
    selected=[];seen=set()
    for key,reverse in [('dc_p95',True),('dc_p05',False),('hue_component_p90',True),('robust_shift_norm',True)]:
        candidates=sorted(real,key=lambda r:r[key],reverse=reverse)
        for row in candidates:
            marker=(row['model'],row['image_id'])
            if marker not in seen:
                seen.add(marker);selected.append(row)
                if sum(r.get('selection_key')==key for r in selected)>=3:break
                row['selection_key']=key
                if sum(r.get('selection_key')==key for r in selected)>=3:break
    preview=[]
    for i,row in enumerate(selected,1):
        gt_rgb,_=read_rgb(DATASET['val']/'image'/f'{row["image_id"]}.jpg',cfg['preview_max_side'])
        gen_rgb,_=read_rgb(model_path(row['image_id'],row['model']),cfg['preview_max_side'])
        name=f'real_{i:02d}_{row["model"]}_{row["image_id"]}.png'
        card(gt_rgb,gen_rgb,f'{row["model"]} / {row["image_id"]}',sheets/name,cfg,display)
        preview.append({'path':str((sheets/name).relative_to(ROOT)),**row})
    # Reference counterexample: same ideal chroma, different hue; show RGB gamut effects.
    image_id=samples[len(samples)//2][0];gt_rgb,_=read_rgb(DATASET['val']/'image'/f'{image_id}.jpg',cfg['preview_max_side']);gt_lab=lab_from_rgb(gt_rgb)
    for name,x,_,_,_ in interventions(gt_lab,cfg):
        if name in ['identity','local_hue_90_area_0.5','global_shift_16','local_shift_area_0.75','mixed_chroma_gain_loss','grayscale']:
            dest=sheets/f'synthetic_{name}.png';card(gt_rgb,rgb_from_lab(x),name,dest,cfg,display)
    save_json(out/'preview_manifest.json',preview)
    # Resolution sensitivity of the same measurements: candidate parameters were fitted at 256.
    sensitivity=[]
    for row in sorted(real,key=lambda r:r['abs_dc_p95'],reverse=True)[:12]:
        rgb_g,_=read_rgb(DATASET['val']/'image'/f'{row["image_id"]}.jpg',4096)
        rgb_m,_=read_rgb(model_path(row['image_id'],row['model']),4096)
        if rgb_m.shape!=rgb_g.shape:rgb_m=cv2.resize(rgb_m,(rgb_g.shape[1],rgb_g.shape[0]))
        native=pair_metrics(lab_from_rgb(rgb_g),lab_from_rgb(rgb_m),cfg['grid_size'])
        sensitivity.append({'image_id':row['image_id'],'model':row['model'],'analysis_abs_dc_p95':row['abs_dc_p95'],'native_abs_dc_p95':native['abs_dc_p95'],'analysis_robust_shift':row['robust_shift_norm'],'native_robust_shift':native['robust_shift_norm']})
    save_json(out/'resolution_sensitivity.json',sensitivity)
    metrics={'gt_images':len(gt),'real_pairs':len(real),'synthetic_source_images':len(samples),'synthetic_cases':len(synthetic),'elapsed_seconds':round(time.time()-start,2),
             'val_partitions':{p:sum(r['partition']==p for r in val) for p in ['calibration','holdout']},'display':display,
             'A_holdout':a['results']['holdout'],'D_holdout':d['results']['holdout']}
    save_json(out/'run_summary.json',metrics)
    manifest['completed_at']=datetime.now(timezone.utc).isoformat();manifest['result_counts']=metrics;save_json(out/'manifest.json',manifest)
    print(json.dumps({k:v for k,v in metrics.items() if k not in ['A_holdout','D_holdout']},ensure_ascii=False,indent=2),flush=True)
    print('OUTPUT',out,flush=True)


if __name__=='__main__':main()
