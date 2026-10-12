import json
import re

ALL_JSON = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer\exports\reviewed_1_10000_all.json"

with open(ALL_JSON, "r", encoding="utf-8") as f:
    anns = json.load(f)["annotations"]

patterns = [
    r"^核查修正：",
    r"^原5.0满分复核：核查发现：全图轻微偏",
    r"^原5.0满分复核：核查发现：色彩过饱和",
    r"^原5.0满分复核：核查发现：局部色彩欠饱和",
    r"^原5.0满分核查修正：",
    r"核查修正"
]

cv_direct_candidates = []
for idx, ann in enumerate(anns):
    note = ann.get("review_note", "")
    for p in patterns:
        if re.search(p, note):
            cv_direct_candidates.append({
                "task_id": idx + 1,
                "image_id": ann["image_id"],
                "file_path": ann.get("file_path", ""),
                "note": note,
                "defects": ann.get("defects", [])
            })
            break

print(f"Total initial CV direct physics fix candidates matched: {len(cv_direct_candidates)}")

# 打印一些典型例子
for item in cv_direct_candidates[:15]:
    defs_str = ", ".join([f"{d.get('id')}-{d.get('severity')}" for d in item['defects']])
    print(f"Task #{item['task_id']} ({item['image_id']}): defs=[{defs_str}] | note: {item['note']}")

# 保存匹配清单
out_path = r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer\intermediate\audits\cv_physics_direct_candidates.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(cv_direct_candidates, f, ensure_ascii=False, indent=2)
print(f"Saved to {out_path}")
