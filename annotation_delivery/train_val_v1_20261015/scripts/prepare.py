"""Offline inventory and two-stage queue. This module never invokes a model."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
FOUR = ['B', 'C', 'D', 'F']
SIX = ['B', 'C', 'D', 'E1', 'E2', 'F']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return Path(path).absolute().relative_to(ROOT).as_posix()


def write(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    os.replace(temporary, path)


def write_lines(path, values):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False) + '\n')
    os.replace(temporary, path)


def lines(path):
    with Path(path).open(encoding='utf-8') as stream:
        return [json.loads(line) for line in stream if line.strip()]


def description_flags(defects):
    """Literal format candidates only; these counts do not decide semantic correctness."""
    descriptions = [d.get('description', '') for d in defects]
    reference = re.compile(r'\bGT\b|ground\s*truth|真值|参考图|原图', re.IGNORECASE)
    heading = re.compile(r'^(?:[^\n:：]{1,32}[（(]\s*(?:[A-F]\d?[- ]?)?L[123]\s*[）)]\s*[:：]|(?:[A-F]\d?[- ]?)?L[123]\s*[:：]|[【\[].{1,20}[】\]]\s*[:：]?)')
    return {'explicit_reference_descriptions': sum(bool(reference.search(d)) for d in descriptions),
            'severity_heading_descriptions': sum(bool(heading.search(d)) for d in descriptions),
            'missing_descriptions': sum(not d.strip() for d in descriptions),
            'obsolete_A_labels': sum(d.get('id') == 'A' for d in defects)}


def inventory(destination):
    if destination.exists():
        raise ValueError('Preserve existing inventory; use a new --output directory')
    destination.mkdir(parents=True)
    cfg = read(PROJECT / 'config.json')
    cv = read(ROOT / cfg['source_config'])
    registry = {}

    def register(path):
        path = Path(path)
        name = rel(path)
        if name not in registry:
            registry[name] = {'sha256': sha(path), 'bytes': path.stat().st_size}
        return {'path': name, 'sha256': registry[name]['sha256']}

    register(PROJECT / 'config.json')
    register(ROOT / cfg['source_config'])
    for name in [cv['gt_filter']['exclude_manifest'], cv['a']['confirmed_manifest']]:
        register(ROOT / name)
    for block in ['display', 'color_evidence']:
        if cv[block].get('reference_manifest'):
            register(ROOT / cv[block]['reference_manifest'])
    excluded = read(ROOT / cv['gt_filter']['exclude_manifest'])
    if excluded.get('unresolved'):
        raise ValueError('Frozen upstream filter unexpectedly contains unresolved GT')
    blocked = {(x['split'], Path(x['image_id']).stem) for x in excluded['excluded_GT']}
    fixed_manifest = read(ROOT / cv['a']['confirmed_manifest'])
    fixed = {x['source_sample_key']: x for x in fixed_manifest['records'] if x['GT_eligible']}

    if cfg['sources']['experiment_annotations_eligible'] is not False:
        raise ValueError('Experiment annotations are retired, not delivery baselines')
    legacy_file = ROOT / cfg['sources']['legacy_reviewed']
    legacy_ref = register(legacy_file)
    legacy = {}
    for row in read(legacy_file)['annotations']:
        identity = 'train/lcad/' + Path(row['image_id']).stem
        if identity in legacy:
            raise ValueError(f'Duplicate legacy identity: {identity}')
        legacy[identity] = row

    records, skipped, fixed_rows = [], [], []
    groups = defaultdict(Counter)
    legacy_audit = []
    image_hashes = {}

    def image_sha(path):
        name = rel(path)
        if name not in image_hashes:
            image_hashes[name] = sha(path)
        return image_hashes[name]

    for split in cfg['scope']['splits']:
        dataset = ROOT / cv['datasets'][split]
        for model in cfg['scope']['models']:
            pools = list((ROOT / 'LS_lcad_reviewer/tasks_pool' / split).glob(f'*{model}*.json'))
            if len(pools) != 1:
                raise ValueError(f'Expected one task pool for {split}/{model}')
            pool_ref = register(pools[0])
            tasks = read(pools[0])
            generated_files = {}
            for file in (dataset / 'model' / model).iterdir():
                if file.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    if file.stem in generated_files:
                        raise ValueError(f'Duplicate generated image: {file.stem}')
                    generated_files[file.stem] = file
            for index, task in enumerate(tasks, 1):
                original = task['data']['original_record']
                stem = Path(original['image_id']).stem
                identity = f'{split}/{model}/{stem}'
                if (split, stem) in blocked:
                    skipped.append({'source_sample_key': identity, 'task_idx': index, 'reason': 'frozen_GT_excluded'})
                    continue
                gt = dataset / 'image' / f'{stem}.jpg'
                generated = generated_files[stem]
                gt_hash, model_hash = image_sha(gt), image_sha(generated)
                record = {'source_sample_key': identity, 'split': split, 'model': model, 'task_idx': index,
                          'image_id': original['image_id'], 'gt_path': rel(gt), 'model_path': rel(generated),
                          'gt_sha256': gt_hash, 'model_sha256': model_hash,
                          'source_task': {**pool_ref, 'task_idx': index, 'original_record_preserved_in_source': True},
                          'raw_preannotation_present': isinstance(original.get('defects'), list),
                          'baseline': None,
                          'stage_completion': {'initial_rgb': False, 'secondary_chroma': False},
                          'checked_categories': [], 'pending_categories': SIX.copy()}
                counter = groups[f'{split}/{model}']
                counter['eligible'] += 1
                if identity in fixed:
                    a = fixed[identity]
                    if model_hash != a['source_model_sha256']:
                        raise ValueError(f'Frozen A model hash changed: {identity}')
                    record.update(route='fixed_A', state='fixed_A_saved', checked_categories=['A'], pending_categories=[])
                    fixed_rows.append({'source_sample_key': identity, 'split': split, 'model': model,
                                       'checked_categories': ['A'], 'inspection_complete': True,
                                       'defects': a['A_only_defects'], 'score': 1.0,
                                       'provenance': {'authority': 'frozen_user_A_confirmation',
                                                      'manifest': cv['a']['confirmed_manifest'], 'human_number': a['number']}})
                    counter['fixed_A'] += 1
                else:
                    baseline = None
                    if identity in legacy:
                        prior = legacy[identity]
                        flags = description_flags(prior['defects'])
                        baseline = {'source': {**legacy_ref, 'image_id': prior['image_id'], 'kind': 'legacy_reviewed_export'},
                                    'defects': prior['defects'], 'status': cfg['sources']['legacy_status'],
                                    'requires_full_NR_review': True, 'format_candidate_flags': flags}
                        if any(flags.values()):
                            legacy_audit.append({'source_sample_key': identity, **flags})
                    if baseline is not None:
                        record.update(route='secondary_chroma', state='secondary_ready', baseline=baseline)
                        record['baseline_scope_note'] = 'Unverified legacy source only; all six NR categories await review'
                        counter['secondary_ready'] += 1
                        counter[baseline['source']['kind']] += 1
                    else:
                        record.update(route='initial_rgb', state='initial_ready')
                        counter['initial_ready'] += 1
                    counter['visual'] += 1
                records.append(record)
            print(f'Inventoried {split}/{model}: {dict(groups[f"{split}/{model}"])}', flush=True)

    identities = [r['source_sample_key'] for r in records]
    if len(identities) != len(set(identities)):
        raise ValueError('Duplicate source identity across source pools')
    scoped_fixed = {k for k in fixed if k.split('/')[0] in cfg['scope']['splits']}
    if {r['source_sample_key'] for r in fixed_rows} != scoped_fixed:
        raise ValueError('Not all scoped frozen A records were routed')
    if any(r['split'] == 'test' for r in records):
        raise ValueError('Test data entered the delivery scope')

    # Stable groups keep split/model separate; both stages of a new sample share the same group.
    buckets = defaultdict(list)
    for row in records:
        if row['route'] != 'fixed_A':
            buckets[(row['route'], row['split'], row['model'])].append(row)
    jobs = []
    for (route, split, model), bucket in sorted(buckets.items()):
        for start in range(0, len(bucket), 24):
            chunk = bucket[start:start + 24]
            group = f'{split}_{model}_{"new" if route == "initial_rgb" else "inherited"}_{start // 24 + 1:04d}'
            common = {'group_id': group, 'split': split, 'model': model,
                      'source_sample_keys': [r['source_sample_key'] for r in chunk],
                      'samples': len(chunk), 'sheets': (len(chunk) + 5) // 6, 'attempts': 0,
                      'conversation_id': None, 'packet_path': None, 'lease': None}
            if route == 'initial_rgb':
                jobs.append({**common, 'job_id': 'initial_' + group, 'stage': 'initial_rgb', 'state': 'ready', 'depends_on': None})
                jobs.append({**common, 'job_id': 'secondary_' + group, 'stage': 'secondary_chroma', 'state': 'waiting_initial',
                             'depends_on': 'initial_' + group})
            else:
                jobs.append({**common, 'job_id': 'secondary_' + group, 'stage': 'secondary_chroma', 'state': 'ready', 'depends_on': None})

    totals = Counter()
    for value in groups.values():
        totals.update(value)
    summary = {'prepared_at': datetime.now(timezone.utc).isoformat(), 'annotation_contract': cfg['annotation_contract'],
               'scope': cfg['scope'], 'totals': dict(totals), 'by_split_model': {k: dict(v) for k, v in groups.items()},
               'excluded_model_samples': len(skipped), 'image_files_hashed': len(image_hashes),
               'experiment_annotations_used': 0,
               'sole_secondary_baseline': legacy_ref,
               'legacy_format_audit': {'candidate_samples': len(legacy_audit),
                                       'counts': dict(sum((Counter({k: v for k, v in row.items() if k != 'source_sample_key'}) for row in legacy_audit), Counter())),
                                       'scope': 'eligible_non_A_legacy_samples', 'semantic_correctness_inferred': False},
               'jobs': dict(Counter(f'{j["stage"]}/{j["state"]}' for j in jobs)),
               'new_initial_completed': 0, 'new_secondary_completed': 0, 'model_calls': 0,
               'scheduler_implemented': False, 'quota_restore_confirmed': False, 'production_ready': False}
    write_lines(destination / 'inventory.jsonl', records)
    write_lines(destination / 'queue.jsonl', jobs)
    write(destination / 'fixed_A_final.json', {'annotation_contract': cfg['annotation_contract'], 'reviews': fixed_rows})
    write(destination / 'excluded_sources.json', skipped)
    write(destination / 'legacy_format_audit.json', {'note': 'Literal candidates only; every legacy sample needs full NR review', 'samples': legacy_audit})
    write(destination / 'source_registry.json', registry)
    write(destination / 'inventory_summary.json', summary)
    write(destination / 'checkpoint.json', {'state': 'offline_prepared_no_calls', 'model_calls': 0,
                                         'stop_reason': 'await_quota_confirmation_and_scheduler_implementation',
                                         'jobs_file': 'queue.jsonl', 'sessions': [], 'running_jobs': [],
                                         'global_concurrency': 16})
    print(json.dumps({'totals': dict(totals), 'jobs': summary['jobs'], 'model_calls': 0}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=PROJECT / read(PROJECT / 'config.json')['preparation']['inventory'])
    args = parser.parse_args()
    inventory(args.output.resolve())
