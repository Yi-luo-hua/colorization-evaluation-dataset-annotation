"""Fit on 9 real GT weak references + synthetic development; freeze before holdout."""
import itertools
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2
import numpy as np
import engine
import optimize
import global_models as gm
import d_color_groups as grouping
from workflow import read_json, write_json, utc

ROOT = engine.ROOT / 'LS_lcad_reviewer/intermediate/experiments'


def stress_changes(gt, eval_cfg):
    yield from optimize.alterations(gt, eval_cfg)
    for a, b in [(20, -15), (1, 1)]:
        x = gt.copy(); x[..., 1] = a; x[..., 2] = b
        yield f'tint_{a}_{b}', x, True, False, 1
    x = gt.copy(); x[..., 1:] *= 0.1
    yield 'severe_desaturation_0.1', x, False, False, 1
    base = engine.rgb(gt).astype(np.float32) / 255
    for domain in ['encoded', 'linear']:
        for i, gains in enumerate([[1.15, 1, .85], [.85, 1, 1.15]]):
            transformed = np.clip((base if domain == 'encoded' else gm.to_linear(base)) * np.array(gains), 0, 1)
            if domain == 'linear': transformed = gm.to_srgb(transformed)
            full = engine.lab(np.rint(transformed * 255).astype(np.uint8))
            box = optimize.strong_bbox(np.linalg.norm(full[..., 1:] - gt[..., 1:], axis=-1), .1)
            x1, y1, x2, y2 = box; full[y1:y2, x1:x2] = gt[y1:y2, x1:x2]
            yield f'partial_{domain}_gain90_{i}', full, False, False, .9


def main():
    started = time.perf_counter(); cv2.setNumThreads(1)
    config = read_json(ROOT / 'real_boundary_full_fast_20261012/manifest.json')['configuration']
    settings = read_json(Path(__file__).with_name('d_group_config.json'))
    out = ROOT / 'cv_d_color_groups_20261012'
    out.mkdir()  # Preserve every earlier run.
    full = read_json(ROOT / 'real_boundary_full_fast_20261012/manifest.json')
    reviews = {r['sample_key']: r for r in read_json(ROOT / 'real_boundary_full_fast_20261012/reviews_gemini.json')['reviews']}
    ids = sorted({r['source_sample_key'].split('/')[-1] for r in full['records']},
                 key=lambda i: hashlib.sha256(f'{settings["seed"]}:Dgroups:{i}'.encode()).hexdigest())
    development_ids = set(ids[:settings['real_development_GT_count']])
    real = []
    for r in full['records']:
        gt_rgb = engine.read_rgb(engine.ROOT / r['gt_path'], config['analysis_max_side'])
        gen_rgb = engine.read_rgb(engine.ROOT / r['model_path'], config['analysis_max_side'])
        if gt_rgb.shape != gen_rgb.shape:
            gen_rgb = cv2.resize(gen_rgb, (gt_rgb.shape[1], gt_rgb.shape[0]), interpolation=cv2.INTER_AREA)
        gt, gen = engine.lab(gt_rgb), engine.lab(gen_rgb)
        metrics, flags, _ = engine.measure(gt, gen, config)
        image_id = r['source_sample_key'].split('/')[-1]
        real.append({'sample_key': r['sample_key'], 'image_id': image_id,
                     'partition': 'development' if image_id in development_ids else 'holdout',
                     'd_target': any(d['id'] == 'D' for d in reviews[r['sample_key']]['defects']),
                     'a_target': any(d['id'] == 'A' for d in reviews[r['sample_key']]['defects']),
                     'baseline_d': flags['d_candidate'], 'scale_explains_shift': flags['scale_explains_shift'],
                     'metrics': metrics, 'group_features': grouping.measure(gt, gen, grouping.prepare_groups(gt, settings['features']), settings)})
    write_json(out / 'real_records.json', real)
    print('Real features: 36 samples, split by 18 GT IDs', flush=True)
    calibration_manifest = read_json(ROOT / 'cv_models_v4_20261012/manifest.json')
    optimize.OPT = calibration_manifest['optimization_configuration']
    eval_cfg = read_json(ROOT / 'cv_geometry_v3_20261012/manifest.json')['evaluation_configuration']
    development = [(i, 'development') for i, p, _ in calibration_manifest['samples'] if p == 'development']
    holdout = [(i, 'regression') for i in read_json(ROOT / 'cv_models_stress_20261012/manifest.json')['samples']]
    old_rows = read_json(ROOT / 'cv_models_v4_20261012/records.json') + read_json(ROOT / 'cv_models_stress_20261012/records.json')
    previous = {(r['image_id'], r['intervention']): r for r in old_rows}
    def trial(item):
        image_id, part = item
        gt = engine.lab(engine.read_rgb(engine.ROOT / config['datasets']['val'] / 'image' / f'{image_id}.jpg', config['analysis_max_side']))
        groups = grouping.prepare_groups(gt, settings['features']); rows = []
        for name, x, a, d, area in stress_changes(gt, eval_cfg):
            gen = engine.lab(engine.rgb(x))
            old = previous.get((image_id, name))
            if old:
                metrics = dict(old['metrics']); metrics['global_models'] = old['models']
                row = {'metrics': metrics, 'models': old['models'], 'baseline_d': old['baseline_d']}
                v4 = gm.predict_d(row, config['global_models']['d'])
                scale = (metrics['scalar_gain'] > 0 and metrics['scalar_intercept_norm'] < config['d']['minimum_shift'] and
                         metrics['scalar_fit_median_error'] < config['d']['scale_explanation_ratio'] * metrics['translation_fit_median_error'])
            else:
                metrics, flags, _ = engine.measure(gt, gen, config)
                v4 = flags['d_candidate']; scale = flags['scale_explains_shift']
            rows.append({'image_id': image_id, 'partition': part, 'intervention': name, 'a_target': a, 'd_target': d,
                         'baseline_d': v4, 'scale_explains_shift': scale, 'metrics': metrics,
                         'group_features': grouping.measure(gt, gen, groups, settings)})
        return rows
    synthetic = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, rows in enumerate(pool.map(trial, development + holdout), 1):
            synthetic.extend(rows)
            if i % 12 == 0: print(f'Synthetic GT sources: {i}/72', flush=True)
    write_json(out / 'synthetic_records.json', synthetic)
    synth_dev = [r for r in synthetic if r['partition'] == 'development' and not r['a_target']]
    real_dev = [r for r in real if r['partition'] == 'development' and not r['a_target']]
    base_dev = optimize.confusion(synth_dev, [r['baseline_d'] for r in synth_dev], 'd_target')
    candidates = []
    for values in itertools.product(*settings['search'].values()):
        params = dict(zip(settings['search'], values))
        synth_score = optimize.confusion(synth_dev, [grouping.predict(r, params, config) for r in synth_dev], 'd_target')
        if synth_score['f1'] < base_dev['f1'] - settings['maximum_synthetic_development_f1_loss']: continue
        real_score = optimize.confusion(real_dev, [grouping.predict(r, params, config) for r in real_dev], 'd_target')
        candidates.append({'parameters': params, 'synthetic_development': synth_score, 'real_weak_development': real_score})
    candidates.sort(key=lambda c: (c['real_weak_development']['f1'], -c['real_weak_development']['fp'], c['synthetic_development']['f1']), reverse=True)
    winner = candidates[0]['parameters'] if candidates else None
    result = {'created_at': utc(), 'real_reference': 'Gemini High weak observations, not human ground truth',
              'real_split_by_GT': {p: [i for i in ids if (i in development_ids) == (p == 'development')] for p in ['development', 'holdout']},
              'synthetic_regression_is_previously_used_GT': True, 'winner': winner, 'eligible_parameter_sets': len(candidates),
              'top_development_trials': candidates[:10], 'source_sha256': {p.name: engine.sha256(p) for p in [Path(__file__), Path(grouping.__file__), Path(__file__).with_name('d_group_config.json'), Path(__file__).with_name('config.json')]}}
    for name, rows in [('real_weak_development', real_dev), ('real_weak_holdout', [r for r in real if r['partition'] == 'holdout' and not r['a_target']]),
                       ('real_weak_all', [r for r in real if not r['a_target']]), ('synthetic_development', synth_dev),
                       ('synthetic_regression', [r for r in synthetic if r['partition'] == 'regression' and not r['a_target']])]:
        result[name] = {'cases': len(rows), 'v4': optimize.confusion(rows, [r['baseline_d'] for r in rows], 'd_target')}
        if winner: result[name]['groups'] = optimize.confusion(rows, [grouping.predict(r, winner, config) for r in rows], 'd_target')
    if winner:
        for r in real: r['group_prediction'] = grouping.predict(r, winner, config)
        write_json(out / 'real_records.json', real)
        frozen = [r for r in synthetic if r['partition'] == 'regression' and not r['a_target']]
        result['regression_by_intervention'] = {n: {'v4': optimize.confusion([r for r in frozen if r['intervention'] == n], [r['baseline_d'] for r in frozen if r['intervention'] == n], 'd_target'),
                  'groups': optimize.confusion([r for r in frozen if r['intervention'] == n], [grouping.predict(r, winner, config) for r in frozen if r['intervention'] == n], 'd_target')}
                  for n in sorted({r['intervention'] for r in frozen})}
    result['wall_seconds'] = time.perf_counter() - started
    write_json(out / 'results.json', result)
    print({k: v for k, v in result.items() if k in ['winner', 'eligible_parameter_sets', 'real_weak_development', 'real_weak_holdout', 'real_weak_all', 'synthetic_development', 'synthetic_regression', 'wall_seconds']}, flush=True)


if __name__ == '__main__': main()
