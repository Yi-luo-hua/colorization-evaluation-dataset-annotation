import json
from pathlib import Path

audit_path = Path("LS_lcad_reviewer/intermediate/audits/audit_needs_grounding_3501_4000.json")
sheets_meta_path = Path("LS_lcad_reviewer/intermediate/audits/sheets_meta_3501_4000.json")

with open(audit_path, "r", encoding="utf-8") as f:
    audits = json.load(f)

# 建立 task_idx -> sheet 映射
task_to_sheet = {}
if sheets_meta_path.exists():
    with open(sheets_meta_path, "r", encoding="utf-8") as f:
        sheets_data = json.load(f)
        # sheets_data structure: either list or dict
        if isinstance(sheets_data, list):
            for item in sheets_data:
                task_to_sheet[item.get("task_idx")] = item.get("sheet", "unknown")
        elif isinstance(sheets_data, dict):
            for s_name, s_items in sheets_data.items():
                if isinstance(s_items, list):
                    for item in s_items:
                        task_to_sheet[item.get("task_idx")] = s_name

# 筛选高危样本
severe_items = []
for a in audits:
    m = a.get("metrics", {})
    t_idx = a["task_idx"]
    susp = a.get("suspicion", 0)
    score = a.get("score", 0)
    r_sat = m.get("r_sat", 1.0)
    red_loss = m.get("red_loss", 0.0)
    b_to_g = m.get("blue_to_green", 0.0)
    bleed_r = m.get("bleed_ratio", 1.0)
    p90 = m.get("p90_edge", 0.0)
    dc = m.get("delta_c", 0.0)
    local_peak = m.get("max_local_peak", 0.0)
    
    is_severe = False
    severe_tags = []
    
    if susp >= 5.0:
        is_severe = True
        severe_tags.append(f"HighSusp({susp:.1f})")
    if r_sat < 0.35:
        is_severe = True
        severe_tags.append(f"SevereDesat({r_sat:.2f})")
    if r_sat > 1.80:
        is_severe = True
        severe_tags.append(f"SevereOversat({r_sat:.2f})")
    if red_loss > 0.45:
        is_severe = True
        severe_tags.append(f"RedLoss({red_loss:.2f})")
    if b_to_g > 0.20:
        is_severe = True
        severe_tags.append(f"BlueToGreen({b_to_g:.2f})")
    if bleed_r > 1.60 and p90 > 40.0:
        is_severe = True
        severe_tags.append(f"SevereBleed({bleed_r:.2f},P90={p90:.1f})")
    if dc > 0.22:
        is_severe = True
        severe_tags.append(f"SevereDeltaC({dc:.2f})")
    if local_peak > 0.38:
        is_severe = True
        severe_tags.append(f"LocalPeak({local_peak:.2f})")
        
    if is_severe:
        severe_items.append({
            "task_idx": t_idx,
            "orig_score": score,
            "suspicion": susp,
            "sheet": task_to_sheet.get(t_idx, "N/A"),
            "tags": severe_tags,
            "image_id": a.get("image_id", "")
        })

print(f"Total severe items: {len(severe_items)}")
for s in severe_items[:30]:
    print(f"Task #{s['task_idx']} (Orig {s['orig_score']}, Sheet {s['sheet']}): {', '.join(s['tags'])} | {s['image_id']}")
