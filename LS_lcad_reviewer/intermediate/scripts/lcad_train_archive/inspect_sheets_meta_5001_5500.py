import json

meta_path = 'LS_lcad_reviewer/intermediate/audits/sheets_meta_5001_5500.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)

for t in meta[:12]:
    reasons_str = "; ".join(t.get('reasons', []))
    print(f"Idx {t['task_idx']} ({t['image_id']}): Score={t['score']}, Susp={t.get('suspicion', 0):.1f}, Reasons={reasons_str}")
