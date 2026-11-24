"""Check the structure of one agy delivery against its single-Markdown packet."""
import argparse
import json
import re
from pathlib import Path

CATEGORIES = {"A", "B", "C", "D", "E1", "E2", "F"}
STATUSES = {"hit", "clear"}


def validate(packet):
    body = packet.read_text(encoding="utf8")
    expected = re.findall(r"!\[(S\d+)\]\(", body)
    result = re.search(r"结果写入 (\.\./_results/[a-f0-9]{32}\.json)", body)
    if not expected or not result:
        raise ValueError("任务 Markdown 缺少样本或结果路径")
    rows = json.loads((packet.parent / result[1]).read_text(encoding="utf-8-sig"))
    return validate_rows(rows, expected)


def validate_rows(rows, expected):
    if not isinstance(rows, list) or any(not isinstance(r, dict) for r in rows):
        raise ValueError("结果应为样本对象数组")
    ids = [r.get("id") for r in rows]
    if len(ids) != len(expected) or set(ids) != set(expected):
        raise ValueError("结果的 S 编号与任务不一致")
    for row in rows:
        key = row["id"]
        checks = row.get("checks")
        if not isinstance(checks, dict) or set(checks) != CATEGORIES or any(
            s not in STATUSES for s in checks.values()
        ):
            raise ValueError(f"{key}.checks 七类状态不完整或不合法")
        defects = row.get("defects")
        if not isinstance(defects, list):
            raise ValueError(f"{key}.defects 应为数组")
        hits = set()
        for i, defect in enumerate(defects):
            if not isinstance(defect, dict) or defect.get("severity") not in ("L1", "L2", "L3") or not all(
                isinstance(defect.get(k), str) and defect[k].strip() for k in ("object", "description", "category")
            ):
                raise ValueError(f"{key}.defects[{i}] 字段有误")
            hits.add(defect["category"])
        if hits != {k for k,v in checks.items() if v == "hit"}:
            raise ValueError(f"{key}.defects 类别与 hit 不一致")
    return len(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    try:
        print(f"结构通过：{validate(args.packet)} 条")
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f"{error}\n")
