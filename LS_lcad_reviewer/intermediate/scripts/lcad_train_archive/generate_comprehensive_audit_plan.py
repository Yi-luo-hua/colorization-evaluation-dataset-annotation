import sys
import json
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
TASKS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"

with open(ALL_FILE, "r", encoding="utf-8") as f:
    anns = json.load(f)["annotations"]

with open(TASKS_FILE, "r", encoding="utf-8") as f:
    raw_tasks = json.load(f)

# Load audit metrics map
audit_metrics_map = {}
for af in AUDITS_DIR.glob("audit_needs_grounding_*.json"):
    try:
        with open(af, "r", encoding="utf-8") as f:
            for item in json.load(f):
                audit_metrics_map[item["task_idx"]] = item.get("metrics", {})
    except Exception:
        pass

# Machine patterns to identify un-grounded tasks
machine_patterns = [
    r'场景物体',
    r'核查发现局部缺陷',
    r'色彩微调',
    r'核查修正：全图',
    r'核查修正：场景物体',
    r'核查修正：画面色彩',
    r'核查修正：色彩欠饱和',
    r'核查修正：色彩过饱和',
    r'核查发现：画面色彩偏',
    r'核查发现：全图轻微偏',
    r'核查发现：全图整体轻微偏',
    r'核查发现：全图整体色调轻微偏',
    r'核查发现：饱和度偏高浓艳',
    r'核查发现：局部色彩欠饱和褪色',
    r'核查发现：主体轮廓边缘溢色',
    r'原5\.0满分严重漏检，核查发现：画面色彩偏',
    r'原5\.0满分严重漏检，核查发现：全图轻微偏',
    r'原5\.0满分复核：核查发现：全图轻微偏',
    r'原5\.0满分复核：核查发现：色彩过饱和浓艳',
    r'原5\.0满分复核：核查发现：局部色彩欠饱和',
    r'原5\.0满分核查修正：'
]

un_grounded_ids = []
all_map = {}
for a in anns:
    tid = a['human_review']['task_id']
    all_map[tid] = a
    note = a.get('review_note', '')
    defs = a.get('defects', [])
    
    if note == '审查通过' and not defs:
        continue
        
    is_machine = any(re.search(p, note) for p in machine_patterns)
    for d in defs:
        desc = d.get('description', '')
        if '场景物体' in desc or '关键主体或背景' in desc or '局部关键区域' in desc:
            is_machine = True
            break
            
    if is_machine:
        un_grounded_ids.append(tid)

un_grounded_ids.sort()
print(f"Total un-grounded tasks needing visual large image review: {len(un_grounded_ids)}")
print(f"Task 30 included: {30 in un_grounded_ids}")

raw_map = {}
for idx, t in enumerate(raw_tasks):
    tid = t.get("id") or (idx + 1)
    data = t.get("data", {})
    orig_rec = data.get("original_record", {})
    raw_map[tid] = {
        "orig_score": orig_rec.get("gpt_score", data.get("gpt_score", 3.0)),
        "orig_defects": orig_rec.get("defects", data.get("defects", []))
    }

# Build batches (20 sheets = 120 tasks)
BATCH_SIZE = 120
batches = []
num_batches = (len(un_grounded_ids) + BATCH_SIZE - 1) // BATCH_SIZE

for b_idx in range(num_batches):
    chunk_ids = un_grounded_ids[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
    batch_num = b_idx + 1
    items = []
    for tid in chunk_ids:
        ann = all_map[tid]
        raw_info = raw_map.get(tid, {})
        metrics = audit_metrics_map.get(tid, {})
        items.append({
            "task_id": tid,
            "image_id": ann["image_id"],
            "file_path": ann.get("file_path", ""),
            "original_gpt_score": raw_info.get("orig_score", ann.get("original_gpt_score")),
            "current_review_note": ann.get("review_note", ""),
            "current_defects": ann.get("defects", []),
            "metrics": metrics
        })
    
    sheet_count = (len(chunk_ids) + 5) // 6
    batches.append({
        "batch_no": batch_num,
        "batch_name": f"remaining_batch_{batch_num:02d}",
        "task_count": len(chunk_ids),
        "sheet_count": sheet_count,
        "task_id_range": [min(chunk_ids), max(chunk_ids)],
        "task_ids": chunk_ids,
        "items": items
    })

total_sheets = sum(b["sheet_count"] for b in batches)
plan = {
    "total_remaining_tasks": len(un_grounded_ids),
    "batch_size": BATCH_SIZE,
    "sheet_chunk_size": 6,
    "num_batches": len(batches),
    "total_sheets": total_sheets,
    "batches": batches
}

out_plan = AUDITS_DIR / "remaining_visual_audit_plan_50_batches.json"
with open(out_plan, "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)

print(f"Successfully generated 50-batch plan: {len(batches)} batches, {total_sheets} total sheets.")
print(f"Saved to: {out_plan.name} ({out_plan.stat().st_size} bytes)")

# Batch 01 details
b1 = batches[0]
print(f"\nBatch 01 summary: {b1['task_count']} tasks, range [{b1['task_id_range'][0]} ~ {b1['task_id_range'][1]}], {b1['sheet_count']} sheets.")
for idx, it in enumerate(b1['items']):
    if it['task_id'] == 30:
        s_no = idx // 6 + 1
        c_no = idx % 6 + 1
        print(f"  >>> Task 30 ({it['image_id']}) is in Batch 01, Sheet {s_no:02d}, Card {c_no}!")
