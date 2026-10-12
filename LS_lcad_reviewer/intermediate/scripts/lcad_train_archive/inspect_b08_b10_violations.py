import json

with open('LS_lcad_reviewer/exports/reviewed_1_10000_all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

anno_map = {a['human_review']['task_id']: a for a in data['annotations']}

for b_idx in [7, 9]: # Batch 08 is idx 7, Batch 10 is idx 9
    b = plan['batches'][b_idx]
    b_no = b['batch_no']
    print(f"\n=== Batch {b_no:02d} Violations ===")
    
    for i, it in enumerate(b['items']):
        tid = it['task_id']
        ann = anno_map[tid]
        defs = ann.get('defects', [])
        orig = ann.get('original_gpt_score', 5.0)
        dc = it.get('metrics', {}).get('delta_c', 0.0)
        sheet_no = (i // 6) + 1
        slot_no = (i % 6) + 1
        
        if len(defs) == 0 and (orig < 4.0 or dc >= 0.08):
            print(f"Sheet {sheet_no:02d} Slot {slot_no} | Task #{tid} (img: {it['image_id']}): orig={orig}, dc={dc:.3f}")
