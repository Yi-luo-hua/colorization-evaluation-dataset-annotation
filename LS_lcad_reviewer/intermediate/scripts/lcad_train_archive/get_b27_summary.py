import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PLAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "remaining_visual_audit_plan_50_batches.json"

with open(PLAN_FILE, 'r', encoding='utf-8') as f:
    plan = json.load(f)

b27 = [b for b in plan['batches'] if b['batch_no'] == 27][0]
items = b27['items']

print(f"Batch 27 total tasks: {len(items)}, range: {items[0]['task_id']} ~ {items[-1]['task_id']}")

out_file = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "b27_tasks_summary.txt"
with open(out_file, 'w', encoding='utf-8') as out:
    for i in range(0, len(items), 6):
        sheet_idx = i // 6 + 1
        out.write(f"=== Sheet {sheet_idx:02d} ===\n")
        chunk = items[i:i+6]
        for t in chunk:
            task_id = t['task_id']
            img = t['image_id']
            score = t.get('gpt_score', t.get('original_gpt_score', 0))
            defects = [f"{d['id']}-{d.get('severity', '')}" for d in t.get('defects', [])]
            defects_str = ','.join(defects) if defects else 'EMPTY'
            dc = t.get('delta_c', 0.0)
            susp = t.get('suspicion_score', 0.0)
            reasons = '; '.join(t.get('reasons', []))
            out.write(f"Task #{task_id:04d} | {img} | orig_score={score:.2f} | defects=[{defects_str}] | dc={dc:.3f} | susp={susp:.1f} | reasons={reasons}\n")
        out.write('\n')

print(f"Summary written to {out_file}")
