#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
investigate_physical_revision_flaws.py
全面深度排查全量 10,000 条标注集中，受“纯物理修正/全局均摊漏检”影响的高危样本。
重点排查维度：
1. 原始打分低 (gpt_score < 3.5) 且原本有缺陷，但最终被清空成零缺陷放行 (defects: []) 的样本；
2. 原始打分极低 (gpt_score < 2.5)，但在最终审核中仅保留了 D-L1 轻度偏色，可能漏检局部错色/溢色；
3. 初筛存在局部色偏峰值 (max_local_peak >= 0.25) 但未被视觉定物，最终仅作泛偏色甚至放行的样本。
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
TASKS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"

def main():
    print("Loading data files...")
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
            "image_id": data.get("image_id", "")
        }

    # 汇总所有初筛 audit 中的 metrics（尤其是 max_local_peak）
    audit_metrics_map = {}
    for af in AUDITS_DIR.glob("audit_needs_grounding_*.json"):
        try:
            with open(af, "r", encoding="utf-8") as f:
                audit_list = json.load(f)
                for a in audit_list:
                    audit_metrics_map[a["task_idx"]] = a
        except Exception:
            pass
    print(f"Loaded audit telemetry for {len(audit_metrics_map)} items.")

    anns = all_data["annotations"]

    # 1. 维度一：原打分低且有缺陷，但最终被清空为 defects: []
    wiped_out_low_score = []
    
    # 2. 维度二：原打分极低 (score <= 2.5)，但最终仅修成单个 D-L1 (轻度偏色)
    under_penalized_d1 = []

    # 3. 维度三：初筛有局部色偏峰值 (peak >= 0.25)，但最终 review_note 只是全图偏色且无具象物体
    local_peak_flattened = []

    for ann in anns:
        tid = ann["human_review"]["task_id"]
        raw_info = raw_map[tid]
        raw_score = raw_info["score"]
        raw_defects = raw_info["defects"]
        
        final_defects = ann.get("defects", [])
        final_note = ann.get("review_note", "")
        
        final_defect_ids = [d["id"] for d in final_defects]
        
        # 检查维度一
        if len(final_defects) == 0 and raw_score < 3.5 and len(raw_defects) > 0:
            wiped_out_low_score.append({
                "task_id": tid,
                "image_id": ann["image_id"],
                "raw_score": raw_score,
                "raw_defects": raw_defects,
                "note": final_note
            })

        # 检查维度二
        if raw_score <= 2.5 and len(final_defects) == 1 and final_defect_ids == ["D"] and final_defects[0].get("severity") == "L1":
            under_penalized_d1.append({
                "task_id": tid,
                "image_id": ann["image_id"],
                "raw_score": raw_score,
                "raw_defects": raw_defects,
                "note": final_note
            })

        # 检查维度三
        if tid in audit_metrics_map:
            am = audit_metrics_map[tid]
            peak = am.get("metrics", {}).get("max_local_peak", 0.0)
            if peak >= 0.28:
                # 检查最终是否抓出了局部物体或错色
                has_c_or_b = any(did in ["B", "C"] for did in final_defect_ids)
                if not has_c_or_b and len(final_defects) <= 1:
                    local_peak_flattened.append({
                        "task_id": tid,
                        "image_id": ann["image_id"],
                        "peak": peak,
                        "raw_score": raw_score,
                        "final_defects": final_defect_ids,
                        "note": final_note
                    })

    print(f"\n==================== 排查结果统计 ====================")
    print(f"1. 原分 < 3.5 且原本有缺陷，最终被【彻底清空成零缺陷放行】的样本数: {len(wiped_out_low_score)}")
    print(f"2. 原分 <= 2.5 (极低分)，最终被【降级仅标记单个 D-L1 轻度偏色】的样本数: {len(under_penalized_d1)}")
    print(f"3. 局部色偏峰值 >= 0.28，但未捕获局部错色/溢色，仅归为泛偏色/放行的样本数: {len(local_peak_flattened)}")

    # 抽样打印维度一
    print("\n--- 维度一样本示例 (像 Task 1 一样被抹空的): ---")
    for item in wiped_out_low_score[:10]:
        d_str = "、".join([f"{d.get('id')}-{d.get('severity','')}" for d in item['raw_defects']])
        print(f"  Task #{item['task_id']} | File: {item['image_id']} | 原分: {item['raw_score']} | 原缺陷: [{d_str}]")

    # 抽样打印维度二
    print("\n--- 维度二样本示例 (极低分仅标 D-L1 的): ---")
    for item in under_penalized_d1[:10]:
        d_str = "、".join([f"{d.get('id')}-{d.get('severity','')}" for d in item['raw_defects']])
        print(f"  Task #{item['task_id']} | File: {item['image_id']} | 原分: {item['raw_score']} | 原缺陷: [{d_str}] | 最终评语: {item['note']}")

    # 抽样打印维度三
    print("\n--- 维度三样本示例 (局部峰值偏色但未抓出具体物体的): ---")
    for item in local_peak_flattened[:10]:
        print(f"  Task #{item['task_id']} | File: {item['image_id']} | 峰值: {item['peak']:.2f} | 最终缺陷: {item['final_defects']} | 最终评语: {item['note']}")

if __name__ == "__main__":
    main()
