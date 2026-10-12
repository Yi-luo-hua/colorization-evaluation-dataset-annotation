import json
from collections import Counter
from pathlib import Path

final_file = r"LS_lcad_reviewer/exports/reviewed_7001_7500_20260930_161800.json"
stream_file = r"LS_lcad_reviewer/streams/tasks_lcad_7001_7500_stream.json"

with open(final_file, 'r', encoding='utf-8') as f:
    final_data = json.load(f)

annotations = final_data['annotations']
total = len(annotations)
print(f"Total annotations: {total}")

# 满分统计
orig_scores = [a.get('original_gpt_score', 0) for a in annotations]
orig_perfect = [s for s in orig_scores if s >= 4.9]
print(f"Original >= 4.9: {len(orig_perfect)}")

# 缺陷统计
defect_counts = Counter()
defect_sev_counts = Counter()
bias_dir_counts = Counter()

a_count = 0
for a in annotations:
    defs = a.get('defects', [])
    for d in defs:
        d_id = d['id']
        sev = d.get('severity', '')
        defect_counts[d_id] += 1
        defect_sev_counts[f"{d_id}-{sev}"] += 1
        if d_id == 'A':
            a_count += 1
        if d_id == 'D':
            desc = d.get('description', '')
            for b in ['偏暖红黄调', '偏冷青蓝调', '偏洋红紫调', '偏草绿黄调']:
                if b in desc:
                    bias_dir_counts[b] += 1
                    break

print("Defect counts:", defect_counts)
print("Defect sev counts:", sorted(defect_sev_counts.items()))
print("Bias direction counts:", bias_dir_counts)

# Stream 统计
with open(stream_file, 'r', encoding='utf-8') as f:
    stream_tasks = json.load(f)

tags = Counter()
for t in stream_tasks:
    tag = t.get('meta', {}).get('review_tag', '')
    tags[tag] += 1
print("Stream tags:", tags)
