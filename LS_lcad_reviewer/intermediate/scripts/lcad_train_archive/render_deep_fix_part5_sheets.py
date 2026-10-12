#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_deep_fix_part5_sheets.py
渲染 Part 5（Batch 7: 48 例 + Batch 9: 2 例，共 50 例高危样本）的高清大图对比看板
保存至 intermediate/inspection_sheets/deep_fix_part5/
"""

import json
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = r"d:\学业文件\MCL\上色评价_数据集标注"
AUDIT_FILE = os.path.join(ROOT_DIR, "LS_lcad_reviewer", "intermediate", "audits", "deep_fix_targets_all.json")
OUT_DIR = os.path.join(ROOT_DIR, "LS_lcad_reviewer", "intermediate", "inspection_sheets", "deep_fix_part5")
os.makedirs(OUT_DIR, exist_ok=True)

GT_BASE = os.path.join(ROOT_DIR, "9_14_10000GT_V1", "image")
LCAD_BASE = os.path.join(ROOT_DIR, "9_14_10000GT_V1", "model", "lcad")

def get_font(size):
    try:
        return ImageFont.truetype("msyh.ttc", size)
    except:
        return ImageFont.load_default()

def render_diff_heatmap(gt_img, lcad_img):
    gt_arr = np.array(gt_img.convert("RGB"), dtype=np.float32)
    lcad_arr = np.array(lcad_img.convert("RGB"), dtype=np.float32)
    diff = np.abs(gt_arr - lcad_arr)
    diff_boost = np.clip(diff * 2.0, 0, 255).astype(np.uint8)
    return Image.fromarray(diff_boost)

def make_card(item):
    task_id = item["task_id"]
    img_rel = item["image_id"]
    filename = os.path.basename(img_rel)
    img_stem = os.path.splitext(filename)[0]

    gt_path = os.path.join(GT_BASE, f"{img_stem}.jpg")
    lcad_path = os.path.join(LCAD_BASE, f"{img_stem}.png")

    if not os.path.exists(gt_path) or not os.path.exists(lcad_path):
        return None

    gt_img = Image.open(gt_path)
    lcad_img = Image.open(lcad_path)

    # 规范尺寸至宽 360
    target_w = 360
    h = int(gt_img.height * (target_w / gt_img.width))
    gt_resized = gt_img.resize((target_w, h), Image.Resampling.LANCZOS)
    lcad_resized = lcad_img.resize((target_w, h), Image.Resampling.LANCZOS)
    diff_img = render_diff_heatmap(gt_resized, lcad_resized)

    # 绘制卡片
    header_h = 70
    card_w = target_w * 3 + 40
    card_h = h + header_h + 30

    card = Image.new("RGB", (card_w, card_h), (255, 255, 255))
    draw = ImageDraw.Draw(card)

    font_title = get_font(18)
    font_sub = get_font(13)
    font_lbl = get_font(14)

    raw_s = item.get("raw_score", "N/A")
    raw_defs = ", ".join([d["id"] + "-" + d.get("severity", "") for d in item.get("raw_defects", [])])
    title = f"Task #{task_id} | File: {filename} | 原始GPT评分: {raw_s} | 原始GPT缺陷: [{raw_defs}]"
    draw.text((15, 10), title, fill=(30, 30, 30), font=font_title)

    sub = f"批次: Batch {item.get('batch_id')} | 待彻底复核原因: 【{item.get('fix_reason')}】 | 当前审核状态: 审查通过"
    draw.text((15, 38), sub, fill=(180, 20, 20), font=font_sub)

    # 粘贴三联图
    y_img = header_h + 15
    draw.text((15, header_h - 10), "GT (真实彩色真值图)", fill=(0, 120, 0), font=font_lbl)
    card.paste(gt_resized, (15, y_img))

    x_lcad = 15 + target_w + 10
    draw.text((x_lcad, header_h - 10), "LCAD (模型生成图)", fill=(180, 60, 0), font=font_lbl)
    card.paste(lcad_resized, (x_lcad, y_img))

    x_diff = x_lcad + target_w + 10
    draw.text((x_diff, header_h - 10), "2x 放大差分热力图", fill=(180, 0, 0), font=font_lbl)
    card.paste(diff_img, (x_diff, y_img))

    # 底部边框线
    draw.line([(0, card_h - 1), (card_w, card_h - 1)], fill=(220, 220, 220), width=2)
    return card

def main():
    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    p5 = [x for x in data if x.get("batch_id") in [7, 9]]
    print(f"Part 5 targets count: {len(p5)}")

    cards_per_sheet = 6
    sheets = (len(p5) + cards_per_sheet - 1) // cards_per_sheet
    print(f"Rendering {sheets} inspection sheets for Part 5...")

    for s_idx in range(sheets):
        batch_items = p5[s_idx * cards_per_sheet : (s_idx + 1) * cards_per_sheet]
        cards = []
        for it in batch_items:
            c = make_card(it)
            if c:
                cards.append(c)

        if not cards:
            continue

        sheet_w = max(c.width for c in cards)
        sheet_h = sum(c.height for c in cards)
        sheet_img = Image.new("RGB", (sheet_w, sheet_h), (245, 245, 245))

        curr_y = 0
        for c in cards:
            sheet_img.paste(c, (0, curr_y))
            curr_y += c.height

        out_name = f"sheet_{s_idx+1:02d}.jpg"
        out_path = os.path.join(OUT_DIR, out_name)
        sheet_img.save(out_path, "JPEG", quality=92)
        print(f"  [OK] Rendered {out_name} ({len(cards)} cards)")

    print(f"\n[DONE] Successfully rendered {sheets} sheets for Part 5 in {OUT_DIR}")

if __name__ == "__main__":
    main()
