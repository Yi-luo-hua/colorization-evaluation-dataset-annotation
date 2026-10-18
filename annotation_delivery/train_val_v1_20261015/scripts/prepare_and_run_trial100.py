"""Agile 100-sample pipeline execution with live dashboard checkpoint synchronization."""
from collections import Counter, defaultdict
import copy
from datetime import datetime, timezone
import json
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

RUN_DIR = DELIVERY_DIR / 'runtime/trial100_no_overlay_20261016_01'
EXPORTS_DIR = RUN_DIR / 'exports'
MAIN_CHECKPOINT = DELIVERY_DIR / 'runtime/autonomous_pipeline_v1/checkpoint.json'


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def update_main_checkpoint(modifier_fn):
    """Safely reads, modifies, and saves the shared dashboard checkpoint.json."""
    if not MAIN_CHECKPOINT.exists():
        return
    try:
        state = json.loads(MAIN_CHECKPOINT.read_text(encoding='utf-8'))
        modifier_fn(state)
        state['updated_at'] = now_iso()

        # Recount stats
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
    except Exception as exc:
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


def prepare_agile_packets(records, cfg, cv, chunk_size=12):
    """Splits 100 samples into smaller 2-sheet (12-sample) agile packets to prevent timeouts."""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    packets_dir = RUN_DIR / 'packets'
    packets_dir.mkdir(parents=True, exist_ok=True)

    packet_jobs = []
    for p_idx, offset in enumerate(range(0, len(records), chunk_size), 1):
        chunk = records[offset:offset + chunk_size]
        p_id = f'P{p_idx:04d}'
        p_dir = packets_dir / p_id
        (p_dir / 'sheets').mkdir(parents=True, exist_ok=True)

        mapping = {f'S{i+1:03d}': r for i, r in enumerate(chunk)}
        sheets = render(chunk, 'secondary_chroma', p_dir / 'sheets', cfg, cv)

        request = {
            'annotation_contract': cfg['annotation_contract'],
            'stage': 'secondary_chroma',
            'packet_id': f'{p_id}-agile-v1',
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

        # Prompts
        common = (DELIVERY_DIR / 'prompts/session.md').read_text(encoding='utf-8')
        role = (DELIVERY_DIR / 'prompts/secondary_chroma.md').read_text(encoding='utf-8')
        listing = '\n'.join(s['path'] + ': ' + ', '.join(s['sample_keys']) for s in sheets)
        current = (
            f'packet_id={request["packet_id"]}，stage=secondary_chroma，render_revision={RENDER_REVISION}。\n'
            f'先读匿名审核底稿：{request["prior_reviews_file"]}\n'
            f'只修改指定结果：{request["result_file"]}\n'
            '指定看板，每张读取一次：\n' + listing + '\n'
            '【质检自查特别要求】：\n'
            '1. 重点重标E1/E2，原B/C/D/F逐P编号review (retain/correct/remove)，严禁遗漏。\n'
            '2. 描述必须使用无GT对比的单图自然句，严禁包含“原本是”、“比原图”、“从某色变为”等词！\n'
            '3. 描述严禁带对象/类别前缀或等级代号（如禁止“外套(L2):”）。\n'
            '保存后只回复“文件已保存”。'
        )
        (p_dir / 'prompt_first.txt').write_text(common + '\n' + role + '\n' + current, encoding='utf-8')
        (p_dir / 'prompt_continue.txt').write_text('继续固定二次角色，本轮编号重新对应。\n' + role + '\n' + current, encoding='utf-8')

        packet_jobs.append({
            'packet_id': p_id,
            'dir': p_dir,
            'samples': len(mapping),
            'sample_keys': [r['source_sample_key'] for r in chunk],
            'sheets': len(sheets)
        })

    print(f"[*] 成功准备并渲染 {len(packet_jobs)} 个敏捷任务包 (每包约 {chunk_size} 样本)！", flush=True)
    return packet_jobs


def execute_packet_agy(job, worker_id='W01', conversation_id=None, rounds=1):
    p_dir = job['dir']
    prompt_file = p_dir / ('prompt_continue.txt' if conversation_id else 'prompt_first.txt')
    prompt = prompt_file.read_text(encoding='utf-8')

    # Update live dashboard: mark worker as running and samples as running
    def mark_start(state):
        w = state.setdefault('workers', {}).setdefault(worker_id, {})
        w.update({
            'role': f'🔥 正在审核 {job["packet_id"]}',
            'conversation_id': conversation_id or 'init_session',
            'rounds': rounds,
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
        '--print-timeout', '180s',
        '--log-file', str(p_dir / 'client.log')
    ]
    if conversation_id:
        cmd += ['--conversation', conversation_id]

    print(f"  [{worker_id}] 启动模型审核任务包 {job['packet_id']} ({job['samples']} 样本, 轮次 {rounds}/8)...", flush=True)
    t0 = time.time()
    res = subprocess.run(cmd, cwd=p_dir, capture_output=True, text=True, encoding='utf-8', errors='replace')
    cost = time.time() - t0

    out_json = {}
    try:
        out_json = json.loads(res.stdout)
    except Exception:
        pass

    conv_id = out_json.get('conversation_id') or conversation_id
    status = out_json.get('status')
    err = out_json.get('error')

    print(f"  [{worker_id}] 任务包 {job['packet_id']} 审核结束 (耗时 {cost:.1f}s, 状态: {status})", flush=True)

    # Validate output immediately and update dashboard
    manifest = read(p_dir / 'manifest_private.json')['sample_mapping']
    request = read(p_dir / 'request.json')
    result_file = p_dir / 'reviews_gemini.json'

    reviews = read(result_file).get('reviews', {}) if result_file.exists() else {}

    def mark_finish(state):
        w = state.setdefault('workers', {}).setdefault(worker_id, {})
        w.update({
            'role': '空闲待命',
            'conversation_id': conv_id,
            'rounds': rounds,
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
                sample_data['last_feedback'] = '模型未保存结果 (null)'
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
                        flagged = f"描述含前缀标题: '{txt}'"
                        break

                if flagged:
                    sample_data['state'] = 'secondary_ready'
                    sample_data['retry_count'] = sample_data.get('retry_count', 0) + 1
                    sample_data['last_feedback'] = flagged
                    state['stats']['qa_retries'] = state['stats'].get('qa_retries', 0) + 1
                else:
                    sample_data['state'] = 'completed'
                    sample_data['defects'] = final
                    sample_data['last_feedback'] = None
            except Exception as e:
                sample_data['state'] = 'secondary_ready'
                sample_data['last_feedback'] = str(e)

    update_main_checkpoint(mark_finish)
    return conv_id, status, err


def export_final_stream():
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if not MAIN_CHECKPOINT.exists():
        return None
    state = json.loads(MAIN_CHECKPOINT.read_text(encoding='utf-8'))
    samples = state.get('samples', {})

    stream_tasks = []
    completed_count = 0
    issues = []

    for sk, s in samples.items():
        if s.get('state') == 'completed':
            completed_count += 1
            stream_tasks.append({
                'id': sk,
                'data': {
                    'source_sample_key': sk
                },
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
        'completed': completed_count,
        'pass_rate': f"{(completed_count / max(len(samples), 1)) * 100:.1f}%",
        'issues': issues
    })
    return stream_file, report_file


def main():
    print("=======================================================")
    print("🚀 【敏捷版 100 组试运行】准备无轮廓看板与多任务包...")
    print("=======================================================")
    records, cfg, cv = get_first_100_secondary_samples()
    # Chunk size: 12 samples (2 sheets) per agile packet
    packet_jobs = prepare_agile_packets(records, cfg, cv, chunk_size=12)

    print("\n=======================================================")
    print("🤖 开始多轮会话执行审核 (实时联动 Web 看板)...")
    print("=======================================================")
    active_conv_id = None
    for idx, job in enumerate(packet_jobs, 1):
        worker_id = f'W{((idx - 1) % 4) + 1:02d}'
        rounds = idx
        conv_id, status, err = execute_packet_agy(job, worker_id=worker_id, conversation_id=active_conv_id, rounds=rounds)
        if status == 'SUCCESS':
            active_conv_id = conv_id
        time.sleep(1)

    print("\n=======================================================")
    print("🎉 全部任务包执行完毕，导出流式检查包与质检报告...")
    print("=======================================================")
    stream_file, report_file = export_final_stream()
    print(f"• 流式检查包: {stream_file.resolve() if stream_file else 'N/A'}")
    print(f"• 质量报告: {report_file.resolve() if report_file else 'N/A'}")


if __name__ == '__main__':
    main()
