import json

with open('intermediate/audits/deep_fix_targets_all.json', encoding='utf-8') as f:
    data = json.load(f)

p4 = [x for x in data if x['batch_id'] == 6]
with open('intermediate/audits/part4_list.txt', 'w', encoding='utf-8') as out:
    for i, item in enumerate(p4):
        sheet_idx = i // 6 + 1
        card_idx = i % 6 + 1
        t_id = item['task_id']
        img = item['image_id']
        s = item['raw_score']
        defs = [d['id'] + '-' + d.get('severity', '') for d in item['raw_defects']]
        out.write(f"{i+1:02d} | Sheet {sheet_idx:02d} #{card_idx} | Task {t_id:04d} | Img {img} | RawScore: {s} | Defs: {defs}\n")

print(f"Dumped {len(p4)} items to intermediate/audits/part4_list.txt")
