#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_zero_defects_sheets.py
根据 zero_defects_batch_plan.json 规划，
为指定的批次渲染标准三联高清大图看板（GT + LCAD + 2x 差分热力图，6 组/张）。
输出目录：intermediate/inspection_sheets/zero_defects_batch_{batch_no:02d}/
"""

import argparse
import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
PLAN_FILE = AUDITS_DIR / "zero_defects_batch_plan.json"
BASE_SHEETS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets"

GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

def get_font(size=14):
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_diff_heatmap(im_gt, im_lc):
    p_gt = im_gt.load()
    p_lc = im_lc.load()
    im_diff = Image.new("RGB", im_gt.size)
    p_diff = im_diff.load()
    w, h = im_gt.size
    for py in range(h):
        for px in range(w):
            r1, g1, b1 = p_gt[px, py]
            r2, g2, b2 = p_lc[px, py]
            diff_r = min(255, abs(r1 - r2) * 2)
            diff_g = min(255, abs(g1 - g2) * 2)
            diff_b = min(255, abs(b1 - b2) * 2)
            p_diff[px, py] = (diff_r, diff_g, diff_b)
    return im_diff

def render_batch(batch_no: int, plan: dict):
    batches = {b["batch_no"]: b for b in plan["batches"]}
    if batch_no not in batches:
        print(f"Error: Batch {batch_no} not found in plan (valid range: 1..{len(batches)})")
        return False

    b_info = batches[batch_no]
    items = b_info["items"]
    out_dir = BASE_SHEETS_DIR / f"zero_defects_batch_{batch_no:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)

    font_title = get_font(18)
    font_text = get_font(13)
    font_sub = get_font(12)

    chunk_size = 6
    num_sheets = (len(items) + chunk_size - 1) // chunk_size
    sheet_w = 1560
    card_h = 360

    print(f"\nRendering Batch {batch_no:02d} ({len(items)} tasks -> {num_sheets} sheets)...")

    for s_idx in range(num_sheets):
        chunk = items[s_idx * chunk_size : (s_idx + 1) * chunk_size]
        actual_h = card_h * len(chunk)
        sheet = Image.new("RGB", (sheet_w, actual_h), (242, 244, 248))
        draw = ImageDraw.Draw(sheet)

        for i, item in enumerate(chunk):
            y = i * card_h
            # 背景卡片
            draw.rectangle([12, y + 10, sheet_w - 12, y + card_h - 10], fill=(255, 255, 255), outline=(215, 220, 230), width=2)

            tid = item["task_id"]
            img_id = item["image_id"]
            stem = Path(img_id).stem
            score = item.get("original_gpt_score", "N/A")
            note = item.get("current_review_note", "")
            metrics = item.get("metrics", {})
            peak = metrics.get("max_local_peak", 0.0)
            dc = metrics.get("delta_c", 0.0)
            diff_mean = metrics.get("diff_mean", 0.0)
            susp = item.get("suspicion", 0.0)

            # 标题头
            header = f"Task #{tid} | Image: {stem} | Orig Score: {score} | Suspicion: {susp:.1f} | ΔC: {dc:.2f} | DiffMean: {diff_mean:.1f} | Peak: {peak:.2f}"
            draw.text((28, y + 16), header, fill=(20, 30, 50), font=font_title)

            # 现存评语摘要
            note_str = f"当前评语: {note[:70]}..." if len(note) > 70 else f"当前评语: {note}"
            draw.text((28, y + 42), note_str, fill=(100, 110, 130), font=font_sub)

            # 加载并渲染图像三联卡
            gt_path = GT_DIR / f"{stem}.jpg"
            lc_path = LCAD_DIR / f"{stem}.png"

            if gt_path.exists() and lc_path.exists():
                try:
                    with Image.open(gt_path) as g_raw, Image.open(lc_path) as l_raw:
                        im_gt = g_raw.convert("RGB")
                        im_lc = l_raw.convert("RGB")
                        im_gt.thumbnail((440, 260), Image.Resampling.BILINEAR)
                        im_lc = im_lc.resize(im_gt.size, Image.Resampling.BILINEAR)

                        im_diff = create_diff_heatmap(im_gt, im_lc)

                        # 绘制子标题
                        draw.text((36, y + 68), "GT (彩色真值图)", fill=(0, 130, 60), font=font_text)
                        draw.text((540, y + 68), "LCAD (模型生成图)", fill=(190, 60, 10), font=font_text)
                        draw.text((1044, y + 68), "2x 差分热力图 (红蓝显影)", fill=(180, 20, 20), font=font_text)

                        sheet.paste(im_gt, (36, y + 92))
                        sheet.paste(im_lc, (540, y + 92))
                        sheet.paste(im_diff, (1044, y + 92))
                except Exception as e:
                    draw.text((36, y + 120), f"Error loading image: {e}", fill=(200, 0, 0), font=font_title)
            else:
                draw.text((36, y + 120), f"File missing: {gt_path} or {lc_path}", fill=(200, 0, 0), font=font_title)

        sheet_path = out_dir / f"sheet_{s_idx + 1:02d}.jpg"
        sheet.save(sheet_path, quality=92)
        print(f"  Saved: {sheet_path.name} ({len(chunk)} cards)")

    return True

def main():
    parser = argparse.ArgumentParser(description="Render zero defect visual audit sheets")
    parser.add_argument("--batch", type=int, default=1, help="Batch number to render (e.g. 1)")
    parser.add_argument("--all", action="store_true", help="Render all batches")
    args = parser.parse_args()

    if not PLAN_FILE.exists():
        print(f"Error: Plan file not found: {PLAN_FILE}")
        return

    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    if args.all:
        for b in plan["batches"]:
            render_batch(b["batch_no"], plan)
    else:
        render_batch(args.batch, plan)

if __name__ == "__main__":
    main()
