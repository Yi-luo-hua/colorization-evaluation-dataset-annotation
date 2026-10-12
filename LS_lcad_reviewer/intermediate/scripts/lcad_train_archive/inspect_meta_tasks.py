import json
from pathlib import Path

WORKSPACE_ROOT = Path("d:/学业文件/MCL/上色评价_数据集标注")
TASKS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"
META_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "sheets_meta_4001_4500.json"

with open(TASKS_FILE, "r", encoding="utf-8") as f:
    all_tasks = json.load(f)

with open(META_FILE, "r", encoding="utf-8") as f:
    meta_list = json.load(f)

tasks_map = {t["data"]["image_id"]: t for t in all_tasks[4000:4500]}

print(f"Meta items: {len(meta_list)}")
for i, m in enumerate(meta_list[:15]):
    t = tasks_map.get(m["image_id"])
    orig = t["data"].get("original_record", {})
    defects = orig.get("defects", [])
    print(f"[{i+1}] Task {m['task_idx']} | Score {m['score']} | Susp {m['suspicion']}")
    for d in defects:
        print(f"    - {d.get('id')} ({d.get('severity')}): {d.get('description')}")
