import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

GT_DIR = Path("d:/学业文件/MCL/上色评价_数据集标注/9_14_10000GT_V1/image")
LCAD_DIR = Path("d:/学业文件/MCL/上色评价_数据集标注/9_14_10000GT_V1/model/lcad")
OUT_DIR = Path("intermediate/inspection_sheets/inspection_sheets_4501_5000_pass")
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open("intermediate/audits/scan_metrics_pass_4501_5000.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

# 优先按分数降序排列，让高分样本集中在前几张看板，便于排查高危漏检
tasks = sorted(tasks, key=lambda x: x["score"], reverse=True)

def render_diff_map(img_gt, img_lc):
    arr_gt = np.array(img_gt, dtype=np.float32)
    arr_lc = np.array(img_lc, dtype=np.float32)
    diff = np.abs(arr_lc - arr_gt) * 2.0  # 2x 放大
    diff = np.clip(diff, 0, 255).astype(np.uint8)
    return Image.fromarray(diff)

def get_font(size):
    try:
        return ImageFont.truetype("msyh.ttc", size)
    except:
        try:
            return ImageFont.truetype("simhei.ttf", size)
        except:
            return ImageFont.load_default()

font_title = get_font(20)
font_sub = get_font(15)
font_label = get_font(16)

ITEMS_PER_SHEET = 6
total_sheets = (len(tasks) + ITEMS_PER_SHEET - 1) // ITEMS_PER_SHEET

ROW_H = 340
HEADER_H = 50
WIDTH = 1500
IMG_W = 440
IMG_H = 280

for s_idx in range(total_sheets):
    sheet_tasks = tasks[s_idx * ITEMS_PER_SHEET : (s_idx + 1) * ITEMS_PER_SHEET]
    sheet_h = len(sheet_tasks) * ROW_H + 20
    sheet_img = Image.new("RGB", (WIDTH, sheet_h), (255, 255, 255))
    draw = ImageDraw.Draw(sheet_img)
    
    for r_idx, t in enumerate(sheet_tasks):
        top_y = r_idx * ROW_H + 10
        tid = t["task_idx"]
        basename = t["basename"]
        score = t["score"]
        anomalies = t.get("anomalies", [])
        
        # 边框和背景
        is_alarm = len(anomalies) > 0
        bg_col = (255, 248, 248) if is_alarm else (250, 250, 250)
        border_col = (220, 50, 50) if is_alarm else (200, 200, 200)
        draw.rectangle([10, top_y, WIDTH - 10, top_y + ROW_H - 10], fill=bg_col, outline=border_col, width=2)
        
        # 头部文本
        title_txt = f"#{tid} | [{ 'PHYSICAL ANOMALY' if is_alarm else 'SELF-CONSISTENT PASS' }] | File: {basename} | Orig Score: {score}"
        draw.text((20, top_y + 6), title_txt, fill=(180, 0, 0) if is_alarm else (0, 80, 180), font=font_title)
        
        detail_txt = f"DeltaC={t['delta_c']}, Rsat={t['r_sat']}, Peak={t['max_peak']}, RedLoss={t['red_loss']}"
        if anomalies:
            detail_txt += f" | Alarm: {'; '.join(anomalies)}"
        draw.text((20, top_y + 30), detail_txt, fill=(100, 100, 100), font=font_sub)
        
        # 图像区域
        gt_path = GT_DIR / (Path(basename).stem + ".jpg")
        lc_path = LCAD_DIR / (Path(basename).stem + ".png")
        
        if gt_path.exists() and lc_path.exists():
            img_gt = Image.open(gt_path).convert("RGB")
            img_lc = Image.open(lc_path).convert("RGB")
            if img_gt.size != img_lc.size:
                img_lc = img_lc.resize(img_gt.size, Image.Resampling.BILINEAR)
                
            img_diff = render_diff_map(img_gt, img_lc)
            
            # 缩放至视口
            gt_thumb = img_gt.resize((IMG_W, IMG_H), Image.Resampling.LANCZOS)
            lc_thumb = img_lc.resize((IMG_W, IMG_H), Image.Resampling.LANCZOS)
            diff_thumb = img_diff.resize((IMG_W, IMG_H), Image.Resampling.LANCZOS)
            
            img_y = top_y + HEADER_H + 5
            x1 = 20
            x2 = x1 + IMG_W + 20
            x3 = x2 + IMG_W + 20
            
            sheet_img.paste(gt_thumb, (x1, img_y))
            sheet_img.paste(lc_thumb, (x2, img_y))
            sheet_img.paste(diff_thumb, (x3, img_y))
            
            # 标签
            draw.text((x1 + 5, img_y + 5), "COCO GT 真值图", fill=(255, 255, 255), font=font_label)
            draw.text((x2 + 5, img_y + 5), "LCAD 生成图", fill=(255, 255, 255), font=font_label)
            draw.text((x3 + 5, img_y + 5), "2x 差分热力图", fill=(255, 255, 255), font=font_label)
            
    out_file = OUT_DIR / f"sheet_{s_idx + 1:02d}.jpg"
    sheet_img.save(out_file, quality=88)
    print(f"Rendered {out_file.name} ({len(sheet_tasks)} tasks)")

print(f"All {total_sheets} pass sheets generated successfully!")
