#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_clean_consolidated_1_10000.py
从所有 20 个最新分批交付文件（含 Double Check 最新改判结果）重新整合生成全量 1-10000 纯净交付版本。
保证：
1. 每一条记录均显式包含 "review_note": ""（空字符串，保留该字段，不删除键名）。
2. 严守权威基准 exports/reviewed_20260930_084839.json 契约，每条 annotation 严格 14 个核心字段，零多余键、零缺失键。
3. 严格 10,000 个任务，task_id 连续无断号、无重复 (1 ~ 10000)。
4. 输出：
   - exports/reviewed_1_10000_clean_{timestamp}.json（最新时间戳版本）
   - exports/reviewed_1_10000_clean.json（标准交付别名版本）
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
EXPORTS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports"

BATCH_SPECS = [
    (1, 500, "reviewed_1_500_20260930_111408.json"),
    (501, 1000, "reviewed_501_1000_20260930_111842.json"),
    (1001, 1500, "reviewed_1001_1500_20260930_111612.json"),
    (1501, 2000, "reviewed_1501_2000_20260930_082139.json"),
    (2001, 2500, "reviewed_2001_2500_20260930_093827.json"),
    (2501, 3000, "reviewed_2501_3000_20260930_101014.json"),
    (3001, 3500, "reviewed_3001_3500_20260930_110626.json"),
    (3501, 4000, "reviewed_3501_4000_20260930_121202.json"),
    (4001, 4500, "reviewed_4001_4500_20260930_135528.json"),
    (4501, 5000, "reviewed_4501_5000_20260930_140753.json"),
    (5001, 5500, "reviewed_5001_5500_20260930_142848.json"),
    (5501, 6000, "reviewed_5501_6000_20260930_150135.json"),
    (6001, 6500, "reviewed_6001_6500_20260930_153605.json"),
    (6501, 7000, "reviewed_6501_7000_20260930_155809.json"),
    (7001, 7500, "reviewed_7001_7500_20260930_161800.json"),
    (7501, 8000, "reviewed_7501_8000_20260930_182342.json"),
    (8001, 8500, "reviewed_8001_8500_20260930_184910.json"),
    (8501, 9000, "reviewed_8501_9000_20260930_190928.json"),
    (9001, 9500, "reviewed_9001_9500_20260930_192616.json"),
    (9501, 10000, "reviewed_9501_10000_20260930_194247.json"),
]

REQUIRED_ANN_KEYS = [
    "image_id",
    "file_path",
    "source_dataset",
    "role",
    "defects",
    "gpt_score",
    "labeling_model",
    "labeling_timestamp",
    "original_gpt_score",
    "review_status",
    "review_note",
    "reviewed_score",
    "needs_rescoring",
    "human_review"
]

def main():
    print("=== 开始从 20 个最新批次整合生成 review_note 为空的纯净整合版 ===")
    
    clean_annotations = []
    seen_task_ids = set()
    total_defects_count = 0
    total_recheck_modified = 0
    
    for start_id, end_id, filename in BATCH_SPECS:
        file_path = EXPORTS_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"缺失批次导出文件: {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            batch_data = json.load(f)
            
        anns = batch_data.get("annotations", [])
        expected_len = end_id - start_id + 1
        if len(anns) != expected_len:
            raise ValueError(f"批次 {filename} 数量不符！预期 {expected_len}，实际 {len(anns)}")
            
        batch_ids = []
        for ann in anns:
            hr = ann.get("human_review", {})
            t_id = hr.get("task_id")
            if t_id is None:
                raise ValueError(f"记录缺失 task_id: {ann.get('image_id')} in {filename}")
            if t_id in seen_task_ids:
                raise ValueError(f"发现重复 task_id: {t_id} in {filename}!")
            seen_task_ids.add(t_id)
            batch_ids.append(t_id)
            
            # 构建严格符合 Schema 规范的纯净 Annotation 字典
            # 严格保留 14 个核心字段，且确保 review_note 字段存在并为空字符串 ""
            clean_item = {}
            for k in REQUIRED_ANN_KEYS:
                if k == "review_note":
                    clean_item["review_note"] = ""
                elif k in ann:
                    clean_item[k] = ann[k]
                else:
                    raise KeyError(f"任务 #{t_id} 缺失必须字段: {k}")
                    
            # 校验 defects 格式
            defects = clean_item.get("defects", [])
            total_defects_count += len(defects)
            for d in defects:
                assert "id" in d and "name" in d and "severity" in d and "description" in d
                
            clean_annotations.append(clean_item)
            
        print(f"  [+] 批次 {start_id:5d}-{end_id:5d} ({filename}) 校验合入 500 条 (task_id: {min(batch_ids)} ~ {max(batch_ids)})")

    # 全局一致性强校验
    print("\n=== 全局数据一致性与序号校验 ===")
    total_count = len(clean_annotations)
    print(f"合入标注总数: {total_count}")
    if total_count != 10000:
        raise ValueError(f"标注总数必须为 10000，当前为: {total_count}")
        
    expected_ids = set(range(1, 10001))
    if seen_task_ids != expected_ids:
        missing = sorted(list(expected_ids - seen_task_ids))
        raise ValueError(f"序号存在断号或超出: 缺失前 5 项: {missing[:5]}")
        
    # 按 task_id 升序严整排列
    clean_annotations.sort(key=lambda a: a["human_review"]["task_id"])
    
    # 验证每一个 task 的 review_note 都是严格等于 ""
    for idx, ann in enumerate(clean_annotations):
        t_id = ann["human_review"]["task_id"]
        assert t_id == idx + 1, f"任务排序异常: idx={idx+1}, task_id={t_id}"
        assert ann["review_note"] == "", f"任务 #{t_id} review_note 不为空！"
        assert set(ann.keys()) == set(REQUIRED_ANN_KEYS), f"任务 #{t_id} 字段集合不匹配基准"

    print("[PASS] 10,000 个任务完全按 1~10000 升序排列，所有条目 review_note 字段均存在且严格为空字符串！")
    print(f"总缺陷数: {total_defects_count} (平均每张图 {total_defects_count/10000:.2f} 处缺陷)")

    now_iso = datetime.now(timezone.utc).isoformat()
    now_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    final_output = {
        "meta": {
            "exported_at": now_iso,
            "total_images": 10000,
            "needs_rescoring": True
        },
        "annotations": clean_annotations
    }

    timestamped_filename = f"reviewed_1_10000_clean_{now_ts}.json"
    timestamped_path = EXPORTS_DIR / timestamped_filename
    alias_filename = "reviewed_1_10000_clean.json"
    alias_path = EXPORTS_DIR / alias_filename
    
    print("\n=== 写入纯净整合版交付文件 ===")
    print(f"1. 写入时间戳交付版: {timestamped_filename}")
    with open(timestamped_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    ts_size_mb = timestamped_path.stat().st_size / 1024 / 1024
    print(f"   完成写入: {timestamped_filename} ({ts_size_mb:.2f} MB)")

    print(f"2. 写入标准别名交付版: {alias_filename}")
    with open(alias_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    alias_size_mb = alias_path.stat().st_size / 1024 / 1024
    print(f"   完成写入: {alias_filename} ({alias_size_mb:.2f} MB)")

    print(f"\n[SUCCESS] 全量 1-10000 纯净交付版本整合全部达成！")

if __name__ == "__main__":
    main()
