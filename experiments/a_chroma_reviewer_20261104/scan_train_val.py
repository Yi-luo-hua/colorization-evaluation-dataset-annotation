"""Measure chroma on every generated train/val image, independent of label state."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

from prepare_candidates import LOCAL, ROOT, write
from review_no_gt import chroma_regions

METRICS = ('mean_C', 'largest_C3_pct', 'largest_C5_pct', 'largest_C8_pct')
TIERS = {'high_suspicion': (1.5, 5, 0.25, 0.05), 'borderline': (3, 20, 1, 0.25)}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def inventory():
    delivery = read(ROOT / 'annotation_delivery/train_val_v1_20261015/config.json')
    config = read(ROOT / delivery['source_config'])
    exclusions = read(ROOT / config['gt_filter']['exclude_manifest'])
    blocked = {(row['split'], Path(row['image_id']).stem) for row in exclusions['excluded_GT']}
    records = []
    for split in ('train', 'val'):
        for model in delivery['scope']['models']:
            directory = ROOT / config['datasets'][split] / 'model' / model
            paths = sorted(path for path in directory.iterdir()
                           if path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg'})
            pool, = (ROOT / 'LS_lcad_reviewer/tasks_pool' / split).glob(f'*{model}*.json')
            expected = {Path(t['data']['original_record']['image_id']).stem for t in read(pool)}
            stems = {path.stem for path in paths}
            if stems != expected or len(stems) != len(paths):
                raise ValueError(f'Generated files do not match the unique task pool IDs for {split}/{model}')
            records.extend({'sample_key': f'{split}/{model}/{path.stem}', 'split': split, 'model': model,
                            'generated_path': path.relative_to(ROOT).as_posix(),
                            'frozen_gt_excluded': (split, path.stem) in blocked} for path in paths)
    return records


def measure(record):
    with Image.open(ROOT / record['generated_path']) as source:
        image = ImageOps.exif_transpose(source).convert('RGB')
    rgb = np.asarray(image)
    lab = cv2.cvtColor(rgb.astype(np.float32) / 255, cv2.COLOR_RGB2LAB)
    ab = lab[:, :, 1:]
    chroma = np.linalg.norm(ab, axis=2)
    midtones = (lab[:, :, 0] >= 12) & (lab[:, :, 0] <= 92)
    color = ab[midtones] if midtones.any() else ab.reshape(-1, 2)
    average = color.mean(axis=0, dtype=np.float64)
    areas = {row['C_min']: row['area_pct'] for row in chroma_regions(chroma)}
    return {**record, 'exact_rgb_gray': bool((rgb[:, :, 0] == rgb[:, :, 1]).all()
                                             and (rgb[:, :, 1] == rgb[:, :, 2]).all()),
            'mean_C': round(float(chroma.mean(dtype=np.float64)), 5),
            'var_ab': round(float(np.var(ab, axis=(0, 1), dtype=np.float64).sum()), 5),
            'midtone_a': round(float(average[0]), 5), 'midtone_b': round(float(average[1]), 5),
            'midtone_tint_C': round(float(np.linalg.norm(average)), 5),
            **{f'largest_C{threshold}_pct': areas.get(threshold, 0.0) for threshold in (3, 5, 8)}}


def scan(records, output):
    cv2.setNumThreads(1)
    print(f'Found {len(records)} unique generated train/val files', flush=True)
    target = output / 'all_metrics.csv'
    temporary = target.with_suffix('.tmp')
    with temporary.open('w', newline='', encoding='utf-8-sig') as stream, ThreadPoolExecutor(max_workers=8) as pool:
        writer = None
        for index, row in enumerate(pool.map(measure, records), 1):
            if writer is None:
                writer = csv.DictWriter(stream, fieldnames=list(row))
                writer.writeheader()
            writer.writerow(row)
            if index % 2000 == 0:
                stream.flush()
                print(f'Measured {index}/{len(records)}', flush=True)
    temporary.replace(target)
    write(output / 'coverage.json', {'total': len(records), 'scope': dict(Counter(
        f'{row["split"]}/{row["model"]}' for row in records)),
        'frozen_gt_excluded_included': sum(row['frozen_gt_excluded'] for row in records)})


def export_candidates(output):
    coverage = read(output / 'coverage.json')
    with (output / 'all_metrics.csv').open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    if len({row['sample_key'] for row in rows}) != len(rows) or len(rows) != coverage['total']:
        raise ValueError('Metrics file has incomplete or duplicate coverage')

    candidates = []
    for row in rows:
        mean, area3, area5, area8 = (float(row[field]) for field in METRICS)
        for tier, (max_mean, max_area3, max_area5, max_area8) in TIERS.items():
            if mean <= max_mean and area3 < max_area3 and area5 < max_area5 and area8 < max_area8:
                candidates.append({'tier': tier, **row})
                break
    candidates.sort(key=lambda row: (row['tier'] == 'borderline', float(row['mean_C']), row['sample_key']))
    with (output / 'candidates.csv').open('w', newline='', encoding='utf-8-sig') as stream:
        writer = csv.DictWriter(stream, fieldnames=['tier', *rows[0]])
        writer.writeheader()
        writer.writerows(candidates)

    groups = {group: {tier: 0 for tier in TIERS} for group in coverage['scope']}
    for row in candidates:
        groups[f'{row["split"]}/{row["model"]}'][row['tier']] += 1
    summary = {**coverage, 'candidate_count': len(candidates), 'groups': groups,
               'tiers': {tier: sum(row['tier'] == tier for row in candidates) for tier in TIERS},
               'rules': {tier: dict(zip(METRICS, limits)) for tier, limits in TIERS.items()},
               'rule_operators': dict(zip(METRICS, ('<=', '<', '<', '<'))),
               'frozen_gt_excluded_among_candidates': sum(row['frozen_gt_excluded'] == 'True' for row in candidates),
               'exact_rgb_gray_count': sum(row['exact_rgb_gray'] == 'True' for row in rows),
               'method': 'Generated pixels only. OpenCV CIELAB C*=sqrt(a*^2+b*^2); largest 8-connected area as % of image.',
               'result_type': 'Screening candidates for visual review'}
    write(output / 'summary.json', summary)
    print(json.dumps(summary['tiers']), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=LOCAL / 'train_val_A_scan')
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not args.report_only:
        scan(inventory(), output)
    export_candidates(output)


if __name__ == '__main__':
    main()
