"""Extract all 112 self-consistent pass tasks + 6 zero-defect safe pass tasks from batch 4001-4500 (total 118 tasks) for double check.
"""
import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
TASKS_10000_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"
STREAM_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams" / "tasks_lcad_4001_4500_stream.json"
REVIEWED_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_4001_4500_20260930_135528.json"
OUT_PASS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_4001_4500.json"

def main():
    with open(STREAM_FILE, "r", encoding="utf-8") as f:
        stream_tasks = json.load(f)

    with open(REVIEWED_FILE, "r", encoding="utf-8") as f:
        reviewed_data = json.load(f)

    reviewed_map = {a["human_review"]["task_id"]: a for a in reviewed_data["annotations"]}

    # Identify the pass items
    tag_counts = {}
    for t in stream_tasks:
        tg = t["data"].get("review_tag")
        tag_counts[tg] = tag_counts.get(tg, 0) + 1
    
    pass_tag = [k for k, v in tag_counts.items() if v == 112][0]
    print(f"Identified pass_tag in stream: {repr(pass_tag)} (count={tag_counts[pass_tag]})")

    zero_defect_task_ids = {4103, 4162, 4188, 4191, 4307, 4410}

    pass_items = []
    for t in stream_tasks:
        data = t["data"]
        t_idx = data["task_idx"]
        is_pass_tag = (data.get("review_tag") == pass_tag)
        is_zero_defect = (t_idx in zero_defect_task_ids)

        if is_pass_tag or is_zero_defect:
            rev = reviewed_map.get(t_idx, {})
            orig_rec = data.get("original_record", {})
            orig_score = orig_rec.get("gpt_score", 0.0)
            orig_defects = orig_rec.get("defects", [])
            img_id = data.get("image_id")
            basename = Path(img_id).stem

            if is_zero_defect:
                susp = 20.0
                reason = "零缺陷满分验真直审核验"
            elif orig_score >= 4.0:
                susp = 10.0
                reason = "高分均摊疑似重点核验"
            else:
                susp = 0.0
                reason = "物理指标自洽保留(二次像素级复核)"

            pass_items.append({
                "task_idx": t_idx,
                "image_id": img_id,
                "basename": basename,
                "score": orig_score,
                "suspicion": susp,
                "reasons": [reason],
                "defects": rev.get("defects", []),
                "orig_defects": orig_defects,
                "is_zero_defect": is_zero_defect,
                "review_note": rev.get("review_note", "")
            })

    # Sort: zero-defect (20.0) first, then high-score (10.0), then normal self-consistent
    pass_items.sort(key=lambda x: (x["suspicion"], x["score"]), reverse=True)

    OUT_PASS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PASS_FILE, "w", encoding="utf-8") as f:
        json.dump(pass_items, f, ensure_ascii=False, indent=2)

    print(f"Total pass tasks extracted: {len(pass_items)}")
    print(f"Zero defect pass count: {sum(1 for x in pass_items if x['is_zero_defect'])}")
    print(f"High score (>=4.0) pass count: {sum(1 for x in pass_items if x['score'] >= 4.0 and not x['is_zero_defect'])}")
    print(f"Standard self-consistent pass count: {sum(1 for x in pass_items if x['suspicion'] == 0.0)}")
    print(f"Saved to: {OUT_PASS_FILE}")

if __name__ == "__main__":
    main()
