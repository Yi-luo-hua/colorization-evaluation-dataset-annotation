import json
from collections import Counter

export_file = r'LS_lcad_reviewer/exports/reviewed_6501_7000_20260930_155809.json'
with open(export_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

annotations = data['annotations']
total = len(annotations)

passed_count = sum(1 for a in annotations if a['review_note'] == "审查通过")
modified_count = total - passed_count

orig_scores = [a['original_gpt_score'] for a in annotations]
reviewed_scores = [a['reviewed_score'] if a['reviewed_score'] is not None else a['gpt_score'] for a in annotations]

perfect_orig = [a for a in annotations if a['original_gpt_score'] >= 4.9]
perfect_orig_count = len(perfect_orig)
perfect_fixed = [a for a in perfect_orig if a['review_note'] != "审查通过"]
perfect_fixed_count = len(perfect_fixed)
perfect_passed = perfect_orig_count - perfect_fixed_count

defect_counts = Counter()
defect_sev_counts = Counter()
bias_counts = Counter()

for a in annotations:
    for d in a['defects']:
        defect_counts[d['id']] += 1
        defect_sev_counts[f"{d['id']}-{d['severity']}"] += 1
    
    note = a['review_note']
    for b in ['偏暖红黄调', '偏冷青蓝调', '偏洋红紫调', '偏草绿黄调']:
        if b in note:
            bias_counts[b] += 1

print(f"Total: {total}")
print(f"Passed: {passed_count} ({passed_count/total*100:.1f}%)")
print(f"Modified: {modified_count} ({modified_count/total*100:.1f}%)")
print(f"Original 5.0 perfect: {perfect_orig_count}")
print(f"Perfect fixed: {perfect_fixed_count} ({perfect_fixed_count/perfect_orig_count*100:.1f}%)")
print(f"Perfect passed: {perfect_passed} ({perfect_passed/perfect_orig_count*100:.1f}%)")

print("\n--- Defect Distribution ---")
for k, v in defect_counts.most_common():
    print(f"  {k}: {v}")

print("\n--- Defect Severity Distribution ---")
for k, v in defect_sev_counts.most_common():
    print(f"  {k}: {v}")

print("\n--- Bias Direction Distribution ---")
for k, v in bias_counts.most_common():
    print(f"  {k}: {v}")

mean_orig = sum(orig_scores) / total
mean_reviewed = sum(reviewed_scores) / total
print(f"\nMean original score: {mean_orig:.2f}")
print(f"Mean reviewed score: {mean_reviewed:.2f}")
