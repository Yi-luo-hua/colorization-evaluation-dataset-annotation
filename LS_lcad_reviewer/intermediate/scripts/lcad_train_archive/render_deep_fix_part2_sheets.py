#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_deep_fix_part2_sheets.py
渲染 Part 2 (Batch 4: Task ID 1501-2000 的 77 个高危样本) 的专属三联高清大图看板
(GT + LCAD + 2x 差分热力图)，包含原打分、原缺陷、当前误清空/降级状态，
存入 intermediate/inspection_sheets/deep_fix_part2/
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
TARGETS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "deep_fix_targets_all.json"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "deep_fix_part2"

def main():
    with open(TARGETS_FILE, "r", encoding="utf-8") as f:
        all_targets = json.load(f)

    # 提取 Part 2: Batch 4 (1501-2000)
    part2_items = [t for t in all_targets if t["batch_id"] == 4]
    print(f"Part 2 targets count: {len(part2_items)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    font_paths = ["msyh.ttc", "simsun.ttc", "simhei.ttf", "arial.ttf"]
    font_title = None
    font_text = None
    for fp in font_paths:
        try:
            font_title = ImageFont.truetype(fp, 18)
            font_text = ImageFont.truetype(fp, 13)
            break
        except Exception:
            continue
    if font_title is None:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    chunk_size = 6
    num_sheets = (len(part2_items) + chunk_size - 1) // chunk_size
    sheet_w = 1560
    card_h = 360

    print(f"Rendering {num_sheets} inspection sheets for Part 2...")

    for sheet_idx in range(num_sheets):
        chunk = part2_items[sheet_idx * chunk_size : (sheet_idx + 1) * chunk_size]
        sheet_h = card_h * len(chunk)
        sheet = Image.new("RGB", (sheet_w, sheet_h), (242, 244, 248))
        draw = ImageDraw.Draw(sheet)

        for i, item in enumerate(chunk):
            y_offset = i * card_h
            draw.rectangle(
                [10, y_offset + 8, sheet_w - 10, y_offset + card_h - 8],
                fill=(255, 255, 255),
                outline=(210, 215, 225),
                width=2
            )

            tid = item["task_id"]
            img_id = item["image_id"]
            stem = Path(img_id).stem
            raw_score = item["raw_score"]
            raw_defects = item["raw_defects"]
            raw_d_str = "、".join([f"{d.get('id')}-{d.get('severity','')}" for d in raw_defects])
            fix_reason = item["fix_reason"]
            current_note = item["current_final_note"]

            header = f"Task #{tid} | File: {stem} | 原始GPT评分: {raw_score} | 原始GPT缺陷: [{raw_d_str}]"
            draw.text((25, y_offset + 14), header, fill=(20, 25, 45), font=font_title)

            # 标注待核验问题
            draw.text(
                (25, y_offset + 40),
                f"⚠️ 待彻底复核原因: 【{fix_reason}】  |  当前审核状态: {current_note}",
                fill=(200, 30, 20),
                font=font_text
            )

            gt_path = GT_DIR / f"{stem}.jpg"
            lc_path = LCAD_DIR / f"{stem}.png"

            if gt_path.exists() and lc_path.exists():
                im_gt = Image.open(gt_path).convert("RGB")
                im_lc = Image.open(lc_path).convert("RGB")
                im_gt.thumbnail((420, 260), Image.Resampling.BILINEAR)
                im_lc = im_lc.resize(im_gt.size, Image.Resampling.BILINEAR)

                draw.text((50, y_offset + 66), "GT (真实彩色真值图)", fill=(0, 120, 50), font=font_title)
                sheet.paste(im_gt, (50, y_offset + 92))

                draw.text((550, y_offset + 66), "LCAD (模型生成图)", fill=(190, 50, 0), font=font_title)
                sheet.paste(im_lc, (550, y_offset + 92))

                im_diff = Image.new("RGB", im_gt.size)
                p_gt = im_gt.load()
                p_lc = im_lc.load()
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

                draw.text((1050, y_offset + 66), "2x 放大差分热力图", fill=(210, 30, 30), font=font_title)
                sheet.paste(im_diff, (1050, y_offset + 92))
            else:
                draw.text((50, y_offset + 100), f"图像文件缺失: {stem}", fill=(255, 0, 0), font=font_title)

        out_path = OUT_DIR / f"sheet_{sheet_idx + 1:02d}.jpg"
        sheet.save(out_path, quality=90)
        print(f"  [OK] Rendered {out_path.name} ({len(chunk)} cards)")

    print(f"\n[DONE] Successfully rendered {num_sheets} sheets for Part 2 in {OUT_DIR}")

if __name__ == "__main__":
    main()
