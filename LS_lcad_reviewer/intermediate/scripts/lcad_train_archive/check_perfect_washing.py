import json
from pathlib import Path

export_path = Path("LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json")
with open(export_path, "r", encoding="utf-8") as f:
    data = json.load(f)

anns = data["annotations"]

orig_perfect_count = 0
unwashed_perfect = []
defects_stats = {}

for i, a in enumerate(anns):
    t_idx = 9501 + i
    orig_s = a.get("original_gpt_score", 0.0)
    defects = a.get("defects", [])
    
    for d in defects:
        did = d.get("id")
        defects_stats[did] = defects_stats.get(did, 0) + 1
        
    if orig_s >= 4.9:
        orig_perfect_count += 1
        if len(defects) == 0:
            unwashed_perfect.append((t_idx, a["image_id"], a.get("review_note")))

print(f"Total tasks: {len(anns)}")
print(f"Original perfect (>=4.9) count: {orig_perfect_count}")
print(f"Unwashed perfect count (defects == []): {len(unwashed_perfect)}")
print("Defects distribution across all 500 tasks:", defects_stats)
