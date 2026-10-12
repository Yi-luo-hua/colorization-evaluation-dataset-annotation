import json
import numpy as np
from PIL import Image
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent
GT_DIR = Path("d:/学业文件/MCL/上色评价_数据集标注/9_14_10000GT_V1/image")
LCAD_DIR = Path("d:/学业文件/MCL/上色评价_数据集标注/9_14_10000GT_V1/model/lcad")

with open("intermediate/audits/audit_pass_4501_5000.json", "r", encoding="utf-8") as f:
    pass_tasks = json.load(f)

results = []
for t in pass_tasks:
    tid = t["task_idx"]
    img_id = t["image_id"]
    basename = t["basename"]
    score = t["score"]
    
    # 路径匹配
    gt_name = Path(basename).stem + ".jpg"
    lc_name = Path(basename).stem + ".png"
    p_gt = GT_DIR / gt_name
    p_lc = LCAD_DIR / lc_name
    
    if not p_gt.exists() or not p_lc.exists():
        continue
        
    img_gt = Image.open(p_gt).convert("RGB")
    img_lc = Image.open(p_lc).convert("RGB")
    
    if img_gt.size != img_lc.size:
        img_lc = img_lc.resize(img_gt.size, Image.Resampling.BILINEAR)
        
    arr_gt = np.array(img_gt, dtype=np.float32) / 255.0
    arr_lc = np.array(img_lc, dtype=np.float32) / 255.0
    
    # 1. 色彩对立空间
    rg_gt = arr_gt[:,:,0] - arr_gt[:,:,1]
    yb_gt = 0.5 * (arr_gt[:,:,0] + arr_gt[:,:,1]) - arr_gt[:,:,2]
    rg_lc = arr_lc[:,:,0] - arr_lc[:,:,1]
    yb_lc = 0.5 * (arr_lc[:,:,0] + arr_lc[:,:,1]) - arr_lc[:,:,2]
    
    d_rg = float(np.mean(rg_lc) - np.mean(rg_gt))
    d_yb = float(np.mean(yb_lc) - np.mean(yb_gt))
    delta_c = float(np.sqrt(d_rg**2 + d_yb**2))
    
    # 2. 饱和度
    hsv_gt = np.array(img_gt.convert("HSV"), dtype=np.float32) / 255.0
    hsv_lc = np.array(img_lc.convert("HSV"), dtype=np.float32) / 255.0
    s_gt = np.mean(hsv_gt[:,:,1])
    s_lc = np.mean(hsv_lc[:,:,1])
    r_sat = float((s_lc + 1e-4) / (s_gt + 1e-4))
    
    # 3. 红色严重脱色率 (GT为红色区域但在LCAD中丢失)
    red_mask_gt = (arr_gt[:,:,0] > 0.45) & (arr_gt[:,:,0] > arr_gt[:,:,1] * 1.35) & (arr_gt[:,:,0] > arr_gt[:,:,2] * 1.35)
    if np.sum(red_mask_gt) > 150:
        red_in_lc = arr_lc[:,:,0][red_mask_gt]
        green_in_lc = arr_lc[:,:,1][red_mask_gt]
        blue_in_lc = arr_lc[:,:,2][red_mask_gt]
        # LCAD不再是明显红色的比例
        lost_red = np.mean((red_in_lc < 0.35) | (red_in_lc < green_in_lc * 1.1) | (red_in_lc < blue_in_lc * 1.1))
        red_loss = float(lost_red)
    else:
        red_loss = 0.0
        
    # 4. 4x4 局部网格最大色偏峰值
    h, w = arr_gt.shape[:2]
    peaks = []
    for r in range(4):
        for c in range(4):
            y1, y2 = int(r * h / 4), int((r + 1) * h / 4)
            x1, x2 = int(c * w / 4), int((c + 1) * w / 4)
            sub_diff = np.sqrt(np.mean((arr_lc[y1:y2, x1:x2] - arr_gt[y1:y2, x1:x2])**2))
            peaks.append(sub_diff)
    max_peak = float(np.max(peaks))
    
    anomalies = []
    if score >= 4.0:
        anomalies.append(f"高分放行待验(Score={score})")
    if red_loss > 0.45:
        anomalies.append(f"红色局部严重脱色(RedLoss={red_loss:.2f})")
    if max_peak > 0.22:
        anomalies.append(f"局部色偏峰值过大(Peak={max_peak:.2f})")
    if r_sat < 0.45:
        anomalies.append(f"整体色彩严重欠饱和(R_sat={r_sat:.2f})")
    elif r_sat > 1.65:
        anomalies.append(f"整体色彩明显过饱和(R_sat={r_sat:.2f})")
    if delta_c > 0.12:
        anomalies.append(f"全局色偏距离过大(DeltaC={delta_c:.2f})")
        
    results.append({
        "task_idx": tid,
        "image_id": img_id,
        "basename": basename,
        "score": score,
        "delta_c": round(delta_c, 3),
        "d_rg": round(d_rg, 3),
        "d_yb": round(d_yb, 3),
        "r_sat": round(r_sat, 2),
        "red_loss": round(red_loss, 2),
        "max_peak": round(max_peak, 2),
        "anomalies": anomalies,
        "existing_defects": [d["name"] for d in t.get("defects", [])]
    })

print(f"Scanned {len(results)} tasks.")
out_scan = Path("intermediate/audits/scan_metrics_pass_4501_5000.json")
with open(out_scan, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

anom_count = sum(1 for r in results if r["anomalies"])
print(f"Detected {anom_count} pass tasks with physical anomalies or high score.")
