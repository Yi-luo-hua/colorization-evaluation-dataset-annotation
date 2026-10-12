# -*- coding: utf-8 -*-
import json
import os

scripts_dir = os.path.dirname(os.path.abspath(__file__))
meta_path = os.path.join(scripts_dir, "..", "audits", "sheets_meta_9501_10000.json")
if not os.path.exists(meta_path):
    meta_path = "sheets_meta_9501_10000.json"

with open(meta_path, "r", encoding="utf-8") as f:
    items = json.load(f)

out_lines = []
curr_sheet = 0

for i, it in enumerate(items):
    sheet_num = (i // 6) + 1
    if sheet_num != curr_sheet:
        curr_sheet = sheet_num
        out_lines.append(f"=== SHEET {curr_sheet:02d} ===")
    
    t_id = it.get("task_idx") or it.get("task_id")
    img_name = it.get("image_id", "")
    orig_s = it.get("score", 0.0)
    susp = it.get("suspicion", 0.0)
    reasons = it.get("reasons", [])
    m = it.get("metrics", {})
    
    b_dir = m.get("bias_direction", "偏暖红黄调")
    dc = m.get("delta_c", 0.0)
    pk = m.get("peak_delta_c", 0.0)
    b2g = m.get("blue_to_green_ratio", 0.0)
    rl = m.get("red_loss_ratio", 0.0)
    bl = m.get("bleed_ratio", 0.0)
    p90 = m.get("p90_edge", 0.0)
    
    reason_str = "; ".join(reasons)
    line = f"  Task #{t_id} | {img_name} | Orig: {orig_s} | Susp: {susp} | {b_dir} (dC={dc:.2f}, Peak={pk:.2f}, B2G={b2g:.2f}, RL={rl:.2f}, Bleed={bl:.2f}/P90={p90:.1f}) | {reason_str}"
    out_lines.append(line)

out_path = os.path.join(scripts_dir, "..", "audits", "sheets_summary_clean_9501_10000.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print(f"Generated clean summary for {len(items)} tasks to {out_path}")
