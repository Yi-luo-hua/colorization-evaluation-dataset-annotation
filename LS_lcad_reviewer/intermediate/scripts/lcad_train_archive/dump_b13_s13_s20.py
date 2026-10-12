import json

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

b13 = [b for b in plan['batches'] if b['batch_no'] == 13][0]
tasks = b13['items']

for s in range(13, 21):
    sub = tasks[(s-1)*6 : s*6]
    print(f'=== Sheet {s} ===')
    for t in sub:
        tidx = t["task_idx"]
        img = t["image_id"]
        sc = t.get("gpt_score", 0)
        dc = t.get("delta_c", 0)
        sus = t.get("suspicions", [])
        print(f'Task #{tidx}: {img} | score={sc:.2f} | dc={dc:.4f} | sus={sus}')

