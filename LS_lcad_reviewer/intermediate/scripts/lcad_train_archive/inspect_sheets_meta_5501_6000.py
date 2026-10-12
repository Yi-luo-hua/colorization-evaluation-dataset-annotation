import json

meta_path = 'LS_lcad_reviewer/intermediate/audits/sheets_meta_5501_6000.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)

print(f"Total high-suspicion items: {len(meta)}")
chunk_size = 6
for i in range(0, len(meta), chunk_size):
    sheet_num = i // chunk_size + 1
    chunk = meta[i:i+chunk_size]
    print(f"=== sheet_{sheet_num:02d}.jpg ({len(chunk)} tasks) ===")
    for t in chunk:
        reasons_str = "; ".join(t.get('reasons', []))
        print(f"  Idx {t['task_idx']} ({t['image_id']}): OrigScore={t['score']}, Susp={t.get('suspicion', 0):.1f}, Reasons={reasons_str}")
