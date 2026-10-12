import json

meta_file = 'LS_lcad_reviewer/intermediate/audits/sheets_meta_8501_9000.json'
with open(meta_file, 'r', encoding='utf-8') as f:
    m = json.load(f)

chunk_size = 6
lines = []
for idx in range(0, len(m), chunk_size):
    sheet_num = idx // chunk_size + 1
    tasks = m[idx:idx+chunk_size]
    lines.append(f'=== SHEET {sheet_num:02d} ===')
    for t in tasks:
        b = t['metrics']['bias_direction']
        dc = t['metrics']['delta_c']
        peak = t['metrics']['max_local_peak']
        b2g = t['metrics']['blue_to_green']
        rl = t['metrics']['red_loss']
        bleed = t['metrics']['bleed_ratio']
        p90 = t['metrics']['p90_edge']
        t_id = t['task_idx']
        img = t['image_id']
        sc = t['score']
        sp = t['suspicion']
        rs = '; '.join(t['reasons'][:2])
        lines.append(f'  Task #{t_id} | {img} | Orig: {sc} | Susp: {sp} | {b} (dC={dc:.2f}, Peak={peak:.2f}, B2G={b2g:.2f}, RL={rl:.2f}, Bleed={bleed:.2f}/P90={p90:.1f}) | {rs}')

out_file = 'LS_lcad_reviewer/intermediate/audits/sheets_summary_clean_8501_9000.txt'
with open(out_file, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Written', len(lines), 'lines to', out_file)
