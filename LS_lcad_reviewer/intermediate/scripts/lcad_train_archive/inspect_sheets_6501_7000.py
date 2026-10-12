import json
import os

meta_file = r'LS_lcad_reviewer/intermediate/audits/sheets_meta_6501_7000.json'
with open(meta_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total items: {len(items)}")
chunk_size = 6
num_sheets = (len(items) + chunk_size - 1) // chunk_size

for sheet_idx in range(num_sheets):
    chunk = items[sheet_idx * chunk_size : (sheet_idx + 1) * chunk_size]
    print(f"\n================ SHEET {sheet_idx+1:02d} ({len(chunk)} items) ================")
    for it in chunk:
        t = it['task_idx']
        b = it['basename']
        sc = it['score']
        susp = it['suspicion']
        dC = it['metrics']['delta_c']
        bias = it['metrics']['bias_direction']
        reasons = "; ".join(it['reasons'][:3])
        print(f"  Task {t} | {b} | Orig: {sc} | Susp: {susp:.1f} | Bias: {bias}(dC={dC:.2f}) | {reasons}")
