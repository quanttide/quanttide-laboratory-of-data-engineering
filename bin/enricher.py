#!/usr/bin/env python3
"""数据增强器 — Pipeline 第二步示例

在 processor.py 校验之后运行，追加派生字段。
演示多步 Pipeline 中每一步的输入输出衔接。
"""

import csv
import hashlib
import sys
from datetime import datetime, timezone


def enrich(input_path: str, output_path: str) -> None:
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    enriched = []
    for row in rows:
        # 空值统计
        nulls = sum(1 for v in row.values() if not v)
        # 记录质量等级
        if nulls == 0:
            quality = "clean"
        elif nulls <= 1:
            quality = "minor"
        else:
            quality = "poor"

        row["_null_count"] = str(nulls)
        row["_quality"] = quality
        enriched.append(row)

    output_fields = fieldnames + ["_null_count", "_quality"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(enriched)

    print(f"  增强完成: {len(enriched)} 行, 追加空值统计/质量等级")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: enricher.py <input.csv> <output.csv>", file=sys.stderr)
        sys.exit(1)
    enrich(sys.argv[1], sys.argv[2])
