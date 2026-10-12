import json

with open('LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_09.json', 'r', encoding='utf-8') as f:
    g09 = json.load(f)

with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

b09 = plan['batches'][8]
items = b09['items']

print(f"Batch 09 batch_no: {b09['batch_no']}, total: {len(items)}")

# 统计 g09 中原本是 pass (defects == []) 还是 grounded (defects != [])
pass_count = 0
grounded_count = 0
for tid_str, d in g09.items():
    if len(d.get('defects', [])) == 0:
        pass_count += 1
    else:
        grounded_count += 1
print(f"Current g09 in file: {len(g09)} tasks -> Grounded: {grounded_count}, Passed: {pass_count}")

# 找出当前在 g09 中判定为 pass，但违反双重硬门槛的任务 (orig_score < 4.0 或 delta_c >= 0.08)
suspicious_passes = []
for it in items:
    tid = it['task_id']
    tid_str = str(tid)
    g_res = g09.get(tid_str, {})
    is_pass = len(g_res.get('defects', [])) == 0
    orig = it['original_gpt_score']
    m = it.get('metrics', {})
    dc = m.get('delta_c', 0.0)
    sheet_no = (items.index(it) // 6) + 1
    
    if is_pass and (orig < 4.0 or dc >= 0.08):
        suspicious_passes.append({
            'task_id': tid,
            'sheet_no': sheet_no,
            'orig_score': orig,
            'delta_c': dc,
            'sat_ratio': m.get('sat_ratio', 1.0),
            'image_id': it['image_id'],
            'current_defects': it.get('current_defects', [])
        })

print(f"\nSuspicious passes found violating double-threshold: {len(suspicious_passes)}")
for sp in suspicious_passes:
    print(f"Sheet {sp['sheet_no']:02d} | Task #{sp['task_id']}: orig={sp['orig_score']}, dc={sp['delta_c']:.3f}, sat_ratio={sp['sat_ratio']:.2f}, img={sp['image_id']}")
