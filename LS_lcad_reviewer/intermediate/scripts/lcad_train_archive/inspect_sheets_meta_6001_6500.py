import json

meta_path = 'LS_lcad_reviewer/intermediate/audits/sheets_meta_6001_6500.json'
with open(meta_path, 'r', encoding='utf-8') as f:
    meta = json.load(f)

print(f"Total high-suspicion items: {len(meta)}")
chunk_size = 6
for i in range(0, len(meta), chunk_size):
    sheet_num = i // chunk_size + 1
    chunk = meta[i:i+chunk_size]
    print(f"\n=== sheet_{sheet_num:02d}.jpg ({len(chunk)} tasks) ===")
    for t in chunk:
        reasons_str = "; ".join(t.get('reasons', []))
        metrics = t.get('metrics', {})
        drg = metrics.get('delta_RG', 0)
        dyb = metrics.get('delta_YB', 0)
        sat_ratio = metrics.get('sat_ratio', 1.0)
        delta_c = metrics.get('delta_c', 0)
        print(f"  Idx {t['task_idx']} ({t['image_id']}): OrigScore={t['score']}, Susp={t.get('suspicion', 0):.1f}, delta_c={delta_c:.3f}, dRG={drg:.3f}, dYB={dyb:.3f}, sat_r={sat_ratio:.2f}")
        print(f"    Reasons: {reasons_str}")
