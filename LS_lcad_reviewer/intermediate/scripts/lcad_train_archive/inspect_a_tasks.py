# -*- coding: utf-8 -*-
import json

with open('LS_lcad_reviewer/exports/reviewed_1_10000_all.json', encoding='utf-8') as f:
    data = json.load(f)

for ann in data['annotations']:
    tid = ann['human_review']['task_id']
    if tid in [6003, 6640]:
        print(f"Task #{tid}: img={ann['image_id']}, orig_score={ann['gpt_score']}")
        for d in ann['defects']:
            print("  Defect:", d)
