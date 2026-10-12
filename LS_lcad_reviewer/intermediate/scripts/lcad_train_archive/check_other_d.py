import json

with open("LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json", "r", encoding="utf-8") as f:
    data = json.load(f)

with open("temp_other_d.txt", "w", encoding="utf-8") as out:
    for a in data["annotations"]:
        for d in a.get("defects", []):
            if d.get("id") == "D":
                desc = d.get("description", "")
                has_dir = any(k in desc for k in ["偏暖红黄调", "偏冷青蓝调", "偏洋红紫调", "偏草绿黄调"])
                if not has_dir:
                    out.write(f"{a['image_id']} D: {desc}\n")
