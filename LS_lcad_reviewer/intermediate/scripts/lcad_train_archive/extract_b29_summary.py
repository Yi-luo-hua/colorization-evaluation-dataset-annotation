import json

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

batch_info = next(b for b in plan['batches'] if b['batch_no'] == 29)
items = batch_info['items']

with open('LS_lcad_reviewer/exports/reviewed_1_10000_all.json', 'r', encoding='utf-8') as f:
    cur_data = json.load(f)
ann_map = {a['human_review']['task_id']: a for a in cur_data['annotations']}

out_lines = []
out_lines.append(f"Batch 29 Total Tasks: {len(items)}")
for i, t in enumerate(items):
    sheet_no = (i // 6) + 1
    pos_in_sheet = (i % 6) + 1
    tid = t['task_id']
    ann = ann_map.get(tid, {})
    gpt_score = ann.get('gpt_score', t.get('original_gpt_score'))
    defects = ann.get('defects', [])
    d_list = [f"{d.get('id','')}-{d.get('severity','')}" for d in defects]
    d_summary = ', '.join(d_list) if d_list else 'None'
    note = ann.get('review_note', '')
    img_id = t.get('image_id', ann.get('image_id', ''))
    out_lines.append(f"Sheet {sheet_no:02d} Card {pos_in_sheet}: Task #{tid}, img: {img_id}, score: {gpt_score}, defects: [{d_summary}], note: {note[:50]}")

with open('LS_lcad_reviewer/intermediate/audits/b29_tasks_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
print('Saved b29_tasks_summary.txt successfully')
