#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_latest_full_stream.py
将最新全量成果 reviewed_1_10000_all.json (涵盖所有历史改判与今日最新终审结果)
100% 精确同步生成全量 Label Studio 流式抽检包 tasks_lcad_1_10000_stream.json。
"""

import json
import shutil
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
TASKS_SRC = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"
REVIEWED_ALL = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"
OUT_STREAM = STREAMS_DIR / "tasks_lcad_1_10000_stream.json"

TAXONOMY = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}

def main():
    print(f"Loading task definitions from {TASKS_SRC}...")
    with open(TASKS_SRC, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    print(f"Loading reviewed records from {REVIEWED_ALL}...")
    with open(REVIEWED_ALL, "r", encoding="utf-8") as f:
        reviewed_data = json.load(f)
    annotations = reviewed_data["annotations"]

    if len(tasks) != len(annotations):
        raise ValueError(f"Length mismatch: tasks={len(tasks)}, annotations={len(annotations)}")

    # 备份现有流式包
    if OUT_STREAM.exists():
        backup_path = OUT_STREAM.with_suffix(".json.bak")
        shutil.copy2(OUT_STREAM, backup_path)
        print(f"Existing stream package backed up to {backup_path.name}")

    stream_tasks = []
    revised_count = 0
    passed_count = 0

    for idx, (t, ann) in enumerate(zip(tasks, annotations)):
        task_idx = idx + 1
        data = t.get("data", {})
        orig_rec = data.get("original_record", {})
        orig_score = orig_rec.get("gpt_score", data.get("gpt_score", 5.0))
        orig_defects = orig_rec.get("defects", data.get("defects", []))

        # 整理最新 defects
        defects = ann.get("defects", [])
        review_note = ann.get("review_note", "审查通过")

        severities = {k: "无此缺陷" for k in TAXONOMY}
        severities["A"] = "未命中"
        descriptions = {k: "" for k in TAXONOMY}

        for d in defects:
            did = d.get("id")
            if did in severities:
                severities[did] = d.get("severity", "L1") if did != "A" else "命中"
                descriptions[did] = d.get("description", "")

        # 判断是否属于改判
        # 1. 缺陷列表结构变化
        # 2. review_note 具有定物改判描述且非默认"审查通过"
        is_revised = False
        if review_note != "审查通过":
            is_revised = True
        elif len(defects) != len(orig_defects):
            is_revised = True
        else:
            orig_set = {(d.get("id"), d.get("severity", "")) for d in orig_defects}
            curr_set = {(d.get("id"), d.get("severity", "")) for d in defects}
            if orig_set != curr_set:
                is_revised = True

        if is_revised:
            review_tag = "洛熙视觉改判"
            revised_count += 1
        else:
            review_tag = "初审核验通过"
            passed_count += 1

        # 计算 rating score (供界面显示与筛选)
        if severities["A"] == "命中":
            rating_score = 1.0
        elif not any(v in ["L1", "L2", "L3"] for v in severities.values()):
            # 全图无缺陷
            rating_score = min(5.0, max(4.5, float(orig_score)))
        else:
            penalty = 0.0
            for code in ["B", "C", "D", "E1", "E2", "F"]:
                v = severities[code]
                if v.startswith("L"):
                    penalty += int(v[1]) * 0.45
            rating_score = max(1.5, round(5.0 - penalty, 1))

        # 构建 pred_result
        pred_result = [
            {
                "from_name": "review_status",
                "to_name": "colorized",
                "type": "choices",
                "value": {"choices": ["已核验"]}
            },
            {
                "from_name": "review_note",
                "to_name": "colorized",
                "type": "textarea",
                "value": {"text": [review_note]}
            },
            {
                "from_name": "score",
                "to_name": "colorized",
                "type": "rating",
                "value": {"rating": round(rating_score, 1)}
            }
        ]

        for cid in ["A", "B", "C", "D", "E1", "E2", "F"]:
            pred_result.append({
                "from_name": f"severity_{cid}",
                "to_name": "colorized",
                "type": "choices",
                "value": {"choices": [severities[cid]]}
            })
            if cid != "A" and severities[cid] != "无此缺陷" and descriptions[cid]:
                pred_result.append({
                    "from_name": f"description_{cid}",
                    "to_name": "colorized",
                    "type": "textarea",
                    "value": {"text": [descriptions[cid]]}
                })
            elif cid == "A" and severities["A"] == "命中" and descriptions["A"]:
                pred_result.append({
                    "from_name": "description_A",
                    "to_name": "colorized",
                    "type": "textarea",
                    "value": {"text": [descriptions["A"]]}
                })

        # 原始信息文本
        if not orig_defects:
            original_gpt_info = f"原始评分: {orig_score} 分 (无扣分缺陷)"
        else:
            orig_lines = [f"原始评分: {orig_score} 分 | 原始检出 {len(orig_defects)} 项缺陷:"]
            for d in orig_defects:
                d_id = d.get("id", "")
                sev = d.get("severity", "")
                name = d.get("name", "")
                desc = d.get("description", "")
                tag = f"[{d_id}-{sev}]" if sev else f"[{d_id}]"
                orig_lines.append(f"• {tag} {name}: {desc}")
            original_gpt_info = "\n".join(orig_lines)

        t_stream = {
            "id": t.get("id", task_idx),
            "data": {
                **data,
                "review_tag": review_tag,
                "review_status": "已核验",
                "task_idx": task_idx,
                "review_note": review_note,
                "review_note_display": review_note if review_note else "审查通过",
                "original_gpt_info": original_gpt_info
            },
            "annotations": [],
            "predictions": [
                {
                    "result": pred_result,
                    "score": round(rating_score, 1),
                    "model_version": "luoxi_v4_expert"
                }
            ]
        }
        stream_tasks.append(t_stream)

    print(f"Writing {len(stream_tasks)} tasks to {OUT_STREAM}...")
    with open(OUT_STREAM, "w", encoding="utf-8") as f:
        json.dump(stream_tasks, f, ensure_ascii=False, indent=2)

    print(f"Success! Full stream package updated:")
    print(f"Total tasks: {len(stream_tasks)}")
    print(f"Revised (洛熙视觉改判): {revised_count} ({revised_count/len(stream_tasks)*100:.2f}%)")
    print(f"Passed  (初审核验通过): {passed_count} ({passed_count/len(stream_tasks)*100:.2f}%)")

if __name__ == "__main__":
    main()
