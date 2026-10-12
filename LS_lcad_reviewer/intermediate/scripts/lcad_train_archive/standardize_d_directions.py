import json
import re

with open("LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json", "r", encoding="utf-8") as f:
    data = json.load(f)

STANDARD_DIRS = ["偏暖红黄调", "偏冷青蓝调", "偏洋红紫调", "偏草绿黄调"]

def get_best_dir(desc):
    # Rule matching
    if any(k in desc for k in ["黄绿", "青绿", "草绿", "绿褐"]):
        return "偏草绿黄调"
    elif any(k in desc for k in ["洋红", "紫红", "红紫", "粉紫"]):
        return "偏洋红紫调"
    elif any(k in desc for k in ["青蓝", "偏冷", "蓝冷", "偏蓝", "冷色", "蓝紫"]):
        return "偏冷青蓝调"
    elif any(k in desc for k in ["黄褐", "黄橙", "暖红", "红橙", "红褐", "暖黄", "偏黄", "暖色", "偏红"]):
        return "偏暖红黄调"
    return "偏暖红黄调"

updated_count = 0
for a in data["annotations"]:
    for d in a.get("defects", []):
        if d.get("id") == "D":
            desc = d.get("description", "")
            if not any(sd in desc for sd in STANDARD_DIRS):
                matched_dir = get_best_dir(desc)
                # Ensure the standard direction is appended or seamlessly integrated
                # e.g. "画面阴影及路面区域带有轻微的棕红色调偏移。" -> "画面阴影及路面区域带有轻微的棕红色调偏移（偏暖红黄调）。"
                new_desc = desc.rstrip("。") + f"（{matched_dir}）。"
                d["description"] = new_desc
                updated_count += 1

with open("LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Standardized {updated_count} D defect descriptions to 100% include standard direction.")
