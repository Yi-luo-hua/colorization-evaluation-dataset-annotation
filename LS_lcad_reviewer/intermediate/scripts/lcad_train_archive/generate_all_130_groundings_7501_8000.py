import json
import os
import sys

# 导入 Part 1 和 Part 2
from groundings_part1_7501_8000 import PART1_GROUNDINGS
from groundings_part2_7501_8000 import PART2_GROUNDINGS

meta_file = r'LS_lcad_reviewer/intermediate/audits/sheets_meta_7501_8000.json'
with open(meta_file, 'r', encoding='utf-8') as f:
    sheets_meta = json.load(f)

expected_task_ids = set([it['task_idx'] for it in sheets_meta])
print(f"Loaded {len(sheets_meta)} tasks from sheets metadata.")

# 合并字典
all_groundings = {}
all_groundings.update(PART1_GROUNDINGS)
all_groundings.update(PART2_GROUNDINGS)

print(f"Total groundings collected: {len(all_groundings)}")

# 完整性校验
missing_ids = expected_task_ids - set(all_groundings.keys())
extra_ids = set(all_groundings.keys()) - expected_task_ids

if missing_ids:
    print(f"Error: Missing tasks in groundings: {sorted(list(missing_ids))}")
    sys.exit(1)
if extra_ids:
    print(f"Warning: Extra tasks in groundings: {sorted(list(extra_ids))}")

# 保存为纯净 JSON
out_path = r'LS_lcad_reviewer/intermediate/audits/grounding_reviews_7501_8000.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_groundings, f, ensure_ascii=False, indent=2)

print(f"Successfully generated pure grounding reviews JSON at: {out_path}")
