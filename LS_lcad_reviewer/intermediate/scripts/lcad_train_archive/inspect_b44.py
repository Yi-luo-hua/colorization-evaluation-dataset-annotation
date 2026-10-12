import json
import numpy as np
from PIL import Image
from pathlib import Path

WORKSPACE = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PLAN_FILE = WORKSPACE / "LS_lcad_reviewer" / "intermediate" / "audits" / "remaining_visual_audit_plan_50_batches.json"

with open(PLAN_FILE, "r", encoding="utf-8") as f:
    plan = json.load(f)

batches = {b["batch_no"]: b for b in plan["batches"]}
b44 = batches[44]
items = b44["items"]

print(f"Batch 44 has {len(items)} items. Range: Task #{items[0]['task_id']} to #{items[-1]['task_id']}")

with open(WORKSPACE / "LS_lcad_reviewer" / "tasks_lcad_10000.json", "r", encoding="utf-8") as f:
    raw_tasks = json.load(f)

summary = []

for idx, it in enumerate(items):
    t_id = it["task_id"]
    raw = raw_tasks[t_id - 1]
    rec = raw["data"]["original_record"]
    img_id = rec["file_path"]
    fname = img_id.split("/")[-1].replace(".png", ".jpg")
    gt_path = WORKSPACE / "9_14_10000GT_V1" / "image" / fname
    gen_path = WORKSPACE / "9_14_10000GT_V1" / "model" / img_id
    
    orig_score = rec.get("gpt_score", 0.0)
    orig_defects = [(d["id"], d.get("severity", "")) for d in rec.get("defects", [])]
    
    try:
        gen_pil = Image.open(gen_path).convert("RGB")
        gt_pil = Image.open(gt_path).convert("RGB").resize(gen_pil.size, Image.Resampling.BILINEAR)
        
        gt_img = np.array(gt_pil, dtype=np.float32) / 255.0
        gen_img = np.array(gen_pil, dtype=np.float32) / 255.0
        
        diff = np.abs(gt_img - gen_img)
        dc_val = float(np.mean(diff))
        
        rg_gt = gt_img[:,:,0] - gt_img[:,:,1]
        yb_gt = 0.5*(gt_img[:,:,0] + gt_img[:,:,1]) - gt_img[:,:,2]
        rg_gen = gen_img[:,:,0] - gen_img[:,:,1]
        yb_gen = 0.5*(gen_img[:,:,0] + gen_img[:,:,1]) - gen_img[:,:,2]
        
        delta_rg = float(np.mean(rg_gen) - np.mean(rg_gt))
        delta_yb = float(np.mean(yb_gen) - np.mean(yb_gt))
        delta_c = float(np.sqrt(delta_rg**2 + delta_yb**2))
        
        s_gt = np.max(gt_img, axis=-1) - np.min(gt_img, axis=-1)
        s_gen = np.max(gen_img, axis=-1) - np.min(gen_img, axis=-1)
        r_sat = float((np.mean(s_gen) + 1e-4) / (np.mean(s_gt) + 1e-4))
        
        summary.append({
            "sheet_no": (idx // 6) + 1,
            "slot_idx": idx % 6,
            "task_id": t_id,
            "image_id": img_id,
            "score": orig_score,
            "defects": orig_defects,
            "dc": dc_val,
            "delta_c": delta_c,
            "drg": delta_rg,
            "dyb": delta_yb,
            "r_sat": r_sat
        })
    except Exception as e:
        print(f"Error Task #{t_id}: {e}")

out_path = WORKSPACE / "LS_lcad_reviewer" / "intermediate" / "scripts" / "batch_44_meta_summary.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"Saved {len(summary)} items to {out_path}")
print(f"Score >= 4.5 count: {sum(1 for s in summary if s['score'] >= 4.5)}")
print(f"Score < 4.5 count: {sum(1 for s in summary if s['score'] < 4.5)}")
