import json
from pathlib import Path

EXPORTS_DIR = Path("exports")
STREAMS_DIR = Path("streams")
AUDITS_DIR = Path("intermediate/audits")

batch_export = EXPORTS_DIR / "reviewed_4501_5000_20260930_140753.json"
stream_file = STREAMS_DIR / "tasks_lcad_4501_5000_stream.json"

with open(batch_export, "r", encoding="utf-8") as f:
    export_data = json.load(f)

with open(stream_file, "r", encoding="utf-8") as f:
    stream_data = json.load(f)

stream_map = {t["id"]: t for t in stream_data}

pass_tasks = []
for i, ann in enumerate(export_data["annotations"]):
    tid = 4501 + i
    st = stream_map.get(tid, {})
    tag = st.get("data", {}).get("review_tag", "")
    note = ann.get("review_note", "")
    # 只要不是 物理修正 且 不是 视觉改判，就是这 99 个保留样本
    if "物理" not in tag and "视觉" not in tag:
        pass_tasks.append({
            "task_idx": tid,
            "image_id": ann["image_id"],
            "basename": Path(ann["file_path"]).name,
            "score": ann["gpt_score"],
            "defects": ann["defects"],
            "review_note": note,
            "review_tag": tag
        })

print(f"Extracted {len(pass_tasks)} pass tasks for 4501-5000.")
out_path = AUDITS_DIR / "audit_pass_4501_5000.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(pass_tasks, f, ensure_ascii=False, indent=2)

print(f"Saved to {out_path}")
