import json

target_file = r'LS_lcad_reviewer/exports/reviewed_7501_8000_20260930_182342.json'
with open(target_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

annotations = data['annotations']
print(f"Total annotations: {len(annotations)}")

orig_scores = [t['original_gpt_score'] for t in annotations]
rev_scores = [t['gpt_score'] for t in annotations]

cleaned_perfect = 0
retained_perfect = 0
modified_count = 0
pass_count = 0

defect_counts = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'E1': 0, 'E2': 0}
severity_counts = {'L1': 0, 'L2': 0, 'L3': 0}
score_bins = {'1.0-1.99': 0, '2.0-2.99': 0, '3.0-3.99': 0, '4.0-4.89': 0, '4.9-5.0': 0}

for t in annotations:
    note = t.get('review_note', '')
    defects = t.get('defects', [])
    score = t.get('gpt_score', 0.0)
    orig_s = t.get('original_gpt_score', 0.0)

    if note == "审查通过":
        pass_count += 1
    else:
        modified_count += 1

    if orig_s >= 4.9:
        if note == "审查通过":
            retained_perfect += 1
        else:
            cleaned_perfect += 1

    for d in defects:
        did = d['id']
        defect_counts[did] = defect_counts.get(did, 0) + 1
        sev = d.get('severity')
        if sev:
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

    if score < 2.0:
        score_bins['1.0-1.99'] += 1
    elif score < 3.0:
        score_bins['2.0-2.99'] += 1
    elif score < 4.0:
        score_bins['3.0-3.99'] += 1
    elif score < 4.9:
        score_bins['4.0-4.89'] += 1
    else:
        score_bins['4.9-5.0'] += 1

print(f"Pass count: {pass_count}")
print(f"Modified count: {modified_count}")
print(f"Original perfect (>=4.9): {cleaned_perfect + retained_perfect}")
print(f"Cleaned perfect: {cleaned_perfect}")
print(f"Retained perfect: {retained_perfect}")
print(f"Average orig score: {sum(orig_scores)/len(orig_scores):.2f}")
print(f"Average reviewed score: {sum(rev_scores)/len(rev_scores):.2f}")
print("Score bins:", score_bins)
print("Defect counts:", defect_counts)
print("Severity counts:", severity_counts)
