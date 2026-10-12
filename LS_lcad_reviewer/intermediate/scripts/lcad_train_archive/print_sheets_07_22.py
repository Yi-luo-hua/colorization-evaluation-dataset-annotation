import json

with open('LS_lcad_reviewer/intermediate/audits/sheets_meta_7501_8000.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

chunk_size = 6
num_sheets = (len(items) + chunk_size - 1) // chunk_size

for sheet_idx in range(num_sheets):
    sheet_num = sheet_idx + 1
    if sheet_num >= 7:
        chunk = items[sheet_idx * chunk_size : (sheet_idx + 1) * chunk_size]
        print(f"=== SHEET {sheet_num:02d} ({len(chunk)} items) ===")
        for it in chunk:
            trigs = '; '.join(it.get('reasons', []))
            m = it.get('metrics', {})
            print(f"  Task #{it['task_idx']} | {it['basename']} | Orig: {it['score']} | Susp: {it['suspicion']} | Bias: {m.get('bias_direction')} (dC={m.get('delta_c',0):.2f}) | Triggers: {trigs}")
