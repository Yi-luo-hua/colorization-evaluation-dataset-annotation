import json
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
ALL_FILE = EXPORTS_DIR / "reviewed_1_10000_all.json"
CLEAN_FILE = EXPORTS_DIR / "reviewed_1_10000_clean.json"

BATCH_SPECS = [
    (1, 500, "reviewed_1_500_20260930_111408.json"),
    (501, 1000, "reviewed_501_1000_20260930_111842.json"),
    (1001, 1500, "reviewed_1001_1500_20260930_111612.json"),
    (1501, 2000, "reviewed_1501_2000_20260930_082139.json"),
    (2001, 2500, "reviewed_2001_2500_20260930_093827.json"),
    (2501, 3000, "reviewed_2501_3000_20260930_101014.json"),
    (3001, 3500, "reviewed_3001_3500_20260930_110626.json"),
    (3501, 4000, "reviewed_3501_4000_20260930_121202.json"),
    (4001, 4500, "reviewed_4001_4500_20260930_135528.json"),
    (4501, 5000, "reviewed_4501_5000_20260930_140753.json"),
    (5001, 5500, "reviewed_5001_5500_20260930_142848.json"),
    (5501, 6000, "reviewed_5501_6000_20260930_150135.json"),
    (6001, 6500, "reviewed_6001_6500_20260930_153605.json"),
    (6501, 7000, "reviewed_6501_7000_20260930_155809.json"),
    (7001, 7500, "reviewed_7001_7500_20260930_161800.json"),
    (7501, 8000, "reviewed_7501_8000_20260930_182342.json"),
    (8001, 8500, "reviewed_8001_8500_20260930_184910.json"),
    (8501, 9000, "reviewed_8501_9000_20260930_190928.json"),
    (9001, 9500, "reviewed_9001_9500_20260930_192616.json"),
    (9501, 10000, "reviewed_9501_10000_20260930_194247.json"),
]

def main():
    print("=== Synchronizing all batch export files and timestamped exports ===")
    
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
    
    all_anns = all_data["annotations"]
    ann_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}
    
    # 1. Update each of the 20 batch files
    for start_id, end_id, filename in BATCH_SPECS:
        file_path = EXPORTS_DIR / filename
        batch_anns = []
        for tid in range(start_id, end_id + 1):
            if tid in ann_map:
                batch_anns.append(ann_map[tid])
            else:
                raise ValueError(f"Task {tid} missing in all_annotations!")

        batch_data = {
            "meta": {
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "total_images": len(batch_anns),
                "needs_rescoring": any(a.get("needs_rescoring", False) for a in batch_anns)
            },
            "annotations": batch_anns
        }
        
        with open(file_path, "w", encoding="utf-8") as bf:
            json.dump(batch_data, bf, ensure_ascii=False, indent=2)
            
        print(f"  [OK] Batch {start_id:5d}-{end_id:5d} synced -> {filename}")

    # 2. Generate new timestamped all deliverable
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_file = EXPORTS_DIR / f"reviewed_1_10000_{now_str}.json"
    with open(timestamped_file, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Exported latest timestamped deliverable -> {timestamped_file.name}")

    # 3. Synchronize clean version into no_review_note if it exists to fix schema errors
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    # 针对历史 legacy 遗留文件 reviewed_1_10000_no_review_note.json 进行同步（补充符合标准的 review_note=""）
    legacy_no_note = EXPORTS_DIR / "reviewed_1_10000_no_review_note.json"
    if legacy_no_note.exists():
        with open(legacy_no_note, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Fixed and synced legacy {legacy_no_note.name} with clean schema")

    legacy_no_note_ts = EXPORTS_DIR / "reviewed_1_10000_no_review_note_20261001_132045.json"
    if legacy_no_note_ts.exists():
        with open(legacy_no_note_ts, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Fixed and synced legacy {legacy_no_note_ts.name} with clean schema")

    print("\n[SUCCESS] All exports and 20 batch files successfully synchronized!")

if __name__ == "__main__":
    main()
