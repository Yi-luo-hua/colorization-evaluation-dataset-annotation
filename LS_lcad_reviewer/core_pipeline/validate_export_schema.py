"""Official Schema Validator for Colorization Review Deliverables.
Strictly validates that any exported file matches the exact schema of:
LS_lcad_reviewer/exports/reviewed_20260930_084839.json
Ensures zero arbitrary additions or omissions of fields.
"""
import argparse
import json
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_20260930_084839.json"

REQUIRED_ROOT_KEYS = {"meta", "annotations"}
REQUIRED_META_KEYS = {"exported_at", "total_images", "needs_rescoring"}
REQUIRED_ANN_KEYS = {
    "image_id", "file_path", "source_dataset", "role", "defects",
    "gpt_score", "labeling_model", "labeling_timestamp", "original_gpt_score",
    "review_status", "review_note", "reviewed_score", "needs_rescoring", "human_review"
}
REQUIRED_DEFECT_KEYS = {"id", "name", "severity", "description"}
REQUIRED_HR_KEYS = {"task_id", "annotation_id", "completed_by", "updated_at"}

def validate_file(target_path: Path, verbose: bool = True) -> bool:
    if not target_path.exists():
        print(f"[FAIL] File not found: {target_path}")
        return False

    try:
        data = json.loads(target_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[FAIL] Invalid JSON format: {e}")
        return False

    errors = []

    # 1. Root keys check
    root_keys = set(data.keys())
    if root_keys != REQUIRED_ROOT_KEYS:
        diff_added = root_keys - REQUIRED_ROOT_KEYS
        diff_missing = REQUIRED_ROOT_KEYS - root_keys
        if diff_added:
            errors.append(f"Root object has unauthorized extra keys: {diff_added}")
        if diff_missing:
            errors.append(f"Root object is missing required keys: {diff_missing}")

    # 2. Meta object check
    meta = data.get("meta")
    if not isinstance(meta, dict):
        errors.append("Field 'meta' must be a dictionary object.")
    else:
        meta_keys = set(meta.keys())
        if meta_keys != REQUIRED_META_KEYS:
            diff_added = meta_keys - REQUIRED_META_KEYS
            diff_missing = REQUIRED_META_KEYS - meta_keys
            if diff_added:
                errors.append(f"'meta' object has unauthorized extra keys: {diff_added}")
            if diff_missing:
                errors.append(f"'meta' object is missing required keys: {diff_missing}")
        if "total_images" in meta and not isinstance(meta["total_images"], int):
            errors.append(f"'meta.total_images' must be an integer, got {type(meta['total_images'])}")
        if "needs_rescoring" in meta and not isinstance(meta["needs_rescoring"], bool):
            errors.append(f"'meta.needs_rescoring' must be a boolean, got {type(meta['needs_rescoring'])}")

    # 3. Annotations check
    anns = data.get("annotations")
    if not isinstance(anns, list):
        errors.append("Field 'annotations' must be a list of records.")
    else:
        # Check total_images count
        if meta and meta.get("total_images") != len(anns):
            errors.append(f"'meta.total_images' ({meta.get('total_images')}) does not match len(annotations) ({len(anns)})")

        seen_images = set()
        TAXONOMY = {"A": "缺色", "B": "溢色", "C": "错色", "D": "偏色", "E1": "过饱和", "E2": "欠饱和", "F": "视觉自然度"}

        for idx, item in enumerate(anns):
            if not isinstance(item, dict):
                errors.append(f"Annotation record #{idx} is not an object.")
                break

            # Key set assertion
            item_keys = set(item.keys())
            if item_keys != REQUIRED_ANN_KEYS:
                diff_added = item_keys - REQUIRED_ANN_KEYS
                diff_missing = REQUIRED_ANN_KEYS - item_keys
                if diff_added:
                    errors.append(f"Task #{idx} ({item.get('image_id')}) has extra keys: {diff_added}")
                if diff_missing:
                    errors.append(f"Task #{idx} ({item.get('image_id')}) is missing keys: {diff_missing}")

            # Duplicate image_id check
            img_id = item.get("image_id")
            if not img_id:
                errors.append(f"Task #{idx} is missing 'image_id'")
            elif img_id in seen_images:
                errors.append(f"Duplicate image_id detected: {img_id}")
            else:
                seen_images.add(img_id)

            # Check review_status
            if item.get("review_status") != "已核验":
                errors.append(f"Task #{idx} ({img_id}) review_status must be '已核验', got {repr(item.get('review_status'))}")

            # Check defects
            defects = item.get("defects")
            if not isinstance(defects, list):
                errors.append(f"Task #{idx} ({img_id}) 'defects' must be a list, got {type(defects)}")
            else:
                defect_ids = []
                for d_idx, d in enumerate(defects):
                    if not isinstance(d, dict):
                        errors.append(f"Task #{idx} defect #{d_idx} is not an object.")
                    else:
                        d_keys = set(d.keys())
                        if d_keys != REQUIRED_DEFECT_KEYS:
                            errors.append(f"Task #{idx} defect #{d_idx} keys mismatch: extra={d_keys - REQUIRED_DEFECT_KEYS}, missing={REQUIRED_DEFECT_KEYS - d_keys}")
                        
                        d_id = d.get("id")
                        d_name = d.get("name")
                        d_sev = d.get("severity")
                        defect_ids.append(d_id)

                        if d_id not in TAXONOMY:
                            errors.append(f"Task #{idx} ({img_id}) invalid defect id: {d_id}")
                        elif d_name != TAXONOMY[d_id]:
                            errors.append(f"Task #{idx} ({img_id}) defect name mismatch: id={d_id}, expected={TAXONOMY[d_id]}, got={d_name}")

                        if d_id == "A":
                            if d_sev != "":
                                errors.append(f"Task #{idx} ({img_id}) defect A severity must be empty string '', got {repr(d_sev)}")
                        else:
                            if d_sev not in ("L1", "L2", "L3"):
                                errors.append(f"Task #{idx} ({img_id}) defect {d_id} severity must be L1/L2/L3, got {repr(d_sev)}")
                # E1 (过饱和) 与 E2 (欠饱和) 按照具体物品分别标注，不再执行整图级互斥拦截
                # 允许同一任务中不同视觉实体分别标注过饱和与欠饱和

                # Check pass purity
                review_note = item.get("review_note", "")
                if review_note == "审查通过" and len(defects) > 0:
                    errors.append(f"Task #{idx} ({img_id}) marked as '审查通过' but has non-empty defects ({len(defects)} items)")

                # Check A fuse logic & reviewed_score / needs_rescoring contract
                has_a = ("A" in defect_ids)
                rev_score = item.get("reviewed_score")
                needs_resc = item.get("needs_rescoring")

                if has_a:
                    if rev_score != 1.0:
                        errors.append(f"Task #{idx} ({img_id}) defect A present, reviewed_score must be 1.0, got {rev_score}")
                    if needs_resc is not False:
                        errors.append(f"Task #{idx} ({img_id}) defect A present, needs_rescoring must be False, got {needs_resc}")
                else:
                    if rev_score is not None:
                        errors.append(f"Task #{idx} ({img_id}) defect A not present, reviewed_score must be null, got {rev_score}")
                    if needs_resc is not True:
                        errors.append(f"Task #{idx} ({img_id}) defect A not present, needs_rescoring must be True, got {needs_resc}")

                # Note: gpt_score strictly preserves the original score from tasks_lcad_10000.json.
                # Score recalculation is performed by downstream offline algorithms, NOT during review!
                if item.get("gpt_score") != item.get("original_gpt_score"):
                    errors.append(f"Task #{idx} ({img_id}) gpt_score ({item.get('gpt_score')}) must equal original_gpt_score ({item.get('original_gpt_score')})")

            # Check human_review
            hr = item.get("human_review")
            if not isinstance(hr, dict):
                errors.append(f"Task #{idx} ({img_id}) 'human_review' must be a dict object.")
            else:
                hr_keys = set(hr.keys())
                if hr_keys != REQUIRED_HR_KEYS:
                    errors.append(f"Task #{idx} ({img_id}) human_review keys mismatch: extra={hr_keys - REQUIRED_HR_KEYS}, missing={REQUIRED_HR_KEYS - hr_keys}")

            if len(errors) > 20:
                break

    if errors:
        if verbose:
            print(f"[FAIL] Validation FAILED for {target_path.name}:")
            for err in errors[:20]:
                print(f"   * {err}")
            if len(errors) > 20:
                print(f"   * ... and {len(errors) - 20} more errors.")
        return False
    else:
        if verbose:
            print(f"[PASS] 100% Schema & Logic Compliant: {target_path.name} (Matched reviewed_20260930_084839.json)")
        return True

def main():
    parser = argparse.ArgumentParser(description="Validate deliverables against standard benchmark schema.")
    parser.add_argument("target", nargs="?", default=None, help="Target JSON file to validate (or omit to validate all in exports/)")
    args = parser.parse_args()

    exports_dir = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"

    if args.target:
        p = Path(args.target)
        if p.exists():
            target_path = p.resolve()
        elif (WORKSPACE_ROOT / p).exists():
            target_path = (WORKSPACE_ROOT / p).resolve()
        elif (exports_dir / p).exists():
            target_path = (exports_dir / p).resolve()
        elif (exports_dir / p.name).exists():
            target_path = (exports_dir / p.name).resolve()
        else:
            target_path = p.resolve()
        success = validate_file(target_path)
        sys.exit(0 if success else 1)
    else:
        print(f"Validating all files in {exports_dir} against official benchmark...")
        all_passed = True
        for p in sorted(exports_dir.glob("reviewed_*.json")):
            if p.name == BENCHMARK_FILE.name:
                continue
            if not validate_file(p):
                all_passed = False
        sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
