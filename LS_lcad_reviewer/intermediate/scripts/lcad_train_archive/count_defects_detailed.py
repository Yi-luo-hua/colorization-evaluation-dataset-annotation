# -*- coding: utf-8 -*-
"""
count_defects_detailed.py
精细统计最新 reviewed_1_10000_clean.json 的缺陷分布：
1. 单样本缺陷项数分布 (0, 1, 2, 3, 4, 5+ 个缺陷的任务数及占比)
2. 各缺陷大类 (A, B, C, D, E1, E2, F) 的总缺陷实例数、涉及的任务数及在总缺陷中的占比
3. 各缺陷大类下细分严重级别 (L1, L2, L3) 的精确数量与占比
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

TARGET_FILE = Path(r"d:\学业文件\MCL\上色评价_数据集标注\LS_lcad_reviewer\exports\reviewed_1_10000_clean.json")

def main():
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    annotations = data['annotations']
    total_tasks = len(annotations)

    # 1. 缺陷数量分布 (per task)
    defect_counts_per_task = Counter()
    
    # 2. 缺陷大类统计
    # defect_id -> total count
    defect_type_total = Counter()
    # defect_id -> set of task_ids
    defect_type_tasks = defaultdict(set)
    
    # 3. 细分级别统计: (defect_id, severity) -> count
    severity_counter = Counter()

    total_defect_instances = 0

    for ann in annotations:
        tid = ann['human_review']['task_id']
        defects = ann.get('defects', [])
        num_defects = len(defects)
        defect_counts_per_task[num_defects] += 1
        total_defect_instances += num_defects

        for d in defects:
            d_id = d['id']
            sev = d.get('severity', '')
            defect_type_total[d_id] += 1
            defect_type_tasks[d_id].add(tid)
            severity_counter[(d_id, sev)] += 1

    print(f"=== 全量 10,000 条任务缺陷详细统计 ===")
    print(f"总任务数: {total_tasks}")
    print(f"总缺陷实例数: {total_defect_instances}")
    print()

    print("--- 1. 每张图像包含的缺陷个数分布 (Defect Count per Image) ---")
    for cnt in sorted(defect_counts_per_task.keys()):
        num = defect_counts_per_task[cnt]
        pct = (num / total_tasks) * 100
        desc = "审查通过 (放行)" if cnt == 0 else f"{cnt} 项缺陷"
        print(f"  * {desc:<16}: {num:>5} 张 ({pct:>5.2f}%)")
    print()

    print("--- 2. 各缺陷大类统计 (Defect Type Overview) ---")
    type_names = {
        'A': '缺色',
        'B': '溢色',
        'C': '错色',
        'D': '偏色',
        'E1': '过饱和',
        'E2': '欠饱和',
        'F': '视觉自然度'
    }
    for d_id in ['A', 'B', 'C', 'D', 'E1', 'E2', 'F']:
        tot = defect_type_total[d_id]
        task_num = len(defect_type_tasks[d_id])
        task_pct = (task_num / total_tasks) * 100
        tot_pct = (tot / total_defect_instances) * 100 if total_defect_instances > 0 else 0
        print(f"  * [{d_id}] {type_names[d_id]:<6}: 出现 {tot:>5} 次 (占总缺陷 {tot_pct:>5.2f}%) | 涉及 {task_num:>5} 张图像 (占全集 {task_pct:>5.2f}%)")
    print()

    print("--- 3. 各缺陷细分级别分布 (Severity Breakdown) ---")
    for d_id in ['A', 'B', 'C', 'D', 'E1', 'E2', 'F']:
        print(f"  * [{d_id}] {type_names[d_id]}:")
        if d_id == 'A':
            cnt = severity_counter[('A', '')]
            print(f"      - 熔断 (无细分): {cnt:>5} 处 (100.00%)")
        else:
            tot = defect_type_total[d_id]
            for s in ['L1', 'L2', 'L3']:
                cnt = severity_counter[(d_id, s)]
                pct = (cnt / tot) * 100 if tot > 0 else 0
                print(f"      - {s}: {cnt:>5} 处 ({pct:>5.2f}%)")

if __name__ == '__main__':
    main()
