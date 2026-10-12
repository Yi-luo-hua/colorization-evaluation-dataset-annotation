# -*- coding: utf-8 -*-
"""
render_suspect_pass_sheets.py
读取 intermediate/audits/suspect_passes_to_review.json，
渲染高清三联大图看板（GT + LCAD + 2x 差分热力图，6 组/张）。
输出目录：LS_lcad_reviewer/intermediate/inspection_sheets/suspect_passes_review/
"""

import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
SUSPECT_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "suspect_passes_to_review.json"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "suspect_passes_review"
OUT_DIR.mkdir(parents=True, exist_ok=True)

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

def render_suspect_sheets():
    if not SUSPECT_FILE.exists():
        print(f"Error: {SUSPECT_FILE} not found!")
        return

    with open(SUSPECT_FILE, "r", encoding="utf-8") as f:
        items = json.load(f)

    print(f"Loaded {len(items)} suspect pass items. Rendering into sheets...")

    font_title = get_font(18)
    font_text = get_font(13)
    font_sub = get_font(12)
    font_badge = get_font(14)

    chunk_size = 6
    num_sheets = (len(items) + chunk_size - 1) // chunk_size
    sheet_w = 1560
    card_h = 360

    manifest = []

    for s_idx in range(num_sheets):
        chunk = items[s_idx * chunk_size : (s_idx + 1) * chunk_size]
        actual_h = card_h * len(chunk)
        sheet = Image.new("RGB", (sheet_w, actual_h), (242, 244, 248))
        draw = ImageDraw.Draw(sheet)

        for i, item in enumerate(chunk):
            y = i * card_h
            global_idx = s_idx * chunk_size + i + 1

            # Card background
            draw.rectangle([12, y + 10, sheet_w - 12, y + card_h - 10], fill=(255, 255, 255), outline=(215, 220, 230), width=2)

            tid = item["task_id"]
            img_id = item["image_id"]
            stem = Path(img_id).stem
            score = item.get("orig_score", 5.0)
            dc = item.get("delta_c", 0.0)
            sat_r = item.get("sat_ratio", 1.0)
            peak = item.get("max_peak", 0.0)
            bias_dir = item.get("bias_direction", "")
            reasons = item.get("reasons", [])
            note_all = item.get("review_note_all", "审查通过")

            # File paths
            gt_path = GT_DIR / f"{stem}.jpg"
            lcad_path = LCAD_DIR / f"{stem}.png"
            if not gt_path.exists(): gt_path = GT_DIR / f"{stem}.png"
            if not lcad_path.exists(): lcad_path = LCAD_DIR / f"{stem}.jpg"

            thumb_w, thumb_h = 360, 260
            img_y = y + 70

            if gt_path.exists() and lcad_path.exists():
                gt_raw = Image.open(gt_path).convert("RGB")
                lc_raw = Image.open(lcad_path).convert("RGB")

                gt_img = gt_raw.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                lcad_img = lc_raw.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                diff_img = create_diff_heatmap(gt_img, lcad_img)

                sheet.paste(gt_img, (28, img_y))
                sheet.paste(lcad_img, (410, img_y))
                sheet.paste(diff_img, (792, img_y))

                draw.text((28, img_y - 18), "GT 真值图", fill=(40, 140, 60), font=font_text)
                draw.text((410, img_y - 18), "LCAD 生成图", fill=(30, 100, 200), font=font_text)
                draw.text((792, img_y - 18), "2x 色彩差分热力图 (红/黄斑=严重偏离)", fill=(210, 50, 40), font=font_text)

            # Header
            header = f"[{global_idx:03d}/{len(items)}] Task #{tid} | Image: {stem} | Orig Score: {score:.2f} | ΔC: {dc:.3f} | Sat: {sat_r:.2f} | Peak: {peak:.2f}"
            draw.text((28, y + 16), header, fill=(20, 30, 50), font=font_title)

            reason_str = " | ".join(reasons)
            draw.text((28, y + 42), f"触发预警: {reason_str} | 方向: {bias_dir}", fill=(200, 40, 40), font=font_sub)

            # Right side audit checklist
            info_x = 1180
            draw.rectangle([info_x - 10, img_y, sheet_w - 28, img_y + thumb_h], fill=(253, 248, 248), outline=(240, 220, 220), width=1)
            draw.text((info_x, img_y + 12), "【放行嫌疑项视觉直审】", fill=(180, 40, 30), font=font_badge)
            draw.text((info_x, img_y + 38), f"原放行评语: {note_all[:45]}...", fill=(100, 110, 120), font=font_sub)
            draw.text((info_x, img_y + 60), f"物理色差 ΔC: {dc:.3f}", fill=(200, 50, 50) if dc >= 0.08 else (50, 60, 80), font=font_text)
            draw.text((info_x, img_y + 82), f"饱和度比值: {sat_r:.2f}", fill=(200, 50, 50) if sat_r < 0.65 or sat_r > 1.60 else (50, 60, 80), font=font_text)
            draw.text((info_x, img_y + 104), f"局部色偏峰值: {peak:.2f}", fill=(200, 50, 50) if peak > 0.18 else (50, 60, 80), font=font_text)
            
            draw.text((info_x, img_y + 130), "直审判断原则:", fill=(80, 90, 100), font=font_text)
            draw.text((info_x, img_y + 152), "• 若差分图高亮: 锁定具体物体判缺陷", fill=(120, 130, 145), font=font_sub)
            draw.text((info_x, img_y + 172), "• 若原分低但差分全黑且高保真: 维持放行", fill=(120, 130, 145), font=font_sub)
            draw.text((info_x, img_y + 192), "• 严防服饰/招牌常识错色漏判", fill=(120, 130, 145), font=font_sub)

            manifest.append({
                "sample_idx": global_idx,
                "sheet": f"sheet_{s_idx + 1:02d}.jpg",
                "pos_in_sheet": i + 1,
                "task_id": tid,
                "image_id": img_id,
                "orig_score": score,
                "delta_c": dc,
                "sat_ratio": sat_r,
                "max_peak": peak,
                "bias_direction": bias_dir,
                "reasons": reasons
            })

        out_sheet_path = OUT_DIR / f"sheet_{s_idx + 1:02d}.jpg"
        sheet.save(out_sheet_path, quality=92)
        print(f"Saved {out_sheet_path.name} ({len(chunk)} cards)")

    manifest_path = OUT_DIR / "suspect_sheets_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Saved suspect manifest to {manifest_path}")

if __name__ == "__main__":
    render_suspect_sheets()
