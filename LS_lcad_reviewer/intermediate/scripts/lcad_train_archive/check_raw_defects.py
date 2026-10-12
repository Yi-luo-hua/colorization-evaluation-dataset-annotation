# -*- coding: utf-8 -*-
import json
from pathlib import Path

def main():
    with open('LS_lcad_reviewer/tasks_lcad_10000.json', 'r', encoding='utf-8') as f:
        raw_tasks = json.load(f)

    with open('LS_lcad_reviewer/intermediate/audits/suspect_detailed_cv_diff.json', 'r', encoding='utf-8') as f:
        suspects = json.load(f)

    suspect_img_map = {s['image_id']: s for s in suspects}

    count_with_raw_defects = 0
    print("--- Sample of Suspects with Raw Defects from tasks_lcad_10000.json ---")
    samples_printed = 0
    for idx, t in enumerate(raw_tasks):
        img_id = t['data'].get('image_id')
        if img_id in suspect_img_map:
            s_info = suspect_img_map[img_id]
            orig_rec = t['data'].get('original_record', {})
            raw_defects = orig_rec.get('defects', [])
            score = orig_rec.get('gpt_score')
            if raw_defects:
                count_with_raw_defects += 1
                if samples_printed < 8:
                    print(f"Task index #{idx+1} ({s_info['sheet']} pos {s_info['pos']}): orig_score={score}, raw_defects count={len(raw_defects)}")
                    for d in raw_defects:
                        print(f"   [{d.get('id')}-{d.get('severity')}] {d.get('name')}: {d.get('description')}")
                    print("---")
                    samples_printed += 1

    print(f"\nTotal suspects: {len(suspects)}")
    print(f"Suspects that had raw defects in tasks_lcad_10000.json: {count_with_raw_defects}")

if __name__ == '__main__':
    main()
