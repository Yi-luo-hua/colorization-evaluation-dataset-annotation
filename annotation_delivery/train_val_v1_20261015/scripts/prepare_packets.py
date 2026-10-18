"""Render a balanced starter set of real offline packets; no agy invocation."""
import argparse
from collections import defaultdict, deque
import copy
import json
from pathlib import Path
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from prepare import PROJECT, ROOT, read, write, lines, sha, rel, SIX
from secondary_review import POLICY, prepare_secondary_files

sys.path.insert(0, str(ROOT / 'experiments/cv_workflow'))
import engine

RENDER_REVISION = 'plain_difference_no_candidate_overlay_v1'


def balanced(jobs, stage, count):
    buckets = defaultdict(deque)
    for job in jobs:
        if job['stage'] == stage and job['state'] == 'ready':
            buckets[(job['split'], job['model'])].append(job)
    selected = []
    while buckets and len(selected) < count:
        for key in sorted(list(buckets)):
            selected.append(buckets[key].popleft())
            if not buckets[key]:
                del buckets[key]
            if len(selected) == count:
                break
    return selected


def render(rows, stage, destination, cfg, cv):
    layout = cfg['layout']
    font_path = 'C:/Windows/Fonts/msyh.ttc'
    title_font = ImageFont.truetype(font_path, 20)
    small_font = ImageFont.truetype(font_path, 16)
    sheets = []
    third_title = '2×RGB绝对差：亮区不等于错色' if stage == 'initial_rgb' else '彩度红增蓝减；差分不是缺陷标签'
    for offset in range(0, len(rows), layout['groups_per_sheet']):
        chunk = rows[offset:offset + layout['groups_per_sheet']]
        canvas = Image.new('RGB', (layout['width'], layout['card_height'] * len(chunk)), (240, 242, 245))
        draw = ImageDraw.Draw(canvas)
        sheet_name = f'sheet_{len(sheets) + 1:03d}.png'
        ids = []
        for row_number, record in enumerate(chunk):
            local = f'S{offset + row_number + 1:03d}'
            ids.append(local)
            top = row_number * layout['card_height']
            draw.rectangle((8, top + 5, layout['width'] - 8, top + layout['card_height'] - 5), fill='white', outline=(200, 205, 215))
            draw.text((18, top + 10), f'行{row_number + 1}  {local}', fill='black', font=title_font)
            draw.text((18, top + 39), 'GT色取左列、生成色取中列；差分颜色不是物体色，差分亮暗不是缺陷标签。', fill=(65, 65, 70), font=small_font)
            gt_path, gen_path = ROOT / record['gt_path'], ROOT / record['model_path']
            if sha(gt_path) != record['gt_sha256'] or sha(gen_path) != record['model_sha256']:
                raise ValueError(f'Source changed since inventory: {record["source_sample_key"]}')
            gt, generated = engine.read_rgb(gt_path), engine.read_rgb(gen_path)
            if generated.shape != gt.shape:
                generated = cv2.resize(generated, (gt.shape[1], gt.shape[0]), interpolation=cv2.INTER_LINEAR)
            if stage == 'initial_rgb':
                heat = np.clip(2 * np.abs(generated.astype(np.int16) - gt.astype(np.int16)), 0, 255).astype(np.uint8)
            else:
                gt_lab, gen_lab = engine.lab(gt), engine.lab(generated)
                heat = engine.heatmap(gt_lab, gen_lab, cv['display'])
            for column, (pixels, title) in enumerate(zip([gt, generated, heat], ['GT', '生成图', third_title])):
                left = 18 + column * 515
                draw.text((left, top + 68), title, fill=(65, 65, 70), font=small_font)
                image = Image.fromarray(pixels)
                image.thumbnail((layout['image_box_width'], layout['image_box_height']), Image.Resampling.LANCZOS)
                canvas.paste(image, (left + (layout['image_box_width'] - image.width) // 2,
                                     top + 94 + (layout['image_box_height'] - image.height) // 2))
        target = destination / sheet_name
        canvas.save(target)
        sheets.append({'path': str(target.resolve()), 'sha256': sha(target), 'sample_keys': ids,
                       'groups': len(chunk), 'size': list(canvas.size)})
    return sheets


def packet(job, inventory, destination, cfg, cv, packet_id):
    packet_dir = destination / job['stage'] / packet_id / 'prepared_001'
    packet_dir.mkdir(parents=True)
    sheet_dir = packet_dir / 'sheets'
    sheet_dir.mkdir()
    rows = [inventory[key] for key in job['source_sample_keys']]
    sheets = render(rows, job['stage'], sheet_dir, cfg, cv)
    mapping = {f'S{i:03d}': r for i, r in enumerate(rows, 1)}
    target = packet_dir / 'reviews_gemini.json'
    write(target, {'schema_version': 'delivery_review_compact_v2', 'annotation_contract': cfg['annotation_contract'],
                   'stage': job['stage'], 'packet_id': packet_id, 'reviews': {key: None for key in mapping}})
    prior_file = None
    if job['stage'] == 'secondary_chroma':
        prior_file = packet_dir / 'prior_reviews.json'
        prior = {}
        for key, row in mapping.items():
            if row['baseline'] is None:
                raise ValueError('Secondary starter packet lacks a completed initial baseline')
            prior[key] = [{k: copy.deepcopy(d[k]) for k in ['id', 'severity', 'object', 'description'] if k in d}
                          for d in row['baseline']['defects'] if d.get('id') in SIX]
        write(prior_file, {'schema_version': 'delivery_anonymous_prior_v2',
                          'status': 'unverified_legacy_labels_full_NR_review_required',
                          'note': 'May contain GT comparisons or missing descriptions; an empty list is not verified negative evidence.',
                          'reviews': prior})
    allowed = [s['path'] for s in sheets]
    if prior_file:
        allowed.append(str(prior_file.resolve()))
    request = {'annotation_contract': cfg['annotation_contract'], 'label_semantics': cfg['label_semantics'],
               'render_revision': RENDER_REVISION, 'candidate_overlays': False,
               'description_policy': cfg['description_policy'], 'stage': job['stage'], 'packet_id': packet_id,
               'groups_per_sheet': 6, 'samples': len(rows), 'sheets': sheets,
               'checked_categories': cfg['stages'][job['stage']]['checked_categories'],
               'allowed_read_files': allowed, 'result_file': str(target.resolve()),
               'prior_reviews_file': str(prior_file.resolve()) if prior_file else None}
    if job['stage'] == 'secondary_chroma' and cfg['stages']['secondary_chroma']['merge'] == POLICY:
        prepare_secondary_files(packet_dir, request, mapping)
    write(packet_dir / 'request.json', request)
    write(packet_dir / 'manifest_private.json', {'job': job, 'sample_mapping': mapping,
                                               'source_access': 'host_only_never_send_to_model'})
    common = (PROJECT / 'prompts/session.md').read_text(encoding='utf-8')
    role = (PROJECT / f'prompts/{job["stage"]}.md').read_text(encoding='utf-8')
    listing = '\n'.join(f'{s["path"]}: '+', '.join(s['sample_keys']) for s in sheets)
    current = (f'本轮packet_id={packet_id}，stage={job["stage"]}，契约={cfg["annotation_contract"]}，共{len(rows)}个样本。\n'
               f'指定结果文件：{target.resolve()}\n'
               + (f'匿名审核底稿：{prior_file.resolve()}；先读原标签及P编号，再逐图核对。\n' if prior_file else '')
               + '本轮只允许下面这些看板，每张读取一次：\n' + listing + '\n'
               + '只修改指定结果文件，不读request.json或manifest_private.json；不执行命令。保存后只回复“文件已保存”。\n')
    (packet_dir / 'prompt_first.txt').write_text(common + '\n' + role + '\n' + current, encoding='utf-8')
    (packet_dir / 'prompt_continue.txt').write_text(
        '继续本会话固定角色；新一轮S编号与上轮无关。按各类独立分级和单图质量规则，一图一次、不猜细节。描述用自然句，不含GT比较，不加对象／等级标题。\n'
        + role + '\n' + current, encoding='utf-8')
    artifacts = [*sheet_dir.glob('*.png'), packet_dir / 'request.json', packet_dir / 'manifest_private.json',
                 packet_dir / 'prompt_first.txt', packet_dir / 'prompt_continue.txt']
    if prior_file:
        artifacts.append(prior_file)
    write(packet_dir / 'packet_integrity.json', {str(p.relative_to(packet_dir)): sha(p) for p in artifacts})
    return {'job_id': job['job_id'], 'packet_id': packet_id, 'annotation_contract': cfg['annotation_contract'],
            'stage': job['stage'], 'split': job['split'], 'model': job['model'],
            'samples': len(rows), 'sheets': len(sheets), 'packet_path': str(packet_dir.resolve()),
            'state': 'prepared_not_started', 'conversation_id': None, 'model_calls': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    active = read(PROJECT / 'config.json')['preparation']
    parser.add_argument('--inventory', type=Path, default=PROJECT / active['inventory'])
    parser.add_argument('--output', type=Path, default=PROJECT / active['starter'])
    parser.add_argument('--jobs-per-stage', type=int, default=8)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve existing packets; use a new --output directory')
    cfg = read(PROJECT / 'config.json')
    cv = read(ROOT / cfg['source_config'])
    summary = read(args.inventory / 'inventory_summary.json')
    if summary['annotation_contract'] != cfg['annotation_contract']:
        raise ValueError('Retired inventory contract; prepare current NR legacy-only inventory')
    for name, expected in read(args.inventory / 'source_registry.json').items():
        if sha(ROOT / name) != expected['sha256']:
            raise ValueError(f'Inventory source changed: {name}')
    inventory_rows = lines(args.inventory / 'inventory.jsonl')
    inventory = {r['source_sample_key']: r for r in inventory_rows}
    jobs = lines(args.inventory / 'queue.jsonl')
    selected = balanced(jobs, 'initial_rgb', args.jobs_per_stage) + balanced(jobs, 'secondary_chroma', args.jobs_per_stage)
    args.output.mkdir(parents=True)
    write(args.output / 'config_snapshot.json', cfg)
    write(args.output / 'cv_config_snapshot.json', cv)
    sources = [Path(__file__), Path(__file__).with_name('prepare.py'), Path(__file__).with_name('secondary_review.py'),
               Path(__file__).with_name('review_contract.py'), Path(engine.__file__),
               PROJECT / 'RULES.md', PROJECT / 'config.json', *(PROJECT / 'prompts').glob('*.md')]
    write(args.output / 'build_source_registry.json', {rel(p): sha(p) for p in sources})
    packets = []
    for number, job in enumerate(selected, 1):
        packets.append(packet(job, inventory, args.output, cfg, cv, f'P{number:04d}'))
        print(f'Prepared {job["job_id"]}: {job["samples"]} samples, {job["sheets"]} boards', flush=True)
    write(args.output / 'starter_index.json', {'annotation_contract': cfg['annotation_contract'], 'model_calls': 0, 'packets': packets,
                                             'note': 'Initial balanced starter set only; all remaining jobs are in inventory queue'})
    print(f'{len(packets)} offline packets ready; model calls: 0')


if __name__ == '__main__':
    main()
