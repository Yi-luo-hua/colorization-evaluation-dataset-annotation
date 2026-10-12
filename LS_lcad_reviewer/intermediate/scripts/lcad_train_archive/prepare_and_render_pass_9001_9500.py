#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
prepare_and_render_pass_9001_9500.py
提取 9001-9500 批次的自洽保留任务并渲染专属三联对比看板（GT + LCAD + 2x 差分热力图）。
"""

import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
STREAM_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams" / "tasks_lcad_9001_9500_stream.json"
REVIEWED_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_9001_9500_20260930_192616.json"
OUT_AUDIT_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_9001_9500.json"
OUT_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets" / "inspection_sheets_9001_9500_pass"
INDEX_PATH = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "sheets_index_pass_9001_9500.txt"

GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)

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
    
    gt_thumb = gt_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    lcad_thumb = lcad_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    diff_thumb = diff_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    row_w = target_w * 3 + 40
    row_h = target_h + 40
    row_img = Image.new("RGB", (row_w, row_h), (255, 255, 255))
    draw = ImageDraw.Draw(row_img)
    
    font_bold = get_font(13)
    font_sub = get_font(11)
    
    alarms = task_info.get("alarms", [])
    has_alarm = len(alarms) > 0
    t_id = task_info["task_id"]
    score = task_info["score"]
    
    header_color = (180, 0, 0) if has_alarm else (0, 70, 150)
    tag_str = "[PHYSICAL ANOMALY]" if has_alarm else "[SELF-CONSISTENT PASS]"
    
    title_text = f"#{t_id} | {tag_str} | File: {basename} | Orig Score: {score}"
    draw.text((10, 4), title_text, fill=header_color, font=font_bold)
    
    metrics = task_info.get("metrics", {})
    sub_text = f"DeltaC={metrics.get('delta_c', 'N/A')}, Rsat={metrics.get('r_sat', 'N/A')}, Peak={metrics.get('peak_diff', 'N/A')}, RedLoss={metrics.get('red_loss', 'N/A')}"
    if alarms:
        sub_text += f" | Alarm: {'; '.join(alarms)}"
    draw.text((10, 20), sub_text, fill=(100, 100, 100), font=font_sub)
    
    y_off = 36
    row_img.paste(gt_thumb, (10, y_off))
    row_img.paste(lcad_thumb, (15 + target_w, y_off))
    row_img.paste(diff_thumb, (20 + target_w * 2, y_off))
    
    draw.text((14, y_off + 4), "COCO GT 真值图", fill=(255, 255, 255), font=font_sub)
    draw.text((19 + target_w, y_off + 4), "LCAD 生成图", fill=(255, 255, 255), font=font_sub)
    draw.text((24 + target_w * 2, y_off + 4), "2x 差分热力图", fill=(255, 255, 255), font=font_sub)
    
    border_color = (200, 50, 50) if has_alarm else (150, 180, 220)
    draw.rectangle([2, 2, row_w - 3, row_h - 2], outline=border_color, width=1)
    
    return row_img

def calc_metrics(gt_np, lcad_np):
    diff = np.abs(gt_np - lcad_np)
    diff_gray = np.mean(diff, axis=2)
    peak = float(np.max(diff_gray))
    
    red_mask = (gt_np[:, :, 0] > gt_np[:, :, 1] + 0.15) & (gt_np[:, :, 0] > gt_np[:, :, 2] + 0.15)
    red_loss = 0.0
    if np.sum(red_mask) > 100:
        lcad_r = lcad_np[red_mask, 0]
        gt_r = gt_np[red_mask, 0]
        red_loss = float(np.mean(np.maximum(0, gt_r - lcad_r)))
        
    gt_max = np.max(gt_np, axis=2)
    gt_min = np.min(gt_np, axis=2)
    gt_sat = np.where(gt_max > 1e-4, (gt_max - gt_min) / (gt_max + 1e-4), 0.0)
    
    lcad_max = np.max(lcad_np, axis=2)
    lcad_min = np.min(lcad_np, axis=2)
    lcad_sat = np.where(lcad_max > 1e-4, (lcad_max - lcad_min) / (lcad_max + 1e-4), 0.0)
    
    mean_gt_sat = float(np.mean(gt_sat))
    mean_lcad_sat = float(np.mean(lcad_sat))
    r_sat = float(mean_lcad_sat / (mean_gt_sat + 1e-4))
    
    delta_c = float(np.mean(np.abs(np.mean(gt_np, axis=(0,1)) - np.mean(lcad_np, axis=(0,1)))))
    
    return {
        "delta_c": round(delta_c, 3),
        "r_sat": round(r_sat, 2),
        "peak_diff": round(peak, 2),
        "red_loss": round(red_loss, 2)
    }

def main():
    print("[*] 读取批次数据与流式包...")
    with open(STREAM_FILE, "r", encoding="utf-8") as f:
        stream_data = json.load(f)
    with open(REVIEWED_FILE, "r", encoding="utf-8") as f:
        reviewed_data = json.load(f)
        
    rev_map = {a["human_review"]["task_id"]: a for a in reviewed_data["annotations"]}
    
    pass_tasks = []
    for item in stream_data:
        data = item["data"]
        tag = data.get("review_tag")
        if tag == "初审核验通过":
            t_idx = data["task_idx"]
            rev = rev_map.get(t_idx, {})
            score = rev.get("reviewed_score") if rev.get("reviewed_score") is not None else rev.get("gpt_score", 0.0)
            orig_score = rev.get("original_gpt_score", score)
            img_id = data.get("image_id", "")
            basename = Path(img_id).stem
            defects = rev.get("defects", [])
            
            stem = basename
            gt_p = GT_DIR / f"{stem}.jpg"
            lc_p = LCAD_DIR / f"{stem}.png"
            if not gt_p.exists(): gt_p = GT_DIR / f"{stem}.png"
            if not lc_p.exists(): lc_p = LCAD_DIR / f"{stem}.jpg"
            
            metrics = {}
            alarms = []
            if gt_p.exists() and lc_p.exists():
                gt_img = Image.open(gt_p).convert("RGB")
                lc_img = Image.open(lc_p).convert("RGB").resize(gt_img.size, Image.Resampling.BILINEAR)
                gt_np = np.array(gt_img, dtype=np.float32) / 255.0
                lc_np = np.array(lc_img, dtype=np.float32) / 255.0
                metrics = calc_metrics(gt_np, lc_np)
                if metrics["red_loss"] > 0.15:
                    alarms.append(f"RedLoss={metrics['red_loss']}")
                if metrics["r_sat"] < 0.65 or metrics["r_sat"] > 1.35:
                    alarms.append(f"Rsat={metrics['r_sat']}")
                if metrics["delta_c"] > 0.08:
                    alarms.append(f"DeltaC={metrics['delta_c']}")
                    
            pass_tasks.append({
                "task_id": t_idx,
                "task_idx": t_idx,
                "image_id": img_id,
                "basename": basename,
                "score": round(score, 2),
                "orig_score": round(orig_score, 2),
                "defects": defects,
                "metrics": metrics,
                "alarms": alarms,
                "suspicion": len(alarms) * 5.0
            })
            
    print(f"[*] 成功提取 {len(pass_tasks)} 个自洽保留任务 (预期 117 个)")
    
    with open(OUT_AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(pass_tasks, f, ensure_ascii=False, indent=2)
    print(f"[+] 审计元数据已保存: {OUT_AUDIT_FILE}")
    
    pass_tasks_sorted = sorted(pass_tasks, key=lambda x: x["task_id"])
    
    rows_per_sheet = 6
    total_sheets = (len(pass_tasks_sorted) + rows_per_sheet - 1) // rows_per_sheet
    index_lines = []
    
    for s_idx in range(total_sheets):
        batch = pass_tasks_sorted[s_idx * rows_per_sheet : (s_idx + 1) * rows_per_sheet]
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
