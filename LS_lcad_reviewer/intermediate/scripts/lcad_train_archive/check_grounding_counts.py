import sys
import json
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"
SHEETS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "inspection_sheets"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"

with open(ALL_FILE, "r", encoding="utf-8") as f:
    anns = json.load(f)["annotations"]

# 1. 物理看板图片（大图）生成覆盖度分析
tasks_with_sheets = set()

# A. sheets_meta_*.json
for sm in AUDITS_DIR.glob("sheets_meta_*.json"):
    try:
        with open(sm, "r", encoding="utf-8") as f:
            for item in json.load(f):
                tid = item.get("task_idx") or item.get("id") or item.get("task_id")
                if tid: tasks_with_sheets.add(int(tid))
    except Exception: pass

# B. audit_pass_*.json
for ap in AUDITS_DIR.glob("audit_pass_*.json"):
    try:
        with open(ap, "r", encoding="utf-8") as f:
            for item in json.load(f):
                tid = item.get("task_idx") or item.get("id") or item.get("task_id")
                if tid: tasks_with_sheets.add(int(tid))
    except Exception: pass

# C. deep_fix_targets_all.json
dft = AUDITS_DIR / "deep_fix_targets_all.json"
if dft.exists():
    with open(dft, "r", encoding="utf-8") as f:
        for item in json.load(f):
            tid = item.get("task_id") or item.get("task_idx")
            if tid: tasks_with_sheets.add(int(tid))

# D. cv_physical_audit_plan.json
cap = AUDITS_DIR / "cv_physical_audit_plan.json"
if cap.exists():
    with open(cap, "r", encoding="utf-8") as f:
        for item in json.load(f).get("items", []):
            tid = item.get("task_id")
            if tid: tasks_with_sheets.add(int(tid))

# E. random_sample_200_items.json
rs = AUDITS_DIR / "random_sample_200_items.json"
if rs.exists():
    with open(rs, "r", encoding="utf-8") as f:
        for item in json.load(f):
            tid = item.get("human_review", {}).get("task_id") or item.get("task_id")
            if tid: tasks_with_sheets.add(int(tid))

# F. grounding_targets_1001_1500.json
gt = AUDITS_DIR / "grounding_targets_1001_1500.json"
if gt.exists():
    with open(gt, "r", encoding="utf-8") as f:
        for item in json.load(f):
            tid = item.get("task_idx") or item.get("id") or item.get("task_id")
            if tid: tasks_with_sheets.add(int(tid))

# G. grounding_reviews_*.json
for gr in AUDITS_DIR.glob("grounding_reviews_*.json"):
    try:
        with open(gr, "r", encoding="utf-8") as f:
            for k in json.load(f).keys():
                try: tasks_with_sheets.add(int(k))
                except: pass
    except Exception: pass

# 2. 评语内容分析（是否包含具体视觉实体）
generic_cv = []
pure_pass = []
grounded = []

generic_patterns = [
    r"^核查修正：全图",
    r"^原5\.0满分复核：核查发现：全图轻微偏",
    r"^原5\.0满分核查修正：全图轻微偏",
    r"^核查修正：全图饱和度",
    r"^原5\.0满分核查修正：局部色彩欠饱和",
    r"^原5\.0满分核查修正：色彩过饱和"
]

for ann in anns:
    tid = ann["human_review"]["task_id"]
    note = ann.get("review_note", "")
    defs = ann.get("defects", [])
    
    if note == "审查通过" and not defs:
        pure_pass.append(ann)
    elif any(re.search(p, note) for p in generic_patterns):
        generic_cv.append(ann)
    else:
        grounded.append(ann)

print("=" * 60)
print(f"全量任务总数: {len(anns)}")
print("=" * 60)
print("【维度一：视觉大图看板（inspection_sheets）物理生成与查验覆盖度】")
print(f"  - 曾生成高清大图看板进行视觉直审的图像: {len(tasks_with_sheets)} 张 ({len(tasks_with_sheets)/100:.1f}%)")
print(f"  - 从未生成大图看板（仅走纯CV初筛/分流）的图像: {10000 - len(tasks_with_sheets)} 张 ({(10000 - len(tasks_with_sheets))/100:.1f}%)")
print()
print("【维度二：最终交付结果中的标注具象定物属性】")
print(f"  - 具象定物视觉直审描述样本 (含具体物体/部位/服装等精准名词): {len(grounded)} 张 ({len(grounded)/100:.1f}%)")
print(f"  - 泛化 CV 物理修正样本 (仅标注全图偏色/饱和度公式，无具体实体名称): {len(generic_cv)} 张 ({len(generic_cv)/100:.1f}%)")
print(f"  - 零缺陷自洽放行样本 (审查通过): {len(pure_pass)} 张 ({len(pure_pass)/100:.1f}%)")
print("=" * 60)

# 进一步交叉分析：在从未生成大图看板的 4106 张图中，它们的最终标注状态是什么？
unseen_ids = sorted(list(set(range(1, 10001)) - tasks_with_sheets))
all_map = {a["human_review"]["task_id"]: a for a in anns}

print("\n【从未上过看板大图的 4106 张图样本抽样分析】")
for tid in unseen_ids[:15]:
    ann = all_map[tid]
    defs = [f"{d['id']}-{d.get('severity','')}" for d in ann.get("defects", [])]
    note = ann.get("review_note", "")
    print(f"Task #{tid:5d}: defs={defs} | note: {note}")

# 统计这 4106 张图的 review_note 前缀与特征
from collections import Counter
unseen_prefixes = Counter()
for tid in unseen_ids:
    ann = all_map[tid]
    note = ann.get("review_note", "")
    prefix = note.split("：")[0] if "：" in note else note[:15]
    unseen_prefixes[prefix] += 1

print("\n【未上大图任务的 review_note 前缀分布】")
for k, v in unseen_prefixes.most_common(10):
    print(f"  {k}: {v} ({v/len(unseen_ids)*100:.1f}%)")

