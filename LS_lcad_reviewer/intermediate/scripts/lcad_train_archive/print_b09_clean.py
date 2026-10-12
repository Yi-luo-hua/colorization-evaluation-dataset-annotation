import json

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)
items = plan['batches'][8]['items']

out_lines = []
for i, it in enumerate(items):
    tid = it['task_id']
    orig = it['original_gpt_score']
    m = it.get('metrics', {})
    dc = m.get('delta_c', 0.0)
    sheet_no = (i // 6) + 1
    slot_no = (i % 6) + 1
    
    if orig < 4.0 or dc >= 0.08:
        defs = it.get('current_defects', [])
        def_strs = []
        for d in defs:
            def_strs.append(f"{d.get('id')}-{d.get('severity')}: {d.get('name')} ({d.get('description')})")
        def_str = ' | '.join(def_strs) if def_strs else 'None'
        out_lines.append(f"Sheet {sheet_no:02d} Slot {slot_no} | Task #{tid} (img: {it['image_id']}): orig={orig}, dc={dc:.3f}")
        if def_strs:
            out_lines.append(f"   Orig Defs: {def_str}")

with open('LS_lcad_reviewer/intermediate/audits/b09_flagged_list.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print(f"Written {len(out_lines)} lines to b09_flagged_list.txt")
