# -*- coding: utf-8 -*-
import json

with open('LS_lcad_reviewer/exports/reviewed_1_10000_all.json', 'r', encoding='utf-8') as f:
    all_data = json.load(f)

with open('LS_lcad_reviewer/intermediate/audits/suspect_pass_revisions_plan.json', 'r', encoding='utf-8') as f:
    plan = json.load(f)

rev_map = {int(k): v for k, v in plan['revisions'].items()}

matched = 0
for ann in all_data['annotations']:
    tid = ann['human_review']['task_id']
    if tid in rev_map:
        matched += 1
        if matched <= 5:
            print(f"Task #{tid}:")
            print(f"  Current review_status: {ann['review_status']}")
            print(f"  Current review_note: {ann['review_note']}")
            print(f"  Current defects count: {len(ann['defects'])}")
            print(f"  Planned defects count: {len(rev_map[tid]['defects'])}")
            print(f"  Planned review_note: {rev_map[tid]['review_note'][:60]}...")
            print("---")

print(f"Total matched in all.json: {matched} / {len(rev_map)}")
