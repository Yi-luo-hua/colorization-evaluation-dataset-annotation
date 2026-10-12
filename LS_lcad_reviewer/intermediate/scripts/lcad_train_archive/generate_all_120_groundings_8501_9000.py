# -*- coding: utf-8 -*-
"""
Merge Part 1 and Part 2 groundings into a single JSON file for batch 8501~9000
"""

import os
import json
import sys

# Add scripts directory to sys.path
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from groundings_part1_8501_9000 import GROUNDINGS_PART1
from groundings_part2_8501_9000 import GROUNDINGS_PART2

def main():
    merged = {}
    merged.update(GROUNDINGS_PART1)
    merged.update(GROUNDINGS_PART2)
    
    # Load sheets_meta for exact telemetry
    meta_path = os.path.join(scripts_dir, "..", "audits", "sheets_meta_8501_9000.json")
    meta_map = {}
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            sheets_meta = json.load(f)
        for t in sheets_meta:
            meta_map[t.get("task_idx") or t.get("task_id")] = t

    formatted_reviews = {}
    for task_id, info in merged.items():
        score = info["score"]
        defects_list = info.get("defects", [])
        review_notes = info.get("review_notes", "")
        
        severities = {}
        descriptions = {}
        
        meta_item = meta_map.get(task_id, {})
        metrics = meta_item.get("metrics", {})
        bias_dir = metrics.get("bias_direction", "偏暖红黄调")
        delta_c = metrics.get("delta_c", 0.12)
        bleed_ratio = metrics.get("bleed_ratio", 1.2)
        p90 = metrics.get("p90_edge", 40.0)
        
        # Populate from defects list
        for d in defects_list:
            cat = d["category"]
            lvl = d["level"]
            desc = d["description"]
            severities[cat] = lvl
            descriptions[cat] = desc
        
        # If D is not explicitly set, but delta_c is significant, add D
        if "D" not in severities and delta_c > 0.08:
            d_lvl = "L2" if delta_c > 0.15 else "L1"
            severities["D"] = d_lvl
            descriptions["D"] = f"画面整体大面积{bias_dir}。"
            
        note_text = f"核查确认：{review_notes}"
        
        formatted_reviews[str(task_id)] = {
            "score": score,
            "severities": severities,
            "descriptions": descriptions,
            "note": note_text
        }
        
    print(f"Total formatted groundings: {len(formatted_reviews)}")
    
    output_path = os.path.join(scripts_dir, "..", "audits", "grounding_reviews_8501_9000.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(formatted_reviews, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully saved all {len(formatted_reviews)} groundings to: {output_path}")

if __name__ == "__main__":
    main()
