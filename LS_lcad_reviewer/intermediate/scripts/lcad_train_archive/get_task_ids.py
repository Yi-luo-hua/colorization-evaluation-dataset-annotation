import json

meta = json.load(open('LS_lcad_reviewer/intermediate/audits/sheets_meta_7001_7500.json', encoding='utf-8'))
for sheet_idx in range(1, 22):
    start_i = (sheet_idx - 1) * 6
    end_i = min(sheet_idx * 6, len(meta))
    items = meta[start_i:end_i]
    ids = [m['task_idx'] for m in items]
    print(f"Sheet {sheet_idx:02d}: {ids}")
