import json

data = json.load(open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', encoding='utf-8'))
b42 = data['batches'][41] # Batch 42
raw_tasks = json.load(open('LS_lcad_reviewer/tasks_lcad_10000.json', encoding='utf-8'))

tasks_info = []
for tid in b42['task_ids']:
    t = raw_tasks[tid-1]
    orig = t['data']['original_record']
    score = orig['gpt_score']
    img = orig['image_id']
    defs = [d['id'] + '-' + str(d.get('severity', '')) + ': ' + d.get('description', '') for d in orig.get('defects', [])]
    tasks_info.append({
        'task_id': tid,
        'image_id': img,
        'score': score,
        'defects': defs
    })

print(f"Total tasks: {len(tasks_info)}")
low_scores = [t for t in tasks_info if t['score'] < 4.5]
high_scores = [t for t in tasks_info if t['score'] >= 4.5]
print(f"High scores (>=4.5): {len(high_scores)}")
print(f"Low scores (<4.5): {len(low_scores)}")

with open('LS_lcad_reviewer/intermediate/scripts/batch_42_meta_summary.json', 'w', encoding='utf-8') as f:
    json.dump(tasks_info, f, ensure_ascii=False, indent=2)
print("Saved to batch_42_meta_summary.json")
