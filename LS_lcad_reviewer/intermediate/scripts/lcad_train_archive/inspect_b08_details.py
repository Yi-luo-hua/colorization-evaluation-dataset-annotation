import json

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

b08 = plan['batches'][7]
items = b08['items']

tids = [1544, 1553, 1561, 1567, 1571, 1578, 1592, 1606, 1607, 1608, 1612, 1617, 1618, 1627, 1641, 1644, 1646, 1652, 1658, 1679, 1680, 1681, 1683, 1687, 1722, 1723, 1725, 1737, 1743, 1749, 1751, 1757]

out_lines = []
for i, it in enumerate(items):
    if it['task_id'] in tids:
        tid = it['task_id']
        orig = it['original_gpt_score']
        m = it.get('metrics', {})
        dc = m.get('delta_c', 0.0)
        sheet_no = (i // 6) + 1
        slot_no = (i % 6) + 1
        defs = it.get('current_defects', [])
        def_strs = [f"{d.get('id')}-{d.get('severity')}: {d.get('description')}" for d in defs]
        out_lines.append(f"Sheet {sheet_no:02d} Slot {slot_no} | Task #{tid} (img: {it['image_id']}): orig={orig}, dc={dc:.3f}")
        for ds in def_strs:
            out_lines.append(f"   {ds}")

with open('LS_lcad_reviewer/intermediate/audits/b08_violations_detail.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print(f"Written {len(out_lines)} lines to b08_violations_detail.txt")
