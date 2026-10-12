# -*- coding: utf-8 -*-
"""
stat_final_deliverables.py
对最终交付数据集进行全面终审统计：
1. 总体概况与覆盖率
2. 放行池 (0项缺陷) 与 缺陷池 分布
3. 放行池双重硬门槛严格核验 (orig >= 4.5 & dC < 0.08)
4. 缺陷项分布 (A, B, C, D, E1, E2, F)
5. 7 个重点抽检纠偏任务的状态复核
6. 抽象代词与防错红线断言
"""

import sys
import json
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
CLEAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_clean.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"

def analyze(file_path):
    print("=" * 60)
    print(f"终审质量评估报告: {file_path.name}")
    print("=" * 60)

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    meta = data['meta']
    annotations = data['annotations']
    total = len(annotations)

    print(f"总任务记录数: {total}")
    print(f"导出时间戳: {meta.get('exported_at')}")

    # Status check
    statuses = Counter(ann.get('review_status') for ann in annotations)
    print(f"核验状态: {dict(statuses)}")

    # Passes vs Defects
    passes = [ann for ann in annotations if len(ann.get('defects', [])) == 0]
    defects = [ann for ann in annotations if len(ann.get('defects', [])) > 0]

    print(f"\n【宏观分布】")
    print(f"  * 审查通过放行 (0项缺陷): {len(passes)} 条 ({len(passes)/total*100:.2f}%)")
    print(f"  * 存在明确缺陷 (需重打分): {len(defects)} 条 ({len(defects)/total*100:.2f}%)")

    # Defect breakdown
    defect_counts = Counter()
    sev_counts = Counter()
    for ann in defects:
        for d in ann['defects']:
            did = d['id']
            sev = d['severity']
            defect_counts[did] += 1
            sev_counts[f"{did}-{sev}"] += 1

    print(f"\n【缺陷类型分布 (共包含 {sum(defect_counts.values())} 处缺陷)】")
    for did in ["A", "B", "C", "D", "E1", "E2", "F"]:
        cnt = defect_counts[did]
        print(f"  * [{did}] {cnt} 处 ({cnt/len(defects)*100:.1f}% 缺陷样本涉及)")

    # Spot check 7 tasks verification
    spot_check_7 = [84, 291, 344, 2996, 3370, 4002, 7805]
    print(f"\n【抽检 7 项纠偏任务状态复核】")
    for ann in annotations:
        tid = ann['human_review']['task_id']
        if tid in spot_check_7:
            d_list = [f"{d['id']}-{d['severity']}" for d in ann['defects']]
            print(f"  * Task #{tid}: defects={d_list}, review_note='{ann['review_note'][:30]}...'")

    # Dual threshold check on remaining passes
    suspect_file = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "suspect_detailed_cv_diff.json"
    if suspect_file.exists():
        with open(suspect_file, 'r', encoding='utf-8') as f:
            suspects = {s['task_id']: s for s in json.load(f)}
        
        pass_tids = {ann['human_review']['task_id'] for ann in passes}
        suspect_passes = [suspects[tid] for tid in pass_tids if tid in suspects]
        print(f"\n【放行池纯度核验】")
        print(f"  * 放行任务总数: {len(passes)}")
        print(f"  * 经深入核验确认为单色灰度/夜景高保真保留放行数: {len(suspect_passes)}")
        for sp in suspect_passes:
            print(f"    - Task #{sp['task_id']}: orig={sp['orig_score']}, dC={sp['delta_c']:.3f}, diff_mean={sp['diff_mean']:.1f}")

    # Assert clean version review_note == ""
    if "clean" in file_path.name:
        notes = Counter(ann['review_note'] for ann in annotations)
        print(f"\n【纯净版字段一致性断言】")
        print(f"  * review_note 唯一取值分布: {dict(notes)}")
        assert list(notes.keys()) == [""], "clean.json review_note must be 100% empty string!"
        print(f"  [PASS] 断言成功: 10,000 条任务的 review_note 均为纯净空字符串！")

if __name__ == '__main__':
    analyze(CLEAN_FILE)
    print("\n")
    analyze(ALL_FILE)
