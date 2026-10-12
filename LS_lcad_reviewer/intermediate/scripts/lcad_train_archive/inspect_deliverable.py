import json

with open('LS_lcad_reviewer/exports/reviewed_9501_10000_20260930_194247.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

anns = data['annotations']

none_scores = []
orig_perfect = 0
remained_perfect = 0

for i, a in enumerate(anns):
    t_idx = 9501 + i
    rev_s = a.get('reviewed_score')
    orig_s = a.get('original_gpt_score')
    gpt_s = a.get('gpt_score')
    
    if rev_s is None:
        none_scores.append((t_idx, 'reviewed_score is None'))
    if orig_s is None:
        none_scores.append((t_idx, 'original_gpt_score is None'))
    if gpt_s is None:
        none_scores.append((t_idx, 'gpt_score is None'))
        
    if orig_s is not None and orig_s >= 4.9:
        orig_perfect += 1
        # In reviewed file, what score represents final score?
        # Let's check both gpt_score and reviewed_score
        final_s = a.get('gpt_score')
        if final_s is not None and final_s >= 4.9:
            remained_perfect += 1

print(f"None scores found: {len(none_scores)}")
print(f"Orig perfect: {orig_perfect}, Remained perfect (>=4.9): {remained_perfect}")

# Check review status
statuses = {}
for a in anns:
    st = a.get('review_status')
    statuses[st] = statuses.get(st, 0) + 1
print("Statuses:", statuses)

# Check all placeholder words across all annotations
bad_patterns = ['关键主体', '关键区域', '局部关键区域', '主要物体', '未指定物体', '背景区域']
found_bad = []
for i, a in enumerate(anns):
    t_idx = 9501 + i
    full_text = json.dumps(a['defects'], ensure_ascii=False) + ' ' + str(a.get('review_note', ''))
    for bp in bad_patterns:
        if bp in full_text:
            found_bad.append((t_idx, a['image_id'], bp))

print(f"Total placeholder matches: {len(found_bad)}")
for item in found_bad:
    print("  ", item)
