import json
from pathlib import Path

export_path = Path("LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json")
with open(export_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for a in data["annotations"]:
    if a["image_id"] == "lcad/000000560481.png":
        for d in a["defects"]:
            if d["id"] == "D":
                d["description"] = "草地与远景树林绿化呈现轻微的偏草绿黄调色偏移。"
    elif a["image_id"] == "lcad/000000576676.png":
        for d in a["defects"]:
            if d["id"] == "D":
                d["description"] = "厨房左侧青蓝木板墙面与挂架厨具整体略带偏冷青蓝调，部分物体色彩表现不够中性。"

with open(export_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated 9646 and 9915 defect descriptions.")
