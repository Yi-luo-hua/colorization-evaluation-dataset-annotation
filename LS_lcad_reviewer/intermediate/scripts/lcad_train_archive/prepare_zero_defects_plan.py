#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_zero_defects_plan.py
提取 reviewed_1_10000_clean.json 中全部 1,439 个 0 项缺陷任务，
计算其物理差分指标与嫌疑度，并按 20 张看板/批（120 个任务/批）划分为 12 个批次。
"""

import json
import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
AUDITS_DIR.mkdir(parents=True, exist_ok=True)
PLAN_FILE = AUDITS_DIR / "zero_defects_batch_plan.json"
ALL_FILE = AUDITS_DIR / "zero_defects_remaining_all.json"

def calculate_metrics(gt_path, lcad_path):
    try:
        with Image.open(gt_path) as g_img, Image.open(lcad_path) as l_img:
            g_rgb = np.array(g_img.convert("RGB").resize((256, 256), Image.Resampling.BILINEAR), dtype=np.float32)
            l_rgb = np.array(l_img.convert("RGB").resize((256, 256), Image.Resampling.BILINEAR), dtype=np.float32)
    except Exception as e:
        return {"error": str(e), "diff_mean": 0.0, "delta_c": 0.0, "sat_ratio": 1.0, "max_local_peak": 0.0, "suspicion": 0.0}

    # 差分
    diff = np.abs(g_rgb - l_rgb)
    diff_mean = float(np.mean(diff))

    # 对立色度
    rg_g = g_rgb[:, :, 0] - g_rgb[:, :, 1]
    yb_g = 0.5 * (g_rgb[:, :, 0] + g_rgb[:, :, 1]) - g_rgb[:, :, 2]
    rg_l = l_rgb[:, :, 0] - l_rgb[:, :, 1]
    yb_l = 0.5 * (l_rgb[:, :, 0] + l_rgb[:, :, 1]) - l_rgb[:, :, 2]

    delta_rg = np.mean(rg_l - rg_g) / 255.0
    delta_yb = np.mean(yb_l - yb_g) / 255.0
    delta_c = float(np.sqrt(delta_rg**2 + delta_yb**2))

    # 饱和度比
    def calc_sat(arr):
        mx = np.max(arr, axis=2)
        mn = np.min(arr, axis=2)
        return (mx - mn) / (mx + 1e-4)

    sat_g = np.mean(calc_sat(g_rgb))
    sat_l = np.mean(calc_sat(l_rgb))
    sat_ratio = float((sat_l + 1e-4) / (sat_g + 1e-4))

    # 局部 4x4 网格色偏峰值
    h, w, _ = g_rgb.shape
    bh, bw = max(1, h // 4), max(1, w // 4)
    peaks = []
    for i in range(4):
        for j in range(4):
            sub_g = g_rgb[i*bh:(i+1)*bh, j*bw:(j+1)*bw]
            sub_l = l_rgb[i*bh:(i+1)*bh, j*bw:(j+1)*bw]
            if sub_g.size > 0:
                p_diff = np.mean(np.abs(sub_g - sub_l)) / 255.0
                peaks.append(p_diff)
    max_local_peak = float(max(peaks)) if peaks else 0.0

    return {
        "diff_mean": round(diff_mean, 2),
        "delta_c": round(delta_c, 4),
        "sat_ratio": round(sat_ratio, 3),
        "max_local_peak": round(max_local_peak, 3)
    }

def main():
    print("Loading clean dataset...")
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    annotations = clean_data.get("annotations", [])
    zero_items = []
    for idx, ann in enumerate(annotations):
        if len(ann.get("defects", [])) == 0:
            task_id = ann.get("human_review", {}).get("task_id", idx + 1)
            zero_items.append({
                "index": idx,
                "task_id": task_id,
                "image_id": ann["image_id"],
                "original_gpt_score": ann.get("original_gpt_score", ann.get("gpt_score")),
                "current_review_note": ann.get("review_note", "")
            })

    print(f"Total zero-defect items: {len(zero_items)}")
    print("Calculating physical metrics for all zero-defect items...")

    for i, item in enumerate(zero_items):
        stem = Path(item["image_id"]).stem
        gt_path = GT_DIR / f"{stem}.jpg"
        lcad_path = LCAD_DIR / f"{stem}.png"

        metrics = calculate_metrics(gt_path, lcad_path)
        item["metrics"] = metrics

        # 计算嫌疑度
        score = item["original_gpt_score"]
        diff_mean = metrics["diff_mean"]
        delta_c = metrics["delta_c"]
        sat_ratio = metrics["sat_ratio"]
        peak = metrics["max_local_peak"]

        suspicion = 0.0
        # 异常低分判定
        if score < 4.0:
            suspicion += 5.0 + (4.0 - score) * 2.0
        # 差分均值
        if diff_mean > 30.0:
            suspicion += (diff_mean - 30.0) / 10.0
        # 色度差
        if delta_c > 0.08:
            suspicion += (delta_c - 0.08) * 20.0
        # 饱和度异常
        if sat_ratio < 0.6:
            suspicion += (0.6 - sat_ratio) * 5.0
        elif sat_ratio > 1.5:
            suspicion += (sat_ratio - 1.5) * 4.0
        # 局部峰值
        if peak > 0.25:
            suspicion += (peak - 0.25) * 10.0

        item["suspicion"] = round(suspicion, 2)

        if (i + 1) % 200 == 0 or (i + 1) == len(zero_items):
            print(f"Processed {i + 1}/{len(zero_items)} tasks...")

    # 保存全量计算结果
    with open(ALL_FILE, "w", encoding="utf-8") as f:
        json.dump(zero_items, f, indent=2, ensure_ascii=False)
    print(f"Saved all items with metrics to {ALL_FILE}")

    # 排序：嫌疑度由高到低（把高危漏网之鱼优先放在最前面审查，同时保证全部覆盖）
    zero_items_sorted = sorted(zero_items, key=lambda x: x["suspicion"], reverse=True)

    # 批次划分：每张看板 6 个任务，每批 20 张看板（120 个任务）
    chunk_size = 6
    sheets_per_batch = 20
    batch_size = chunk_size * sheets_per_batch # 120

    batches = []
    total_items = len(zero_items_sorted)
    num_batches = (total_items + batch_size - 1) // batch_size

    for b_idx in range(num_batches):
        b_items = zero_items_sorted[b_idx * batch_size : (b_idx + 1) * batch_size]
        b_sheets = (len(b_items) + chunk_size - 1) // chunk_size
        batches.append({
            "batch_no": b_idx + 1,
            "total_items": len(b_items),
            "total_sheets": b_sheets,
            "sheet_start_idx": b_idx * sheets_per_batch + 1,
            "sheet_end_idx": b_idx * sheets_per_batch + b_sheets,
            "items": b_items
        })

    plan = {
        "title": "0项缺陷剩余任务大图视觉筛查全量执行规划",
        "total_zero_defect_tasks": total_items,
        "total_batches": num_batches,
        "sheets_per_batch": sheets_per_batch,
        "items_per_sheet": chunk_size,
        "batches": batches
    }

    with open(PLAN_FILE, "w", encoding="utf-8") as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully generated plan with {num_batches} batches into {PLAN_FILE}!")
    for b in batches:
        print(f"Batch {b['batch_no']:02d}: {b['total_items']} tasks, {b['total_sheets']} sheets (Sheets {b['sheet_start_idx']}..{b['sheet_end_idx']}), max suspicion: {b['items'][0]['suspicion']}, min suspicion: {b['items'][-1]['suspicion']}")

if __name__ == "__main__":
    main()
