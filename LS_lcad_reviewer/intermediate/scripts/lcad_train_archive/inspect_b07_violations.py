import json

with open('LS_lcad_reviewer/exports/reviewed_1_10000_all.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

b07 = plan['batches'][6]
items = b07['items']
anno_map = {a['human_review']['task_id']: a for a in data['annotations']}

violations = []
for i, it in enumerate(items):
    tid = it['task_id']
    ann = anno_map[tid]
    defs = ann.get('defects', [])
    orig = ann.get('original_gpt_score', 5.0)
    dc = it.get('metrics', {}).get('delta_c', 0.0)
    sheet_no = (i // 6) + 1
    slot_no = (i % 6) + 1
    
    if len(defs) == 0 and (orig < 4.0 or dc >= 0.08):
        violations.append((sheet_no, slot_no, tid, orig, dc, it['image_id'], it.get('current_defects', [])))

print(f'Batch 07 total violations: {len(violations)}')
out_lines = []
for v in violations:
    defs_str = ' | '.join([f"{d.get('id')}-{d.get('severity')}: {d.get('name')} ({d.get('description')})" for d in v[6]]) if v[6] else 'None'
    line = f"Sheet {v[0]:02d} Slot {v[1]} | Task #{v[2]} (orig={v[3]}, dc={v[4]:.3f}, img={v[5]})\n   Orig Defs: {defs_str}"
    print(line)
    out_lines.append(line)

with open('LS_lcad_reviewer/intermediate/audits/b07_violations_detail.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
