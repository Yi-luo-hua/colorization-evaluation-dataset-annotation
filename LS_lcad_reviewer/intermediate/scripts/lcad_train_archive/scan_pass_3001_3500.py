import json
import numpy as np
from pathlib import Path
from PIL import Image

WORKSPACE_ROOT = Path("d:/学业文件/MCL/上色评价_数据集标注")
PASS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_3001_3500.json"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"

pass_tasks = json.loads(PASS_FILE.read_text(encoding="utf-8"))

def rgb_to_opp(img_np):
    r, g, b = img_np[:, :, 0], img_np[:, :, 1], img_np[:, :, 2]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    rg = r - g
    yb = 0.5 * (r + g) - b
    return lum, rg, yb

def get_sat(img_np):
    r, g, b = img_np[:, :, 0] / 255.0, img_np[:, :, 1] / 255.0, img_np[:, :, 2] / 255.0
    cmax = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin
    sat = np.zeros_like(cmax)
    mask = cmax > 1e-4
    sat[mask] = delta[mask] / cmax[mask]
    return sat

scanned_results = []

for t in pass_tasks:
    idx = t["task_idx"]
    img_id = t["image_id"]
    stem = Path(img_id).stem
    
    gt_path = GT_DIR / f"{stem}.jpg"
    lcad_path = LCAD_DIR / f"{stem}.png"
    
    if not gt_path.exists() or not lcad_path.exists():
        continue
        
    try:
        gt_img = Image.open(gt_path).convert("RGB")
        lcad_img = Image.open(lcad_path).convert("RGB")
        
        # 尺寸对齐
        if gt_img.size != lcad_img.size:
            lcad_img = lcad_img.resize(gt_img.size, Image.Resampling.BILINEAR)
            
        gt_np = np.array(gt_img, dtype=np.float32)
        lcad_np = np.array(lcad_img, dtype=np.float32)
        
        # 色度与偏色
        _, rg_gt, yb_gt = rgb_to_opp(gt_np)
        _, rg_lcad, yb_lcad = rgb_to_opp(lcad_np)
        
        d_rg = float(np.mean(rg_lcad) - np.mean(rg_gt))
        d_yb = float(np.mean(yb_lcad) - np.mean(yb_gt))
        delta_c = float(np.sqrt(d_rg**2 + d_yb**2) / 255.0)
        
        # 饱和度
        sat_gt = get_sat(gt_np)
        sat_lcad = get_sat(lcad_np)
        mean_sat_gt = float(np.mean(sat_gt))
        mean_sat_lcad = float(np.mean(sat_lcad))
        sat_ratio = float((mean_sat_lcad + 1e-4) / (mean_sat_gt + 1e-4))
        
        # 差分绝对值平均
        diff = np.abs(lcad_np - gt_np)
        mean_diff = float(np.mean(diff))
        
        # 判定偏色方向
        if d_rg > 0 and d_yb > 0:
            d_dir = "偏暖红黄调"
        elif d_rg < 0 and d_yb < 0:
            d_dir = "偏冷青蓝调"
        elif d_rg > 0 and d_yb < 0:
            d_dir = "偏洋红紫调"
        else:
            d_dir = "偏黄绿暖调"
            
        # 异常标记
        alarms = []
        if sat_ratio < 0.25 or mean_sat_lcad < 0.04:
            alarms.append(f"严重脱色(R_sat={sat_ratio:.2f})")
        elif sat_ratio < 0.65:
            alarms.append(f"明显欠饱和(R_sat={sat_ratio:.2f})")
        elif sat_ratio > 1.60 and mean_sat_lcad > 0.35:
            alarms.append(f"过饱和浓艳(R_sat={sat_ratio:.2f})")
            
        if delta_c > 0.15:
            alarms.append(f"严重全局偏色({d_dir}, Delta_C={delta_c:.2f})")
        elif delta_c > 0.08:
            alarms.append(f"明显全局偏色({d_dir}, Delta_C={delta_c:.2f})")
            
        if mean_diff > 35.0:
            alarms.append(f"像素级平均差分过大(Diff={mean_diff:.1f})")
            
        scanned_results.append({
            "task_idx": idx,
            "image_id": img_id,
            "score": t["score"],
            "delta_c": delta_c,
            "d_dir": d_dir,
            "sat_ratio": sat_ratio,
            "mean_diff": mean_diff,
            "alarms": alarms
        })
    except Exception as e:
        print(f"Error on task {idx}: {e}")

OUT_SCAN = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "scan_pass_3001_3500.json"
OUT_SCAN.write_text(json.dumps(scanned_results, ensure_ascii=False, indent=2), encoding="utf-8")

flagged = [r for r in scanned_results if r["alarms"]]
print(f"Scanned {len(scanned_results)} pass tasks.")
print(f"Found {len(flagged)} tasks with suspicious physical anomalies!")
for f in flagged[:15]:
    print(f"Task #{f['task_idx']} (orig score {f['score']}): {', '.join(f['alarms'])}")
if len(flagged) > 15:
    print(f"... and {len(flagged) - 15} more flagged tasks")
