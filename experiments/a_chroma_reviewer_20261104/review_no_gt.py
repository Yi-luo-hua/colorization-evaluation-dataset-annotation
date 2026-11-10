"""Independent generated-image A review with native Antigravity read receipts."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from html import escape
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from threading import Event
from urllib.parse import quote

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps

from prepare_candidates import LOCAL, ROOT, write

sys.path.insert(0, str(ROOT / 'annotation_delivery/train_val_v1_20261015/scripts'))
from batch_auth import batch_environment, prepare_worker_profile
from visual_receipts import path_key, read_visual_receipts

MODEL = 'gemini-3.8-flash-high'
LABELS = ('A', 'not_A', 'unsure')
DISPLAY_LABELS = {'A': 'A', 'not_A': '非 A', 'unsure': '待定', 'pending': '待分类'}
PROMPT = '''本任务只判上色结果的 A 缺色。按中性灰背景、正常显示下的可见色调判：全图只有黑、白、灰，任何区域都辨不出色调，才标 A。只要全图薄薄的淡黄、蓝灰、棕褐，或者小块真实可辨的绿、红等，标 not_A。低彩度、有色单色、局部留色均不符合 A。不要判断配色好坏、E2、D 或 GT。彩度数值及位置只导航疑似连续色区，不能用固定阈值下结论，孤立噪点不算可见色块。只在画面显示或可辨性确实拿不准时用 unsure，并说明疑点。
先依次用原生图像工具各读一次列出的 PNG 看板，观察全图和小区域。再读列出的 hints.json 核对疑点，它只由同一生成图计算。不要读其他文件、执行代码、查原始图、查标签或搜索。已写对的条目保留。按以下格式把完整 JSON 写入指定绝对路径；命令行回复仅确认保存。每张图必须恰好一条，A 写全图观察，not_A 写可见色调与位置，unsure 写具体不确定点。禁止用数值代替视觉证据。
格式示例 {"reviews":{"EXAMPLE":{"label":"not_A","evidence":"画面右下方的窗框留有可辨的淡蓝色。"}}}。实际编号只使用板上的编号。'''


def chroma_regions(chroma):
    height, width = chroma.shape
    regions = []
    for threshold in (1.5, 3, 5, 8):
        count, _, stats, centers = cv2.connectedComponentsWithStats(
            (chroma >= threshold).astype(np.uint8), connectivity=8)
        if count == 1:
            continue
        index = 1 + int(stats[1:, cv2.CC_STAT_AREA].argmax())
        x, y = centers[index]
        box = stats[index, :4]
        regions.append({'C_min': threshold, 'area_pct': round(100 * int(stats[index, 4]) / chroma.size, 3),
                        'center_pct': [round(100 * x / width), round(100 * y / height)],
                        'box_pct': [round(100 * int(v) / d) for v, d in zip(box, (width, height, width, height))]})
    return regions


def prepare(run):
    manifest = LOCAL / 'manifest.json'
    raw = manifest.read_bytes()
    records = json.loads(raw)['records']
    if len(records) != 600 or len({r['id'] for r in records}) != 600:
        raise ValueError('Expected the frozen queue of 600 unique candidates')
    jobs = []
    for start in range(0, len(records), 24):
        directory = run / f'job_{start // 24 + 1:02d}'
        directory.mkdir(parents=True, exist_ok=True)
        sheets, hints = [], {}
        subset = records[start:start + 24]
        for offset in range(0, len(subset), 6):
            group = subset[offset:offset + 6]
            board = Image.new('RGB', (1344, 944), '#737373')
            draw = ImageDraw.Draw(board)
            for index, row in enumerate(group):
                path = ROOT / row['model_path']
                if sha256(path.read_bytes()).hexdigest() != row['model_sha256']:
                    raise ValueError(f'Changed generated image {row["id"]}')
                with Image.open(path) as source:
                    im = ImageOps.exif_transpose(source).convert('RGB')
                lab = cv2.cvtColor(np.asarray(im, dtype=np.float32) / 255, cv2.COLOR_RGB2LAB)
                hints[row['id']] = chroma_regions(np.linalg.norm(lab[:, :, 1:], axis=2))
                im.thumbnail((432, 430), Image.Resampling.LANCZOS)
                x, y = index % 3 * 448, index // 3 * 472
                draw.text((x + 10, y + 8), row['id'], fill='white', font_size=21)
                board.paste(im, (x + (448 - im.width) // 2, y + 34 + (430 - im.height) // 2))
            path = directory / f'board_{offset // 6 + 1}.png'
            board.save(path)
            sheets.append({'path': str(path), 'ids': [r['id'] for r in group]})
        write(directory / 'hints.json', hints)
        jobs.append({'directory': str(directory), 'sheets': sheets})
    write(run / 'plan.json', {'manifest_sha256': sha256(raw).hexdigest(), 'jobs': jobs})


def reviewed(directory, sheets, cid):
    ids = {key for sheet in sheets for key in sheet['ids']}
    receipt = read_visual_receipts(cid, sheets) if cid else {'seen': [], 'missing': [s['path'] for s in sheets]}
    seen = {key for sheet in sheets if sheet['path'] in receipt['seen'] for key in sheet['ids']}
    try:
        results = json.loads((directory / 'reviews.json').read_text(encoding='utf-8-sig'))['reviews']
    except (OSError, ValueError, KeyError, TypeError):
        results = {}
    if not isinstance(results, dict) or set(results) - ids:
        results = {}
    valid = {key: value for key, value in results.items() if key in seen and isinstance(value, dict)
             and set(value) == {'label', 'evidence'} and value['label'] in LABELS
             and isinstance(value['evidence'], str) and value['evidence'].strip()}
    return valid, sorted(ids - valid.keys()), receipt


def output_check_commands(result_path):
    if any(char in result_path for char in ('$', '`', "'", '"')):
        return set()
    commands = set()
    for quote_mark in ('"', "'"):
        quoted = f'{quote_mark}{result_path}{quote_mark}'
        for verb in ('Test-Path', 'Get-Item'):
            commands.update({f'{verb} {quoted}', f'{verb} -Path {quoted}'})
        commands.update({f'Get-Content -Raw {quoted}', f'Get-Content {quoted} -Raw'})
        for field in ('Name', 'FullName'):
            commands.add(f'Get-Item {quoted} | Select-Object {field}, Length, LastWriteTime')
    commands.add(f'''powershell -NoProfile -Command "Get-Item '{result_path}' | Select-Object FullName, Length, LastWriteTime"''')
    return commands


def audit_access(directory, sheets, status, output_checks=None):
    receipt = status['receipt']
    output_file = str(directory / 'reviews.json')
    result_path = path_key(output_file)
    permitted_checks = output_check_commands(output_file) if output_checks is not None else set()
    readable = {path_key(sheet['path']) for sheet in sheets}
    readable.update([path_key(str(directory / 'hints.json')), result_path])
    violations = []
    with Path(receipt['transcript']).open(encoding='utf-8') as stream:
        for line in stream:
            for call in json.loads(line).get('tool_calls') or []:
                name, args = call['name'], call.get('args', {})
                path = path_key(args.get('AbsolutePath') or args.get('ImagePath') or args.get('Path') or args.get('TargetFile'))
                if name in {'read_file', 'view_file', 'view_image'} and path in readable:
                    continue
                if name in {'write_file', 'edit_file', 'replace_file_content', 'multi_replace_file_content'} and path == result_path:
                    continue
                if name == 'run_command' and args.get('CommandLine') in permitted_checks:
                    output_checks.append(args['CommandLine'])
                    continue
                violations.append({'tool': name, 'path': path})
    return violations


def run_job(job, profile, stop):
    directory = Path(job['directory'])
    if stop.is_set():
        return
    if (directory / 'launch_0.json').exists():
        return
    sheets = job['sheets']
    marker = directory / 'auth_browser.log'
    environment = batch_environment(marker, profile)
    executable = Path.home() / 'AppData/Local/agy/bin/agy.exe'
    command = [str(executable), '--model', MODEL, '--mode', 'accept-edits', '--disable-slash-commands',
               '--dangerously-skip-permissions', '--output-format', 'json', '--print-timeout', '0']
    path = directory / 'reviews.json'
    prompt = job.get('prompt', PROMPT) + '\n看板文件：\n' + '\n'.join(s['path'] for s in sheets)
    hints = directory / 'hints.json'
    if hints.is_file():
        prompt += f'\n彩度位置辅助：{hints}'
    prompt += f'\n只写此文件：{path}'
    cid, frozen = None, {}
    write(directory / 'prompt.json', {'prompt': prompt, 'model': MODEL})
    for attempt in range(6):
        log = directory / f'client_{attempt}.log'
        args = command + ['--log-file', str(log), '-p', prompt]
        if cid:
            args += ['--conversation', cid]
        with (directory / f'stdout_{attempt}.json').open('wb') as out, (directory / f'stderr_{attempt}.txt').open('wb') as err:
            process = subprocess.Popen(args, cwd=directory, env=environment, stdout=out, stderr=err)
            write(directory / f'launch_{attempt}.json', {'pid': process.pid, 'resumed_cid': cid})
            process.wait()
        stderr = (directory / f'stderr_{attempt}.txt').read_text(encoding='utf-8', errors='replace')
        try:
            native = json.loads((directory / f'stdout_{attempt}.json').read_text(encoding='utf-8-sig'))
        except ValueError:
            native = {}
        actual_cid = native.get('conversation_id')
        if cid and actual_cid != cid:
            write(directory / 'status.json', {'state': 'identity_mismatch', 'expected': cid, 'actual': actual_cid})
            return
        cid = actual_cid or cid
        valid, missing, receipt = reviewed(directory, sheets, cid)
        frozen = {**valid, **frozen}
        missing = sorted(set(missing) - frozen.keys())
        write(directory / 'verified_partial.json', frozen)
        error = str(native.get('error') or '')
        # On continuation the envelope can repeat history. The exclusive stderr belongs to this call.
        fresh_error = (error if attempt == 0 else '') + '\n' + stderr
        fatal = re.search(r'User location is not supported|RESOURCE_EXHAUSTED|Individual quota reached|quota (?:exhausted|reached)|UNAUTHENTICATED', fresh_error, re.I)
        if fatal or marker.exists():
            stop.set()
        state = 'complete' if not missing else 'global_stop' if stop.is_set() else 'incomplete'
        write(directory / 'status.json', {'state': state, 'attempt': attempt, 'cid': cid, 'native_status': native.get('status'),
                                          'native_error': error, 'global_fault': fatal.group() if fatal else None,
                                          'auth_browser_blocked': marker.exists(), 'receipt': receipt, 'missing': missing})
        if not missing:
            write(directory / 'accepted.json', frozen)
            print(f'{directory.name} complete ({len(frozen)})', flush=True)
            return
        if not cid or attempt == 5 or stop.wait(20):
            print(f'{directory.name} {state}: {len(frozen)} verified, {len(missing)} pending; {error}', flush=True)
            return
        write(path, {'reviews': frozen})
        prompt = (f'继续。保留已经验收的条目，补齐这些编号 {missing}。'
                  f'只用图像工具读取此前未成功读取的看板 {receipt["missing"]}。'
                  '已读过的板不要重读。继续按全图可辨色调规则判断，每条包含 label 和 evidence，'
                  f'将已有和补齐的条目一起写入 {path}。')


def report(run):
    plan = json.loads((run / 'plan.json').read_text(encoding='utf-8'))
    raw = (LOCAL / 'manifest.json').read_bytes()
    if sha256(raw).hexdigest() != plan['manifest_sha256']:
        raise ValueError('Candidate manifest changed')
    records = json.loads(raw)['records']
    results, audit, hints = {}, {}, {}
    for job in plan['jobs']:
        directory = Path(job['directory'])
        hints.update(json.loads((directory / 'hints.json').read_text(encoding='utf-8')))
        partial = directory / 'verified_partial.json'
        status_path = directory / 'status.json'
        if not partial.exists() or not status_path.exists():
            continue
        labels = json.loads(partial.read_text(encoding='utf-8'))
        if not labels:
            continue
        status = json.loads(status_path.read_text(encoding='utf-8'))
        violations = audit_access(directory, job['sheets'], status)
        audit[directory.name] = {'cid': status['cid'], 'images_seen': len(status['receipt']['seen']),
                                 'verified_labels': len(labels), 'unexpected_tool_access': violations}
        if not violations:
            results.update(labels)
    counts = Counter(r['label'] for r in results.values())
    priority = {key for key, value in results.items() if value['label'] == 'A' and any(
        (r['C_min'] == 3 and r['area_pct'] >= 20) or (r['C_min'] == 5 and r['area_pct'] >= 1)
        for r in hints[key])}
    payload = {'model': MODEL, 'manifest_sha256': plan['manifest_sha256'], 'total': len(records),
               'counts': dict(counts), 'pending': [r['id'] for r in records if r['id'] not in results],
               'priority_review': sorted(priority),
               'reviews': {key: results[key] for key in sorted(results)}}
    write(run / 'results.json', payload)
    write(run / 'input_audit.json', audit)
    cards = []
    for row in records:
        rid = row['id']
        result = results.get(rid, {'label': 'pending', 'evidence': '待分类'})
        label, evidence = result['label'], result['evidence']
        path = quote(Path(os.path.relpath(ROOT / row['model_path'], run)).as_posix())
        region_text = '，'.join(f'C* ≥ {r["C_min"]} 时占 {r["area_pct"]:.3g}%'
                                for r in hints[rid]) or '采样阈值下未检出连续彩度区域'
        mark = ' · 优先复核' if rid in priority else ''
        cards.append(f'<article data-label="{label}" data-id="{rid}" data-priority="{rid in priority}"><a href="{path}" target="_blank" title="打开原尺寸生成图">'
                     f'<img loading="lazy" src="{path}" alt="{rid}"></a><b>{rid} · {DISPLAY_LABELS[label]}{mark}</b><p>{escape(evidence)}</p>'
                     f'<details><summary>最大连续彩度区</summary><p>{escape(region_text)}</p></details></article>')
    (run / 'review.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>A 缺色复核</title><style>body{margin:0;font:16px system-ui;background:#222;color:#eee}header{position:sticky;top:0;background:#222;padding:16px;z-index:1}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px;padding:16px}article{background:#363636;padding:8px}img{display:block;width:100%;height:220px;object-fit:contain;background:#737373}.grayscale img{filter:grayscale(1)}p{margin:.5em 0}input,select{font:inherit;margin-left:8px}a{color:#c4e4ff}</style>
<header><strong>A 缺色 · 仅看生成图</strong> ''' + escape(f'{len(results)}/{len(records)} 已核验 · A {counts["A"]} · 非 A {counts["not_A"]} · 待定 {counts["unsure"]} · 待分类 {len(payload["pending"])}') + '''
<label>筛选<select id="filter"><option value="">全部</option><option>A</option><option value="priority">优先复核（''' + str(len(priority)) + '''）</option><option value="not_A">非 A</option><option value="unsure">待定</option><option value="pending">待分类</option></select></label><input id="search" aria-label="样本编号" placeholder="输入样本编号"><label><input id="gray" type="checkbox">去色对照</label> <a href="results.json">结果 JSON</a></header><main>'''
        + '\n'.join(cards) + '''</main><script>const filter=document.querySelector('#filter'),search=document.querySelector('#search'),gray=document.querySelector('#gray');function update(){const q=search.value.trim().toUpperCase();for(const card of document.querySelectorAll('article')){const matches=filter.value==='priority'?card.dataset.priority==='True':!filter.value||filter.value===card.dataset.label;card.hidden=!matches||!card.dataset.id.includes(q)}}filter.onchange=update;search.oninput=update;gray.onchange=()=>document.body.classList.toggle('grayscale',gray.checked);</script></html>''', encoding='utf-8')
    print(f'Verified: {len(results)}/{len(records)}. {dict(counts)}', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=8, choices=range(1, 17))
    parser.add_argument('--skip', type=int, default=0)
    parser.add_argument('--first', type=int)
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    run = LOCAL / 'no_gt_20261111'
    if not (run / 'plan.json').exists():
        prepare(run)
    plan = json.loads((run / 'plan.json').read_text(encoding='utf-8'))
    if not args.report_only:
        profile = prepare_worker_profile(run / 'worker_profile')
        stop = Event()
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            for _ in executor.map(lambda job: run_job(job, profile, stop), plan['jobs'][args.skip:args.first]):
                pass
    report(run)


if __name__ == '__main__':
    main()
