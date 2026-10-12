# -*- coding: utf-8 -*-
import json

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

b31 = [b for b in plan['batches'] if b['batch_no'] == 31][0]
tasks = b31['items']

with open('LS_lcad_reviewer/intermediate/audits/b31_tasks_summary.txt', 'w', encoding='utf-8') as f:
    f.write(f'Batch 31 Total Tasks: {len(tasks)}\n')
    for i, t in enumerate(tasks):
        sheet_no = (i // 6) + 1
        card_no = (i % 6) + 1
        tid = t['task_id']
        img = t['image_id']
        score = t['original_gpt_score']
        cur_note = t.get('current_review_note', '')[:50].replace('\n', ' ')
        defs = [f"{d['id']}-{d.get('severity','')}" for d in t.get('current_defects', [])]
        defs_str = ", ".join(defs)
        f.write(f'Sheet {sheet_no:02d} Card {card_no}: Task #{tid}, img: {img}, score: {score}, defects: [{defs_str}], note: {cur_note}\n')

print('Extracted', len(tasks), 'tasks to b31_tasks_summary.txt')
