import json
from collections import Counter
from pathlib import Path

sample_path = Path("LS_lcad_reviewer/intermediate/audits/random_sample_200_items.json")
items = json.load(open(sample_path, encoding="utf-8"))

total = len(items)
zero_defects = [x for x in items if len(x.get("defects", [])) == 0]
orig_5 = [x for x in items if x.get("gpt_score", 0) >= 4.9]
orig_5_zero = [x for x in orig_5 if len(x.get("defects", [])) == 0]

defect_counter = Counter()
severity_counter = Counter()

abstract_words = ["关键主体", "局部关键", "关键背景"]
abstract_found = []

for x in items:
    note = x.get("review_note", "")
    for d in x.get("defects", []):
        defect_counter[d["id"]] += 1
        severity_counter[f"{d['id']}-{d.get('severity','')}"] += 1
        desc = d.get("description", "")
        for w in abstract_words:
            if w in desc:
                abstract_found.append((x["human_review"]["task_id"], w, desc))
    for w in abstract_words:
        if w in note:
            abstract_found.append((x["human_review"]["task_id"], w, note))

print(f"Total Sampled: {total}")
print(f"Zero-defect items: {len(zero_defects)} ({len(zero_defects)/total*100:.1f}%)")
print(f"Orig 5.0 items: {len(orig_5)} ({len(orig_5)/total*100:.1f}%)")
print(f"Orig 5.0 verified as true 5.0 (zero-defect): {len(orig_5_zero)}")
print("Defect distribution across 200 samples:")
for k, v in defect_counter.most_common():
    print(f"  Defect {k}: {v}")
print(f"Abstract words detected: {len(abstract_found)}")
