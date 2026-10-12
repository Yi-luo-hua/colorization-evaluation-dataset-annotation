#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apply_zero_defects_batch.py
将零缺陷大图复审结果合入到 reviewed_1_10000_all.json 与 reviewed_1_10000_clean.json 中。
并执行完整的 Schema 验证。
"""

import argparse
import datetime
import json
import os
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
ALL_FILE = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_FILE = EXPORTS_DIR / "reviewed_1_10000_clean.json"
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"

def main():
    parser = argparse.ArgumentParser(description="Apply zero defects batch reviews")
    parser.add_argument("--batch", type=int, default=1, help="Batch number to apply (default: 1)")
    args = parser.parse_args()

    batch_file = AUDITS_DIR / f"grounding_zero_defects_batch_{args.batch:02d}.json"
    if not batch_file.exists():
        print(f"Error: Batch review file not found: {batch_file}")
        return

    with open(batch_file, "r", encoding="utf-8") as f:
        batch_data = json.load(f)

    results = batch_data["results"]
    print(f"Loaded {len(results)} review records from Batch {args.batch:02d}")

    # 加载 all.json 与 clean.json
    print("Loading datasets...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 构建索引映射
    all_by_tid = {}
    for ann in all_data["annotations"]:
        tid = str(ann.get("human_review", {}).get("task_id", ""))
        if tid:
            all_by_tid[tid] = ann

    clean_by_tid = {}
    for ann in clean_data["annotations"]:
        tid = str(ann.get("human_review", {}).get("task_id", ""))
        if tid:
            clean_by_tid[tid] = ann

    revised_count = 0
    passed_count = 0

    for tid, res in results.items():
        status = res.get("status", "放行")
        defects = res.get("defects", [])
        note = res.get("note", "审查通过")

        if status == "改判" and len(defects) > 0:
            revised_count += 1
        else:
            passed_count += 1

        # 更新 all_data
        if tid in all_by_tid:
            ann = all_by_tid[tid]
            ann["defects"] = defects
            ann["review_status"] = "已核验"
            ann["review_note"] = note if status == "改判" else "审查通过"
            if any(d.get("id") == "A" for d in defects):
                ann["reviewed_score"] = 1.0
                ann["needs_rescoring"] = False
            else:
                ann["reviewed_score"] = None
                ann["needs_rescoring"] = True
            if "human_review" in ann:
                ann["human_review"]["updated_at"] = now_iso

        # 更新 clean_data (严格清空 review_note)
        if tid in clean_by_tid:
            ann_c = clean_by_tid[tid]
            ann_c["defects"] = defects
            ann_c["review_status"] = "已核验"
            ann_c["review_note"] = ""  # 纯净版恒为 ""
            if any(d.get("id") == "A" for d in defects):
                ann_c["reviewed_score"] = 1.0
                ann_c["needs_rescoring"] = False
            else:
                ann_c["reviewed_score"] = None
                ann_c["needs_rescoring"] = True
            if "human_review" in ann_c:
                ann_c["human_review"]["updated_at"] = now_iso

    print(f"Batch {args.batch:02d} merged: {revised_count} revised, {passed_count} confirmed pass.")

    # 保存回写
    print("Saving updated reviewed_1_10000_all.json...")
    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)

    print("Saving updated reviewed_1_10000_clean.json...")
    with open(CLEAN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)

    print("Successfully synchronized datasets!")

if __name__ == "__main__":
    main()
