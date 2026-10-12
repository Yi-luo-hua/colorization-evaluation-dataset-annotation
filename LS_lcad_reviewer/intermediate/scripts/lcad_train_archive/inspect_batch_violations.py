# -*- coding: utf-8 -*-
import json
import os
import sys

BASE_DIR = r"d:\学业文件\MCL\上色评价_数据集标注"
PLAN_PATH = os.path.join(BASE_DIR, "LS_lcad_reviewer", "intermediate", "audits", "remaining_visual_audit_plan_50_batches.json")
EXPORTS_PATH = os.path.join(BASE_DIR, "LS_lcad_reviewer", "exports", "reviewed_1_10000_all.json")

batch_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 6

with open(PLAN_PATH, "r", encoding="utf-8") as f:
    plan = json.load(f)

with open(EXPORTS_PATH, "r", encoding="utf-8") as f:
    export_data = json.load(f)

batch_data = plan["batches"][batch_idx - 1]
items = batch_data["items"]
export_map = {ann["human_review"]["task_id"]: ann for ann in export_data["annotations"]}

print(f"=== Inspecting Batch {batch_idx:02d} ({batch_data.get('batch_id', '')}, total {len(items)} tasks) ===")

violations = []
for i, it in enumerate(items):
    tid = it["task_id"]
    ann = export_map.get(tid)
    defs = ann.get("defects", [])
    orig = ann.get("original_gpt_score", 5.0)
    dc = it.get("metrics", {}).get("delta_c", 0.0)
    sheet_no = (i // 6) + 1
    slot_no = (i % 6) + 1
    
    if len(defs) == 0 and (orig < 4.0 or dc >= 0.08):
        violations.append({
            "sheet_no": sheet_no,
            "slot_no": slot_no,
            "tid": tid,
            "orig": orig,
            "dc": dc,
            "img": it.get("image_id"),
            "current_defects": it.get("current_defects", [])
        })

print(f"Batch {batch_idx:02d} total violations: {len(violations)}")
out_lines = []
for v in violations:
    defs_str = " | ".join([f"{d.get('id')}-{d.get('severity')}: {d.get('name')} ({d.get('description', '')})" for d in v["current_defects"]]) if v["current_defects"] else "None"
    line = f"Sheet {v['sheet_no']:02d} Slot {v['slot_no']} | Task #{v['tid']} (orig={v['orig']}, dc={v['dc']:.3f}, img={v['img']})\n   Orig Defs: {defs_str}"
    print(line)
    out_lines.append(line)

detail_file = os.path.join(BASE_DIR, "LS_lcad_reviewer", "intermediate", "audits", f"b{batch_idx:02d}_violations_detail.txt")
with open(detail_file, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))
print(f"Saved violation details to {detail_file}")
