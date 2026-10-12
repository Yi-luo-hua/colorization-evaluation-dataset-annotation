import json

target_file = r'LS_lcad_reviewer/exports/reviewed_7501_8000_20260930_182342.json'
with open(target_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

annotations = data['annotations']
print(f"Total annotations: {len(annotations)}")

pass_count = sum(1 for t in annotations if t.get('review_note') == '审查通过')
modified_count = sum(1 for t in annotations if t.get('review_note') != '审查通过')

orig_scores = [t['original_gpt_score'] for t in annotations]
reviewed_scores = [t['reviewed_score'] for t in annotations]

# 如果 reviewed_score 是 None，看计算的评分（通过扣分公式）
calc_scores = []
for t in annotations:
    rs = t.get('reviewed_score')
    if rs is not None:
        calc_scores.append(rs)
    else:
        # 计算扣分
        defects = t.get('defects', [])
        penalty = 0.0
        for d in defects:
            sev = d.get('severity', '')
            if sev.startswith('L'):
                penalty += int(sev[1]) * 0.45
        score = max(1.5, round(5.0 - penalty, 2))
        calc_scores.append(score)

print(f"Pass count: {pass_count}")
print(f"Modified count: {modified_count}")
print(f"Average original score: {sum(orig_scores)/len(orig_scores):.2f}")
print(f"Average calculated reviewed score: {sum(calc_scores)/len(calc_scores):.2f}")

orig_perfect = sum(1 for s in orig_scores if s >= 4.9)
print(f"Original perfect (>=4.9): {orig_perfect}")

defect_stats = {}
severity_stats = {'L1': 0, 'L2': 0, 'L3': 0}
for t in annotations:
    for d in t.get('defects', []):
        did = d['id']
        defect_stats[did] = defect_stats.get(did, 0) + 1
        sev = d.get('severity')
        if sev in severity_stats:
            severity_stats[sev] += 1

print(f"Defect counts: {defect_stats}")
print(f"Severity counts: {severity_stats}")
