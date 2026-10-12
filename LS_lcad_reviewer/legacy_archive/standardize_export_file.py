"""Standardizes an export JSON deliverable to strictly conform to benchmark schema:
LS_lcad_reviewer/exports/reviewed_20260930_084839.json
Ensures:
1. meta has strictly: exported_at, total_images, needs_rescoring.
2. annotations has strictly the 14 standard keys.
3. defects has strictly the 4 standard keys.
4. human_review has strictly the 4 standard keys.
5. All unauthorized intermediate keys (refinement, task_idx, etc.) are purged.
"""
import argparse
import json
import sys
from pathlib import Path

REQUIRED_ANN_KEYS = [
    "image_id", "file_path", "source_dataset", "role", "defects",
    "gpt_score", "labeling_model", "labeling_timestamp", "original_gpt_score",
    "review_status", "review_note", "reviewed_score", "needs_rescoring", "human_review"
]

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
TASKS_10000_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"

_ORIG_MAP = None
def get_original_records_map():
    global _ORIG_MAP
    if _ORIG_MAP is None:
        _ORIG_MAP = {}
        if TASKS_10000_FILE.exists():
            tasks = json.loads(TASKS_10000_FILE.read_text(encoding="utf-8"))
            for t in tasks:
                d = t.get("data", {})
                img = d.get("image_id")
                orig = d.get("original_record", {})
                if img:
                    _ORIG_MAP[img] = orig
    return _ORIG_MAP

def standardize_file(file_path: Path):
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False

    orig_map = get_original_records_map()
    data = json.loads(file_path.read_text(encoding="utf-8"))
    
    # 1. Clean meta
    raw_meta = data.get("meta", {})
    clean_meta = {
        "exported_at": raw_meta.get("exported_at", ""),
        "total_images": len(data.get("annotations", [])),
        "needs_rescoring": True
    }
    
    # 2. Clean annotations
    clean_anns = []
    for item in data.get("annotations", []):
        ann = {}
        img_id = item.get("image_id") or item.get("file_path", "")
        orig_rec = orig_map.get(img_id, {})
        
        ann["image_id"] = img_id
        ann["file_path"] = item.get("file_path") or img_id
        ann["source_dataset"] = orig_rec.get("source_dataset", item.get("source_dataset", "coco"))
        ann["role"] = orig_rec.get("role", item.get("role", "lcad"))
        
        # Clean defects & check pass purity
        raw_note = item.get("review_note", "")
        raw_defects = item.get("defects", [])
        clean_defects = []
        
        # Check if defect A was mentioned in review_note or present in raw_defects
        is_a_fuse = ("A熔断" in raw_note or "A 熔断" in raw_note or "缺色 A" in raw_note or "缺色(A" in raw_note)
        orig_a_item = next((d for d in raw_defects if isinstance(d, dict) and d.get("id") == "A"), None)
        has_a_defect = (orig_a_item is not None) or is_a_fuse
        
        if has_a_defect:
            # Preserve original specific description if available!
            a_desc = (orig_a_item.get("description") if orig_a_item and orig_a_item.get("description") 
                      else "全图彩色信息严重丢失退化为黑白灰阶（缺色 A 熔断）。")
            clean_defects = [{
                "id": "A",
                "name": "缺色",
                "severity": "",
                "description": a_desc
            }]
            final_note = raw_note if (raw_note and raw_note != "审查通过") else "全图缺色 A 熔断"
        else:
            if isinstance(raw_defects, list):
                for d in raw_defects:
                    if isinstance(d, dict):
                        d_id = d.get("id", "")
                        d_sev = d.get("severity", "")
                        if d_id in ("B", "C", "D", "E1", "E2", "F") and d_sev in ("L1", "L2", "L3"):
                            clean_defects.append({
                                "id": d_id,
                                "name": d.get("name", ""),
                                "severity": d_sev,
                                "description": d.get("description", "")
                            })
                            
            if len(clean_defects) == 0:
                final_note = "审查通过"
            else:
                final_note = raw_note if (raw_note and raw_note != "审查通过") else "核查发现局部缺陷"
                        
        ann["defects"] = clean_defects
        
        # Maintain gpt_score strictly as original value from tasks_lcad_10000.json
        orig_score = orig_rec.get("gpt_score", item.get("original_gpt_score", item.get("gpt_score", 0.0)))
        ann["gpt_score"] = orig_score
        ann["labeling_model"] = orig_rec.get("labeling_model", item.get("labeling_model", "gpt-5.6-sol"))
        ann["labeling_timestamp"] = orig_rec.get("labeling_timestamp", item.get("labeling_timestamp", ""))
        ann["original_gpt_score"] = orig_score
        
        ann["review_status"] = "已核验"
        ann["review_note"] = final_note
        
        # Determine reviewed_score and needs_rescoring according to defect A presence
        has_a = any(d.get("id") == "A" for d in clean_defects)
        if has_a:
            ann["reviewed_score"] = 1.0
            ann["needs_rescoring"] = False
        else:
            ann["reviewed_score"] = None
            ann["needs_rescoring"] = True
        
        # Clean human_review
        hr = item.get("human_review", {})
        clean_hr = {
            "task_id": hr.get("task_id", 0) if isinstance(hr, dict) else 0,
            "annotation_id": hr.get("annotation_id", 0) if isinstance(hr, dict) else 0,
            "completed_by": hr.get("completed_by", 1) if isinstance(hr, dict) else 1,
            "updated_at": hr.get("updated_at", "") if isinstance(hr, dict) else ""
        }
        ann["human_review"] = clean_hr
        clean_anns.append(ann)
        
    out_payload = {
        "meta": clean_meta,
        "annotations": clean_anns
    }
    
    file_path.write_text(json.dumps(out_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Successfully standardized: {file_path.name}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for p in sys.argv[1:]:
            standardize_file(Path(p))
    else:
        print("Usage: python standardize_export_file.py <file_path> ...")
