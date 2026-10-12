# -*- coding: utf-8 -*-
"""
fix_defect_a_compliance.py
严格对齐 V4 规范中的 A 缺陷契约：
- 若 defects 中包含 id == 'A':
    d['severity'] = ""
    ann['reviewed_score'] = 1.0
    ann['needs_rescoring'] = False
- 确保 clean.json 的 review_note 100% 为 ""
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"

def fix_file(file_path, is_clean=False):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fixed_a = 0
    for ann in data['annotations']:
        has_a = False
        for d in ann.get('defects', []):
            if d.get('id') == 'A':
                has_a = True
                d['severity'] = ""
                d['name'] = "缺色"

        if has_a:
            ann['reviewed_score'] = 1.0
            ann['needs_rescoring'] = False
            fixed_a += 1

        if is_clean:
            ann['review_note'] = ""

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Fixed {fixed_a} defect A instances in {file_path.name}")

def main():
    fix_file(ALL_FILE, is_clean=False)
    fix_file(CLEAN_FILE, is_clean=True)

if __name__ == '__main__':
    main()
