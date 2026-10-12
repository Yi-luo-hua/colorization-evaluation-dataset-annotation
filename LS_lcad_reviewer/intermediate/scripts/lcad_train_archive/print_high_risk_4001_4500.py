import json

with open('LS_lcad_reviewer/intermediate/audits/sheets_meta_4001_4500.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f"Total: {len(items)}")
for i, x in enumerate(items):
    reasons_str = "; ".join(x.get('reasons', []))
    print(f"[{i+1}/{len(items)}] Task {x['task_idx']} | Base: {x['basename']} | OrigScore: {x['score']} | Susp: {x['suspicion']:.1f}")
    print(f"   Reasons: {reasons_str}")
