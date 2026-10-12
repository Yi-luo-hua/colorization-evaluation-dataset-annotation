import json
from collections import Counter

file_path = 'LS_lcad_reviewer/exports/reviewed_4501_5000_20260930_140753.json'
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

# Sample grounded cases
print("\nSample Visual Grounded cases:")
count = 0
for a in annos:
    if "核查发现：" in a['review_note'] and count < 10:
        print(f"- Image: {a['image_id']} | Orig: {a['gpt_score']} | Note: {a['review_note']}")
        count += 1
