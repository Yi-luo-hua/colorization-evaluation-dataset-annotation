import json

file_path = 'LS_lcad_reviewer/exports/reviewed_8001_8500_20260930_184910.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

tasks = data['annotations']
orig_scores = []
new_scores = []
defect_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E1': 0, 'E2': 0, 'F': 0}
bias_counts = {}

high_orig = [] # orig >= 4.9

for t in tasks:
    os_ = t['original_gpt_score']
    ns = t['gpt_score']
    orig_scores.append(os_)
    new_scores.append(ns)
    if os_ >= 4.9:
        high_orig.append((os_, ns))
    for d in t.get('defects', []):
        cat = d.get('id', '')
        if cat in defect_counts:
            defect_counts[cat] += 1
    rev_note = t.get('review_note', '')
    for b in ['偏暖红黄调', '偏冷青蓝调', '偏洋红紫调', '偏草绿黄调']:
        if b in rev_note:
            bias_counts[b] = bias_counts.get(b, 0) + 1

lines = []
lines.append('=== 8001-8500 统计指标 ===')
lines.append(f'总任务数: {len(tasks)}')
lines.append(f'原始平均分: {sum(orig_scores)/len(orig_scores):.2f}')
lines.append(f'审校后平均分: {sum(new_scores)/len(new_scores):.2f}')
lines.append(f'原满分/高分(>=4.9)拦截清洗数: {len(high_orig)}')
if high_orig:
    lines.append(f'原满分审校后平均分: {sum(x[1] for x in high_orig)/len(high_orig):.2f}')

lines.append('\n缺陷频次统计:')
for k, v in defect_counts.items():
    lines.append(f'  {k}: {v}')

lines.append('\n偏色方向唯一分布统计:')
for k, v in bias_counts.items():
    lines.append(f'  {k}: {v}')

def get_bins(scores):
    bins = {'0.0-2.0': 0, '2.0-3.0': 0, '3.0-4.0': 0, '4.0-4.8': 0, '4.9-5.0': 0}
    for s in scores:
        if s <= 2.0: bins['0.0-2.0'] += 1
        elif s <= 3.0: bins['2.0-3.0'] += 1
        elif s <= 4.0: bins['3.0-4.0'] += 1
        elif s < 4.9: bins['4.0-4.8'] += 1
        else: bins['4.9-5.0'] += 1
    return bins

lines.append(f'\n分数分段分布 (审校前): {get_bins(orig_scores)}')
lines.append(f'分数分段分布 (审校后): {get_bins(new_scores)}')

content = '\n'.join(lines)
with open('LS_lcad_reviewer/intermediate/audits/batch_8001_8500_report_data.txt', 'w', encoding='utf-8') as f:
    f.write(content)

print('Written report data successfully!')
