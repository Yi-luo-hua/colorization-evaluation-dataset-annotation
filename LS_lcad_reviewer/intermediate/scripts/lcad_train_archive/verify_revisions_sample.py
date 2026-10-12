# -*- coding: utf-8 -*-
import json

def main():
    with open('LS_lcad_reviewer/intermediate/audits/suspect_pass_revisions_plan.json', 'r', encoding='utf-8') as f:
        plan = json.load(f)

    revs = plan['revisions']
    keys = list(revs.keys())[:12]
    for k in keys:
        r = revs[k]
        print(f"Task #{r['task_id']} ({r['image_id']}):")
        for d in r['defects']:
            print(f"   [{d['id']}-{d['severity']}] {d['name']}: {d['description']}")
        print(f"   Note: {r['review_note'][:60]}...")
        print("---")

    # Check for abstract placeholder violations across all 365 revisions
    abstract_patterns = ["局部关键区域", "关键主体或背景", "局部配饰与边缘区域", "偏暖黄或泛青冷"]
    violators = []
    for k, r in revs.items():
        for d in r['defects']:
            desc = d['description']
            for pat in abstract_patterns:
                if pat in desc:
                    violators.append((r['task_id'], pat, desc))

    print(f"\nAbstract pattern check: found {len(violators)} violations.")
    if violators:
        for v in violators[:5]:
            print(f"Task #{v[0]}: matched '{v[1]}' in '{v[2]}'")

if __name__ == '__main__':
    main()
