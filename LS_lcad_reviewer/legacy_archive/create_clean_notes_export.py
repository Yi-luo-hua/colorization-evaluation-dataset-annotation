"""Create a delivery version where the review_note field is completely empty ("").
Strictly preserves all other fields, ordering, and structure.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"

def main():
    src_file = EXPORTS_DIR / "reviewed_1_10000_20260930_200411.json"
    if not src_file.exists():
        src_file = EXPORTS_DIR / "reviewed_1_10000_all.json"
        
    print(f"Reading from: {src_file.name}")
    with open(src_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    anns = data.get("annotations", [])
    total = len(anns)
    print(f"Total records: {total}")

    non_empty_before = sum(1 for a in anns if a.get("review_note") != "")
    print(f"Non-empty review_notes before: {non_empty_before}")

    # Set all review_note to ""
    for a in anns:
        a["review_note"] = ""

    non_empty_after = sum(1 for a in anns if a.get("review_note") != "")
    print(f"Non-empty review_notes after: {non_empty_after}")

    now_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_ts_path = EXPORTS_DIR / f"reviewed_1_10000_clean_{now_ts}.json"
    clean_alias_path = EXPORTS_DIR / "reviewed_1_10000_clean.json"

    print(f"Writing to: {clean_ts_path.name}")
    with open(clean_ts_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Writing to: {clean_alias_path.name}")
    with open(clean_alias_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    size_mb = clean_ts_path.stat().st_size / (1024 * 1024)
    print(f"Done! Cleaned file size: {size_mb:.2f} MB")

if __name__ == "__main__":
    main()
