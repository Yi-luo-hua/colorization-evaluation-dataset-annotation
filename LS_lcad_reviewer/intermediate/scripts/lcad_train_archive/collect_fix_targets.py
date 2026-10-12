#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
collect_fix_targets.py
精确提取所有受早期物理修正缺陷影响的高危任务清单：
1. 原打分 < 3.5 且原本有缺陷，但最终被误清空为 defects: [] 的样本；
2. 原打分 <= 2.5 且最终仅被降级标记为单个 D-L1 轻度偏色的样本。
去重并按批次分组保存，为后续分批生成大图看板视觉细致核验做准备。
"""

import json
from pathlib import Path
from collections import defaultdict

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
TASKS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
OUT_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "deep_fix_targets_all.json"

def main():
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        raw_tasks = json.load(f)
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    raw_map = {}
    for t in raw_tasks:
        tid = t.get("id") or (len(raw_map) + 1)
        data = t.get("data", {})
        orig_rec = data.get("original_record", {})
        raw_map[tid] = {
            "score": orig_rec.get("gpt_score", data.get("gpt_score", 3.0)),
            "defects": orig_rec.get("defects", data.get("defects", [])),
            "image_id": data.get("image_id", ""),
            "original_record": orig_rec
        }

    anns = all_data["annotations"]
    targets = []
    seen_tids = set()

    for ann in anns:
        tid = ann["human_review"]["task_id"]
        raw_info = raw_map[tid]
        raw_score = raw_info["score"]
        raw_defects = raw_info["defects"]
        
        final_defects = ann.get("defects", [])
        final_defect_ids = [d["id"] for d in final_defects]
        final_note = ann.get("review_note", "")

        is_wiped = (len(final_defects) == 0 and raw_score < 3.5 and len(raw_defects) > 0)
        is_under_d1 = (raw_score <= 2.5 and len(final_defects) == 1 and final_defect_ids == ["D"] and final_defects[0].get("severity") == "L1")

        if is_wiped or is_under_d1:
            reason = "误清空为零缺陷" if is_wiped else "极低分被降级为单一D-L1"
            targets.append({
                "task_id": tid,
                "image_id": ann["image_id"],
                "raw_score": raw_score,
                "raw_defects": raw_defects,
                "current_final_defects": final_defects,
                "current_final_note": final_note,
                "fix_reason": reason,
                "batch_id": (tid - 1) // 500 + 1
            })
            seen_tids.add(tid)

    targets.sort(key=lambda x: x["task_id"])
    print(f"Total deduplicated targets to fix: {len(targets)}")

    batch_groups = defaultdict(list)
    for t in targets:
        batch_groups[t["batch_id"]].append(t)

    print("\nBatch Breakdown:")
    for b in sorted(batch_groups.keys()):
        start = (b - 1) * 500 + 1
        end = b * 500
        wiped_c = sum(1 for x in batch_groups[b] if x["fix_reason"] == "误清空为零缺陷")
        under_c = sum(1 for x in batch_groups[b] if x["fix_reason"] == "极低分被降级为单一D-L1")
        print(f"  Batch {b:2d} ({start:5d}-{end:5d}): Total {len(batch_groups[b]):2d} items (误清空: {wiped_c}, 降级D-L1: {under_c})")

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(targets, f, ensure_ascii=False, indent=2)
    print(f"\nSaved target list to: {OUT_FILE}")

if __name__ == "__main__":
    main()
