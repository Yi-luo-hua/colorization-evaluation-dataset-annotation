import json
from pathlib import Path

export_path = Path("LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json")
with open(export_path, "r", encoding="utf-8") as f:
    data = json.load(f)

anns = data["annotations"]

# Count bias directions in D
bias_dirs = {"偏暖红黄调": 0, "偏冷青蓝调": 0, "偏洋红紫调": 0, "偏草绿黄调": 0, "其他": 0}
for a in anns:
    for d in a.get("defects", []):
        if d.get("id") == "D":
            desc = d.get("description", "")
            matched = False
            for k in ["偏暖红黄调", "偏冷青蓝调", "偏洋红紫调", "偏草绿黄调"]:
                if k in desc:
                    bias_dirs[k] += 1
                    matched = True
                    break
            if not matched:
                bias_dirs["其他"] += 1

print("Bias directions in D:", bias_dirs)

# Count defect categories
cats = {}
for a in anns:
    for d in a.get("defects", []):
        cid = d.get("id")
        cats[cid] = cats.get(cid, 0) + 1
print("Defect categories:", cats)

# Count severities
sevs = {}
for a in anns:
    for d in a.get("defects", []):
        sev = d.get("severity")
        sevs[sev] = sevs.get(sev, 0) + 1
print("Severities:", sevs)

# Grounded review notes count
grounded_count = 0
for a in anns:
    note = a.get("review_note", "")
    if "核查确认" in note:
        grounded_count += 1
print(f"Grounded reviews count (visual verified): {grounded_count}")
