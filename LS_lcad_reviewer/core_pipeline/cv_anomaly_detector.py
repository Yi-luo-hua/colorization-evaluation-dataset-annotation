"""Universal CV Physical Colorization Telemetry & Anomaly Detector (V4 Standard - Calibrated).
Completely decoupled from GPT scores and heuristic patches.
Based on empirical CIELAB color physics calibrated across 2,856 validation samples.
"""
import argparse
import json
import sys
from pathlib import Path
import cv2
import numpy as np

def get_workspace_root() -> Path:
    curr = Path(__file__).resolve().parent
    while curr != curr.parent:
        if (curr / "LS_lcad_reviewer").exists() and (curr / "9_14_10000GT_V1").exists():
            return curr
        curr = curr.parent
    return Path(r"d:\学业文件\MCL\上色评价_数据集标注")

WORKSPACE_ROOT = get_workspace_root()

def resolve_dataset_paths(model: str, split: str, workspace_root: Path):
    if split == "train":
        base_dir = workspace_root / "9_14_10000GT_V1"
        tasks_file = workspace_root / "LS_lcad_reviewer" / "tasks_pool" / "train" / f"tasks_{model}_10000.json"
        if not tasks_file.exists():
            tasks_file = workspace_root / "LS_lcad_reviewer" / f"tasks_{model}_10000.json"
    elif split == "val":
        base_dir = workspace_root / "10_5_val_V1"
        tasks_file = workspace_root / "LS_lcad_reviewer" / "tasks_pool" / "val" / f"tasks_{model}_val_1428.json"
    elif split == "test":
        base_dir = workspace_root / "10_5_test_V1"
        tasks_file = workspace_root / "LS_lcad_reviewer" / "tasks_pool" / "test" / f"tasks_{model}_test_2857.json"
    else:
        raise ValueError(f"Unknown split: {split}")

    gt_dir = base_dir / "image"
    model_dir = base_dir / "model" / model
    return gt_dir, model_dir, tasks_file

def find_model_image(model_dir: Path, base: str):
    for ext in [".png", ".jpg", ".jpeg"]:
        p = model_dir / f"{base}{ext}"
        if p.exists():
            return p
    return model_dir / f"{base}.png"

def imread_rgb_float(path: Path):
    try:
        data = np.fromfile(str(path), dtype=np.uint8)
        img_bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return None
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        return img_rgb
    except Exception:
        return None

def compute_physical_metrics(gt_rgb: np.ndarray, model_rgb: np.ndarray):
    if gt_rgb.shape != model_rgb.shape:
        model_rgb = cv2.resize(model_rgb, (gt_rgb.shape[1], gt_rgb.shape[0]), interpolation=cv2.INTER_LINEAR)

    gt_bgr = cv2.cvtColor(gt_rgb, cv2.COLOR_RGB2BGR)
    model_bgr = cv2.cvtColor(model_rgb, cv2.COLOR_RGB2BGR)
    gt_lab = cv2.cvtColor(gt_bgr, cv2.COLOR_BGR2LAB)
    model_lab = cv2.cvtColor(model_bgr, cv2.COLOR_BGR2LAB)

    # 1. Chroma
    c_gt = np.sqrt(gt_lab[:, :, 1] ** 2 + gt_lab[:, :, 2] ** 2)
    c_model = np.sqrt(model_lab[:, :, 1] ** 2 + model_lab[:, :, 2] ** 2)
    mean_c_gt = float(np.mean(c_gt))
    mean_c_model = float(np.mean(c_model))
    ratio_gray_model = float(np.mean(c_model < 3.0))

    # 2. D 全图偏色: 色度重心偏移向量 Delta ab
    delta_a_mean = float(np.mean(model_lab[:, :, 1]) - np.mean(gt_lab[:, :, 1]))
    delta_b_mean = float(np.mean(model_lab[:, :, 2]) - np.mean(gt_lab[:, :, 2]))
    delta_ab_norm = float(np.sqrt(delta_a_mean ** 2 + delta_b_mean ** 2))

    if delta_b_mean > 0 and delta_a_mean > 0:
        bias_dir = "偏暖红黄调"
    elif delta_b_mean > 0 and delta_a_mean <= 0:
        bias_dir = "偏黄绿调"
    elif delta_b_mean <= 0 and delta_a_mean <= 0:
        bias_dir = "偏冷青蓝调"
    else:
        bias_dir = "偏紫红调"

    # 3. CIELAB Perceptual Delta E
    diff_l = gt_lab[:, :, 0] - model_lab[:, :, 0]
    diff_a = gt_lab[:, :, 1] - model_lab[:, :, 1]
    diff_b = gt_lab[:, :, 2] - model_lab[:, :, 2]
    delta_e = np.sqrt(diff_l ** 2 + diff_a ** 2 + diff_b ** 2)
    mean_delta_e = float(np.mean(delta_e))
    p90_delta_e = float(np.percentile(delta_e, 90))

    # 4. C 解耦色相漂移 Delta H* (有色彩区域 C_gt > 10.0)
    chromatic_mask = (c_gt > 10.0)
    delta_c = c_model - c_gt
    if np.sum(chromatic_mask) > 100:
        delta_e_chrom = delta_e[chromatic_mask]
        delta_l_chrom = diff_l[chromatic_mask]
        delta_c_chrom = delta_c[chromatic_mask]
        h_diff_sq = np.maximum(0.0, delta_e_chrom ** 2 - delta_l_chrom ** 2 - delta_c_chrom ** 2)
        delta_h = np.sqrt(h_diff_sq)
        p90_delta_h = float(np.percentile(delta_h, 90))
        p95_delta_c_pos = float(np.percentile(np.maximum(0.0, delta_c_chrom), 95))
        p95_delta_c_neg = float(np.percentile(np.maximum(0.0, -delta_c_chrom), 95))
    else:
        p90_delta_h = 0.0
        p95_delta_c_pos = 0.0
        p95_delta_c_neg = 0.0

    # 5. B 溢色边缘色差外渗
    gt_gray = (gt_rgb[:, :, 0] * 0.299 + gt_rgb[:, :, 1] * 0.587 + gt_rgb[:, :, 2] * 0.114)
    gt_gray_u8 = (gt_gray * 255).astype(np.uint8)
    edges = cv2.Canny(gt_gray_u8, 50, 150)
    edge_band = cv2.dilate(edges, np.ones((5, 5), np.uint8))
    edge_mask = (edge_band > 0)
    if np.sum(edge_mask) > 100:
        edge_chroma_diff = np.abs(delta_c[edge_mask])
        leak_p90 = float(np.percentile(edge_chroma_diff, 90))
    else:
        leak_p90 = 0.0

    # 诊断性遥测警报生成 (基于 2856 例样本标定分位数)
    anomalies = []
    suspicion = 0.0

    # A 缺色熔断
    is_breaker_a = (ratio_gray_model > 0.90 and mean_c_model < 2.5 and mean_c_gt > 8.0)
    if is_breaker_a:
        anomalies.append(f"【A缺色熔断】全域上色失败(纯灰阶占比{ratio_gray_model*100:.0f}%, 彩度均值{mean_c_model:.1f})")
        suspicion += 10.0

    # D 全图偏色 (标定阈值: L1>=10.0, L2>=18.0)
    if delta_ab_norm >= 18.0:
        anomalies.append(f"【D全图显著偏色】{bias_dir}(||Δab||={delta_ab_norm:.1f})")
        suspicion += 4.0
    elif delta_ab_norm >= 10.0:
        anomalies.append(f"【D全图轻度偏色】{bias_dir}(||Δab||={delta_ab_norm:.1f})")
        suspicion += 2.0

    # C 错色 (标定阈值: L1>=25.0, L2>=42.0)
    if p90_delta_h >= 42.0:
        anomalies.append(f"【C局部显著错色】(P90 ΔH*={p90_delta_h:.1f})")
        suspicion += 4.0
    elif p90_delta_h >= 25.0:
        anomalies.append(f"【C疑似局部错色】(P90 ΔH*={p90_delta_h:.1f})")
        suspicion += 2.0

    # E1 局部过饱和 (标定阈值: >=32.0)
    if p95_delta_c_pos >= 32.0:
        anomalies.append(f"【E1局部浓艳过饱和】(ΔC+={p95_delta_c_pos:.1f})")
        suspicion += 2.5

    # E2 局部欠饱和 (标定阈值: >=42.0)
    if p95_delta_c_neg >= 42.0:
        anomalies.append(f"【E2局部严重褪色泛灰】(ΔC-={p95_delta_c_neg:.1f})")
        suspicion += 2.5

    # B 溢色 (标定阈值: >=38.0)
    if leak_p90 >= 38.0:
        anomalies.append(f"【B边缘显著色彩外渗】(Leak P90={leak_p90:.1f})")
        suspicion += 3.0

    needs_revision = (len(anomalies) > 0)

    return {
        "needs_revision": needs_revision,
        "suspicion": suspicion,
        "anomalies": anomalies,
        "metrics": {
            "is_breaker_a": is_breaker_a,
            "mean_c_gt": mean_c_gt,
            "mean_c_model": mean_c_model,
            "ratio_gray_model": ratio_gray_model,
            "delta_ab_norm": delta_ab_norm,
            "bias_dir": bias_dir,
            "delta_a_mean": delta_a_mean,
            "delta_b_mean": delta_b_mean,
            "mean_delta_e": mean_delta_e,
            "p90_delta_e": p90_delta_e,
            "p90_delta_h": p90_delta_h,
            "p95_delta_c_pos": p95_delta_c_pos,
            "p95_delta_c_neg": p95_delta_c_neg,
            "leak_p90": leak_p90
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Calibrated Universal CV Telemetry and Anomaly Detector")
    parser.add_argument("--model", default="lcad", choices=["lcad", "unicolor"], help="Target model")
    parser.add_argument("--split", default="val", choices=["train", "val", "test"], help="Dataset split")
    parser.add_argument("--start", type=int, default=1, help="Start task index (1-based)")
    parser.add_argument("--end", type=int, default=1000, help="End task index (1-based)")
    parser.add_argument("--tasks-file", default=None, help="Explicit tasks JSON file")
    parser.add_argument("--out-audit", default=None, help="Path to write audit JSON")
    args = parser.parse_args()

    gt_dir, model_dir, default_tasks_file = resolve_dataset_paths(args.model, args.split, WORKSPACE_ROOT)
    tasks_file = Path(args.tasks_file) if args.tasks_file else default_tasks_file

    if not tasks_file.exists():
        print(f"Error: Tasks file not found: {tasks_file}")
        sys.exit(1)

    default_out = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / f"audit_{args.model}_{args.split}_{args.start}_{args.end}.json"
    out_p = Path(args.out_audit) if args.out_audit else default_out
    out_p.parent.mkdir(parents=True, exist_ok=True)

    with open(tasks_file, "r", encoding="utf-8") as f:
        all_tasks = json.load(f)

    subset = all_tasks[args.start - 1: args.end]
    print(f"Scanning [{args.model.upper()} | {args.split.upper()}] tasks {args.start} to {args.end} ({len(subset)} tasks)...")

    audit_list = []
    alert_count = 0
    normal_count = 0

    for idx, t in enumerate(subset):
        task_idx = args.start + idx
        data = t.get("data", {})
        img_id = data.get("image_id", "")
        base = Path(img_id).stem

        gt_path = gt_dir / f"{base}.jpg"
        model_path = find_model_image(model_dir, base)

        gt_rgb = imread_rgb_float(gt_path)
        model_rgb = imread_rgb_float(model_path)

        if gt_rgb is None or model_rgb is None:
            res = {"needs_revision": False, "suspicion": 0.0, "anomalies": ["文件缺失或读取失败"], "metrics": {}}
        else:
            res = compute_physical_metrics(gt_rgb, model_rgb)

        has_alert = res.get("needs_revision", False)
        if has_alert:
            alert_count += 1
        else:
            normal_count += 1

        # 铁律：不再放行任何图片，100% 任务全量写入审计表用于大图视觉直审
        audit_list.append({
            "task_idx": task_idx,
            "image_id": img_id,
            "basename": base,
            "suspicion": res["suspicion"],
            "reasons": res["anomalies"],
            "metrics": res["metrics"],
            "cv_alert": has_alert
        })

    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(audit_list, f, ensure_ascii=False, indent=2)

    print(f"\n--- CV 物理特征与遥测计算完毕 [{args.model} | {args.split}] ---")
    print(f"全量任务数 (100% 送大图直审) : {len(audit_list)}")
    print(f"CV 预警项 (物理色差显著)     : {alert_count}")
    print(f"CV 平稳项 (大图常规直审)     : {normal_count}")
    print(f"已导出全量 100% 待审大图清单 ({len(audit_list)} 项) 至: {out_p}")

if __name__ == "__main__":
    main()
