"""Merge Master's Label Studio reviews into an existing reviewed deliverable JSON.

This script acts as the optional branch merger:
If Master performs spot checks in Label Studio and submits completions,
this script extracts those manual reviews from SQLite (or an exported JSON)
and patches them directly into the already-generated deliverable dataset.
"""
import argparse
import copy
import json
import os
import re
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DB_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "data" / "label_studio.sqlite3"
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"

TAXONOMY = {
    "A": "缺色",
    "B": "溢色",
    "C": "错色",
    "D": "偏色",
    "E1": "过饱和",
    "E2": "欠饱和",
    "F": "视觉自然度"
}


def find_latest_reviewed_file():
    if not EXPORTS_DIR.exists():
        return None
    files = sorted(
        [f for f in EXPORTS_DIR.glob("reviewed_*.json") if not f.name.endswith(".bak")],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    return files[0] if files else None


def load_completions_from_sqlite(project_id=None):
    if not DB_FILE.exists():
        print(f"Warning: SQLite database not found at {DB_FILE}")
        return {}

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    query = """
        SELECT t.id, t.data, tc.result, tc.id, tc.updated_at, tc.completed_by_id, tc.project_id
        FROM task_completion tc
        JOIN task t ON tc.task_id = t.id
    """
    params = []
    if project_id is not None:
        query += " WHERE tc.project_id = ?"
        params.append(project_id)
    query += " ORDER BY tc.updated_at ASC"  # Later ones will overwrite earlier

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()

    completions = {}
    for r in rows:
        t_id, t_data_str, tc_res_str, tc_id, updated_at, completed_by, pid = r
        try:
            d = json.loads(t_data_str)
            img_id = d.get("image_id")
            if not img_id:
                continue
            res = json.loads(tc_res_str)
            completions[img_id] = {
                "task_id": t_id,
                "annotation_id": tc_id,
                "result": res,
                "updated_at": updated_at,
                "completed_by": completed_by,
                "project_id": pid,
                "original_record": d.get("original_record", {})
            }
        except Exception:
            continue

    return completions


def load_completions_from_json_export(export_path):
    p = Path(export_path)
    if not p.exists():
        raise FileNotFoundError(f"Export file not found: {export_path}")
    data = json.loads(p.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError("Export JSON must be a list of tasks")

    completions = {}
    for task in data:
        t_data = task.get("data", {})
        img_id = t_data.get("image_id")
        if not img_id:
            continue
        anns = [a for a in task.get("annotations", []) if not a.get("was_cancelled")]
        if not anns:
            continue
        # Use latest annotation
        latest_ann = sorted(anns, key=lambda a: a.get("updated_at", ""), reverse=True)[0]
        completions[img_id] = {
            "task_id": task.get("id"),
            "annotation_id": latest_ann.get("id"),
            "result": latest_ann.get("result", []),
            "updated_at": latest_ann.get("updated_at"),
            "completed_by": latest_ann.get("completed_by"),
            "project_id": task.get("project"),
            "original_record": t_data.get("original_record", {})
        }
    return completions


def parse_v4_result(result_list):
    """Parses raw Label Studio result choices/texts into V4 defects and status."""
    res_map = {}
    for r in result_list:
        from_name = r.get("from_name")
        if from_name:
            res_map[from_name] = r

    def get_choice(field_name):
        return res_map.get(field_name, {}).get("value", {}).get("choices", [])

    def get_text(field_name):
        return "\n".join(res_map.get(field_name, {}).get("value", {}).get("text", []))

    review_status_choices = get_choice("review_status")
    review_status = review_status_choices[0] if review_status_choices else "已核验"

    a_choice = get_choice("severity_A")
    is_a_hit = (a_choice == ["命中"])

    defects = []
    if is_a_hit:
        defects = [{
            "id": "A",
            "name": "缺色",
            "severity": "",
            "description": get_text("description_A")
        }]
    else:
        for code, name in TAXONOMY.items():
            if code == "A":
                continue
            sev = get_choice("severity_" + code)
            if sev and len(sev) == 1 and sev[0] in ("L1", "L2", "L3"):
                defects.append({
                    "id": code,
                    "name": name,
                    "severity": sev[0],
                    "description": get_text("description_" + code)
                })

    raw_note = get_text("review_note")
    is_pass = any(kw in raw_note for kw in ["初审核验通过", "满分全检通过", "物理指标自洽", "审查通过"])
    if is_pass or not raw_note:
        review_note = "审查通过"
    else:
        clean_note = re.sub(r"^【[^】]+】\s*", "", raw_note).strip()
        review_note = clean_note if clean_note else "审查通过"

    reviewed_score = 1.0 if is_a_hit else None
    needs_rescoring = not is_a_hit

    return {
        "defects": defects,
        "review_status": review_status,
        "review_note": review_note,
        "reviewed_score": reviewed_score,
        "needs_rescoring": needs_rescoring
    }


def merge_reviews(target_file, project_id=None, source_export=None, dry_run=False, output_file=None):
    target_path = Path(target_file).resolve()
    if not target_path.exists():
        print(f"Error: Deliverable file not found: {target_path}")
        sys.exit(1)

    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "annotations" not in data or not isinstance(data["annotations"], list):
        print(f"Error: Invalid deliverable format: 'annotations' key missing or not a list.")
        sys.exit(1)

    ann_list = data["annotations"]
    print(f"Loaded target deliverable: {target_path.name} ({len(ann_list)} tasks)")

    # Fetch completions from SQLite or source export
    if source_export:
        print(f"Loading Master's completions from export file: {source_export}")
        completions = load_completions_from_json_export(source_export)
    else:
        print(f"Loading Master's completions from SQLite: {DB_FILE.name}" + (f" (Project {project_id})" if project_id else ""))
        completions = load_completions_from_sqlite(project_id)

    print(f"Total available completions in source: {len(completions)}")

    # Match and patch
    patched_count = 0
    newly_reviewed = 0
    updated_existing = 0

    for item in ann_list:
        img_id = item.get("image_id")
        if img_id not in completions:
            continue

        comp = completions[img_id]
        parsed = parse_v4_result(comp["result"])

        prev_human = item.get("human_review", {})
        was_manual = (prev_human.get("task_id") is not None)

        # Apply patch
        item["defects"] = parsed["defects"]
        item["review_status"] = parsed["review_status"]
        item["review_note"] = parsed["review_note"]
        item["reviewed_score"] = parsed["reviewed_score"]
        item["needs_rescoring"] = parsed["needs_rescoring"]
        item["human_review"] = {
            "task_id": comp["task_id"],
            "annotation_id": comp["annotation_id"],
            "completed_by": comp["completed_by"],
            "updated_at": comp["updated_at"]
        }

        patched_count += 1
        if was_manual:
            updated_existing += 1
        else:
            newly_reviewed += 1

        defect_summary = ", ".join([f"{d['id']}-{d['severity']}" for d in parsed['defects']]) or "无缺陷"
        print(f"  [PATCHED] {img_id} -> 状态: {parsed['review_status']} | 缺陷: [{defect_summary}] | 备注: {parsed['review_note'][:30]}...")

    # Recalculate total manual count
    total_manual = sum(1 for item in ann_list if item.get("human_review", {}).get("task_id") is not None)

    # Update metadata
    if "meta" in data:
        data["meta"]["manual_reviews_count"] = total_manual
        data["meta"]["last_master_merge_at"] = datetime.utcnow().isoformat()
        if project_id:
            data["meta"]["merged_project_id"] = project_id

    print("\n--- Merge Summary ---")
    print(f"Total records in dataset : {len(ann_list)}")
    print(f"Completions matched     : {patched_count} (New: {newly_reviewed}, Updated: {updated_existing})")
    print(f"Total manual reviews now : {total_manual} / {len(ann_list)}")

    if dry_run:
        print("\nDry-run mode enabled. No changes were written to disk.")
        return

    out_path = Path(output_file).resolve() if output_file else target_path

    # If updating in-place, make a backup first
    if out_path == target_path:
        bak_file = target_path.with_suffix(".json.bak")
        shutil.copy2(target_path, bak_file)
        print(f"Backup created at: {bak_file.name}")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved updated deliverable: {out_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Merge Master's Label Studio reviews into deliverable dataset"
    )
    parser.add_argument(
        "deliverable",
        nargs="?",
        default=None,
        help="Path to reviewed_{range}_{timestamp}.json deliverable file. If omitted, uses the latest in exports/"
    )
    parser.add_argument(
        "--project-id",
        type=int,
        default=None,
        help="Filter completions by Label Studio Project ID (optional)"
    )
    parser.add_argument(
        "--source-export",
        type=str,
        default=None,
        help="Path to an exported JSON file from Label Studio (optional alternative to SQLite)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output destination path. If not provided, updates the deliverable in-place with a backup."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview merge results without writing to disk"
    )

    args = parser.parse_args()

    target_file = args.deliverable
    if not target_file:
        latest = find_latest_reviewed_file()
        if not latest:
            print("Error: No reviewed deliverables found in exports/ directory, please specify one explicitly.")
            sys.exit(1)
        print(f"No deliverable specified. Automatically selected latest: {latest.name}")
        target_file = str(latest)

    merge_reviews(
        target_file=target_file,
        project_id=args.project_id,
        source_export=args.source_export,
        dry_run=args.dry_run,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
