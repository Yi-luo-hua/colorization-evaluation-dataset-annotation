# -*- coding: utf-8 -*-
"""
render_spot_check_100_pass.py
从 reviewed_1_10000_clean.json 的 1,788 例 0 缺陷放行样本中，
采用 10 分段分层均匀抽样抽取 100 张样本，
渲染为标准三联高清大图看板（GT + LCAD + 2x 差分热力图，6 组/张，共 17 张看板）。
输出目录：LS_lcad_reviewer/intermediate/inspection_sheets/spot_check_100_pass/
"""

import json
import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "spot_check_100_pass"
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

def calc_color_metrics(gt_img, lcad_img):
    gt_np = np.array(gt_img, dtype=np.float32) / 255.0
    lc_np = np.array(lcad_img, dtype=np.float32) / 255.0
    
    # Delta C in opponent color space
    rg_gt = gt_np[:,:,0] - gt_np[:,:,1]
    yb_gt = 0.5 * (gt_np[:,:,0] + gt_np[:,:,1]) - gt_np[:,:,2]
    rg_lc = lc_np[:,:,0] - lc_np[:,:,1]
    yb_lc = 0.5 * (lc_np[:,:,0] + lc_np[:,:,1]) - lc_np[:,:,2]
    
    delta_rg = float(np.mean(rg_lc - rg_gt))
    delta_yb = float(np.mean(yb_lc - yb_gt))
    delta_c = float(np.sqrt(delta_rg**2 + delta_yb**2))
    
    # Saturation
    def rgb_to_sat(arr):
        mx = np.max(arr, axis=2)
        mn = np.min(arr, axis=2)
        s = np.zeros_like(mx)
        nz = mx > 1e-4
        s[nz] = (mx[nz] - mn[nz]) / mx[nz]
        return float(np.mean(s))
        
    s_gt = rgb_to_sat(gt_np)
    s_lc = rgb_to_sat(lc_np)
    r_sat = float((s_lc + 1e-4) / (s_gt + 1e-4))
    
    return delta_c, r_sat, delta_rg, delta_yb

def sample_100_passes():
    with open(CLEAN_FILE, "r", encoding="utf-8") as f:
        clean_data = json.load(f)
    with open(ALL_FILE, "r", encoding="utf-8") as f:
        all_data = json.load(f)
        
    all_map = {a["human_review"]["task_id"]: a for a in all_data["annotations"]}
    
    pass_items = []
    for ann in clean_data["annotations"]:
        if len(ann.get("defects", [])) == 0:
            tid = ann["human_review"]["task_id"]
            all_ann = all_map.get(tid, {})
            pass_items.append({
                "task_id": tid,
                "image_id": ann["image_id"],
                "file_path": ann["file_path"],
                "original_gpt_score": ann["original_gpt_score"],
                "review_note_all": all_ann.get("review_note", "")
            })
            
    print(f"Total pass items in dataset: {len(pass_items)}")
    
    # Stratified sampling across 10 intervals of 1,000 tasks
    sampled_100 = []
    for bucket_idx in range(10):
        low = bucket_idx * 1000 + 1
        high = (bucket_idx + 1) * 1000
        bucket_items = [it for it in pass_items if low <= it["task_id"] <= high]
        print(f"Bucket [{low:5d} ~ {high:5d}]: {len(bucket_items)} passes available.")
        
        # Take 10 evenly spaced items from this bucket
        if len(bucket_items) >= 10:
            indices = np.linspace(0, len(bucket_items) - 1, 10, dtype=int)
            picked = [bucket_items[idx] for idx in indices]
        else:
            picked = bucket_items
        sampled_100.extend(picked)
        
    print(f"Total sampled items: {len(sampled_100)}")
    return sampled_100

def main():
    items = sample_100_passes()
    assert len(items) == 100, f"Expected 100 items, got {len(items)}"
    
    # Fonts
    font_title = get_font(18)
    font_text = get_font(13)
    font_sub = get_font(12)
    font_badge = get_font(14)
    
    chunk_size = 6
    num_sheets = (len(items) + chunk_size - 1) // chunk_size
    sheet_w = 1560
    card_h = 360
    
    print(f"Rendering 100 spot-check passes into {num_sheets} sheets...")
    
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
            score = item.get("original_gpt_score", 5.0)
            note_all = item.get("review_note_all", "审查通过")
            
            # File paths
            gt_path = GT_DIR / f"{stem}.jpg"
            lcad_path = LCAD_DIR / f"{stem}.png"
            if not gt_path.exists(): gt_path = GT_DIR / f"{stem}.png"
            if not lcad_path.exists(): lcad_path = LCAD_DIR / f"{stem}.jpg"
            
            thumb_w, thumb_h = 360, 260
            img_y = y + 70
            
            dc, sat_r, drg, dyb = 0.0, 1.0, 0.0, 0.0
            if gt_path.exists() and lcad_path.exists():
                gt_raw = Image.open(gt_path).convert("RGB")
                lc_raw = Image.open(lcad_path).convert("RGB")
                
                gt_img = gt_raw.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                lcad_img = lc_raw.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                
                dc, sat_r, drg, dyb = calc_color_metrics(gt_img, lcad_img)
                diff_img = create_diff_heatmap(gt_img, lcad_img)
                
                sheet.paste(gt_img, (28, img_y))
                sheet.paste(lcad_img, (410, img_y))
                sheet.paste(diff_img, (792, img_y))
                
                draw.text((28, img_y - 18), "GT 真值图", fill=(40, 140, 60), font=font_text)
                draw.text((410, img_y - 18), "LCAD 生成图", fill=(30, 100, 200), font=font_text)
                draw.text((792, img_y - 18), "2x 色彩差分热力图 (红/黄斑=严重偏离)", fill=(210, 50, 40), font=font_text)
            
            # Header
            header = f"[{global_idx:03d}/100] Task #{tid} | Image: {stem} | Orig Score: {score:.2f} | ΔC: {dc:.3f} | Sat Ratio: {sat_r:.2f}"
            draw.text((28, y + 16), header, fill=(20, 30, 50), font=font_title)
            
            note_str = f"审校说明: {note_all[:65]}..." if len(note_all) > 65 else f"审校说明: {note_all}"
            draw.text((28, y + 42), note_str, fill=(100, 110, 130), font=font_sub)
            
            # Right side audit checklist
            info_x = 1180
            draw.rectangle([info_x - 10, img_y, sheet_w - 28, img_y + thumb_h], fill=(248, 250, 253), outline=(225, 230, 240), width=1)
            draw.text((info_x, img_y + 12), "【0缺陷放行专项质检】", fill=(30, 120, 60), font=font_badge)
            draw.text((info_x, img_y + 40), f"当前标记: 审查通过 (0缺陷放行)", fill=(40, 140, 60), font=font_text)
            draw.text((info_x, img_y + 65), f"物理色差 ΔC: {dc:.3f} (门槛 < 0.08)", fill=(50, 60, 80) if dc < 0.08 else (200, 50, 50), font=font_text)
            draw.text((info_x, img_y + 90), f"饱和度比值: {sat_r:.2f}", fill=(50, 60, 80), font=font_text)
            draw.text((info_x, img_y + 120), "质检核查重点:", fill=(100, 110, 130), font=font_sub)
            draw.text((info_x, img_y + 140), "• 观察2x热力图是否基本暗黑", fill=(120, 130, 145), font=font_sub)
            draw.text((info_x, img_y + 160), "• 核对是否存在服饰/背景错色", fill=(120, 130, 145), font=font_sub)
            draw.text((info_x, img_y + 180), "• 核对环境光是否严重偏色", fill=(120, 130, 145), font=font_sub)
            draw.text((info_x, img_y + 200), "• 核对是否存在网格溢色与边缘虚化", fill=(120, 130, 145), font=font_sub)
            
            manifest.append({
                "sample_idx": global_idx,
                "sheet": f"sheet_{s_idx + 1:02d}.jpg",
                "pos_in_sheet": i + 1,
                "task_id": tid,
                "image_id": img_id,
                "orig_score": score,
                "delta_c": round(dc, 4),
                "sat_ratio": round(sat_r, 4),
                "review_note_all": note_all
            })
            
        out_sheet_path = OUT_DIR / f"sheet_{s_idx + 1:02d}.jpg"
        sheet.save(out_sheet_path, quality=92)
        print(f"Saved {out_sheet_path.name} ({len(chunk)} cards)")
        
    manifest_path = OUT_DIR / "spot_check_100_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"Saved manifest to {manifest_path}")

if __name__ == "__main__":
    main()
