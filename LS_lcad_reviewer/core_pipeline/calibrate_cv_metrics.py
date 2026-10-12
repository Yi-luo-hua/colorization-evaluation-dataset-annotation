"""Statistical Calibration Tool for CV Physical Colorization Metrics (V4 Standard).
Runs across a dataset split (e.g. val) to extract continuous distributions of:
1. Model Chroma (A 缺色熔断)
2. Global White Balance / Chroma Drift ||Delta ab|| (D 全图偏色)
3. Decoupled Hue Shift Delta H* (C 错色)
4. Chroma Deviation Delta C* (E1 过饱和 / E2 欠饱和)
5. Edge Color Leakage Flux (B 溢色)
6. CIELAB Perceptual Color Difference Delta E
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

def rgb_to_cielab_float(img_rgb: np.ndarray):
    # Convert float [0, 1] RGB to CIELAB: L in [0, 100], a in [-127, 127], b in [-127, 127]
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    return lab

def compute_image_metrics(gt_rgb: np.ndarray, model_rgb: np.ndarray):
    if gt_rgb.shape != model_rgb.shape:
        model_rgb = cv2.resize(model_rgb, (gt_rgb.shape[1], gt_rgb.shape[0]), interpolation=cv2.INTER_LINEAR)

    gt_lab = rgb_to_cielab_float(gt_rgb)
    model_lab = rgb_to_cielab_float(model_rgb)

    # 1. Chroma components
    c_gt = np.sqrt(gt_lab[:, :, 1] ** 2 + gt_lab[:, :, 2] ** 2)
    c_model = np.sqrt(model_lab[:, :, 1] ** 2 + model_lab[:, :, 2] ** 2)
    mean_c_gt = float(np.mean(c_gt))
    mean_c_model = float(np.mean(c_model))
    p95_c_model = float(np.percentile(c_model, 95))
    ratio_gray_model = float(np.mean(c_model < 3.0))

    # 2. D 全图偏色: 色度重心偏移向量 Delta ab
    delta_a_mean = float(np.mean(model_lab[:, :, 1]) - np.mean(gt_lab[:, :, 1]))
    delta_b_mean = float(np.mean(model_lab[:, :, 2]) - np.mean(gt_lab[:, :, 2]))
    delta_ab_norm = float(np.sqrt(delta_a_mean ** 2 + delta_b_mean ** 2))
    
    # 3. CIELAB Perceptual Color Difference Delta E
    diff_l = gt_lab[:, :, 0] - model_lab[:, :, 0]
    diff_a = gt_lab[:, :, 1] - model_lab[:, :, 1]
    diff_b = gt_lab[:, :, 2] - model_lab[:, :, 2]
    delta_e = np.sqrt(diff_l ** 2 + diff_a ** 2 + diff_b ** 2)
    mean_delta_e = float(np.mean(delta_e))
    p90_delta_e = float(np.percentile(delta_e, 90))

    # 4. C 解耦色相漂移 Delta H* (在真值有色彩区域 C_gt > 10.0 上计算)
    chromatic_mask = (c_gt > 10.0)
    delta_c = c_model - c_gt
    if np.sum(chromatic_mask) > 100:
        delta_e_chrom = delta_e[chromatic_mask]
        delta_l_chrom = diff_l[chromatic_mask]
        delta_c_chrom = delta_c[chromatic_mask]
        # Delta H* = sqrt(max(0, Delta E^2 - Delta L^2 - Delta C^2))
        h_diff_sq = np.maximum(0.0, delta_e_chrom ** 2 - delta_l_chrom ** 2 - delta_c_chrom ** 2)
        delta_h = np.sqrt(h_diff_sq)
        mean_delta_h = float(np.mean(delta_h))
        p90_delta_h = float(np.percentile(delta_h, 90))
        max_delta_h = float(np.percentile(delta_h, 99))
    else:
        mean_delta_h, p90_delta_h, max_delta_h = 0.0, 0.0, 0.0

    # 5. E1 / E2 彩度偏差 Delta C*
    if np.sum(chromatic_mask) > 100:
        delta_c_chrom = delta_c[chromatic_mask]
        p95_delta_c_pos = float(np.percentile(np.maximum(0.0, delta_c_chrom), 95))
        p95_delta_c_neg = float(np.percentile(np.maximum(0.0, -delta_c_chrom), 95))
    else:
        p95_delta_c_pos, p95_delta_c_neg = 0.0, 0.0

    # 6. B 溢色跨边界渗透: 沿 GT 亮度边界检测色度外渗
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

    return {
        "mean_c_gt": mean_c_gt,
        "mean_c_model": mean_c_model,
        "p95_c_model": p95_c_model,
        "ratio_gray_model": ratio_gray_model,
        "delta_ab_norm": delta_ab_norm,
        "delta_a_mean": delta_a_mean,
        "delta_b_mean": delta_b_mean,
        "mean_delta_e": mean_delta_e,
        "p90_delta_e": p90_delta_e,
        "p90_delta_h": p90_delta_h,
        "max_delta_h": max_delta_h,
        "p95_delta_c_pos": p95_delta_c_pos,
        "p95_delta_c_neg": p95_delta_c_neg,
        "leak_p90": leak_p90
    }

def print_distribution_table(name: str, values: list):
    arr = np.array(values)
    print(f"\n[{name}] (样本数: {len(arr)})")
    print(f"  Min   : {np.min(arr):.2f}")
    print(f"  P25   : {np.percentile(arr, 25):.2f}")
    print(f"  P50   : {np.percentile(arr, 50):.2f} (中位数)")
    print(f"  P75   : {np.percentile(arr, 75):.2f}")
    print(f"  P90   : {np.percentile(arr, 90):.2f}")
    print(f"  P95   : {np.percentile(arr, 95):.2f}")
    print(f"  Max   : {np.max(arr):.2f}")
    print(f"  均值  : {np.mean(arr):.2f} +/- {np.std(arr):.2f}")

def main():
    parser = argparse.ArgumentParser(description="Calibrate CV Physical Metrics")
    parser.add_argument("--model", default="lcad", choices=["lcad", "unicolor"], help="Target model")
    parser.add_argument("--split", default="val", choices=["train", "val", "test"], help="Split")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of images")
    args = parser.parse_args()

    val_base = WORKSPACE_ROOT / "10_5_val_V1" if args.split == "val" else WORKSPACE_ROOT / "9_14_10000GT_V1"
    gt_dir = val_base / "image"
    model_dir = val_base / "model" / args.model

    gt_files = sorted(list(gt_dir.glob("*.jpg")))
    if args.limit:
        gt_files = gt_files[:args.limit]

    print(f"======================================================================")
    print(f" 开始对 [{args.model.upper()} | {args.split.upper()}] 进行底层色彩物理指标统计校准")
    print(f" GT 目录: {gt_dir}")
    print(f" 模型目录: {model_dir}")
    print(f" 样本总数: {len(gt_files)}")
    print(f"======================================================================")

    results = []
    for idx, gt_p in enumerate(gt_files):
        base = gt_p.stem
        exts = [".png", ".jpg", ".jpeg"]
        model_p = None
        for ext in exts:
            cand = model_dir / f"{base}{ext}"
            if cand.exists():
                model_p = cand
                break
        if not model_p:
            continue

        gt_rgb = imread_rgb_float(gt_p)
        model_rgb = imread_rgb_float(model_p)
        if gt_rgb is None or model_rgb is None:
            continue

        m = compute_image_metrics(gt_rgb, model_rgb)
        m["base"] = base
        results.append(m)

        if (idx + 1) % 200 == 0 or (idx + 1) == len(gt_files):
            print(f"已处理 {idx + 1}/{len(gt_files)} 组图像...")

    print(f"\n======================================================================")
    print(f" 物理特征统计分位数分布报告 (共有效分析 {len(results)} 组真实样本)")
    print(f"======================================================================")

    print_distribution_table("1. 全图色度重心偏移 ||Δab|| (D 全图偏色)", [r["delta_ab_norm"] for r in results])
    print_distribution_table("2. 解耦色相角漂移 P90 ΔH* (C 错色特征)", [r["p90_delta_h"] for r in results])
    print_distribution_table("3. 局部正向彩度超额 P95 ΔC+ (E1 过饱和特征)", [r["p95_delta_c_pos"] for r in results])
    print_distribution_table("4. 局部负向彩度亏缺 P95 ΔC- (E2 欠饱和特征)", [r["p95_delta_c_neg"] for r in results])
    print_distribution_table("5. 边缘色差外渗 P90 (B 溢色渗透特征)", [r["leak_p90"] for r in results])
    print_distribution_table("6. CIELAB 感知总色差均值 Mean ΔE", [r["mean_delta_e"] for r in results])
    print_distribution_table("7. 模型全图像素彩度均值 Mean C_model (A 缺色参考)", [r["mean_c_model"] for r in results])
    print_distribution_table("8. 模型灰阶像素(<3.0)占比 (A 缺色熔断参考)", [r["ratio_gray_model"] for r in results])

    out_json = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / f"calibration_stats_{args.model}_{args.split}.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n全量校准原始数据已保存至: {out_json}")

if __name__ == "__main__":
    main()
