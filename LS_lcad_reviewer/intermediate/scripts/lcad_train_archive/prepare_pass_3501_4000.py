"""Extract all 101 self-consistent pass tasks from batch 3501-4000 for double check.
"""
import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
STREAM_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams" / "tasks_lcad_3501_4000_stream.json"
REVIEWED_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_3501_4000_20260930_121202.json"
OUT_PASS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_3501_4000.json"

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
    
    pass_tag = [k for k, v in tag_counts.items() if v == 101][0]
    print(f"Identified pass_tag in stream: {repr(pass_tag)} (count={tag_counts[pass_tag]})")

    pass_items = []
    for t in stream_tasks:
        data = t["data"]
        t_idx = data["task_idx"]
        if data.get("review_tag") == pass_tag:
            rev = reviewed_map.get(t_idx, {})
            orig_rec = data.get("original_record", {})
            orig_score = orig_rec.get("gpt_score", 0.0)
            orig_defects = orig_rec.get("defects", [])
            img_id = data.get("image_id")
            basename = Path(img_id).stem

            if orig_score >= 4.0:
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
                "review_note": rev.get("review_note", "")
            })

    # Sort: high-score first
    pass_items.sort(key=lambda x: (x["suspicion"], x["score"]), reverse=True)

    OUT_PASS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PASS_FILE, "w", encoding="utf-8") as f:
        json.dump(pass_items, f, ensure_ascii=False, indent=2)

    print(f"Total pass tasks extracted: {len(pass_items)}")
    print(f"High score (>=4.0) pass count: {sum(1 for x in pass_items if x['score'] >= 4.0)}")
    print(f"Standard self-consistent pass count: {sum(1 for x in pass_items if x['suspicion'] == 0.0)}")
    print(f"Saved to: {OUT_PASS_FILE}")

if __name__ == "__main__":
    main()
