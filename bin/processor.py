#!/usr/bin/env python3
"""量潮数据处理器 — CSV 格式校验 & 元数据注入

从 qtdata-cli 编排调用，职责：
1. 校验 CSV 格式（列数一致性、非空行）
2. 注入处理元数据（时间戳、记录指纹、行号）
3. 输出标准化 CSV

用法: python3 processor.py <input.csv> <output.csv>
返回码: 0=成功, 1=格式错误
"""

import csv
import hashlib
import sys
from datetime import datetime, timezone


def process(input_path: str, output_path: str) -> None:
    with open(input_path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        print("错误: 空文件", file=sys.stderr)
        sys.exit(1)

    header = rows[0]
    num_cols = len(header)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    errors = 0

    # 校验并构建输出
    output = []
    output.append(list(header) + ["_row_id", "_processed_at", "_record_hash"])

    for i, row in enumerate(rows[1:], start=2):
        # 跳过完全空行
        if not any(cell.strip() for cell in row):
            continue
        # 列数不一致
        if len(row) != num_cols:
            print(f"  警告: 第{i}行列数不一致 (期望{num_cols}列, 实际{len(row)}列)", file=sys.stderr)
            errors += 1
        # 记录指纹
        finger = hashlib.sha256("|".join(row).encode()).hexdigest()[:12]
        output.append(list(row) + [str(i), now, finger])

    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output)

    total = len(output) - 1  # 减去 header
    print(f"  共 {total} 条记录, {errors} 条警告", file=sys.stderr)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: processor.py <input.csv> <output.csv>", file=sys.stderr)
        sys.exit(1)
    process(sys.argv[1], sys.argv[2])
