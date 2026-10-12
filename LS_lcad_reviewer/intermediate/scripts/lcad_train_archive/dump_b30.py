import json

plan_file = 'LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json'
with open(plan_file, 'r', encoding='utf-8') as f:
    plan = json.load(f)

b30 = plan['batches'][29] # 0-indexed, batch 30
tasks = b30['items']
out_lines = [f'Batch 30 Total Tasks: {len(tasks)}']

for i, t in enumerate(tasks):
    sheet_no = i // 6 + 1
    card_no = i % 6 + 1
    t_idx = t['task_id']
    img = t['image_id']
    score = t.get('original_gpt_score', 0)
    defects = t.get('current_defects', [])
    d_str = ', '.join([f"{d.get('id','')}-{d.get('severity','')}" for d in defects])
    note = t.get('current_review_note', '')[:30]
    out_lines.append(f'Sheet {sheet_no:02d} Card {card_no}: Task #{t_idx}, img: {img}, score: {score}, defects: [{d_str}], note: {note}')

with open('LS_lcad_reviewer/intermediate/audits/b30_tasks_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print('Saved b30_tasks_summary.txt, total tasks:', len(tasks))
