# -*- coding: utf-8 -*-
"""
apply_suspect_pass_revisions.py
将 365 项具象定物改判同步写入：
1. LS_lcad_reviewer/exports/reviewed_1_10000_all.json
2. LS_lcad_reviewer/exports/reviewed_1_10000_clean.json

严格遵循：
- clean.json 的 review_note 100% 为 ""
- all.json 的 review_note 详细记录具象定物描述（不带【...】前缀）
- gpt_score 与 original_gpt_score 严格保持不变
- defects 字段包含完整的 id, name, severity, description
- 零抽象占位符，零 E1/E2 互斥
- 备份原文件
"""

import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PLAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "suspect_pass_revisions_plan.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

def main():
    if not PLAN_FILE.exists():
        print(f"Error: {PLAN_FILE} not found!")
        return

    with open(PLAN_FILE, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    rev_map = {int(k): v for k, v in plan['revisions'].items()}
    print(f"Loaded {len(rev_map)} revisions from plan.")

    # 1. Update ALL_FILE
    print(f"Updating {ALL_FILE.name}...")
    shutil.copy2(ALL_FILE, ALL_FILE.with_suffix('.json.bak'))
    with open(ALL_FILE, 'r', encoding='utf-8') as f:
        all_data = json.load(f)

    updated_count_all = 0
    now_iso = datetime.now(timezone.utc).isoformat()
    for ann in all_data['annotations']:
        tid = ann['human_review']['task_id']
        if tid in rev_map:
            r = rev_map[tid]
            ann['defects'] = r['defects']
            ann['review_note'] = r['review_note']
            ann['review_status'] = "已核验"
            ann['reviewed_score'] = None
            ann['needs_rescoring'] = True
            ann['human_review']['updated_at'] = now_iso
            updated_count_all += 1

    all_data['meta']['exported_at'] = now_iso
    with open(ALL_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully updated {updated_count_all} items in {ALL_FILE.name}")

    # 2. Update CLEAN_FILE
    print(f"Updating {CLEAN_FILE.name}...")
    shutil.copy2(CLEAN_FILE, CLEAN_FILE.with_suffix('.json.bak'))
    with open(CLEAN_FILE, 'r', encoding='utf-8') as f:
        clean_data = json.load(f)

    updated_count_clean = 0
    for ann in clean_data['annotations']:
        tid = ann['human_review']['task_id']
        if tid in rev_map:
            r = rev_map[tid]
            ann['defects'] = r['defects']
            ann['review_note'] = ""  # Clean version invariant: always ""
            ann['review_status'] = "已核验"
            ann['reviewed_score'] = None
            ann['needs_rescoring'] = True
            ann['human_review']['updated_at'] = now_iso
            updated_count_clean += 1
        else:
            # Ensure 100% review_note is "" in clean.json
            ann['review_note'] = ""

    clean_data['meta']['exported_at'] = now_iso
    with open(CLEAN_FILE, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)
    print(f"Successfully updated {updated_count_clean} items in {CLEAN_FILE.name}")

if __name__ == '__main__':
    main()
