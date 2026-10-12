import json
from collections import Counter

file_path = 'LS_lcad_reviewer/exports/reviewed_6001_6500_20260930_153605.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

annos = data['annotations']
total = len(annos)
perfect_orig = sum(1 for a in annos if a['gpt_score'] >= 4.9)
reviewed_scores = [a['reviewed_score'] for a in annos if a['reviewed_score'] is not None]

defect_counts = Counter()
defect_severities = Counter()
status_counts = Counter(a['review_status'] for a in annos)
pure_passed = sum(1 for a in annos if len(a['defects']) == 0)

for a in annos:
    for d in a['defects']:
        defect_counts[d['id']] += 1
        defect_severities[f"{d['id']}-{d['severity']}"] += 1

print(f"Total images: {total}")
print(f"Original >= 4.9: {perfect_orig}")
print(f"Reviewed A (score=1.0): {len(reviewed_scores)}")
print(f"Pure Passed (zero defects): {pure_passed}")
print(f"Status: {dict(status_counts)}")
print(f"Defect IDs: {dict(defect_counts.most_common())}")
print(f"Defect Severities: {dict(defect_severities.most_common())}")

# 偏色方向
warm = cold = magenta = green = other = 0
for a in annos:
    for d in a['defects']:
        if d['id'] == 'D':
            desc = d['description']
            if any(w in desc for w in ['暖', '黄', '红', '褐', '橙']):
                warm += 1
            elif any(c in desc for c in ['冷', '青', '蓝']):
                cold += 1
            elif any(m in desc for m in ['紫', '洋红']):
                magenta += 1
            elif any(g in desc for g in ['绿']):
                green += 1
            else:
                other += 1

print(f"Bias directions: Warm={warm}, Cold={cold}, Magenta={magenta}, Green={green}, Other={other}")
