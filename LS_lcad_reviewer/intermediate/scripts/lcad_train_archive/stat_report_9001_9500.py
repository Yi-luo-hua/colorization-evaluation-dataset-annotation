# -*- coding: utf-8 -*-
import json

target_file = r'exports/reviewed_9001_9500_20260930_192616.json'
with open(target_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

annotations = data['annotations']

orig_scores = [t['original_gpt_score'] for t in annotations]
reviewed_scores = []
for t in annotations:
    rs = t.get('reviewed_score')
    if rs is not None:
        reviewed_scores.append(rs)
    else:
        defects = t.get('defects', [])
        penalty = 0.0
        for d in defects:
            sev = d.get('severity', '')
            if sev.startswith('L'):
                penalty += int(sev[1]) * 0.45
        score = max(1.0, round(5.0 - penalty, 2))
        reviewed_scores.append(score)

pass_items = [t for t in annotations if t.get('review_note') == '核查发现局部缺陷']
grounded_items = [t for t in annotations if '原5.0满分严重漏检' in t.get('review_note', '') or '核查确认' in t.get('review_note', '') or '原4.23' in t.get('review_note', '')]
cv_items = [t for t in annotations if t not in pass_items and t not in grounded_items]

print(f"Total: {len(annotations)}")
print(f"Physical Self-Consistent Pass (采信原缺陷): {len(pass_items)}")
print(f"Visual Grounded (肉眼看板具象定物改判): {len(grounded_items)}")
print(f"CV Refined (CV物理指标直接修正): {len(cv_items)}")

# 原始满分 (>= 4.9)
orig_perfect = [t for t in annotations if t['original_gpt_score'] >= 4.9]
print(f"Original perfect count: {len(orig_perfect)}")
cleaned_perfect = len([t for t in orig_perfect if t not in pass_items])
print(f"Cleaned perfect count: {cleaned_perfect}")

# 分数统计
print(f"Orig avg: {sum(orig_scores)/len(orig_scores):.3f}")
print(f"Reviewed avg: {sum(reviewed_scores)/len(reviewed_scores):.3f}")

# 缺陷分布
defect_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E1': 0, 'E2': 0, 'F': 0}
severity_counts = {'L1': 0, 'L2': 0, 'L3': 0}
for t in annotations:
    for d in t.get('defects', []):
        did = d['id']
        defect_counts[did] = defect_counts.get(did, 0) + 1
        sev = d.get('severity')
        if sev in severity_counts:
            severity_counts[sev] += 1

print("Defects:", defect_counts)
print("Severities:", severity_counts)

# 分数段分布
bins = {'1.0-1.99': 0, '2.0-2.99': 0, '3.0-3.99': 0, '4.0-4.89': 0, '4.9-5.0': 0}
for s in reviewed_scores:
    if s < 2.0:
        bins['1.0-1.99'] += 1
    elif s < 3.0:
        bins['2.0-2.99'] += 1
    elif s < 3.999:
        bins['3.0-3.99'] += 1
    elif s < 4.9:
        bins['4.0-4.89'] += 1
    else:
        bins['4.9-5.0'] += 1
print("Reviewed score bins:", bins)
