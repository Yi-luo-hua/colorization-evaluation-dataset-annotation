"""Run the train/val A shortlist through native, paired-image Antigravity review."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import csv
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
from threading import Event
from urllib.parse import quote, unquote, urlsplit

import numpy as np
from PIL import Image, ImageDraw, ImageOps

from review_no_gt import LABELS, LOCAL, MODEL, ROOT, audit_access, prepare_worker_profile, run_job, write


PROMPT = '''只根据列出的图像判定 A 缺色。每个文件左侧是原尺寸生成图，右侧是同图保持亮度的去色副本。逐张用原生图像工具各读一次。先比较全图的中间亮度区域，判断左图是否有微弱而可辨认的整体色调，再比较具体区域，找很小的残余颜色。只要左图存在可辨认的色调，即使很弱、局部很小、或只有统一的一种色调，也标 not_A。全图及局部都只能辨认出黑白灰时标 A。孤立噪点不计。显示或可辨性确实拿不准时标 unsure。
not_A 写出左图上能复核的色调与位置，A 写明看过的全图和局部，unsure 写具体疑点。不要猜测其他类别，不要读取其他文件、执行代码或搜索。实际图上编号每张恰好写一条。只写指定 JSON，格式为 {"reviews":{"EXAMPLE":{"label":"not_A","evidence":"左下角物体呈浅褐色。"}}}，命令行仅确认保存。'''


def paired_board(source, rid, destination):
    with Image.open(source) as image:
        original = ImageOps.exif_transpose(image).convert('RGB')
    rgb = np.asarray(original, dtype=np.float32) / 255
    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    luminance = linear @ np.array([.2126, .7152, .0722], dtype=np.float32)
    gray = np.where(luminance <= .0031308, 12.92 * luminance, 1.055 * luminance ** (1 / 2.4) - .055)
    neutral = Image.fromarray(np.rint(gray * 255).clip(0, 255).astype(np.uint8)).convert('RGB')
    width, height = original.size
    board = Image.new('RGB', (2 * width + 36, height + 48), '#808080')
    draw = ImageDraw.Draw(board)
    draw.text((12, 6), f'{rid} / Original', fill='white', font_size=15)
    draw.text((24 + width, 6), 'Same image / Gray', fill='white', font_size=15)
    board.paste(original, (12, 29))
    board.paste(neutral, (24 + width, 29))
    board.save(destination)


def prepare(source, directory):
    with source.open(newline='', encoding='utf-8-sig') as stream:
        candidates = list(csv.DictReader(stream))
    if not candidates or len(candidates) != len({row['sample_key'] for row in candidates}):
        raise ValueError('Expected a nonempty shortlist with unique sample keys')
    ordered = sorted(candidates, key=lambda row: sha256(row['sample_key'].encode()).digest())
    records, jobs = {}, []
    for offset in range(0, len(ordered), 4):
        job_dir = directory / f'job_{offset // 4 + 1:02d}'
        job_dir.mkdir(parents=True, exist_ok=True)
        sheets = []
        for index, row in enumerate(ordered[offset:offset + 4], offset + 1):
            rid = f'S{index:03d}'
            path = job_dir / f'{rid}.png'
            paired_board(ROOT / row['generated_path'], rid, path)
            records[rid] = {**row, 'review_id': rid, 'comparison_path': path.relative_to(directory).as_posix()}
            sheets.append({'path': str(path), 'ids': [rid]})
        jobs.append({'directory': str(job_dir), 'sheets': sheets})
    return {'shortlist_sha256': sha256(source.read_bytes()).hexdigest(), 'records': records, 'jobs': jobs}


def report(plan, directory):
    accepted, audit = {}, {}
    for job in plan['jobs']:
        job_dir = Path(job['directory'])
        status_path = job_dir / 'status.json'
        if not status_path.exists():
            continue
        status = json.loads(status_path.read_text(encoding='utf8'))
        audit[job_dir.name] = status
        if not status.get('receipt', {}).get('seen'):
            continue
        status['output_checks'] = []
        status['unexpected_access'] = audit_access(job_dir, job['sheets'], status, status['output_checks'])
        if not status['unexpected_access']:
            accepted.update(json.loads((job_dir / 'verified_partial.json').read_text(encoding='utf8')))

    rows = [{**record, **accepted.get(rid, {'label': 'pending', 'evidence': ''})}
            for rid, record in plan['records'].items()]
    labels = (*LABELS, 'pending')
    rows.sort(key=lambda row: (labels.index(row['label']), row['tier'] == 'borderline', float(row['mean_C'])))
    for filename, records in [('all_reviews.csv', rows), ('A_candidates.csv', [r for r in rows if r['label'] == 'A'])]:
        target = directory / filename
        temporary = target.with_suffix('.tmp')
        with temporary.open('w', newline='', encoding='utf-8-sig') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(records)
        temporary.replace(target)
    counts = Counter(row['label'] for row in rows)
    groups = {group: {label: sum(r['label'] == label and f'{r["split"]}/{r["model"]}' == group for r in rows)
                      for label in labels} for group in sorted({f'{r["split"]}/{r["model"]}' for r in rows})}
    result = {'model': MODEL, 'shortlist_sha256': plan['shortlist_sha256'], 'total': len(rows),
              'counts': {label: counts[label] for label in labels}, 'groups': groups,
              'A_with_frozen_gt_exclusion': sum(r['label'] == 'A' and r['frozen_gt_excluded'] == 'True' for r in rows),
              'audit': audit}
    write(directory / 'summary.json', result)
    page_rows = [{'id': row['review_id'], 'key': row['sample_key'], 'label': row['label'],
                  'evidence': row['evidence'], 'excluded': row['frozen_gt_excluded'] == 'True',
                  'image': quote(Path(os.path.relpath(ROOT / row['generated_path'], directory)).as_posix()),
                  'pair': quote(row['comparison_path'])} for row in rows]
    page_data = json.dumps({'shortlist': plan['shortlist_sha256'], 'rows': page_rows}, ensure_ascii=False)
    template = Path(__file__).with_name('manual_a_review.html').read_text(encoding='utf8')
    (directory / 'manual_review.html').write_text(template.replace('/* REVIEW_DATA */', page_data.replace('<', '\\u003c')),
                                                   encoding='utf8')
    print(json.dumps(result['counts']), flush=True)


def serve(plan, directory, port):
    page = directory / 'manual_review.html'
    page_url = '/' + quote(page.relative_to(ROOT).as_posix())
    assets = {page.relative_to(ROOT).as_posix(): page}
    for row in plan['records'].values():
        pair = directory / row['comparison_path']
        assets[pair.relative_to(ROOT).as_posix()] = pair
        assets[row['generated_path']] = ROOT / row['generated_path']

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == '/':
                self.send_response(302)
                self.send_header('Location', page_url)
                self.end_headers()
                return
            asset = assets.get(unquote(path).lstrip('/'))
            if asset is None or not asset.is_file():
                self.send_error(404)
                return
            content = asset.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', mimetypes.guess_type(asset.name)[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)

    ThreadingHTTPServer(('127.0.0.1', port), Handler).serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=16, choices=range(1, 17))
    parser.add_argument('--source', type=Path, default=LOCAL / 'train_val_A_scan/candidates.csv')
    parser.add_argument('--output', type=Path, default=LOCAL / 'train_val_A_review')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--report-only', action='store_true')
    mode.add_argument('--serve', type=int, metavar='PORT')
    args = parser.parse_args()
    directory = args.output.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / 'plan.json'
    if not path.exists():
        write(path, prepare(args.source, directory))
    plan = json.loads(path.read_text(encoding='utf8'))
    print(f'{len(plan["records"])} images, {len(plan["jobs"])} native jobs', flush=True)
    if args.serve is not None:
        serve(plan, directory, args.serve)
        return
    if not args.report_only:
        profile = prepare_worker_profile(directory / 'worker_profile')
        stop = Event()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for _ in pool.map(lambda job: run_job({**job, 'prompt': PROMPT}, profile, stop), plan['jobs']):
                pass
    report(plan, directory)


if __name__ == '__main__':
    main()
