import json

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

b10 = plan['batches'][9]
items = b10['items']

tids = [2002, 2102, 2137, 2141, 2147, 2156, 2163, 2171, 2183, 2190, 2192, 2204, 2206, 2213, 2224, 2227]

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
        print(f"Sheet {sheet_no:02d} Slot {slot_no} | Task #{tid} (img: {it['image_id']}): orig={orig}, dc={dc:.3f}")
        for ds in def_strs:
            print(f"   {ds}")
