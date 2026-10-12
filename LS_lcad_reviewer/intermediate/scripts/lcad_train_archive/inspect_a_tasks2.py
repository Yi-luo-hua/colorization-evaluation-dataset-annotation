# -*- coding: utf-8 -*-
import json

with open('LS_lcad_reviewer/exports/reviewed_1_10000_clean.json', encoding='utf-8') as f:
    data = json.load(f)

for idx, ann in enumerate(data['annotations'], 1):
    if ann.get('image_id') in ['lcad/000000345745.png', 'lcad/000000380510.png']:
        print(f"Task index #{idx}, Task ID #{ann['human_review']['task_id']}: img={ann['image_id']}")
        print(f"  score={ann['gpt_score']}, reviewed_score={ann['reviewed_score']}, needs_rescoring={ann['needs_rescoring']}")
        for d in ann['defects']:
            print("  Defect:", d)
