import json
from collections import Counter

ALL_JSON = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer\exports\reviewed_1_10000_all.json"

with open(ALL_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

anns = data["annotations"]
total = len(anns)
zero_defect = 0
defect_counts = Counter()
defect_levels = Counter()
score_1_count = 0
pending_count = 0

for ann in anns:
    defs = ann.get("defects", [])
    if not defs:
        zero_defect += 1
    for d in defs:
        d_id = d.get("id")
        sev = d.get("severity")
        defect_counts[d_id] += 1
        defect_levels[f"{d_id}-{sev}"] += 1
    
    score = ann.get("reviewed_score")
    if score == 1.0:
        score_1_count += 1
    if ann.get("review_status") == "待审核":
        pending_count += 1

print(f"Total annotations: {total}")
print(f"Pending review count: {pending_count} (Must be 0)")
print(f"Defect-free (Zero Defect / Pass) count: {zero_defect}")
print(f"A-defect (Score 1.0 meltdown) count: {score_1_count}")
print(f"Defect ID counts: {dict(defect_counts)}")
print(f"Defect Level breakdown (top): {dict(defect_levels)}")
