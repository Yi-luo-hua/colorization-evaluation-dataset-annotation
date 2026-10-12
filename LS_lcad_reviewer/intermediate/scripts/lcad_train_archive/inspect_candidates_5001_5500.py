import json

candidate_ids = [
    5340, 5152, 5115, 5385, 5424, 5098, 5201, 5272, 5295, 5209,
    5181, 5203, 5306, 5220, 5213, 5432, 5064, 5131, 5356, 5493,
    5293, 5061, 5054, 5490, 5205, 5089, 5149, 5140, 5100, 5197,
    5020, 5161, 5121, 5005, 5186
]

with open('exports/reviewed_5001_5500_20260930_142848.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for ann in d['annotations']:
    t_id = ann.get('human_review', {}).get('task_id')
    if t_id in candidate_ids:
        print(f"=== Task #{t_id} (orig_score: {ann.get('original_gpt_score')}, status: {ann.get('review_status')}) ===")
        print("  Defects:", json.dumps(ann.get('defects'), ensure_ascii=False))
        print("  Note:", ann.get('review_note'))
