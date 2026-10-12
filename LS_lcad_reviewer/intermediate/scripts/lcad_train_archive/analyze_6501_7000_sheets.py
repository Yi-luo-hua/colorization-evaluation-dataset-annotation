import json
import os

meta_path = 'LS_lcad_reviewer/intermediate/audits/sheets_meta_6501_7000.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)

tasks_path = 'LS_lcad_reviewer/tasks_lcad_10000.json'
with open(tasks_path, 'r', encoding='utf-8') as f:
    tasks_all = json.load(f)
task_dict = {i + 1: t for i, t in enumerate(tasks_all) if 6501 <= i + 1 <= 7000}

out_path = 'LS_lcad_reviewer/intermediate/audits/sheets_analysis_6501_7000.txt'
out_lines = []
out_lines.append(f"Total tasks in sheets_meta: {len(meta)}")

chunk_size = 6
for i in range(0, len(meta), chunk_size):
    sheet_num = i // chunk_size + 1
    chunk = meta[i:i+chunk_size]
    out_lines.append(f"\n==========================================")
    out_lines.append(f"=== SHEET {sheet_num:02d} ({len(chunk)} items) ===")
    out_lines.append(f"==========================================")
    for t in chunk:
        idx = t['task_idx']
        orig_t = task_dict.get(idx, {})
        orig_preds = orig_t.get('predictions', [{}])[0].get('result', [])
        orig_defects = []
        for r in orig_preds:
            if r.get('from_name') == 'defects':
                orig_defects = r.get('value', {}).get('choices', [])
        defect_str = ", ".join(orig_defects) if orig_defects else "None (Full 5.0)"
        m = t.get('metrics', {})
        drg = m.get('delta_RG', 0)
        dyb = m.get('delta_YB', 0)
        bias = "偏暖红黄调" if drg >= 0 and dyb >= 0 else ("偏冷青蓝调" if drg <= 0 and dyb <= 0 else ("偏洋红紫调" if drg >= 0 and dyb < 0 else "偏草绿黄调"))
        
        out_lines.append(f"\n[Task {idx}] {t['image_id']} | OrigScore: {t['score']} | Susp: {t.get('suspicion', 0):.1f}")
        out_lines.append(f"  OrigDefects: {defect_str}")
        out_lines.append(f"  Reasons: {'; '.join(t.get('reasons', []))}")
        out_lines.append(f"  Metrics: dC={m.get('delta_c', 0):.3f} ({bias}), SatRatio={m.get('sat_ratio', 1):.2f}, BleedRatio={m.get('bleed_ratio', 0):.2f}(P90={m.get('edge_p90', 0):.1f}), BtoG={m.get('blue_to_green', 0):.2f}, RedLoss={m.get('red_loss', 0):.2f}")

with open(out_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(out_lines))
print(f"Written analysis to {out_path}")
