"""Check actual preparation coverage, source preservation and starter packet integrity."""
import argparse
from collections import Counter
from pathlib import Path

from PIL import Image

from prepare import PROJECT, ROOT, read, lines, sha, write, FOUR, SIX
from secondary_review import POLICY, SCHEMA, baseline_from_mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    cfg = read(PROJECT / 'config.json')
    parser.add_argument('--inventory', type=Path, default=PROJECT / cfg['preparation']['inventory'])
    parser.add_argument('--packets', type=Path, default=PROJECT / cfg['preparation']['starter'])
    args = parser.parse_args()
    summary = read(args.inventory / 'inventory_summary.json')
    assert summary['annotation_contract'] == cfg['annotation_contract']
    assert summary['experiment_annotations_used'] == 0
    assert summary['sole_secondary_baseline']['path'] == cfg['sources']['legacy_reviewed']
    records = lines(args.inventory / 'inventory.jsonl')
    jobs = lines(args.inventory / 'queue.jsonl')
    by_key = {r['source_sample_key']: r for r in records}
    assert len(by_key) == len(records)
    assert {r['split'] for r in records} == {'train', 'val'}
    assert all(r['model'] in ['lcad', 'unicolor'] for r in records)
    fixed = {r['source_sample_key']: r for r in read(args.inventory / 'fixed_A_final.json')['reviews']}
    assert set(fixed) == {k for k, r in by_key.items() if r['route'] == 'fixed_A'}
    assert all(r['checked_categories'] == ['A'] and r['score'] == 1.0
               and len(r['defects']) == 1 and r['defects'][0]['id'] == 'A' and r['defects'][0]['severity'] == '' for r in fixed.values())
    visual = set(by_key) - set(fixed)
    initial_members = [key for j in jobs if j['stage'] == 'initial_rgb' for key in j['source_sample_keys']]
    secondary_members = [key for j in jobs if j['stage'] == 'secondary_chroma' for key in j['source_sample_keys']]
    assert len(secondary_members) == len(set(secondary_members)) and set(secondary_members) == visual
    assert len(initial_members) == len(set(initial_members))
    assert set(initial_members) == {k for k, r in by_key.items() if r['route'] == 'initial_rgb'}
    job_map = {j['job_id']: j for j in jobs}
    assert len(job_map) == len(jobs)
    for job in jobs:
        assert 0 < job['samples'] <= 24 and job['samples'] == len(job['source_sample_keys'])
        assert job['sheets'] == (job['samples'] + 5) // 6 and job['attempts'] == 0 and job['lease'] is None
        if job['depends_on']:
            parent = job_map[job['depends_on']]
            assert parent['source_sample_keys'] == job['source_sample_keys'] and job['state'] == 'waiting_initial'
        elif job['stage'] == 'secondary_chroma':
            assert all(by_key[k]['baseline'] is not None and by_key[k]['baseline']['source']['path'] == cfg['sources']['legacy_reviewed']
                       and by_key[k]['baseline']['requires_full_NR_review'] for k in job['source_sample_keys'])
    for row in records:
        if row['route'] == 'secondary_chroma':
            assert row['split'] == 'train' and row['model'] == 'lcad'
            assert row['checked_categories'] == [] and row['pending_categories'] == SIX
        elif row['route'] == 'initial_rgb':
            assert row['baseline'] is None
    source_registry = read(args.inventory / 'source_registry.json')
    for name, expected in source_registry.items():
        assert sha(ROOT / name) == expected['sha256'], f'Source changed: {name}'
    for name, expected in read(args.packets / 'build_source_registry.json').items():
        assert sha(ROOT / name) == expected, f'Build source changed: {name}'
    starter = read(args.packets / 'starter_index.json')
    assert starter['annotation_contract'] == cfg['annotation_contract']
    images = 0
    packet_members = []
    for packet in starter['packets']:
        directory = Path(packet['packet_path'])
        for name, expected in read(directory / 'packet_integrity.json').items():
            assert sha(directory / name) == expected, f'Packet changed: {directory / name}'
        private = read(directory / 'manifest_private.json')
        request = read(directory / 'request.json')
        template = read(directory / 'reviews_gemini.json')
        assert set(private['sample_mapping']) == set(template['reviews'])
        assert all(value is None for value in template['reviews'].values())
        preserved_review = packet['stage']=='secondary_chroma' and cfg['stages']['secondary_chroma']['merge']==POLICY
        assert template['schema_version'] == (SCHEMA if preserved_review else 'delivery_review_compact_v2')
        assert template['annotation_contract'] == request['annotation_contract'] == packet['annotation_contract'] == cfg['annotation_contract']
        assert request['label_semantics'] == cfg['label_semantics'] and request['description_policy'] == cfg['description_policy']
        assert template['stage'] == packet['stage'] and template['packet_id'] == packet['packet_id']
        assert request['checked_categories'] == (FOUR if packet['stage'] == 'initial_rgb' else SIX)
        local_ids = []
        for sheet in request['sheets']:
            path = Path(sheet['path'])
            assert sha(path) == sheet['sha256']
            with Image.open(path) as image:
                image.load()
                assert list(image.size) == sheet['size'] == [1560, 430 * sheet['groups']]
            local_ids.extend(sheet['sample_keys'])
            images += 1
        assert local_ids == list(template['reviews'])
        if packet['stage'] == 'secondary_chroma':
            prior = read(directory / 'prior_reviews.json')
            assert set(prior['reviews']) == set(template['reviews'])
            if preserved_review:
                assert prior['policy'] == request['secondary_merge_policy'] == POLICY
                assert prior['reviews'] == request['secondary_baseline'] == baseline_from_mapping(private['sample_mapping'])
            else:
                assert prior['status'] == 'unverified_legacy_labels_full_NR_review_required'
                assert all(d['id'] in SIX for ds in prior['reviews'].values() for d in ds)
        else:
            assert not (directory / 'prior_reviews.json').exists()
        members = [r['source_sample_key'] for r in private['sample_mapping'].values()]
        assert members == job_map[packet['job_id']]['source_sample_keys']
        packet_members.extend(members)
        prompt = (directory / 'prompt_first.txt').read_text(encoding='utf-8')
        assert all(key not in prompt for key in members)
        assert all(by_key[k]['gt_path'] not in prompt and by_key[k]['model_path'] not in prompt for k in members)
        assert packet['job_id'] not in prompt
        assert '禁止“外套（L2）' in prompt and 'description' in prompt and '自然' in prompt
        assert 'C是具体对象相对GT明显换色' not in prompt and 'D必须是全图整体偏色' not in prompt
        assert packet['model_calls'] == 0 and packet['conversation_id'] is None
    assert len(packet_members) == len(set(packet_members))
    assert not read(args.inventory / 'checkpoint.json')['running_jobs']
    report = {'state': 'offline_preparation_integrity_passed', 'annotation_contract': cfg['annotation_contract'],
              'experiment_annotations_used': 0, 'sole_secondary_baseline': cfg['sources']['legacy_reviewed'],
              'description_policy': cfg['description_policy'], 'inventory_samples': len(records),
              'fixed_A_saved': len(fixed), 'visual_pending_secondary': len(visual),
              'initial_pending': len(initial_members), 'secondary_ready': len(visual) - len(initial_members),
              'queue_jobs': len(jobs), 'starter_packets': len(starter['packets']), 'starter_boards': images,
              'starter_unique_samples': len(set(packet_members)), 'protected_source_files_checked': len(source_registry),
              'new_model_calls': 0, 'semantic_accuracy_validated': False,
              'visual_inspection': 'separate host inspection required; file checks alone are not visual acceptance',
              'split_model_counts': dict(Counter(f'{r["split"]}/{r["model"]}' for r in records))}
    write(args.packets / 'verification.json', report)
    print(report)


if __name__ == '__main__':
    main()
