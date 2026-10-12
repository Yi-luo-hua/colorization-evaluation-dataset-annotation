# -*- coding: utf-8 -*-
import json
from pathlib import Path

WORKSPACE = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
ALL_FILE = WORKSPACE / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
PLAN_FILE = WORKSPACE / "LS_lcad_reviewer" / "intermediate" / "audits" / "remaining_visual_audit_plan_50_batches.json"

with open(ALL_FILE, encoding='utf-8') as f:
    all_data = json.load(f)
ann_map = {ann['human_review']['task_id']: ann for ann in all_data['annotations']}

with open(PLAN_FILE, encoding='utf-8') as f:
    plan = json.load(f)

b21 = [b for b in plan['batches'] if b['batch_no'] == 21][0]

for s in range(20):
    print(f"\n==================== SHEET {s+1:02d} ====================")
    chunk = b21['items'][s*6 : (s+1)*6]
    for it in chunk:
        tid = it['task_id']
        ann = ann_map[tid]
        score = ann.get('original_gpt_score')
        note = ann.get('review_note', '')
        metrics = it.get('metrics', {})
        dc = metrics.get('delta_c', 0.0)
        peak = metrics.get('max_local_peak', 0.0)
        img = it['image_id']
        defects = ann.get('defects', [])
        d_str = ", ".join([f"{d['id']}-{d.get('severity','')}" for d in defects])
        print(f"Task #{tid} | {img} | Score: {score} | ΔC: {dc:.3f} | Peak: {peak:.3f} | Defects: [{d_str}]")
        print(f"  Note: {note}")
        for d in defects:
            print(f"    - [{d['id']}-{d.get('severity','')}] {d['name']}: {d.get('description')}")
