import json

plan_file = 'LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json'
with open(plan_file, 'r', encoding='utf-8') as f:
    plan = json.load(f)

b32 = plan['batches'][31] # 0-indexed, batch 32
tasks = b32['items']
out_lines = [f'Batch 32 Total Tasks: {len(tasks)}']

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

with open('LS_lcad_reviewer/intermediate/audits/b32_tasks_summary.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))

print('Saved b32_tasks_summary.txt, total tasks:', len(tasks))
