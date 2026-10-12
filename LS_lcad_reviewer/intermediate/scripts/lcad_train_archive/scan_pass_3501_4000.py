"""Scan all 101 pass tasks for batch 3501-4000 with rigorous CV metrics.
"""
import json
import numpy as np
from pathlib import Path
from PIL import Image

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PASS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_3501_4000.json"
GT_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "image"
LCAD_DIR = WORKSPACE_ROOT / "9_14_10000GT_V1" / "model" / "lcad"
OUT_SCAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "scan_metrics_pass_3501_4000.json"

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

def main():
    with open(PASS_FILE, "r", encoding="utf-8") as f:
        pass_tasks = json.load(f)

    scanned_results = []
    suspicious_count = 0

    for t in pass_tasks:
        idx = t["task_idx"]
        img_id = t["image_id"]
        stem = Path(img_id).stem
        gt_path = GT_DIR / f"{stem}.jpg"
        lcad_path = LCAD_DIR / f"{stem}.png"

        if not gt_path.exists() or not lcad_path.exists():
            continue

        gt_img = Image.open(gt_path).convert("RGB")
        lcad_img = Image.open(lcad_path).convert("RGB")
        if gt_img.size != lcad_img.size:
            lcad_img = lcad_img.resize(gt_img.size, Image.Resampling.BILINEAR)

        gt_np = np.array(gt_img, dtype=np.float32)
        lcad_np = np.array(lcad_img, dtype=np.float32)

        # Opposition color space
        _, rg_gt, yb_gt = rgb_to_opp(gt_np)
        _, rg_lcad, yb_lcad = rgb_to_opp(lcad_np)

        d_rg = float(np.mean(rg_lcad) - np.mean(rg_gt))
        d_yb = float(np.mean(yb_lcad) - np.mean(yb_gt))
        delta_c = float(np.sqrt(d_rg**2 + d_yb**2) / 255.0)

        # Saturation
        sat_gt = get_sat(gt_np)
        sat_lcad = get_sat(lcad_np)
        m_s_gt = float(np.mean(sat_gt))
        m_s_lc = float(np.mean(sat_lcad))
        r_sat = float((m_s_lc + 1e-4) / (m_s_gt + 1e-4))

        # Red loss
        red_mask_gt = (gt_np[:, :, 0] > 120) & (gt_np[:, :, 0] > 1.3 * gt_np[:, :, 1]) & (gt_np[:, :, 0] > 1.3 * gt_np[:, :, 2])
        if np.sum(red_mask_gt) > 200:
            red_lc_sat = sat_lcad[red_mask_gt]
            red_loss = float(np.mean(red_lc_sat < 0.15))
        else:
            red_loss = 0.0

        # Max local peak (4x4 grid)
        h, w = gt_np.shape[:2]
        ch, cw = h // 4, w // 4
        peaks = []
        for r in range(4):
            for c in range(4):
                grid_gt = gt_np[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
                grid_lc = lcad_np[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
                _, r1, y1 = rgb_to_opp(grid_gt)
                _, r2, y2 = rgb_to_opp(grid_lc)
                peak_dist = np.sqrt((np.mean(r2) - np.mean(r1))**2 + (np.mean(y2) - np.mean(y1))**2) / 255.0
                peaks.append(peak_dist)
        max_peak = float(max(peaks)) if peaks else 0.0

        # Anomalies detection
        anomalies = []
        if red_loss > 0.40:
            anomalies.append(f"红色局部严重脱色(RedLoss={red_loss:.2f})")
        if max_peak > 0.22:
            anomalies.append(f"局部色偏峰值过大(Peak={max_peak:.2f})")
        if r_sat < 0.35 and m_s_gt > 0.15:
            anomalies.append(f"整体色彩严重欠饱和(R_sat={r_sat:.2f})")
        if delta_c > 0.12:
            anomalies.append(f"全局色偏显著(DeltaC={delta_c:.2f})")

        if anomalies:
            suspicious_count += 1

        scanned_results.append({
            "task_idx": idx,
            "image_id": img_id,
            "basename": stem,
            "score": t["score"],
            "delta_c": round(delta_c, 3),
            "d_rg": round(d_rg, 2),
            "d_yb": round(d_yb, 2),
            "r_sat": round(r_sat, 3),
            "mean_s_lc": round(m_s_lc, 3),
            "mean_s_gt": round(m_s_gt, 3),
            "red_loss": round(red_loss, 3),
            "max_peak": round(max_peak, 3),
            "anomalies": anomalies,
            "existing_defects": t["defects"]
        })

    OUT_SCAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_SCAN_FILE, "w", encoding="utf-8") as f:
        json.dump(scanned_results, f, ensure_ascii=False, indent=2)

    print(f"Scanned {len(scanned_results)} tasks.")
    print(f"Anomalies flagged by physical scan: {suspicious_count}")
    for item in scanned_results:
        if item["anomalies"]:
            print(f"  Task #{item['task_idx']} ({item['basename']}): Score={item['score']} -> {', '.join(item['anomalies'])}")

if __name__ == "__main__":
    main()
