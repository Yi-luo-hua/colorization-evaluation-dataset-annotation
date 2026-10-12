#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_remaining_batch_sheets.py
根据 remaining_visual_audit_plan_35_batches.json 规划，
为指定的批次渲染标准三联高清大图看板（GT + LCAD + 2x 差分热力图，6 组/张）。
输出目录：intermediate/inspection_sheets/remaining_batch_{batch_no:02d}/
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
PLAN_FILE = AUDITS_DIR / "remaining_visual_audit_plan_50_batches.json"
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

def create_diff_heatmap(gt_img, lcad_img):
    gt_np = np.array(gt_img, dtype=np.float32) / 255.0
    lcad_np = np.array(lcad_img, dtype=np.float32) / 255.0
    diff = np.abs(gt_np - lcad_np)
    diff_mag = np.clip(diff * 2.0 * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(diff_mag)

def render_batch(batch_no: int, plan: dict):
    batches = {b["batch_no"]: b for b in plan["batches"]}
    if batch_no not in batches:
        print(f"Error: Batch {batch_no} not found in plan (valid range: 1..{len(batches)})")
        return False

    b_info = batches[batch_no]
    items = b_info["items"]
    out_dir = BASE_SHEETS_DIR / f"remaining_batch_{batch_no:02d}"
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

            # 标题头
            header = f"Task #{tid} | Image: {stem} | Orig Score: {score} | Peak: {peak:.2f} | ΔC: {dc:.2f}"
            draw.text((28, y + 16), header, fill=(20, 30, 50), font=font_title)

            # 现存评语摘要
            note_str = f"当前评语: {note[:65]}..." if len(note) > 65 else f"当前评语: {note}"
            draw.text((28, y + 42), note_str, fill=(100, 110, 130), font=font_sub)

            # 加载并渲染图像三联卡
            gt_path = GT_DIR / f"{stem}.jpg"
            lcad_path = LCAD_DIR / f"{stem}.png"
            if not gt_path.exists(): gt_path = GT_DIR / f"{stem}.png"
            if not lcad_path.exists(): lcad_path = LCAD_DIR / f"{stem}.jpg"

            thumb_w, thumb_h = 360, 260
            img_y = y + 70

            if gt_path.exists() and lcad_path.exists():
                gt_img = Image.open(gt_path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                lcad_img = Image.open(lcad_path).convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                diff_img = create_diff_heatmap(gt_img, lcad_img)

                # 贴图
                sheet.paste(gt_img, (28, img_y))
                sheet.paste(lcad_img, (410, img_y))
                sheet.paste(diff_img, (792, img_y))

                # 标签
                draw.text((28, img_y - 18), "GT 真值图", fill=(40, 140, 60), font=font_text)
                draw.text((410, img_y - 18), "LCAD 生成图", fill=(30, 100, 200), font=font_text)
                draw.text((792, img_y - 18), "2x 色彩差分热力图 (红/黄斑=严重偏离)", fill=(210, 50, 40), font=font_text)

                # 右侧详细辅助信息栏 (x: 1180 ~ 1530)
                info_x = 1180
                draw.rectangle([info_x - 10, img_y, sheet_w - 28, img_y + thumb_h], fill=(248, 250, 253), outline=(225, 230, 240), width=1)
                draw.text((info_x, img_y + 12), "【待核查状态与缺陷】", fill=(30, 40, 60), font=font_text)
                
                defs = item.get("current_defects", [])
                def_str = "、".join([f"{d.get('id')}-{d.get('severity','')}" for d in defs]) if defs else "无缺陷"
                draw.text((info_x, img_y + 40), f"现有缺陷: {def_str}", fill=(180, 50, 20), font=font_text)
                
                b2g = metrics.get("blue_to_green", 0.0)
                rsat = metrics.get("r_sat", 1.0)
                draw.text((info_x, img_y + 70), f"蓝绿突变: {b2g:.2f}", fill=(80, 90, 110), font=font_sub)
                draw.text((info_x, img_y + 92), f"饱和度比: {rsat:.2f}", fill=(80, 90, 110), font=font_sub)
                draw.text((info_x, img_y + 120), "定物核查要点:", fill=(40, 70, 130), font=font_text)
                draw.text((info_x, img_y + 145), "• 观察热力图高亮区域物体", fill=(90, 100, 120), font=font_sub)
                draw.text((info_x, img_y + 168), "• 锁定服饰/背景/车辆真实颜色", fill=(90, 100, 120), font=font_sub)
                draw.text((info_x, img_y + 191), "• 判定是否为常识错色 C-L2/L3", fill=(90, 100, 120), font=font_sub)
                draw.text((info_x, img_y + 214), "• 杜绝抽象代词，记录具体实体", fill=(90, 100, 120), font=font_sub)

        out_path = out_dir / f"sheet_{s_idx + 1:02d}.jpg"
        sheet.save(out_path, quality=92)
        print(f"  Saved: {out_path.name}")

    print(f"Batch {batch_no:02d} rendering complete -> {out_dir}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Render remaining inspection sheets by batch")
    parser.add_argument("--batch", type=int, default=1, help="Batch number to render (1..34)")
    parser.add_argument("--all", action="store_true", help="Render all batches")
    args = parser.parse_args()

    if not PLAN_FILE.exists():
        print(f"Error: Plan file not found: {PLAN_FILE}")
        sys.exit(1)

    with open(PLAN_FILE, "r", encoding="utf-8") as f:
        plan = json.load(f)

    if args.all:
        for b in range(1, plan["num_batches"] + 1):
            render_batch(b, plan)
    else:
        render_batch(args.batch, plan)

if __name__ == "__main__":
    main()
