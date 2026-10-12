import json

data = json.load(open('LS_lcad_reviewer/intermediate/scripts/batch_50_meta_summary.json', encoding='utf-8'))
for i, it in enumerate(data['items']):
    tid = it['task_id']
    defs = [f"{d['id']}-{d['severity']}" for d in it['current_defects']]
    note = it['current_review_note'].replace('\n', ' ')
    print(f"#{tid} (orig={it['orig_score']}): defs={defs} | note={note}")
