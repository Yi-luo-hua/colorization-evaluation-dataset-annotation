import json

with open("LS_lcad_reviewer/intermediate/audits/cv_physical_audit_plan.json", "r", encoding="utf-8") as f:
    plan = json.load(f)
with open("LS_lcad_reviewer/exports/reviewed_1_10000_all.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

all_map = {ann["human_review"]["task_id"]: ann for ann in all_data["annotations"]}

r1 = plan["items"][:120]
for idx, item in enumerate(r1):
    tid = item["task_id"]
    ann = all_map[tid]
    defs = ann.get("defects", [])
    note = ann.get("review_note", "")
    def_str = "+".join([f"{d.get('id')}-{d.get('severity')}" for d in defs])
    print(f"#{idx+1:03d} (Sheet {idx//6+1:02d}-{idx%6+1}): Task {tid} -> defs: {def_str} | note: {note[:60]}")
