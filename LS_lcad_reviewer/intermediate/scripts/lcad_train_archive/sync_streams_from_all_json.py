#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_streams_from_all_json.py
将 exports/reviewed_1_10000_all.json（包含 100% 全量 Double Check 改判成果）
同步重建更新至全量 20 个 Label Studio 流式抽检包 (streams/tasks_lcad_{start}_{end}_stream.json)。
同时确保完全适配 interface_dual_v4.xml 模板中所需的 original_gpt_info 和 review_note_display 字段。
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"
TASKS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"
ALL_FILE = EXPORTS_DIR / "reviewed_1_10000_all.json"

TAXONOMY = ["A", "B", "C", "D", "E1", "E2", "F"]

def main():
    print(f"Loading authoritative all-data from: {ALL_FILE.name}...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)

    anns_by_tid = {}
    for ann in all_data["annotations"]:
        tid = ann["human_review"]["task_id"]
        anns_by_tid[tid] = ann
    print(f"Loaded {len(anns_by_tid)} annotations.")

    print(f"Loading raw tasks template from: {TASKS_FILE.name}...")
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        raw_tasks = json.load(f)
    print(f"Loaded {len(raw_tasks)} raw tasks.")

    STREAMS_DIR.mkdir(parents=True, exist_ok=True)

    batch_ranges = [(i, min(i + 499, 10000)) for i in range(1, 10001, 500)]
    print(f"Will generate {len(batch_ranges)} stream batches.")

    for start_id, end_id in batch_ranges:
        stream_tasks = []
        for tid in range(start_id, end_id + 1):
            raw_t = raw_tasks[tid - 1]
            raw_data = raw_t.get("data", {})
            ann = anns_by_tid[tid]

            defects = ann.get("defects", [])
            review_note = ann.get("review_note", "")
            if not review_note:
                review_note = "审查通过"

            # 确定 review_tag
            orig_rec = raw_data.get("original_record", {})
            orig_score = orig_rec.get("gpt_score", raw_data.get("gpt_score", 3.0))
            orig_defects = orig_rec.get("defects", raw_data.get("defects", []))

            # 区分 review_tag
            if len(defects) == 0 and review_note == "审查通过":
                review_tag = "初审核验通过"
            elif any(d.get("id") in ["A", "B", "C"] for d in defects) or "改判" in review_note or "追回" in review_note:
                review_tag = "洛熙视觉改判"
            else:
                review_tag = "洛熙物理修正"

            # 格式化 original_gpt_info
            if not orig_defects:
                orig_gpt_info = f"原始评分: {orig_score} 分 (无扣分缺陷)"
            else:
                lines = [f"原始评分: {orig_score} 分 | 原始检出 {len(orig_defects)} 项缺陷:"]
                for d in orig_defects:
                    d_id = d.get("id", "")
                    sev = d.get("severity", "")
                    name = d.get("name", "")
                    desc = d.get("description", "")
                    tag = f"[{d_id}-{sev}]" if sev else f"[{d_id}]"
                    lines.append(f"• {tag} {name}: {desc}")
                orig_gpt_info = "\n".join(lines)

            # 组装各缺陷项严重度与描述字典
            severities = {k: "无此缺陷" for k in TAXONOMY}
            severities["A"] = "未命中"
            descriptions = {k: "" for k in TAXONOMY}

            for d in defects:
                did = d.get("id")
                if did == "A":
                    severities["A"] = "命中"
                    descriptions["A"] = d.get("description", "")
                elif did in severities:
                    severities[did] = d.get("severity", "L1")
                    descriptions[did] = d.get("description", "")

            # 计算用于 rating 控件的兜底得分
            if severities["A"] == "命中":
                rating_score = 1.0
            elif not any(v in ["L1", "L2", "L3"] for v in severities.values()):
                rating_score = 5.0
            else:
                penalty = 0.0
                for code in ["B", "C", "D", "E1", "E2", "F"]:
                    v = severities[code]
                    if v.startswith("L"):
                        penalty += int(v[1]) * 0.45
                rating_score = max(1.5, round(5.0 - penalty, 1))

            # 组装 pred_result
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

            for cid in TAXONOMY:
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

            t_stream = {
                "id": tid,
                "data": {
                    **raw_data,
                    "review_tag": review_tag,
                    "review_status": "已核验",
                    "task_idx": tid,
                    "review_note": review_note,
                    "review_note_display": review_note,
                    "original_gpt_info": orig_gpt_info
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

        out_path = STREAMS_DIR / f"tasks_lcad_{start_id}_{end_id}_stream.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(stream_tasks, f, ensure_ascii=False, indent=2)

        print(f"Batch {start_id:5d}-{end_id:5d}: Exported {len(stream_tasks)} tasks -> {out_path.name}")

    print("\n[SUCCESS] All 20 stream batches successfully synced with Double Check results!")

if __name__ == "__main__":
    main()
