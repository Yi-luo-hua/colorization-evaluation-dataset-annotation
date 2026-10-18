"""Freeze D group parameters, then confirm once on new GT-source interventions."""
import csv
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2
import engine
import optimize
import d_color_groups as grouping
from experiment_d_groups import ROOT, stress_changes
from workflow import read_json, write_json, utc


def main():
    cv2.setNumThreads(1); started = time.perf_counter()
    experiment = ROOT / 'cv_d_color_groups_20261012'
    winner = read_json(experiment / 'results.json')['winner']
    settings = read_json(Path(__file__).with_name('d_group_config.json'))
    config = read_json(ROOT / 'real_boundary_full_fast_20261012/manifest.json')['configuration']
    seen = set()
    for path in ROOT.glob('*/manifest.json'):
        data = read_json(path)
        for s in data.get('samples', []): seen.add(s if isinstance(s, str) else s[0])
        for r in data.get('records', []): seen.add(r.get('source_sample_key', r['sample_key']).split('/')[-1])
    old = engine.ROOT / 'LS_lcad_reviewer/intermediate/audits/cv_workflow_experiment_20261012_01'
    seen.update(s[0] for s in read_json(old / 'v2_manifest.json')['samples'])
    cuts = read_json(old / 'synthetic_sample_manifest.json')['gt_chroma_stratum_boundaries']
    with (old / 'gt_profiles.csv').open(encoding='utf-8-sig') as f: profiles = list(csv.DictReader(f))
    import numpy as np
    samples = []
    for stratum in range(3):
        pool = [r for r in profiles if r['split'] == 'val' and r['image_id'] not in seen and
                int(np.searchsorted(cuts, float(r['mean_c']))) == stratum]
        pool.sort(key=lambda r: hashlib.sha256(f'{settings["seed"]}:Dgroups-confirm:{r["image_id"]}'.encode()).hexdigest())
        samples.extend((r['image_id'], stratum) for r in pool[:8])
    out = ROOT / 'cv_d_groups_confirm_20261012'; out.mkdir()
    write_json(out / 'manifest.json', {'created_at': utc(), 'samples': samples, 'configuration': config,
               'frozen_parameters': winner, 'group_settings': settings, 'previous_GT_excluded': len(seen),
               'selection_uses_labels': False, 'test_split_used': False,
               'source_sha256': {p.name: engine.sha256(p) for p in [Path(__file__), Path(grouping.__file__), Path(__file__).with_name('experiment_d_groups.py'), Path(__file__).with_name('config.json')]}})
    optimize.OPT = read_json(ROOT / 'cv_models_v4_20261012/manifest.json')['optimization_configuration']
    eval_cfg = read_json(ROOT / 'cv_geometry_v3_20261012/manifest.json')['evaluation_configuration']
    def trial(item):
        image_id, stratum = item
        gt = engine.lab(engine.read_rgb(engine.ROOT / config['datasets']['val'] / 'image' / f'{image_id}.jpg', config['analysis_max_side']))
        groups = grouping.prepare_groups(gt, settings['features']); rows = []
        for name, x, a, d, area in stress_changes(gt, eval_cfg):
            gen = engine.lab(engine.rgb(x)); m, f, _ = engine.measure(gt, gen, config)
            r = {'image_id': image_id, 'stratum': stratum, 'intervention': name, 'a_target': a, 'd_target': d,
                 'baseline_d': f['d_candidate'], 'a_prediction': f['a_candidate'], 'scale_explains_shift': f['scale_explains_shift'],
                 'metrics': m, 'group_features': grouping.measure(gt, gen, groups, settings)}
            r['group_prediction'] = grouping.predict(r, winner, config); rows.append(r)
        return rows
    rows = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for i, batch in enumerate(pool.map(trial, samples), 1):
            rows.extend(batch)
            if i % 8 == 0: print(f'New GT confirmation: {i}/24', flush=True)
    write_json(out / 'records.json', rows)
    drows = [r for r in rows if not r['a_target']]
    result = {'GT_sources': len(samples), 'cases': len(rows), 'D_cases': len(drows), 'frozen_parameters': winner,
              'v4': optimize.confusion(drows, [r['baseline_d'] for r in drows], 'd_target'),
              'groups': optimize.confusion(drows, [r['group_prediction'] for r in drows], 'd_target'),
              'cascade_v4': optimize.confusion(rows, [r['baseline_d'] and not r['a_prediction'] for r in rows], 'd_target'),
              'cascade_groups': optimize.confusion(rows, [r['group_prediction'] and not r['a_prediction'] for r in rows], 'd_target'),
              'by_intervention': {n: {'v4': optimize.confusion([r for r in drows if r['intervention'] == n], [r['baseline_d'] for r in drows if r['intervention'] == n], 'd_target'),
                  'groups': optimize.confusion([r for r in drows if r['intervention'] == n], [r['group_prediction'] for r in drows if r['intervention'] == n], 'd_target')}
                  for n in sorted({r['intervention'] for r in drows})}, 'wall_seconds': time.perf_counter() - started}
    write_json(out / 'results.json', result)
    print({k: v for k, v in result.items() if k != 'by_intervention'}, flush=True)


if __name__ == '__main__': main()
