#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_stream_1_10000.py
整合生成全量 1-10000 的 Label Studio 流式抽检包:
LS_lcad_reviewer/streams/tasks_lcad_1_10000_stream.json
确保 100% 包含 Double Check 最新改判结果，且完美适配 interface_dual_v4.xml。
"""

import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
STREAMS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "streams"
OUT_FILE = STREAMS_DIR / "tasks_lcad_1_10000_stream.json"

batch_ranges = [(i, min(i + 499, 10000)) for i in range(1, 10001, 500)]

all_stream_tasks = []
seen_ids = set()

for start_id, end_id in batch_ranges:
    batch_file = STREAMS_DIR / f"tasks_lcad_{start_id}_{end_id}_stream.json"
    if not batch_file.exists():
        raise FileNotFoundError(f"Missing stream batch: {batch_file}")
    
    with open(batch_file, "r", encoding="utf-8") as f:
        tasks = json.load(f)
        
    print(f"Batch {start_id:5d}-{end_id:5d}: {len(tasks)} tasks")
    for t in tasks:
        tid = t["id"]
        if tid in seen_ids:
            raise ValueError(f"Duplicate task id: {tid}")
        seen_ids.add(tid)
        all_stream_tasks.append(t)

if len(all_stream_tasks) != 10000:
    raise ValueError(f"Expected 10000 tasks, got {len(all_stream_tasks)}")

print(f"Total tasks merged: {len(all_stream_tasks)}")
print(f"Writing to {OUT_FILE.name}...")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_stream_tasks, f, ensure_ascii=False, indent=2)

file_size_mb = OUT_FILE.stat().st_size / (1024 * 1024)
print(f"[SUCCESS] Exported 1-10000 stream package: {OUT_FILE} ({file_size_mb:.2f} MB)")
