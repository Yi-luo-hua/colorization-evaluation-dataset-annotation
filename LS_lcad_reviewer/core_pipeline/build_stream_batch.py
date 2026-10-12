"""Universal Batch Stream Builder for Colorization Review (V4 Standard).
Transforms CV anomaly detection audits and AI visual grounded reviews into
standard Label Studio stream packages.
Supports multi-model (lcad, unicolor) and multi-split (train, val, test).
"""
import argparse
import json
import re
import sys
from pathlib import Path

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve().parent
    while curr != curr.parent:
        if (curr / "LS_lcad_reviewer").exists() and (curr / "9_14_10000GT_V1").exists():
            return curr
        curr = curr.parent
    return Path(r"d:\学业文件\MCL\上色评价_数据集标注")

WORKSPACE_ROOT = get_workspace_root()
INTERMEDIATE_AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
DEFAULT_STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"

TAXONOMY = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}


def resolve_tasks_file(model: str, split: str, workspace_root: Path):
    pool_dir = workspace_root / "LS_lcad_reviewer" / "tasks_pool" / split
    if split == "train":
        p = pool_dir / f"tasks_{model}_10000.json"
        if not p.exists():
            p = workspace_root / "LS_lcad_reviewer" / f"tasks_{model}_10000.json"
    elif split == "val":
        p = pool_dir / f"tasks_{model}_val_1428.json"
    elif split == "test":
        p = pool_dir / f"tasks_{model}_test_2857.json"
    else:
        raise ValueError(f"Unknown split: {split}")
    return p


def build_stream(
    start: int,
    end: int,
    model: str = "lcad",
    split: str = "train",
    grounding_file: Path = None,
    audit_file: Path = None,
    tasks_file: Path = None,
    out_file: Path = None
):
    if tasks_file is None:
        tasks_file = resolve_tasks_file(model, split, WORKSPACE_ROOT)
    if audit_file is None:
        audit_file = INTERMEDIATE_AUDITS_DIR / f"audit_{model}_{split}_{start}_{end}.json"
        if not audit_file.exists():
            # Fallback to legacy naming
            audit_file = INTERMEDIATE_AUDITS_DIR / f"audit_needs_grounding_{start}_{end}.json"
    if grounding_file is None:
        grounding_file = INTERMEDIATE_AUDITS_DIR / f"grounding_{model}_{split}_{start}_{end}.json"
        if not grounding_file.exists():
            grounding_file = INTERMEDIATE_AUDITS_DIR / f"grounding_reviews_{start}_{end}.json"
    if out_file is None:
        out_file = DEFAULT_STREAMS_DIR / f"tasks_{model}_{split}_{start}_{end}_stream.json"

    out_file.parent.mkdir(parents=True, exist_ok=True)

    if not tasks_file.exists():
        print(f"Error: Tasks file not found: {tasks_file}")
        sys.exit(1)

    with open(tasks_file, "r", encoding="utf-8") as f:
        all_tasks = json.load(f)

    batch_tasks = all_tasks[start - 1 : end]
    print(f"Loaded {len(batch_tasks)} tasks ({start} to {end}) from {tasks_file.name}")

    audit_map = {}
    if audit_file.exists():
        with open(audit_file, "r", encoding="utf-8") as f:
            audit_list = json.load(f)
            for a in audit_list:
                audit_map[a["task_idx"]] = a
        print(f"Loaded {len(audit_map)} audit alarm items from {audit_file.name}")
    else:
        print(f"Notice: Audit file {audit_file.name} not found. Proceeding without CV telemetry.")

    grounded_reviews = {}
    if grounding_file.exists():
        with open(grounding_file, "r", encoding="utf-8") as f:
            raw_grounding = json.load(f)
            grounded_reviews = {int(k): v for k, v in raw_grounding.items()}
        print(f"Loaded {len(grounded_reviews)} visual grounded reviews from {grounding_file.name}")
    else:
        print(f"Notice: Grounding file {grounding_file.name} not found.")

    stream_tasks = []

    for idx, task in enumerate(batch_tasks):
        task_idx = start + idx
        orig_data = task["data"]
        orig_rec = orig_data.get("original_record", {})
        gpt_score = orig_rec.get("gpt_score", 3.0)
        defects = orig_rec.get("defects", [])

        is_grounded = task_idx in grounded_reviews
        is_audited = task_idx in audit_map

        severities = {k: "无此缺陷" for k in ["B", "C", "D", "E1", "E2", "F"]}
        severities["A"] = "未命中"
        descriptions = {k: "" for k in ["A", "B", "C", "D", "E1", "E2", "F"]}
        final_score = None
        review_tag = "初审核验通过"
        review_note = "审查通过"

        if is_grounded:
            g_item = grounded_reviews[task_idx]
            final_score = g_item.get("score", gpt_score)
            review_note = g_item.get("note", "审查通过")

            g_sevs = g_item.get("severities", {})
            for k, v in g_sevs.items():
                severities[k] = v

            g_descs = g_item.get("descriptions", {})
            for k, v in g_descs.items():
                descriptions[k] = v

            has_any_defect = any(v in ["L1", "L2", "L3"] for v in severities.values()) or (severities.get("A") == "命中")
            review_tag = "大图视觉改判" if has_any_defect else "大图视觉放行"

        elif is_audited:
            review_tag = "CV辅助提示"
            a_item = audit_map[task_idx]
            metrics = a_item.get("metrics", {})
            reasons = a_item.get("reasons", [])

            # Adopt original defects as baseline
            for d in defects:
                d_id = d.get("id")
                if d_id == "A":
                    severities["A"] = "命中"
                    descriptions["A"] = d.get("description", "")
                elif d_id in severities:
                    severities[d_id] = d.get("severity", "L2")
                    descriptions[d_id] = d.get("description", "")

            note_parts = []
            if any("全局色偏显著" in r for r in reasons):
                bias_dir = metrics.get("bias_dir", "偏色")
                delta_c = metrics.get("delta_c_opp", 0.0)
                d_lvl = "L2" if delta_c > 0.20 else "L1"
                severities["D"] = d_lvl
                descriptions["D"] = f"全图受物理色度偏移影响，整体{bias_dir}。"
                note_parts.append(f"物理修正色偏({bias_dir} D-{d_lvl})")

            if any("边缘色差突变" in r for r in reasons):
                r_bleed = metrics.get("bleed_ratio", 1.0)
                b_lvl = "L2" if r_bleed > 2.0 else "L1"
                severities["B"] = b_lvl
                descriptions["B"] = "主体边界轮廓处颜色越界渗透至背景区域。"
                note_parts.append(f"边缘溢色补标(B-{b_lvl})")

            if any("常识错色" in r for r in reasons):
                severities["C"] = "L3"
                descriptions["C"] = "天空区域色彩违背视觉常理，呈现绿色异常色相。"
                note_parts.append("常识错色纠正(C-L3)")

            if any("疑似漏报过饱和" in r for r in reasons):
                severities["E1"] = "L2"
                descriptions["E1"] = "画面局部高光与关键色彩过度浓艳刺眼。"
                note_parts.append("饱和度偏高(E1-L2)")

            if any("疑似漏报缺色或严重欠饱和" in r for r in reasons):
                severities["E2"] = "L2"
                descriptions["E2"] = "画面色彩饱和度过低，主体褪色泛灰。"
                note_parts.append("欠饱和修正(E2-L2)")

            review_note = "；".join(note_parts) if note_parts else "物理指标自洽修正"

        else:
            # Retain original defects
            for d in defects:
                d_id = d.get("id")
                if d_id == "A":
                    severities["A"] = "命中"
                    descriptions["A"] = d.get("description", "")
                elif d_id in severities:
                    severities[d_id] = d.get("severity", "L2")
                    descriptions[d_id] = d.get("description", "")

        # 防错与熔断逻辑核验（E1与E2按物体标注，允许并存）
        if severities.get("A") == "命中":
            final_score = 1.0
            for k in ["B", "C", "D", "E1", "E2", "F"]:
                severities[k] = "无此缺陷"
                descriptions[k] = ""

        # 全图无瑕疵放行
        if not any(v in ["L1", "L2", "L3"] for v in severities.values()) and severities.get("A") != "命中":
            severities["A"] = "未命中"
            for k in ["B", "C", "D", "E1", "E2", "F"]:
                severities[k] = "无此缺陷"
                descriptions[k] = ""
            review_note = "审查通过"

        # Build prediction payload
        rating_score = final_score if final_score is not None else (1.0 if severities["A"] == "命中" else (gpt_score if gpt_score else 3.0))

        pred_results = [
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
                "value": {"text": [f"【{review_tag}】{review_note}"]}
            },
            {
                "from_name": "review_tag",
                "to_name": "colorized",
                "type": "choices",
                "value": {"choices": [review_tag]}
            },
            {
                "from_name": "reviewed_score",
                "to_name": "colorized",
                "type": "rating",
                "value": {"rating": max(1, min(5, round(rating_score)))}
            },
            {
                "from_name": "severity_A",
                "to_name": "colorized",
                "type": "choices",
                "value": {"choices": [severities["A"]]}
            }
        ]

        if severities["A"] == "命中" and descriptions["A"]:
            pred_results.append({
                "from_name": "description_A",
                "to_name": "colorized",
                "type": "textarea",
                "value": {"text": [descriptions["A"]]}
            })

        for cid in ["B", "C", "D", "E1", "E2", "F"]:
            pred_results.append({
                "from_name": f"severity_{cid}",
                "to_name": "colorized",
                "type": "choices",
                "value": {"choices": [severities[cid]]}
            })
            if severities[cid] in ["L1", "L2", "L3"] and descriptions[cid]:
                pred_results.append({
                    "from_name": f"description_{cid}",
                    "to_name": "colorized",
                    "type": "textarea",
                    "value": {"text": [descriptions[cid]]}
                })

        stream_task = {
            "data": orig_data,
            "predictions": [
                {
                    "model_version": "V4",
                    "result": pred_results
                }
            ]
        }
        stream_tasks.append(stream_task)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(stream_tasks, f, ensure_ascii=False, indent=2)

    print(f"\nSuccessfully generated stream package: {out_file.name} ({len(stream_tasks)} tasks)")
    return out_file


def main():
    ap = argparse.ArgumentParser(description="Universal Batch Stream Builder (V4 Standard)")
    ap.add_argument("--start", type=int, default=1, help="Start task index (1-based)")
    ap.add_argument("--end", type=int, default=500, help="End task index (1-based)")
    ap.add_argument("--model", default="lcad", choices=["lcad", "unicolor"], help="Target model")
    ap.add_argument("--split", default="train", choices=["train", "val", "test"], help="Dataset split")
    ap.add_argument("--grounding-file", default=None, help="Explicit path to visual grounding JSON")
    ap.add_argument("--audit-file", default=None, help="Explicit path to audit JSON")
    ap.add_argument("--tasks-file", default=None, help="Explicit path to source tasks JSON")
    ap.add_argument("--out-file", default=None, help="Output stream package JSON path")
    args = ap.parse_args()

    g_file = Path(args.grounding_file) if args.grounding_file else None
    a_file = Path(args.audit_file) if args.audit_file else None
    t_file = Path(args.tasks_file) if args.tasks_file else None
    o_file = Path(args.out_file) if args.out_file else None

    build_stream(
        start=args.start,
        end=args.end,
        model=args.model,
        split=args.split,
        grounding_file=g_file,
        audit_file=a_file,
        tasks_file=t_file,
        out_file=o_file
    )


if __name__ == "__main__":
    main()
