import json

raw_tasks = json.load(open('LS_lcad_reviewer/tasks_lcad_10000.json', encoding='utf-8'))
violating_ids = [8151, 8156, 8159, 8161, 8165, 8185, 8190, 8193, 8218, 8221, 8226, 8228, 8231, 8235, 8247, 8248, 8252, 8257, 8258, 8260, 8261, 8262, 8265, 8272, 8277, 8279, 8282, 8284, 8285, 8287, 8295, 8298, 8311, 8313, 8314, 8316, 8327]

with open('LS_lcad_reviewer/intermediate/scripts/temp_view.txt', 'w', encoding='utf-8') as out:
    for tid in violating_ids:
        t = raw_tasks[tid-1]
        orig = t['data']['original_record']
        img = orig['image_id']
        score = orig['gpt_score']
        out.write(f"Task #{tid} | {img} | Score: {score}\n")
        for d in orig.get('defects', []):
            out.write(f"  [{d.get('id')}-{d.get('severity')}] {d.get('description')}\n")
        out.write("\n")
