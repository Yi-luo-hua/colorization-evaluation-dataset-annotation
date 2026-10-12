import json

with open('LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('temp_check.txt', 'w', encoding='utf-8') as out:
    for a in data['annotations']:
        if a['image_id'] in ['lcad/000000560481.png', 'lcad/000000576676.png']:
            out.write(a['image_id'] + '\n')
            for d in a['defects']:
                out.write(f"  {d['id']}: {d['description']}\n")
            out.write(f"  note: {a.get('review_note')}\n")
