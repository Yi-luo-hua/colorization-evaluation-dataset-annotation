import json

with open("intermediate/audits/audit_pass_3501_4000.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

print(f"Total pass tasks: {len(tasks)}")
for i, t in enumerate(tasks):
    sheet_idx = (i // 6) + 1
    pos = (i % 6) + 1
    if sheet_idx >= 7:
        defects = [d["name"] for d in t.get("defects", [])]
        print(f"Sheet {sheet_idx:02d} Pos {pos}: Task #{t['task_idx']} ({t['image_id']}) score={t['score']} susp={t.get('suspicion')} reasons={t.get('reasons')}")
