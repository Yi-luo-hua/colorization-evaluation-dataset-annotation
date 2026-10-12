# -*- coding: utf-8 -*-
import json
import os

meta_path = 'LS_lcad_reviewer/intermediate/audits/sheets_meta_9001_9500.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)

lines = []
cur_sheet = 0
for i, item in enumerate(meta):
    sheet_idx = i // 6 + 1
    if sheet_idx != cur_sheet:
        cur_sheet = sheet_idx
        lines.append(f'=== SHEET {cur_sheet:02d} ===')
    tid = item.get('task_idx') or item.get('task_id')
    img = item.get('image_id')
    orig = item.get('score')
    susp = item.get('suspicion')
    m = item.get('metrics', {})
    reasons = '; '.join(item.get('reasons', []))
    bdir = m.get('bias_direction', '')
    dc = m.get('delta_c', 0)
    peak = m.get('peak_bias', 0)
    b2g = m.get('blue_to_green', 0)
    rl = m.get('red_loss', 0)
    bleed = m.get('bleed_ratio', 0)
    p90 = m.get('p90_edge', 0)
    lines.append(f'  Task #{tid} | {img} | Orig: {orig} | Susp: {susp} | {bdir} (dC={dc:.2f}, Peak={peak:.2f}, B2G={b2g:.2f}, RL={rl:.2f}, Bleed={bleed:.2f}/P90={p90:.1f}) | {reasons}')

out_path = 'LS_lcad_reviewer/intermediate/audits/sheets_summary_clean_9001_9500.txt'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'Generated summary with {len(meta)} tasks across {cur_sheet} sheets.')
