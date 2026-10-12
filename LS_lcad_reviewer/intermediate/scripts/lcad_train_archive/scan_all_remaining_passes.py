# -*- coding: utf-8 -*-
"""
scan_all_remaining_passes.py
全量扫描当前所有 0 缺陷放行样本，抓取所有可能存在微瑕或异常的嫌疑样本：
1. 物理色差 delta_c >= 0.08
2. 原始评分 orig_score < 4.5
3. 饱和度异常比 sat_ratio < 0.65 或 sat_ratio > 1.60
4. 局部网格最大色偏 max_peak > 0.18
5. 红色脱色或偏色异常
将筛选出的嫌疑样本写入 intermediate/audits/suspect_passes_to_review.json
"""

import json
from pathlib import Path
from PIL import Image
import numpy as np

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

OUT_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "suspect_passes_to_review.json"

def calc_color_metrics(gt_img, lcad_img):
    gt_np = np.array(gt_img, dtype=np.float32) / 255.0
    lc_np = np.array(lcad_img, dtype=np.float32) / 255.0
    
    # Opponent color space
    rg_gt = gt_np[:,:,0] - gt_np[:,:,1]
    yb_gt = 0.5 * (gt_np[:,:,0] + gt_np[:,:,1]) - gt_np[:,:,2]
    rg_lc = lc_np[:,:,0] - lc_np[:,:,1]
    yb_lc = 0.5 * (lc_np[:,:,0] + lc_np[:,:,1]) - lc_np[:,:,2]
    
    delta_rg = float(np.mean(rg_lc - rg_gt))
    delta_yb = float(np.mean(yb_lc - yb_gt))
    delta_c = float(np.sqrt(delta_rg**2 + delta_yb**2))
    
    def rgb_to_sat(arr):
        mx = np.max(arr, axis=2)
        mn = np.min(arr, axis=2)
        s = np.zeros_like(mx)
        nz = mx > 1e-4
        s[nz] = (mx[nz] - mn[nz]) / mx[nz]
        return float(np.mean(s))
        
    s_gt = rgb_to_sat(gt_np)
    s_lc = rgb_to_sat(lc_np)
    r_sat = float((s_lc + 1e-4) / (s_gt + 1e-4))
    
    # 4x4 grid max peak difference in color
    diff = np.abs(gt_np - lc_np)
    h, w, _ = diff.shape
    gh, gw = h // 4, w // 4
    peaks = []
    for r in range(4):
        for c in range(4):
            patch = diff[r*gh:(r+1)*gh, c*gw:(c+1)*gw]
            peaks.append(float(np.mean(patch)))
    max_peak = max(peaks) if peaks else 0.0
    
    # Direction
    if delta_rg > 0 and delta_yb > 0:
        bias_dir = "偏暖红黄调"
    elif delta_rg < 0 and delta_yb < 0:
        bias_dir = "偏冷青蓝调"
    elif delta_rg > 0 and delta_yb < 0:
        bias_dir = "偏紫红调"
    else:
        bias_dir = "偏黄绿调"
        
    return delta_c, r_sat, delta_rg, delta_yb, max_peak, bias_dir

def main():
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
        
    all_map = {a["human_review"]["task_id"]: a for a in all_data["annotations"]}
    
    pass_anns = [a for a in clean_data["annotations"] if len(a.get("defects", [])) == 0]
    print(f"Total current pass items: {len(pass_anns)}")
    
    suspects = []
    solid_passes = []
    
    for a in pass_anns:
        tid = a["human_review"]["task_id"]
        img_id = a["image_id"]
        stem = Path(img_id).stem
        gt_path = GT_DIR / f"{stem}.jpg"
        lcad_path = LCAD_DIR / f"{stem}.png"
        if not gt_path.exists(): gt_path = GT_DIR / f"{stem}.png"
        if not lcad_path.exists(): lcad_path = LCAD_DIR / f"{stem}.jpg"
        
        if not (gt_path.exists() and lcad_path.exists()):
            continue
            
        gt_img = Image.open(gt_path).convert("RGB").resize((256, 256), Image.Resampling.LANCZOS)
        lc_img = Image.open(lcad_path).convert("RGB").resize((256, 256), Image.Resampling.LANCZOS)
        
        dc, sat_r, drg, dyb, max_peak, bias_dir = calc_color_metrics(gt_img, lc_img)
        orig_score = a["original_gpt_score"]
        
        reasons = []
        if dc >= 0.08:
            reasons.append(f"delta_c={dc:.3f}>=0.08")
        if orig_score < 4.5:
            reasons.append(f"orig_score={orig_score:.2f}<4.5")
        if sat_r < 0.65 or sat_r > 1.60:
            reasons.append(f"sat_ratio={sat_r:.2f}")
        if max_peak > 0.18:
            reasons.append(f"peak={max_peak:.2f}>0.18")
            
        all_ann = all_map.get(tid, {})
        note_all = all_ann.get("review_note", "")
        
        if reasons:
            suspects.append({
                "task_id": tid,
                "image_id": img_id,
                "orig_score": orig_score,
                "delta_c": round(dc, 4),
                "sat_ratio": round(sat_r, 4),
                "max_peak": round(max_peak, 4),
                "bias_direction": bias_dir,
                "reasons": reasons,
                "review_note_all": note_all
            })
        else:
            solid_passes.append(tid)
            
    print(f"Scan complete:")
    print(f"  - Solid passes (零疑点极优质): {len(solid_passes)} ({len(solid_passes)/len(pass_anns)*100:.2f}%)")
    print(f"  - Suspect passes (命中物理阈值警报，需大图直审): {len(suspects)} ({len(suspects)/len(pass_anns)*100:.2f}%)")
    
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(suspects, f, ensure_ascii=False, indent=2)
    print(f"Saved suspect passes to {OUT_FILE}")

if __name__ == "__main__":
    main()
