import json
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
POOL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "cv_physical_pool_all.json"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "cv_physical_samples"
SAMPLE_RECORD_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "cv_physical_sample_60_items.json"

def main():
    print(f"Loading CV physical pool from: {POOL_FILE.name}...")
    with open(POOL_FILE, "r", encoding="utf-8") as f:
        pool = json.load(f)

    print(f"Loaded {len(pool)} items in pool.")

    # 分层抽样：共抽取 60 例（10 张看板，每张 6 组）
    # 层 1: 原 5.0 满分，仅 D-L1 (高危漏检小物体错色) -> 抽 20 例
    group1 = [x for x in pool if x["original_gpt_score"] >= 4.9 and len(x["defects"]) == 1 and x["defects"][0]["id"] == "D"]
    # 层 2: 原低分 (< 3.2)，但仅有单一 D-L1 或 E2-L1 (高危均摊) -> 抽 20 例
    group2 = [x for x in pool if x["original_gpt_score"] < 3.2 and len(x["defects"]) <= 1]
    # 层 3: 纯随机从剩余中抽取 -> 抽 20 例
    group3 = [x for x in pool if x not in group1 and x not in group2]

    random.seed(20261001_88)
    sample_g1 = random.sample(group1, min(20, len(group1)))
    sample_g2 = random.sample(group2, min(20, len(group2)))
    sample_g3 = random.sample(group3, min(20, len(group3)))

    sampled = sample_g1 + sample_g2 + sample_g3
    sampled = sorted(sampled, key=lambda x: x["task_id"])
    print(f"Sampled {len(sampled)} items (G1: {len(sample_g1)}, G2: {len(sample_g2)}, G3: {len(sample_g3)}).")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAMPLE_RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(sampled, f, ensure_ascii=False, indent=2)

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
    num_sheets = (len(sampled) + chunk_size - 1) // chunk_size
    sheet_w = 1560
    card_h = 360

    print(f"Rendering {num_sheets} inspection sheets (6 cards/sheet)...")

    for sheet_idx in range(num_sheets):
        chunk = sampled[sheet_idx * chunk_size : (sheet_idx + 1) * chunk_size]
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
            orig_score = item["original_gpt_score"]
            defects = item["defects"]
            review_note = item["review_note"]

            # 汇总缺陷简标
            if not defects:
                defect_summary = "【零缺陷放行 / 审查通过】"
            else:
                d_items = []
                for d in defects:
                    sev = f"-{d.get('severity')}" if d.get('severity') else ""
                    d_items.append(f"{d.get('id')}{sev} {d.get('name', '')}")
                defect_summary = "当前缺陷: " + "、".join(d_items)

            # 截断过长评语
            note_display = review_note if len(review_note) <= 60 else (review_note[:58] + "...")

            # 文本区
            draw.text((25, y_offset + 20), f"Task #{tid} | {stem}", fill=(20, 30, 50), font=font_title)
            draw.text((25, y_offset + 55), f"原GPT分: {orig_score}", fill=(80, 80, 80), font=font_text)
            draw.text((25, y_offset + 80), defect_summary, fill=(180, 40, 40) if defects else (30, 140, 30), font=font_text)
            draw.text((25, y_offset + 110), f"审核备注: {note_display}", fill=(60, 60, 60), font=font_text)

            # 加载并贴图
            gt_path = GT_DIR / f"{stem}.jpg"
            lc_path = LCAD_DIR / f"{stem}.png"

            img_w, img_h = 320, 320
            img_y = y_offset + 20

            # GT
            if gt_path.exists():
                gt_img = Image.open(gt_path).convert("RGB").resize((img_w, img_h), Image.Resampling.LANCZOS)
                sheet.paste(gt_img, (480, img_y))
                draw.text((485, img_y + 5), "GT 彩色真值图", fill=(0, 255, 0), font=font_text)
            else:
                draw.rectangle([480, img_y, 480 + img_w, img_y + img_h], fill=(200, 200, 200))
                draw.text((490, img_y + 140), "GT Not Found", fill=(255, 0, 0), font=font_text)

            # LCAD
            if lc_path.exists():
                lc_img = Image.open(lc_path).convert("RGB").resize((img_w, img_h), Image.Resampling.LANCZOS)
                sheet.paste(lc_img, (830, img_y))
                draw.text((835, img_y + 5), "LCAD 模型生成图", fill=(255, 200, 0), font=font_text)
            else:
                draw.rectangle([830, img_y, 830 + img_w, img_y + img_h], fill=(200, 200, 200))
                draw.text((840, img_y + 140), "LCAD Not Found", fill=(255, 0, 0), font=font_text)

            # 差分对比热力图
            if gt_path.exists() and lc_path.exists():
                from PIL import ImageChops, ImageEnhance
                diff = ImageChops.difference(gt_img, lc_img)
                diff = ImageEnhance.Color(diff).enhance(1.8)
                diff = ImageEnhance.Contrast(diff).enhance(2.2)
                sheet.paste(diff, (1180, img_y))
                draw.text((1185, img_y + 5), "2x 差分对比热力图", fill=(255, 100, 100), font=font_text)

        out_sheet_path = OUT_DIR / f"cv_sheet_{sheet_idx + 1:02d}.jpg"
        sheet.save(out_sheet_path, quality=92)
        print(f"  Saved sheet {sheet_idx + 1}/{num_sheets} -> {out_sheet_path.name}")

    print("\nAll CV physical inspection sheets generated successfully!")

if __name__ == "__main__":
    main()
