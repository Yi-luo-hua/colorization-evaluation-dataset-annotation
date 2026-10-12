import json
import re
from pathlib import Path

FILE_PATH = Path("LS_lcad_reviewer/exports/reviewed_3501_4000_20260930_114314.json")
TASKS_PATH = Path("LS_lcad_reviewer/tasks_lcad_10000.json")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    export_data = json.load(f)

with open(TASKS_PATH, "r", encoding="utf-8") as f:
    tasks = json.load(f)[3500:4000]

meta = export_data.get("meta", {})
anns = export_data.get("annotations", [])

print("=== 1. 基本结构检验 ===")
print(f"Total annotations: {len(anns)}")
print(f"Meta total_images: {meta.get('total_images')}")
print(f"Meta keys: {list(meta.keys())}")
assert len(anns) == 500
assert meta.get("total_images") == 500
assert list(meta.keys()) == ["exported_at", "total_images", "needs_rescoring"]

print("\n=== 2. 字段完整性与一致性检验 ===")
score_diff_count = 0
for idx, (a, orig_t) in enumerate(zip(anns, tasks)):
    raw_score = orig_t["data"].get("original_record", {}).get("gpt_score", orig_t["data"].get("gpt_score"))
    if abs(a["gpt_score"] - raw_score) > 1e-4:
        score_diff_count += 1
    assert a["gpt_score"] == a["original_gpt_score"]
    assert a["review_status"] == "已核验"
    assert a["source_dataset"] == "coco"
    assert a["role"] == "lcad"

print(f"Original score faithfulness diff count: {score_diff_count} (Expected 0)")
assert score_diff_count == 0

print("\n=== 3. 放行与改判统计 ===")
passed_items = [a for a in anns if a["review_note"] == "审查通过"]
modified_items = [a for a in anns if a["review_note"] != "审查通过"]
print(f"Passed items count: {len(passed_items)}")
print(f"Modified items count: {len(modified_items)}")

# 检验放行项必须为 defects == []
empty_defects_in_pass = all(len(a["defects"]) == 0 for a in passed_items)
print(f"All passed items have empty defects: {empty_defects_in_pass}")
assert empty_defects_in_pass

# 检验修改项必须有 defects
has_defects_in_mod = all(len(a["defects"]) > 0 for a in modified_items)
print(f"All modified items have non-empty defects: {has_defects_in_mod}")
assert has_defects_in_mod

# 检验原 5.0 满分拦截情况
orig_5_in_pass = [a for a in passed_items if a["original_gpt_score"] >= 4.9]
print(f"Original >= 4.9 in passed items: {len(orig_5_in_pass)} (Expected 0)")
assert len(orig_5_in_pass) == 0

print("\n=== 4. 具象定物与禁止词检验 ===")
forbidden_words = ["局部关键区域", "关键主体或背景", "关键主体或画面", "局部配饰与边缘区域", "某处区域", "画面局部区域"]
found_forbidden = []
for a in modified_items:
    note = a["review_note"]
    descs = [d["description"] for d in a["defects"]]
    for fw in forbidden_words:
        if fw in note or any(fw in desc for desc in descs):
            found_forbidden.append((a["image_id"], fw))

print(f"Forbidden abstract words count: {len(found_forbidden)}")
assert len(found_forbidden) == 0

print("\n=== 5. 偏色方向唯一定性检验 ===")
ambiguous_words = ["偏暖黄或泛青冷", "偏冷或偏暖", "泛暖或泛冷", "可能偏暖", "可能偏冷"]
found_ambiguous = []
for a in modified_items:
    note = a["review_note"]
    descs = [d["description"] for d in a["defects"]]
    for aw in ambiguous_words:
        if aw in note or any(aw in desc for desc in descs):
            found_ambiguous.append((a["image_id"], aw))

print(f"Ambiguous bias words count: {len(found_ambiguous)}")
assert len(found_ambiguous) == 0

print("\n=== 6. 交互前缀清洗检验 ===")
found_bracket_prefix = [a["image_id"] for a in anns if a["review_note"].startswith("【")]
print(f"Bracket prefix count: {len(found_bracket_prefix)} (Expected 0)")
assert len(found_bracket_prefix) == 0

print("\n[ALL CHECKS PASSED] Deliverable 3501-4000 is 100% compliant and robust!")
