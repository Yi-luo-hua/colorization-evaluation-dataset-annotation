#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_pass_sheets_5001_5500.py
为 5001-5500 批次的 104 个自洽保留任务渲染专属三联对比看板（GT + LCAD + 2x 差分热力图）。
每张看板容纳 6 组对比。
"""

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AUDIT_METRICS_PATH = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "scan_metrics_pass_5001_5500.json"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "inspection_sheets_5001_5500_pass"
INDEX_PATH = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "sheets_index_pass_5001_5500.txt"

GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

OUT_DIR.mkdir(parents=True, exist_ok=True)

# 尝试加载中文字体，找不到则用默认
def get_font(size=14):
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_diff_heatmap(gt_np, lcad_np):
    # gt_np, lcad_np: [0, 1] float
    diff = np.abs(gt_np - lcad_np)
    diff_mag = np.clip(diff * 2.0 * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(diff_mag)

def render_row(task_info, target_w=300, target_h=225):
    basename = task_info["basename"]
    stem = os.path.splitext(basename)[0]
    
    gt_path = GT_DIR / f"{stem}.jpg"
    lcad_path = LCAD_DIR / f"{stem}.png"
    if not gt_path.exists():
        gt_path = GT_DIR / f"{stem}.png"
    if not lcad_path.exists():
        lcad_path = LCAD_DIR / f"{stem}.jpg"
        
    if not gt_path.exists() or not lcad_path.exists():
        return None
        
    gt_img = Image.open(gt_path).convert("RGB")
    lcad_img = Image.open(lcad_path).convert("RGB").resize(gt_img.size, Image.Resampling.BILINEAR)
    
    gt_np = np.array(gt_img, dtype=np.float32) / 255.0
    lcad_np = np.array(lcad_img, dtype=np.float32) / 255.0
    diff_img = create_diff_heatmap(gt_np, lcad_np)
    
    # 缩放到统一展示尺寸
    gt_thumb = gt_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    lcad_thumb = lcad_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    diff_thumb = diff_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # 单行包含标题区 (高32) + 图片区 (高225) + 边距
    row_w = target_w * 3 + 40
    row_h = target_h + 40
    row_img = Image.new("RGB", (row_w, row_h), (255, 255, 255))
    draw = ImageDraw.Draw(row_img)
    
    font_bold = get_font(13)
    font_sub = get_font(11)
    
    # 标题文字
    alarms = task_info.get("alarms", [])
    has_alarm = len(alarms) > 0
    t_id = task_info["task_id"]
    score = task_info["score"]
    
    header_color = (180, 0, 0) if has_alarm else (0, 70, 150)
    tag_str = "[PHYSICAL ANOMALY]" if has_alarm else "[SELF-CONSISTENT PASS]"
    
    title_text = f"#{t_id} | {tag_str} | File: {basename} | Orig Score: {score}"
    draw.text((10, 4), title_text, fill=header_color, font=font_bold)
    
    sub_text = f"DeltaC={task_info.get('delta_c')}, Rsat={task_info.get('r_sat')}, Peak={task_info.get('peak_diff')}, RedLoss={task_info.get('red_loss')}"
    if alarms:
        sub_text += f" | Alarm: {'; '.join(alarms)}"
    draw.text((10, 20), sub_text, fill=(100, 100, 100), font=font_sub)
    
    # 贴图
    y_off = 36
    row_img.paste(gt_thumb, (10, y_off))
    row_img.paste(lcad_thumb, (15 + target_w, y_off))
    row_img.paste(diff_thumb, (20 + target_w * 2, y_off))
    
    # 标签
    draw.text((14, y_off + 4), "COCO GT 真值图", fill=(255, 255, 255), font=font_sub)
    draw.text((19 + target_w, y_off + 4), "LCAD 生成图", fill=(255, 255, 255), font=font_sub)
    draw.text((24 + target_w * 2, y_off + 4), "2x 差分热力图", fill=(255, 255, 255), font=font_sub)
    
    # 边框
    border_color = (200, 50, 50) if has_alarm else (150, 180, 220)
    draw.rectangle([2, 2, row_w - 3, row_h - 2], outline=border_color, width=1)
    
    return row_img

def main():
    print(f"[*] 读取扫描数据: {AUDIT_METRICS_PATH}...")
    with open(AUDIT_METRICS_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)
        
    # 排序：高分优先，其次报警数优先，再按 RedLoss/Peak 降序
    def sort_key(m):
        score = m.get("score", 0.0)
        alarms_cnt = len(m.get("alarms", []))
        red_loss = m.get("red_loss", 0.0)
        peak = m.get("peak_diff", 0.0)
        return (score >= 4.0, score, alarms_cnt, red_loss, peak)
        
    metrics_sorted = sorted(metrics, key=sort_key, reverse=True)
    
    print(f"[*] 准备为 {len(metrics_sorted)} 个任务渲染看板 (每张 6 组)...")
    
    rows_per_sheet = 6
    total_sheets = (len(metrics_sorted) + rows_per_sheet - 1) // rows_per_sheet
    
    index_lines = []
    
    for s_idx in range(total_sheets):
        batch = metrics_sorted[s_idx * rows_per_sheet : (s_idx + 1) * rows_per_sheet]
        rendered_rows = []
        for pos_idx, m in enumerate(batch):
            r = render_row(m)
            if r is not None:
                rendered_rows.append(r)
                alarm_str = f" [{', '.join(m.get('alarms'))}]" if m.get('alarms') else " [CLEAN]"
                index_lines.append(f"Sheet {s_idx+1:02d} Pos {pos_idx+1}: Task #{m['task_id']} ({m['basename']}) score={m['score']}{alarm_str}")
                
        if not rendered_rows:
            continue
            
        sheet_w = rendered_rows[0].width + 10
        sheet_h = sum(r.height + 6 for r in rendered_rows) + 10
        sheet_img = Image.new("RGB", (sheet_w, sheet_h), (245, 245, 245))
        
        y_curr = 6
        for r in rendered_rows:
            sheet_img.paste(r, (5, y_curr))
            y_curr += r.height + 6
            
        sheet_path = OUT_DIR / f"sheet_{s_idx+1:02d}.jpg"
        sheet_img.save(sheet_path, quality=90)
        print(f"[+] 渲染保存: {sheet_path.name} (含 {len(rendered_rows)} 组)")
        
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(index_lines) + "\n")
    print(f"[+] 索引写入: {INDEX_PATH}")
    print(f"[*] 全部 {total_sheets} 张看板渲染完成！")

if __name__ == "__main__":
    main()
