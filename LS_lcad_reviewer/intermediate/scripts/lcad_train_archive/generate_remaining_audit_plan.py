import sys
import json
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

# Collect tasks_with_sheets
tasks_with_sheets = set()
for sm in AUDITS_DIR.glob("sheets_meta_*.json"):
    try:
        with open(sm, "r", encoding="utf-8") as f:
            for item in json.load(f):
                tid = item.get("task_idx") or item.get("id") or item.get("task_id")
                if tid: tasks_with_sheets.add(int(tid))
    except Exception:
        pass

for ap in AUDITS_DIR.glob("audit_pass_*.json"):
    try:
        with open(ap, "r", encoding="utf-8") as f:
            for item in json.load(f):
                tid = item.get("task_idx") or item.get("id") or item.get("task_id")
                if tid: tasks_with_sheets.add(int(tid))
    except Exception:
        pass

for dft_name in [
    "deep_fix_targets_all.json",
    "cv_physical_audit_plan.json",
    "random_sample_200_items.json",
    "grounding_targets_1001_1500.json",
    "cv_physical_sample_60_items.json"
]:
    p = AUDITS_DIR / dft_name
    if p.exists():
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            items = data.get("items", []) if isinstance(data, dict) else data
            for item in items:
                tid = item.get("human_review", {}).get("task_id") or item.get("task_idx") or item.get("id") or item.get("task_id")
                if tid: tasks_with_sheets.add(int(tid))

for gr in AUDITS_DIR.glob("grounding_reviews_*.json"):
    try:
        with open(gr, "r", encoding="utf-8") as f:
            for k in json.load(f).keys():
                try: tasks_with_sheets.add(int(k))
                except Exception: pass
    except Exception:
        pass

unseen_ids = sorted(list(set(range(1, 10001)) - tasks_with_sheets))
print(f"Total unseen tasks: {len(unseen_ids)}")

all_map = {a["human_review"]["task_id"]: a for a in anns}
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
num_batches = (len(unseen_ids) + BATCH_SIZE - 1) // BATCH_SIZE

for b_idx in range(num_batches):
    chunk_ids = unseen_ids[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
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
    "total_remaining_tasks": len(unseen_ids),
    "batch_size": BATCH_SIZE,
    "sheet_chunk_size": 6,
    "num_batches": len(batches),
    "total_sheets": total_sheets,
    "batches": batches
}

out_plan = AUDITS_DIR / "remaining_visual_audit_plan_35_batches.json"
with open(out_plan, "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)

print(f"Successfully built plan: {len(batches)} batches, {total_sheets} total sheets.")
print(f"Saved plan to: {out_plan.name} ({out_plan.stat().st_size} bytes)")

# 打印各批次概要表格数据
print("\nBatch Summary:")
for b in batches:
    r = b["task_id_range"]
    print(f"Batch {b['batch_no']:02d}: Tasks {b['task_count']:3d} | Range: [{r[0]:5d} ~ {r[1]:5d}] | Sheets: {b['sheet_count']:2d} sheets")
