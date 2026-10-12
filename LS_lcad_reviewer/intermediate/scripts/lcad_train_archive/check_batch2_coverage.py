# -*- coding: utf-8 -*-
import json
from pathlib import Path

diff_p = Path(r"LS_lcad_reviewer/intermediate/audits/suspect_detailed_cv_diff.json")
plan_p = Path(r"LS_lcad_reviewer/intermediate/audits/suspect_pass_revisions_plan.json")

with open(diff_p, "r", encoding="utf-8") as f:
    diff_data = json.load(f)

with open(plan_p, "r", encoding="utf-8") as f:
    plan_data = json.load(f)

# Filter tasks for sheets 21 to 40
sheet_names = [f"sheet_{i:02d}.jpg" for i in range(21, 41)]
batch2_tasks = [t for t in diff_data if t["sheet"] in sheet_names]

print(f"Total tasks in Batch 2 (sheets 21..40): {len(batch2_tasks)}")
print(f"Sheet names: {sheet_names[0]} to {sheet_names[-1]}")
print(f"Task ID range: {batch2_tasks[0]['task_id']} to {batch2_tasks[-1]['task_id']}")

# Check how many are currently in plan_data['revisions'] or 'genuine_passes'
revisions = plan_data.get("revisions", {})
genuine_passes = set(plan_data.get("genuine_passes", []))

in_rev = sum(1 for t in batch2_tasks if str(t["task_id"]) in revisions)
in_pass = sum(1 for t in batch2_tasks if t["task_id"] in genuine_passes)
print(f"In revisions: {in_rev}, In genuine_passes: {in_pass}")
