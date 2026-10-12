import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PLAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "cv_physical_audit_plan.json"

with open(PLAN_FILE, "r", encoding="utf-8") as f:
    plan = json.load(f)

items = plan["items"][360:517]
print(f"Total round 4 items: {len(items)}")

for idx, it in enumerate(items[120:], 120):
    tid = it["task_id"]
    iid = it["image_id"]
    orig_s = it["original_gpt_score"]
    defs = [d["id"] for d in it["current_defects"]]
    print(f"[{idx+1:03d}] Sheet {(idx//6)+1:02d} - Task #{tid} ({iid}) - Orig: {orig_s}, Defs: {defs}")
