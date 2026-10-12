"""Render high-definition 3-column inspection sheets for the 101 pass tasks in batch 3501-4000.
Generates sheets with GT + LCAD + 2x difference heatmaps.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PASS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_3501_4000.json"
SCAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "scan_metrics_pass_3501_4000.json"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "inspection_sheets_3501_4000_pass"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

def main():
    with open(PASS_FILE, "r", encoding="utf-8") as f:
        pass_tasks = json.load(f)

    with open(SCAN_FILE, "r", encoding="utf-8") as f:
        scan_results = json.load(f)

    scan_map = {item["task_idx"]: item for item in scan_results}

    # Font setup
    font_paths = ["msyh.ttc", "simsun.ttc", "simhei.ttf", "arial.ttf"]
    font = None
    font_small = None
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, 18)
            font_small = ImageFont.truetype(fp, 13)
            break
        except:
            continue
    if font is None:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    chunk_size = 6
    num_sheets = (len(pass_tasks) + chunk_size - 1) // chunk_size
    sheet_w = 1560
    card_h = 360

    print(f"Generating {num_sheets} sheets for {len(pass_tasks)} pass tasks...")

    for sheet_idx in range(num_sheets):
        chunk = pass_tasks[sheet_idx * chunk_size : (sheet_idx + 1) * chunk_size]
        sheet_h = card_h * len(chunk)
        sheet = Image.new("RGB", (sheet_w, sheet_h), (242, 244, 247))
        draw = ImageDraw.Draw(sheet)

        for i, item in enumerate(chunk):
            y_offset = i * card_h
            t_idx = item["task_idx"]
            base = item["basename"]
            score = item["score"]
            susp = item["suspicion"]
            reasons = item.get("reasons", [])
            scan_info = scan_map.get(t_idx, {})
            anomalies = scan_info.get("anomalies", [])

            # Border card
            card_border_color = (220, 50, 50) if anomalies else (200, 205, 215)
            draw.rectangle([10, y_offset + 8, sheet_w - 10, y_offset + 352], fill=(255, 255, 255), outline=card_border_color, width=2)

            # Header
            header_status = "[PHYSICAL ANOMALY FLAGGED]" if anomalies else "[SELF-CONSISTENT PASS]"
            header = f"#{t_idx} | {header_status} | File: {base} | Orig Score: {score} | Susp: {susp:.1f}"
            draw.text((25, y_offset + 14), header, fill=(20, 25, 40), font=font)

            # Subheader
            sub_parts = []
            if reasons:
                sub_parts.append(f"Reason: {'、'.join(reasons)}")
            if anomalies:
                sub_parts.append(f"Alarm: {'、'.join(anomalies)}")
            if scan_info:
                sub_parts.append(f"ΔC={scan_info.get('delta_c', 0):.2f}, Rsat={scan_info.get('r_sat', 0):.2f}, Peak={scan_info.get('max_peak', 0):.2f}")
            sub_text = " | ".join(sub_parts)
            draw.text((25, y_offset + 38), sub_text, fill=(180, 40, 40) if anomalies else (70, 80, 100), font=font_small)

            # Load images
            gt_path = GT_DIR / f"{base}.jpg"
            lc_path = LCAD_DIR / f"{base}.png"
            if not gt_path.exists() or not lc_path.exists():
                draw.text((25, y_offset + 80), f"Images missing for {base}", fill=(200, 0, 0), font=font)
                continue

            gt_img = Image.open(gt_path).convert("RGB")
            lc_img = Image.open(lc_path).convert("RGB")
            if gt_img.size != lc_img.size:
                lc_img = lc_img.resize(gt_img.size, Image.Resampling.BILINEAR)

            # Difference image
            diff_img = ImageChops.difference(gt_img, lc_img)
            diff_enhanced = diff_img.point(lambda p: min(255, p * 2))

            img_box_w, img_box_h = 470, 280
            for col_idx, (col_img, col_label) in enumerate([(gt_img, "COCO GT 真值图"), (lc_img, "LCAD 生成图"), (diff_enhanced, "2x 差分热力图")]):
                thumb = col_img.copy()
                thumb.thumbnail((img_box_w, img_box_h), Image.Resampling.BICUBIC)
                x_pos = 25 + col_idx * (img_box_w + 20)
                y_pos = y_offset + 60 + (img_box_h - thumb.height) // 2

                draw.rectangle([x_pos - 2, y_pos - 2, x_pos + thumb.width + 1, y_pos + thumb.height + 1], outline=(220, 225, 230), width=1)
                sheet.paste(thumb, (x_pos, y_pos))
                draw.text((x_pos + 6, y_pos + 6), col_label, fill=(255, 255, 255), stroke_fill=(0, 0, 0), stroke_width=2, font=font_small)

        sheet_path = OUT_DIR / f"sheet_{sheet_idx + 1:02d}.jpg"
        sheet.save(sheet_path, quality=92)
        print(f"Saved: {sheet_path.name}")

    print("All inspection sheets successfully generated!")

if __name__ == "__main__":
    main()
