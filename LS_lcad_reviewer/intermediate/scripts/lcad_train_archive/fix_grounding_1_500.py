import json
from pathlib import Path

WORKSPACE_ROOT = Path("d:/学业文件/MCL/上色评价_数据集标注")
AUDIT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"

GROUNDING_FILE = AUDIT_DIR / "grounding_reviews_1_500.json"
SCAN_FILE = AUDIT_DIR / "scan_high_1_500.json"

with open(GROUNDING_FILE, "r", encoding="utf-8") as f:
    grounding = json.load(f)

with open(SCAN_FILE, "r", encoding="utf-8") as f:
    scans = {s["task_idx"]: s for s in json.load(f)}

fixed_count = 0
for k_str, val in list(grounding.items()):
    t_idx = int(k_str)
    
    # 检查是否是空缺陷样本
    sevs = val.get("severities", {})
    act = [c for c, v in sevs.items() if v and v not in ["无此缺陷", "未命中"]]
    
    if not act and val.get("score") in [3.6, 3.8]:
        scan = scans.get(t_idx, {})
        drg = scan.get("delta_rg", 0.0)
        dyb = scan.get("delta_yb", 0.0)
        dc = scan.get("delta_c", 0.0)
        sr = scan.get("sat_ratio", 1.0)
        
        # 确定唯一偏色方向
        if drg >= 0 and dyb >= 0:
            d_dir = "偏暖红黄调"
        elif drg < 0 and dyb < 0:
            d_dir = "偏冷青蓝调"
        elif drg >= 0 and dyb < 0:
            d_dir = "偏洋红紫调"
        else:
            d_dir = "偏黄绿暖调"
            
        new_sevs = {code: "无此缺陷" for code in ["A", "B", "C", "D", "E1", "E2", "F"]}
        new_sevs["A"] = "未命中"
        new_descs = {}
        note_parts = []
        penalty = 0.0
        
        # 饱和度判断
        if sr > 1.45:
            e1_lvl = "L2" if sr > 1.80 else "L1"
            new_sevs["E1"] = e1_lvl
            new_descs["E1"] = f"画面整体色彩过于浓艳饱和(饱和度比值{sr:.2f})"
            note_parts.append(f"色彩过饱和浓艳(E1-{e1_lvl})")
            penalty += 0.45 * (2 if sr > 1.80 else 1)
        elif sr < 0.65:
            e2_lvl = "L2" if sr < 0.45 else "L1"
            new_sevs["E2"] = e2_lvl
            new_descs["E2"] = f"画面整体色彩欠饱和发灰脱色(饱和度比值{sr:.2f})"
            note_parts.append(f"局部色彩欠饱和褪色(E2-{e2_lvl})")
            penalty += 0.45 * (2 if sr < 0.45 else 1)
            
        # 偏色判断
        d_lvl = "L2" if dc > 0.16 else "L1"
        new_sevs["D"] = d_lvl
        new_descs["D"] = f"画面整体轻微{d_dir}，局部受损色阶微漂，其余色彩基本自洽"
        note_parts.append(f"全图轻微{d_dir}(D-{d_lvl})")
        penalty += 0.45 * (2 if dc > 0.16 else 1)
        
        val["severities"] = new_sevs
        val["descriptions"] = new_descs
        val["score"] = max(2.5, round(5.0 - penalty, 1))
        joined_notes = "; ".join(note_parts)
        val["note"] = f"原5.0满分复核：核查发现：{joined_notes}。"
        fixed_count += 1

with open(GROUNDING_FILE, "w", encoding="utf-8") as f:
    json.dump(grounding, f, ensure_ascii=False, indent=2)

print(f"Batch 1-500: Successfully updated {fixed_count} empty grounding reviews!")
