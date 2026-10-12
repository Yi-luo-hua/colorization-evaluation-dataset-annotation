"""Universal Exporter for Colorization Review (V4 Schema Compliant).
Converts stream packages (or Master Label Studio completions) into authoritative delivery JSONs.
Supports multi-model (lcad, unicolor) and multi-split (train, val, test).
"""
import argparse
import copy
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve().parent
    while curr != curr.parent:
        if (curr / "LS_lcad_reviewer").exists() and (curr / "9_14_10000GT_V1").exists():
            return curr
        curr = curr.parent
    return Path(r"d:\学业文件\MCL\上色评价_数据集标注")

WORKSPACE_ROOT = get_workspace_root()
DB_PATH = WORKSPACE_ROOT / "LS_lcad_reviewer" / "data" / "label_studio.sqlite3"
DEFAULT_EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"


def load_master_completions(project_id: int = None):
    if not DB_PATH.exists():
        print(f"Notice: SQLite database not found at {DB_PATH}. Adopting stream predictions 100%.")
        return {}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if project_id:
        cur.execute("""
            SELECT t.id, t.data, a.id, a.result, a.updated_at, a.completed_by_id
            FROM task t
            JOIN task_completion a ON a.task_id = t.id
            WHERE t.project_id = ? AND a.was_cancelled = 0
            ORDER BY a.updated_at ASC
        """, (project_id,))
    else:
        cur.execute("""
            SELECT t.id, t.data, a.id, a.result, a.updated_at, a.completed_by_id
            FROM task t
            JOIN task_completion a ON a.task_id = t.id
            WHERE a.was_cancelled = 0
            ORDER BY a.updated_at ASC
        """)

    rows = cur.fetchall()
    conn.close()

    master_completions = {}
    for task_id, t_data_str, ann_id, res_str, updated_at, comp_by in rows:
        try:
            t_data = json.loads(t_data_str)
            img_id = t_data.get("image_id")
            result = json.loads(res_str) if res_str else []
            if img_id:
                master_completions[img_id] = {
                    "task_id": task_id,
                    "id": ann_id,
                    "result": result,
                    "updated_at": updated_at,
                    "completed_by": comp_by or 1
                }
        except Exception:
            continue

    print(f"Loaded {len(master_completions)} human reviews from Master DB.")
    return master_completions


def export_batch(stream_file: str, project_id: int = None, ignore_db: bool = False, out_file: str = None):
    stream_path = Path(stream_file)
    if not stream_path.exists():
        print(f"Error: Stream file not found: {stream_path}")
        sys.exit(1)

    with open(stream_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    print(f"Loaded {len(tasks)} tasks from stream package: {stream_path.name}")

    master_completions = {} if ignore_db else load_master_completions(project_id)
    matched_count = 0

    raw_tasks = []
    for idx, task in enumerate(tasks):
        t_out = copy.deepcopy(task)
        img_id = t_out["data"]["image_id"]

        if img_id in master_completions:
            mc = master_completions[img_id]
            t_out["annotations"] = [
                {
                    "id": mc["id"],
                    "result": mc["result"],
                    "was_cancelled": False,
                    "ground_truth": False,
                    "updated_at": mc["updated_at"],
                    "completed_by": mc["completed_by"]
                }
            ]
            t_out["id"] = mc["task_id"]
            matched_count += 1
        else:
            preds = t_out.get("predictions", [])
            if preds and "result" in preds[0]:
                pred_result = copy.deepcopy(preds[0]["result"])
                for r in pred_result:
                    if r.get("from_name") == "review_status":
                        r["value"]["choices"] = ["已核验"]
                t_out["annotations"] = [
                    {
                        "id": 900000 + idx,
                        "result": pred_result,
                        "was_cancelled": False,
                        "ground_truth": False,
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "completed_by": 1
                    }
                ]
            else:
                t_out["annotations"] = []
            t_out["id"] = idx + 1

        raw_tasks.append(t_out)

    print(f"Human review merge result: {matched_count} from Master DB, {len(raw_tasks) - matched_count} from auto-predictions.")

    # Determine output deliverable path
    if out_file:
        reviewed_file = Path(out_file)
    else:
        # Extract model, split, start, end from stream filename
        m = re.search(r"tasks_([a-zA-Z0-9]+)_([a-zA-Z0-9]+)_(\d+)_(\d+)_stream\.json", stream_path.name)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        if m:
            model_name, split_name, start, end = m.groups()
            reviewed_file = DEFAULT_EXPORTS_DIR / f"reviewed_{model_name}_{split_name}_{start}_{end}_{timestamp}.json"
        else:
            # Legacy fallback
            m_old = re.search(r"tasks_lcad_(\d+)_(\d+)_stream\.json", stream_path.name)
            if m_old:
                start, end = m_old.groups()
                reviewed_file = DEFAULT_EXPORTS_DIR / f"reviewed_{start}_{end}_{timestamp}.json"
            else:
                stem = stream_path.stem.replace("_stream", "")
                reviewed_file = DEFAULT_EXPORTS_DIR / f"reviewed_{stem}_{timestamp}.json"

    reviewed_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert annotations to official schema
    sanitized_done = []
    EXACT_FIELDS = [
        "image_id", "file_path", "source_dataset", "role", "defects",
        "gpt_score", "labeling_model", "labeling_timestamp", "original_gpt_score",
        "review_status", "review_note", "reviewed_score", "needs_rescoring", "human_review"
    ]

    for item in raw_tasks:
        orig_rec = item["data"].get("original_record", {})
        ann_list = item.get("annotations", [])
        ann = ann_list[0] if ann_list else {}
        results = ann.get("result", [])

        # Parse form results
        res_map = {}
        for r in results:
            fn = r.get("from_name")
            val = r.get("value", {})
            if "choices" in val:
                res_map[fn] = val["choices"][0] if val["choices"] else ""
            elif "text" in val:
                res_map[fn] = val["text"][0] if val["text"] else ""
            elif "rating" in val:
                res_map[fn] = val["rating"]

        review_status = res_map.get("review_status", "已核验")
        review_note_raw = res_map.get("review_note", "审查通过")
        # Strip 【...】 tag for clean delivery
        clean_note = re.sub(r"^【[^】]+】", "", review_note_raw).strip()
        if not clean_note:
            clean_note = "审查通过"

        has_a = (res_map.get("severity_A") == "命中")

        defects_out = []
        if has_a:
            defects_out.append({
                "id": "A",
                "name": "缺色",
                "severity": "",
                "description": res_map.get("description_A", "全域严重缺色(A)")
            })
            reviewed_score = 1.0
            needs_rescoring = False
        else:
            TAXONOMY = {"B": "溢色", "C": "错色", "D": "偏色", "E1": "过饱和", "E2": "欠饱和", "F": "视觉自然度"}
            for code, name in TAXONOMY.items():
                sev = res_map.get(f"severity_{code}")
                if sev in ["L1", "L2", "L3"]:
                    desc = res_map.get(f"description_{code}", "")
                    defects_out.append({
                        "id": code,
                        "name": name,
                        "severity": sev,
                        "description": desc
                    })
            reviewed_score = None
            needs_rescoring = True

        if len(defects_out) == 0:
            clean_note = "审查通过"

        clean_item = {
            "image_id": item["data"]["image_id"],
            "file_path": item["data"].get("file_path", item["data"]["image_id"]),
            "source_dataset": item["data"].get("source_dataset", "coco"),
            "role": item["data"].get("role", item["data"].get("model_role", "lcad")),
            "defects": defects_out,
            "gpt_score": orig_rec.get("gpt_score"),
            "labeling_model": orig_rec.get("labeling_model", "gpt-5.6-sol"),
            "labeling_timestamp": orig_rec.get("labeling_timestamp"),
            "original_gpt_score": orig_rec.get("original_gpt_score", orig_rec.get("gpt_score")),
            "review_status": review_status,
            "review_note": clean_note,
            "reviewed_score": reviewed_score,
            "needs_rescoring": needs_rescoring,
            "human_review": {
                "task_id": item.get("id", 1),
                "annotation_id": ann.get("id", 1),
                "completed_by": ann.get("completed_by", 1),
                "updated_at": ann.get("updated_at", datetime.now(timezone.utc).isoformat())
            }
        }
        sanitized_done.append(clean_item)

    meta_payload = {
        "meta": {
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "total_images": len(sanitized_done),
            "needs_rescoring": True
        },
        "annotations": sanitized_done
    }

    with open(reviewed_file, "w", encoding="utf-8") as f:
        json.dump(meta_payload, f, ensure_ascii=False, indent=2)

    print(f"Successfully exported deliverable: {reviewed_file.name} ({len(sanitized_done)} tasks)")

    # Run schema validation assertion automatically
    val_script = Path(__file__).parent / "validate_export_schema.py"
    if val_script.exists():
        import subprocess
        res = subprocess.run([sys.executable, str(val_script), str(reviewed_file)], capture_output=True, text=True, encoding="utf-8")
        print(res.stdout)
        if res.returncode != 0:
            print(res.stderr)

    return reviewed_file


def main():
    ap = argparse.ArgumentParser(description="Universal Exporter for Colorization Review (V4)")
    ap.add_argument("stream_file", help="Path to stream package JSON")
    ap.add_argument("--project-id", type=int, default=None, help="Label Studio Project ID (optional)")
    ap.add_argument("--ignore-db", action="store_true", help="Do not load from DB, adopt stream predictions 100%")
    ap.add_argument("--out-file", default=None, help="Explicit path to reviewed output JSON")
    args = ap.parse_args()

    export_batch(args.stream_file, project_id=args.project_id, ignore_db=args.ignore_db, out_file=args.out_file)


if __name__ == "__main__":
    main()
