"""Execute 100-sample review strictly by 8-sheets/session with external file read/write."""
from collections import Counter, defaultdict
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass

DELIVERY_DIR = Path(__file__).resolve().parents[1]
ROOT = DELIVERY_DIR.parents[1]
sys.path.insert(0, str(DELIVERY_DIR / 'scripts'))
sys.path.insert(0, str(ROOT / 'experiments/cv_workflow'))

from prepare import PROJECT, read, write, lines, sha, rel, SIX, FOUR
from prepare_packets import render, RENDER_REVISION
from secondary_review import POLICY, REVISION, prepare_secondary_files, baseline_from_mapping, merge_sample
from review_contract import REFERENCE, HEADING, HIDDEN_HISTORY, validate_entry

RUN_DIR = DELIVERY_DIR / 'runtime/trial100_8sheets_20261016_01'
EXPORTS_DIR = RUN_DIR / 'exports'
MAIN_CHECKPOINT = DELIVERY_DIR / 'runtime/autonomous_pipeline_v1/checkpoint.json'


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def update_main_checkpoint(modifier_fn):
    """Safely updates the shared dashboard checkpoint so Web UI reflects real-time status."""
    if not MAIN_CHECKPOINT.exists():
        return
    try:
        state = json.loads(MAIN_CHECKPOINT.read_text(encoding='utf-8'))
        modifier_fn(state)
        state['updated_at'] = now_iso()

        counts = Counter(s.get('state') for s in state.get('samples', {}).values())
        state['stats'].update({
            'total': len(state.get('samples', {})),
            'completed': counts.get('completed', 0),
            'secondary_ready': counts.get('secondary_ready', 0),
            'secondary_running': counts.get('secondary_running', 0),
            'needs_manual': counts.get('needs_manual', 0)
        })

        tmp = MAIN_CHECKPOINT.with_suffix('.tmp')
        tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
        tmp.replace(MAIN_CHECKPOINT)
    except Exception:
        pass


def get_first_100_secondary_samples():
    cfg = read(DELIVERY_DIR / 'config.json')
    cv = read(ROOT / cfg['source_config'])
    inv = {r['source_sample_key']: r for r in lines(DELIVERY_DIR / 'data/preparation_02/inventory.jsonl')}
    queue = lines(DELIVERY_DIR / 'data/preparation_02/queue.jsonl')

    selected_samples = []
    for task in queue:
        if task['stage'] == 'secondary_chroma' and task['state'] == 'ready':
            for key in task['source_sample_keys']:
                if key in inv and key not in selected_samples:
                    selected_samples.append(key)
                if len(selected_samples) == 100:
                    break
        if len(selected_samples) == 100:
            break

    assert len(selected_samples) == 100
    records = [inv[k] for k in selected_samples]
    return records, cfg, cv


def prepare_8sheets_packets(records, cfg, cv):
    """Prepares exactly 100 samples into 8-sheet sessions:
       - Packet 1: 48 samples (8 sheets, S001-S048)
       - Packet 2: 48 samples (8 sheets, S001-S048)
       - Packet 3: 4 samples (1 sheet, S001-S004)
    """
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    packets_dir = RUN_DIR / 'packets'
    packets_dir.mkdir(parents=True, exist_ok=True)

    chunk_sizes = [48, 48, 4]
    cursor = 0
    packet_jobs = []

    for p_idx, size in enumerate(chunk_sizes, 1):
        chunk = records[cursor:cursor + size]
        cursor += size
        p_id = f'Packet_{p_idx:02d}'
        p_dir = packets_dir / p_id
        (p_dir / 'sheets').mkdir(parents=True, exist_ok=True)

        mapping = {f'S{i+1:03d}': r for i, r in enumerate(chunk)}
        sheets = render(chunk, 'secondary_chroma', p_dir / 'sheets', cfg, cv)

        request = {
            'annotation_contract': cfg['annotation_contract'],
            'stage': 'secondary_chroma',
            'packet_id': f'{p_id}-8sheets-v1',
            'checked_categories': SIX,
            'sheets': sheets,
            'render_revision': RENDER_REVISION,
            'candidate_overlays': False,
            'result_file': str((p_dir / 'reviews_gemini.json').resolve()),
            'prior_reviews_file': str((p_dir / 'prior_reviews.json').resolve())
        }
        request['allowed_read_files'] = [s['path'] for s in sheets] + [request['prior_reviews_file']]
        prepare_secondary_files(p_dir, request, mapping)
        write(p_dir / 'request.json', request)
        write(p_dir / 'manifest_private.json', {'sample_mapping': mapping, 'host_only': True})

        # Prompts: Let the session read the sheets by path itself, write to file directly, return only "文件已保存"
        common = (DELIVERY_DIR / 'prompts/session.md').read_text(encoding='utf-8')
        role = (DELIVERY_DIR / 'prompts/secondary_chroma.md').read_text(encoding='utf-8')
        listing = '\n'.join(f"- {s['path']} (对应样本编号: {', '.join(s['sample_keys'])})" for s in sheets)

        instructions = (
            f"packet_id={request['packet_id']}，stage=secondary_chroma，render_revision={RENDER_REVISION}。\n\n"
            f"【本地输入文件路径】：\n"
            f"1. 本地匿名审核底稿：{request['prior_reviews_file']}\n"
            f"2. 本轮分配的看板大图路径（共 {len(sheets)} 张，请自行使用读取工具逐张查看，不要跳过）：\n"
            f"{listing}\n\n"
            f"【核心操作与质检规范】：\n"
            f"1. 自行读取上述 {len(sheets)} 张看板大图与底稿，重点重新标定 E1/E2；原底稿的 B/C/D/F 逐 P 编号审核 (retain/correct/remove)，严禁遗漏！\n"
            f"2. 描述必须使用无 GT 对比的单图自然句，严禁包含“原本是”、“比原图”、“从某色变为”等词！严禁带对象/类别前缀或等级代号（如禁止“外套(L2):”）。\n"
            f"3. 将最终完整审核结果直接修改保存至指定本地结果文件：\n"
            f"   {request['result_file']}\n"
            f"4. 【严禁长文本回复】：严禁在对话回复中返回大段 JSON 或分析！修改并保存文件后，你仅需回复“文件已保存”。"
        )
        (p_dir / 'prompt.txt').write_text(common + '\n' + role + '\n' + instructions, encoding='utf-8')

        packet_jobs.append({
            'packet_id': p_id,
            'dir': p_dir,
            'samples': len(mapping),
            'sample_keys': [r['source_sample_key'] for r in chunk],
            'sheets_count': len(sheets)
        })

    print(f"[*] 成功准备 100 组样本为 {len(packet_jobs)} 个任务包 (前两包各 8 张图/48样本, 尾包 1 张图/4样本)！", flush=True)
    return packet_jobs


def run_packet(job, worker_id='W01'):
    p_dir = job['dir']
    prompt_file = p_dir / 'prompt.txt'
    prompt = prompt_file.read_text(encoding='utf-8')

    # Update dashboard: worker running & samples running
    def mark_start(state):
        w = state.setdefault('workers', {}).setdefault(worker_id, {})
        w.update({
            'role': f'🔥 正在审核 {job["packet_id"]} ({job["sheets_count"]}张图/{job["samples"]}样本)',
            'conversation_id': 'active_reading',
            'rounds': 1,
            'current_task': job['packet_id']
        })
        for sk in job['sample_keys']:
            if sk in state.get('samples', {}):
                state['samples'][sk]['state'] = 'secondary_running'

    update_main_checkpoint(mark_start)

    agy = Path.home() / 'AppData/Local/agy/bin/agy.exe'
    cmd = [
        str(agy), '-p', prompt,
        '--model', 'gemini-3.8-flash-high',
        '--mode', 'accept-edits',
        '--dangerously-skip-permissions',
        '--output-format', 'json',
        '--print-timeout', '0',  # 0 means wait until completion without hard timeout kill
        '--log-file', str(p_dir / 'client.log')
    ]

    print(f"\n=======================================================", flush=True)
    print(f"[{worker_id}] 启动执行 {job['packet_id']}：分配 {job['sheets_count']} 张大图看板，共 {job['samples']} 组样本...", flush=True)
    print(f"👉 模式：由会话自行按路径读取本地图片，结果直接写回本地文件，不通过回复输出 JSON", flush=True)
    print(f"=======================================================", flush=True)

    t0 = time.time()
    res = subprocess.run(cmd, cwd=p_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
    cost = time.time() - t0

    out_json = {}
    try:
        out_json = json.loads(res.stdout)
    except Exception:
        pass

    conv_id = out_json.get('conversation_id')
    status = out_json.get('status')
    err = out_json.get('error')

    print(f"[{worker_id}] {job['packet_id']} 会话完成 (耗时: {cost:.1f}s, 状态: {status})", flush=True)

    # Validate output written to reviews_gemini.json
    manifest = read(p_dir / 'manifest_private.json')['sample_mapping']
    request = read(p_dir / 'request.json')
    result_file = p_dir / 'reviews_gemini.json'

    reviews = read(result_file).get('reviews', {}) if result_file.exists() else {}
    passed_count = 0
    requeued_count = 0

    def mark_finish(state):
        nonlocal passed_count, requeued_count
        w = state.setdefault('workers', {}).setdefault(worker_id, {})
        w.update({
            'role': '空闲就绪',
            'conversation_id': conv_id,
            'rounds': 1,
            'current_task': None
        })
        for lid, rec in manifest.items():
            sk = rec['source_sample_key']
            sample_review = reviews.get(lid)
            baseline = request['secondary_baseline'].get(lid, {})
            sample_data = state.get('samples', {}).get(sk)
            if not sample_data:
                continue

            if not sample_review:
                sample_data['state'] = 'secondary_ready'
                sample_data['last_feedback'] = '模型未将审核结果写入文件 (null)'
                requeued_count += 1
                continue

            try:
                final = merge_sample(sample_review, baseline)
                flagged = None
                for d in final:
                    txt = d.get('description', '')
                    if REFERENCE.search(txt) or HIDDEN_HISTORY.search(txt):
                        flagged = f"描述含对比违规词: '{txt}'"
                        break
                    if HEADING.search(txt):
                        flagged = f"描述含标题前缀: '{txt}'"
                        break

                if flagged:
                    sample_data['state'] = 'secondary_ready'
                    sample_data['retry_count'] = sample_data.get('retry_count', 0) + 1
                    sample_data['last_feedback'] = flagged
                    state['stats']['qa_retries'] = state['stats'].get('qa_retries', 0) + 1
                    requeued_count += 1
                else:
                    sample_data['state'] = 'completed'
                    sample_data['defects'] = final
                    sample_data['last_feedback'] = None
                    passed_count += 1
            except Exception as e:
                sample_data['state'] = 'secondary_ready'
                sample_data['last_feedback'] = str(e)
                requeued_count += 1

    update_main_checkpoint(mark_finish)
    print(f"[{worker_id}] 任务包 {job['packet_id']} 质检核验完毕: ✅ 通过 {passed_count} 组 | 🔁 打回自愈 {requeued_count} 组", flush=True)
    return conv_id, status


def export_stream_file():
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MAIN_CHECKPOINT.exists():
        return None
    state = json.loads(MAIN_CHECKPOINT.read_text(encoding='utf-8'))
    samples = state.get('samples', {})

    stream_tasks = []
    completed_samples = 0
    issues = []

    for sk, s in samples.items():
        if s.get('state') == 'completed':
            completed_samples += 1
            stream_tasks.append({
                'id': sk,
                'data': {'source_sample_key': sk},
                'predictions': [{
                    'model_version': 'gemini-3.8-flash-high / NR_secondary_preserve_20261015_04',
                    'result': [{
                        'from_name': 'defects',
                        'to_name': 'image',
                        'type': 'textarea',
                        'value': {'text': [json.dumps(s.get('defects', []), ensure_ascii=False, indent=2)]}
                    }],
                    'score': 1.0
                }]
            })
        elif s.get('last_feedback'):
            issues.append({'sample': sk, 'feedback': s['last_feedback']})

    stream_file = EXPORTS_DIR / 'tasks_secondary_trial100_stream.json'
    write(stream_file, stream_tasks)

    report_file = EXPORTS_DIR / 'quality_audit_trial100.json'
    write(report_file, {
        'total_samples': len(samples),
        'completed': completed_samples,
        'pass_rate': f"{(completed_samples / max(len(samples), 1)) * 100:.1f}%",
        'qa_requeues_count': len(issues),
        'issues': issues
    })

    print(f"\n=======================================================", flush=True)
    print(f"🎉 100 组试运行流式包导出完成！", flush=True)
    print(f"• 质检通过导出: {completed_samples} / {len(samples)} (通过率: {(completed_samples / max(len(samples), 1)) * 100:.1f}%)", flush=True)
    print(f"• 导出流式包路径: {stream_file.resolve()}", flush=True)
    print(f"• 质检报告路径: {report_file.resolve()}", flush=True)
    print(f"=======================================================\n", flush=True)
    return stream_file, report_file


def main():
    records, cfg, cv = get_first_100_secondary_samples()
    packet_jobs = prepare_8sheets_packets(records, cfg, cv)

    # Synchronize sample inventory to main dashboard checkpoint
    def sync_init_state(state):
        for rec in records:
            sk = rec['source_sample_key']
            if sk not in state.get('samples', {}):
                state.setdefault('samples', {})[sk] = {
                    'source_sample_key': sk,
                    'sample_key': sk.split('/')[-1],
                    'state': 'secondary_ready',
                    'retry_count': 0,
                    'last_feedback': None,
                    'defects': None
                }
    update_main_checkpoint(sync_init_state)

    # Execute the packets
    for idx, job in enumerate(packet_jobs, 1):
        worker_name = f'W{idx:02d}'
        run_packet(job, worker_id=worker_name)
        time.sleep(2)

    export_stream_file()


if __name__ == '__main__':
    main()
