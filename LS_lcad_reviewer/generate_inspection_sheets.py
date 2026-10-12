"""Universal Inspection Sheet Generator (6 groups per sheet).
Renders 3-column comparison cards (GT + Model Colorized + 2x Difference Map).
Supports multiple models (lcad, unicolor) and splits (train, val, test).
"""
import argparse
import json
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

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
    elif split == "val":
        base_dir = workspace_root / "10_5_val_V1"
    elif split == "test":
        base_dir = workspace_root / "10_5_test_V1"
    else:
        raise ValueError(f"Unknown split: {split}")

    gt_dir = base_dir / "image"
    model_dir = base_dir / "model" / model
    return gt_dir, model_dir


def find_model_image(model_dir: Path, base: str):
    for ext in [".png", ".jpg", ".jpeg"]:
        p = model_dir / f"{base}{ext}"
        if p.exists():
            return p
    return model_dir / f"{base}.png"


def generate_sheets(items, gt_dir, model_dir, out_dir, model_name="Model", chunk_size=6, max_sheets=None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    font_paths = ["msyh.ttc", "simsun.ttc", "simhei.ttf", "arial.ttf"]
    font = None
    font_small = None
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, 20)
            font_small = ImageFont.truetype(fp, 14)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()

    num_sheets = (len(items) + chunk_size - 1) // chunk_size
    if max_sheets:
        num_sheets = min(num_sheets, max_sheets)

    sheet_w = 1560
    card_h = 380
    generated_paths = []

    for sheet_idx in range(num_sheets):
        chunk = items[sheet_idx * chunk_size : (sheet_idx + 1) * chunk_size]
        sheet_h = card_h * len(chunk)
        sheet = Image.new("RGB", (sheet_w, sheet_h), (240, 242, 245))
        draw = ImageDraw.Draw(sheet)

        for i, item in enumerate(chunk):
            y_offset = i * card_h
            draw.rectangle([10, y_offset + 8, sheet_w - 10, y_offset + 372], fill=(255, 255, 255), outline=(200, 205, 215), width=2)

            reasons = item.get("reasons", [])
            has_alert = item.get("cv_alert", bool(reasons))
            if reasons:
                reasons_str = "、".join(reasons)
                alert_text = f"【CV遥测预警】{reasons_str}"
                alert_color = (180, 30, 30)
            else:
                alert_text = "【CV遥测平稳】物理色度自洽，请通过大图进行视觉终审确认"
                alert_color = (30, 100, 180)

            base = item.get("basename", Path(item.get("image_id", "")).stem)
            t_idx = item.get("task_idx", item.get("id", i))
            score = item.get("score", item.get("gpt_score", "N/A"))
            susp = item.get("suspicion", 0.0)

            header = f"#{t_idx} | File: {base} | 综合预警指数: {susp:.1f}"
            draw.text((25, y_offset + 14), header, fill=(20, 25, 40), font=font)
            draw.text((25, y_offset + 40), alert_text, fill=alert_color, font=font_small)

            gt_path = gt_dir / f"{base}.jpg"
            model_path = find_model_image(model_dir, base)

            box_w, box_h = 380, 270
            box_y = y_offset + 84

            # Column 1: GT
            draw.text((45, box_y - 20), "GT 真值图", fill=(80, 80, 90), font=font_small)
            if gt_path.exists():
                try:
                    img_gt = Image.open(gt_path).convert("RGB")
                    img_gt.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
                    sheet.paste(img_gt, (45, box_y))
                except Exception as e:
                    draw.text((45, box_y + 100), f"Error: {e}", fill=(200, 0, 0), font=font_small)
            else:
                draw.text((45, box_y + 100), "GT Not Found", fill=(200, 0, 0), font=font_small)

            # Column 2: Colorized Model
            draw.text((545, box_y - 20), f"{model_name.upper()} 上色图", fill=(80, 80, 90), font=font_small)
            if model_path.exists():
                try:
                    img_model = Image.open(model_path).convert("RGB")
                    img_model.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
                    sheet.paste(img_model, (545, box_y))
                except Exception as e:
                    draw.text((545, box_y + 100), f"Error: {e}", fill=(200, 0, 0), font=font_small)
            else:
                draw.text((545, box_y + 100), "Model Image Not Found", fill=(200, 0, 0), font=font_small)

            # Column 3: CIELAB 感知色差热力图 (Turbo)
            draw.text((1045, box_y - 20), "CIELAB 感知色差热力图 (Turbo)", fill=(80, 80, 90), font=font_small)
            try:
                cb_strip = np.linspace(0, 255, 60, dtype=np.uint8).reshape(1, 60)
                cb_strip = np.repeat(cb_strip, 8, axis=0)
                cb_bgr = cv2.applyColorMap(cb_strip, cv2.COLORMAP_TURBO)
                cb_rgb = cv2.cvtColor(cb_bgr, cv2.COLOR_BGR2RGB)
                cb_im = Image.fromarray(cb_rgb)
                sheet.paste(cb_im, (1310, box_y - 18))
                draw.text((1375, box_y - 20), "0→35+", fill=(140, 50, 50), font=font_small)
            except Exception:
                pass

            if gt_path.exists() and model_path.exists():
                try:
                    g_im = Image.open(gt_path).convert("RGB")
                    m_im = Image.open(model_path).convert("RGB")
                    if g_im.size != m_im.size:
                        m_im = m_im.resize(g_im.size, Image.Resampling.BILINEAR)

                    import cv2
                    g_arr = np.array(g_im)
                    m_arr = np.array(m_im)

                    g_bgr = cv2.cvtColor(g_arr, cv2.COLOR_RGB2BGR)
                    m_bgr = cv2.cvtColor(m_arr, cv2.COLOR_RGB2BGR)

                    g_lab = cv2.cvtColor(g_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
                    m_lab = cv2.cvtColor(m_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

                    # CIELAB Perceptual Delta E_ab
                    diff_l = g_lab[:, :, 0] - m_lab[:, :, 0]
                    diff_a = g_lab[:, :, 1] - m_lab[:, :, 1]
                    diff_b = g_lab[:, :, 2] - m_lab[:, :, 2]
                    delta_e = np.sqrt(diff_l ** 2 + diff_a ** 2 + diff_b ** 2)

                    # Scale: 0(Dark Navy) -> 12(Cyan) -> 22(Green) -> 28(Yellow) -> 35+(Fire Red)
                    delta_e_norm = np.clip(delta_e / 35.0 * 255.0, 0, 255).astype(np.uint8)
                    heatmap_bgr = cv2.applyColorMap(delta_e_norm, cv2.COLORMAP_TURBO)
                    heatmap_rgb = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)

                    heatmap_im = Image.fromarray(heatmap_rgb)
                    heatmap_im.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
                    sheet.paste(heatmap_im, (1045, box_y))
                except Exception as e:
                    draw.text((1045, box_y + 100), f"Diff Error: {e}", fill=(200, 0, 0), font=font_small)

        sheet_filename = f"sheet_{sheet_idx + 1:02d}.jpg"
        save_path = out_dir / sheet_filename
        sheet.save(save_path, quality=90)
        generated_paths.append(save_path)
        print(f"Generated inspection sheet: {sheet_filename} ({len(chunk)} cards)")

    return generated_paths


def main():
    parser = argparse.ArgumentParser(description="Universal Inspection Sheet Generator")
    parser.add_argument("--audit-file", required=True, help="Path to audit JSON file")
    parser.add_argument("--out-dir", required=True, help="Output directory for sheets")
    parser.add_argument("--model", default="lcad", choices=["lcad", "unicolor"], help="Target model")
    parser.add_argument("--split", default="train", choices=["train", "val", "test"], help="Dataset split")
    parser.add_argument("--chunk-size", type=int, default=6, help="Cards per sheet")
    parser.add_argument("--max-sheets", type=int, default=None, help="Max sheets to render")
    parser.add_argument("--min-suspicion", type=float, default=0.0, help="Filter items with suspicion >= min")
    args = parser.parse_args()

    audit_path = Path(args.audit_file)
    if not audit_path.exists():
        print(f"Error: Audit file not found: {audit_path}")
        sys.exit(1)

    with open(audit_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    if args.min_suspicion > 0.0:
        items = [it for it in items if it.get("suspicion", 0.0) >= args.min_suspicion]

    print(f"Preparing to render {len(items)} items for [{args.model} | {args.split}]...")
    gt_dir, model_dir = resolve_dataset_paths(args.model, args.split, WORKSPACE_ROOT)

    generate_sheets(
        items,
        gt_dir=gt_dir,
        model_dir=model_dir,
        out_dir=args.out_dir,
        model_name=args.model,
        chunk_size=args.chunk_size,
        max_sheets=args.max_sheets
    )


if __name__ == "__main__":
    main()
