#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_and_scan_pass_5001_5500.py
提取 5001-5500 批次中的 104 个自洽保留任务，并执行底层 CV 物理色度扫描。
"""

import json
import os
from pathlib import Path
from PIL import Image
import numpy as np

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
STREAM_PATH = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams" / "tasks_lcad_5001_5500_stream.json"
AUDIT_OUT_PATH = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_5001_5500.json"
METRICS_OUT_PATH = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "scan_metrics_pass_5001_5500.json"

GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

def rgb_to_opponents(img_np):
    # img_np float [0, 1]
    r = img_np[:, :, 0]
    g = img_np[:, :, 1]
    b = img_np[:, :, 2]
    rg = r - g
    yb = 0.5 * (r + g) - b
    return rg, yb

def analyze_task(task):
    data = task["data"]
    task_id = data.get("task_idx") or task["id"]
    image_id_str = data.get("image_id", "")
    # basename
    basename = os.path.basename(image_id_str)
    stem = os.path.splitext(basename)[0]
    
    gt_path = GT_DIR / f"{stem}.jpg"
    lcad_path = LCAD_DIR / f"{stem}.png"
    
    if not gt_path.exists():
        gt_path = GT_DIR / f"{stem}.png"
    if not lcad_path.exists():
        lcad_path = LCAD_DIR / f"{stem}.jpg"
        
    if not gt_path.exists() or not lcad_path.exists():
        return {
            "task_id": task_id,
            "basename": basename,
            "error": "image_missing",
            "score": data.get("original_record", {}).get("gpt_score", 0.0)
        }
        
    gt_img = Image.open(gt_path).convert("RGB")
    lcad_img = Image.open(lcad_path).convert("RGB").resize(gt_img.size, Image.Resampling.BILINEAR)
    
    gt_np = np.array(gt_img, dtype=np.float32) / 255.0
    lcad_np = np.array(lcad_img, dtype=np.float32) / 255.0
    
    # 饱和度
    gt_hsv = gt_img.convert("HSV")
    lcad_hsv = lcad_img.convert("HSV")
    gt_s = np.array(gt_hsv, dtype=np.float32)[:, :, 1] / 255.0
    lcad_s = np.array(lcad_hsv, dtype=np.float32)[:, :, 1] / 255.0
    
    mean_s_gt = float(np.mean(gt_s))
    mean_s_lcad = float(np.mean(lcad_s))
    r_sat = (mean_s_lcad + 1e-4) / (mean_s_gt + 1e-4)
    
    # 局部色偏 & 全局色差
    diff = np.abs(gt_np - lcad_np)
    diff_rgb = float(np.mean(diff))
    
    gt_rg, gt_yb = rgb_to_opponents(gt_np)
    lcad_rg, lcad_yb = rgb_to_opponents(lcad_np)
    delta_rg = float(np.mean(lcad_rg - gt_rg))
    delta_yb = float(np.mean(lcad_yb - gt_yb))
    delta_c = float(np.sqrt(delta_rg**2 + delta_yb**2))
    
    # 4x4 局部峰值
    h, w, _ = gt_np.shape
    bh, bw = h // 4, w // 4
    peaks = []
    for i in range(4):
        for j in range(4):
            block_diff = np.mean(diff[i*bh:(i+1)*bh, j*bw:(j+1)*bw, :])
            peaks.append(block_diff)
    peak_diff = float(np.max(peaks))
    
    # 红色区域局部脱色率 RedLoss
    red_mask = (gt_np[:, :, 0] > 0.45) & (gt_np[:, :, 0] > gt_np[:, :, 1] * 1.35) & (gt_np[:, :, 0] > gt_np[:, :, 2] * 1.35)
    red_pixels = int(np.sum(red_mask))
    if red_pixels > 150:
        gt_red_s = np.mean(gt_s[red_mask])
        lcad_red_s = np.mean(lcad_s[red_mask])
        red_loss = float(max(0.0, (gt_red_s - lcad_red_s) / (gt_red_s + 1e-4)))
    else:
        red_loss = 0.0

    score = data.get("original_record", {}).get("gpt_score", 0.0)
    
    alarms = []
    if score >= 4.0:
        alarms.append(f"高分放行待验(Score={score:.2f})")
    if red_loss >= 0.40:
        alarms.append(f"红色局部严重脱色(RedLoss={red_loss:.2f})")
    if r_sat < 0.38:
        alarms.append(f"整体色彩严重欠饱和(R_sat={r_sat:.2f})")
    elif r_sat > 1.60:
        alarms.append(f"整体色彩明显过饱和(R_sat={r_sat:.2f})")
    if peak_diff >= 0.18:
        alarms.append(f"局部色偏严重(PeakDiff={peak_diff:.2f})")
        
    return {
        "task_id": task_id,
        "image_id": image_id_str,
        "basename": basename,
        "score": score,
        "delta_c": round(delta_c, 3),
        "r_sat": round(r_sat, 2),
        "peak_diff": round(peak_diff, 2),
        "red_loss": round(red_loss, 2),
        "red_pixels": red_pixels,
        "alarms": alarms,
        "defects": data.get("original_record", {}).get("defects", []),
        "review_note": data.get("review_note", "")
    }

def main():
    print("[*] 读取 streams/tasks_lcad_5001_5500_stream.json...")
    with open(STREAM_PATH, "r", encoding="utf-8") as f:
        stream_data = json.load(f)
        
    pass_tasks = []
    for item in stream_data:
        tag = item.get("data", {}).get("review_tag", "")
        if "通过" in tag:
            pass_tasks.append(item)
            
    print(f"[+] 提取出 {len(pass_tasks)} 个自洽保留任务 (预期 104 个)")
    
    # 保存提取出来的基础任务数据
    simplified_pass = []
    for t in pass_tasks:
        d = t["data"]
        simplified_pass.append({
            "task_idx": d.get("task_idx", t["id"]),
            "image_id": d.get("image_id", ""),
            "basename": os.path.basename(d.get("image_id", "")),
            "score": d.get("original_record", {}).get("gpt_score", 0.0),
            "defects": d.get("original_record", {}).get("defects", []),
            "review_note": d.get("review_note", ""),
            "review_tag": d.get("review_tag", "")
        })
    with open(AUDIT_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(simplified_pass, f, ensure_ascii=False, indent=2)
    print(f"[+] 保存至: {AUDIT_OUT_PATH}")
    
    # CV 物理扫描
    print("[*] 正在执行底层 CV 物理色度扫描...")
    metrics_list = []
    for t in pass_tasks:
        res = analyze_task(t)
        metrics_list.append(res)
        
    with open(METRICS_OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics_list, f, ensure_ascii=False, indent=2)
        
    alarm_cnt = sum(1 for m in metrics_list if m.get("alarms"))
    high_score_cnt = sum(1 for m in metrics_list if m.get("score", 0) >= 4.0)
    print(f"[+] 物理扫描完成: 共扫描 {len(metrics_list)} 个任务，其中 {alarm_cnt} 个触发物理警报，{high_score_cnt} 个评分 >= 4.0")
    print(f"[+] 扫描指标保存至: {METRICS_OUT_PATH}")

if __name__ == "__main__":
    main()
