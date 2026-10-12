import json
from pathlib import Path

audit_path = Path("LS_lcad_reviewer/intermediate/audits/audit_needs_grounding_3501_4000.json")

with open(audit_path, "r", encoding="utf-8") as f:
    audits = json.load(f)

print(f"Total audit items: {len(audits)}")

perfect_count = sum(1 for a in audits if a.get("score", 0) >= 4.9)
print(f"Original >= 4.9 count in audits: {perfect_count}")

# reasons 统计
reason_counts = {}
for a in audits:
    for r in a.get("reasons", []):
        r_type = r.split("(")[0]
        reason_counts[r_type] = reason_counts.get(r_type, 0) + 1

print("Reasons breakdown:")
for r, c in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {r}: {c}")

# 查看分数分布
score_bins = {"<2.0": 0, "2.0-3.0": 0, "3.0-4.0": 0, "4.0-4.89": 0, ">=4.9": 0}
for a in audits:
    s = a.get("score", 0)
    if s < 2.0:
        score_bins["<2.0"] += 1
    elif s < 3.0:
        score_bins["2.0-3.0"] += 1
    elif s < 4.0:
        score_bins["3.0-4.0"] += 1
    elif s < 4.9:
        score_bins["4.0-4.89"] += 1
    else:
        score_bins[">=4.9"] += 1

print("Score bins:")
for b, c in score_bins.items():
    print(f"  {b}: {c}")
