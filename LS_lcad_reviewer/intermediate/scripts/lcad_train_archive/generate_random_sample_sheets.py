#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_random_sample_sheets.py
从全量 10,000 条最终标注集（reviewed_1_10000_all.json）中随机无放回抽取 200 个样本，
生成 6 组/张的标准高清三联对比看板 (GT + LCAD + 2x 差分热力图)，
存入 intermediate/inspection_sheets/random_sample_200/。
"""

import json
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "random_sample_200"
SAMPLE_RECORD_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "random_sample_200_items.json"

ALL_FILE = EXPORTS_DIR / "reviewed_1_10000_all.json"

def main():
    print(f"Loading authoritative annotations from: {ALL_FILE.name}...")
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    annotations = data["annotations"]
    print(f"Total annotations loaded: {len(annotations)}")

    # 随机抽样 200 个
    random.seed(20261001)  # 可复现随机种子
    sampled_anns = sorted(random.sample(annotations, 200), key=lambda x: x["human_review"]["task_id"])
    print(f"Sampled {len(sampled_anns)} items.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_RECORD_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 保存抽样元数据记录
    with open(SAMPLE_RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(sampled_anns, f, ensure_ascii=False, indent=2)
    print(f"Saved sample metadata to: {SAMPLE_RECORD_FILE.name}")

    # 准备字体
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
    num_sheets = (len(sampled_anns) + chunk_size - 1) // chunk_size
    sheet_w = 1560
    card_h = 360

    print(f"Rendering {num_sheets} inspection sheets (6 cards/sheet)...")

    for sheet_idx in range(num_sheets):
        chunk = sampled_anns[sheet_idx * chunk_size : (sheet_idx + 1) * chunk_size]
        sheet_h = card_h * len(chunk)
        sheet = Image.new("RGB", (sheet_w, sheet_h), (242, 244, 248))
        draw = ImageDraw.Draw(sheet)

        for i, ann in enumerate(chunk):
            y_offset = i * card_h
            draw.rectangle(
                [10, y_offset + 8, sheet_w - 10, y_offset + card_h - 8],
                fill=(255, 255, 255),
                outline=(210, 215, 225),
                width=2
            )

            tid = ann["human_review"]["task_id"]
            img_id = ann["image_id"]
            stem = Path(img_id).stem
            orig_score = ann.get("original_gpt_score", ann.get("gpt_score", "N/A"))
            defects = ann.get("defects", [])
            review_note = ann.get("review_note", "")

            # 汇总缺陷简标
            if not defects:
                defect_summary = "【零缺陷放行 / 审查通过】"
            else:
                d_items = []
                for d in defects:
                    sev = f"-{d['severity']}" if d.get('severity') else ""
                    d_items.append(f"{d['id']}{sev} {d['name']}")
                defect_summary = "缺陷: " + "、".join(d_items)

            # 截断过长评语
            note_display = review_note if len(review_note) <= 60 else (review_note[:58] + "...")

            header = f"Task #{tid} | File: {stem} | 原始GPT分: {orig_score}"
            draw.text((25, y_offset + 14), header, fill=(20, 25, 45), font=font_title)

            # 审核结论与评语条
            status_color = (0, 130, 60) if not defects else (190, 40, 20)
            draw.text((25, y_offset + 40), f"{defect_summary}  |  评语: {note_display}", fill=status_color, font=font_text)

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

                # 2x 差分热力图
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

    print(f"\n[DONE] Successfully generated {num_sheets} random sample inspection sheets in {OUT_DIR}")

if __name__ == "__main__":
    main()
