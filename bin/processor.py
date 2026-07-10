#!/usr/bin/env python3
"""量潮数据处理 — 模拟处理器

从 qtdata-cli 调用，接收原始 CSV，输出处理后的 CSV。
用作流程验证的占位处理器。
"""

import csv
import sys


def process(input_path: str, output_path: str) -> None:
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if not rows:
        # 空文件，透传
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
        return

    # 模拟处理：添加处理时间戳和状态列
    processed = []
    for row in rows:
        row["_processed_at"] = "2026-07-10"
        row["_status"] = "ok"
        processed.append(row)

    output_fields = fieldnames + ["_processed_at", "_status"]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(processed)

    print(f"  处理完成: {len(processed)} 行 → {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: processor.py <input.csv> <output.csv>")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2])
