import json

with open('intermediate/audits/double_check_candidates_5001_5500.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

with open('intermediate/audits/inspect_candidates_text.txt', 'w', encoding='utf-8') as out:
    for it in items:
        out.write(f"=== Task #{it['task_id']} ({it['image_id']}) score: {it['score']} ===\n")
        out.write(f"Defects: {json.dumps(it['defects'], ensure_ascii=False)}\n")
        out.write(f"Note: {it['review_note']}\n\n")
print('Dumped to intermediate/audits/inspect_candidates_text.txt')
