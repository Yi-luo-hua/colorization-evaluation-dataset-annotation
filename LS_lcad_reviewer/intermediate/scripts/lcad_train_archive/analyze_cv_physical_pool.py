import json
from pathlib import Path
from collections import Counter

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"

with open(ALL_FILE, "r", encoding="utf-8") as f:
    all_anns = json.load(f)["annotations"]

all_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}

physical_items = []
seen_ids = set()

for sf in sorted(STREAMS_DIR.glob("tasks_lcad_*_*_stream.json")):
    if "1_10000" in sf.name:
        continue
    with open(sf, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    for t in tasks:
        tag = t.get("data", {}).get("review_tag", "")
        if tag == "洛熙物理修正" or "物理修正" in tag:
            tid = t.get("id")
            if tid not in seen_ids and tid in all_map:
                seen_ids.add(tid)
                ann = all_map[tid]
                physical_items.append({
                    "task_id": tid,
                    "image_id": ann["image_id"],
                    "defects": ann.get("defects", []),
                    "review_note": ann.get("review_note", ""),
                    "original_gpt_score": ann.get("original_gpt_score", ann.get("gpt_score")),
                    "file_path": ann.get("file_path", "")
                })

print(f"Total unique CV physical direct items: {len(physical_items)}")

defect_combos = Counter()
score_dist = Counter()

for item in physical_items:
    defs = item["defects"]
    combo = "+".join(sorted([f"{d['id']}-{d.get('severity','')}" for d in defs])) if defs else "EMPTY"
    defect_combos[combo] += 1
    
    score = item["original_gpt_score"]
    try:
        s_float = float(score)
        if s_float >= 4.9:
            score_dist["5.0满分"] += 1
        elif s_float >= 4.0:
            score_dist["4.0-4.8高分"] += 1
        elif s_float >= 3.0:
            score_dist["3.0-3.9中分"] += 1
        else:
            score_dist["<3.0低分"] += 1
    except Exception:
        pass

print("\n--- 原打分分布 ---")
for k, v in score_dist.items():
    print(f"  {k}: {v} ({v/len(physical_items)*100:.1f}%)")

print("\n--- 常见缺陷组合分布 (Top 15) ---")
for k, v in defect_combos.most_common(15):
    print(f"  {k}: {v} ({v/len(physical_items)*100:.1f}%)")

# 保存为总候选池
pool_file = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "cv_physical_pool_all.json"
with open(pool_file, "w", encoding="utf-8") as f:
    json.dump(physical_items, f, ensure_ascii=False, indent=2)
print(f"\nSaved pool to: {pool_file.name}")
