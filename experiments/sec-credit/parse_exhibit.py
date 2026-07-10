#!/usr/bin/env python3
"""Pipeline Step 1: 解析 Exhibit

从 samples/ 目录加载样本 JSON，输出 CSV 供后续步骤处理。
Output: file_name, title, form_type, exhibit_type, text_head
"""

import csv
import json
import sys
from pathlib import Path


def main():
    output = sys.argv[2] if len(sys.argv) > 2 else "/dev/stdout"

    samples_dir = Path(__file__).parent / "samples"

    rows = []
    for f in sorted(samples_dir.glob("*.json")):
        with open(f) as fh:
            ex = json.load(fh)
        rows.append({
            "file_name": ex.get("file_name", ""),
            "title": ex.get("title", ""),
            "form_type": ex.get("metadata", {}).get("form_type", ""),
            "exhibit_type": ex.get("metadata", {}).get("exhibit_type", ""),
            "text_head": ex.get("text_head", ""),
        })

    with open(output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file_name", "title", "form_type", "exhibit_type", "text_head"])
        w.writeheader()
        w.writerows(rows)

    print(f"  已解析 {len(rows)} 个 Exhibit → {output}", file=sys.stderr)


if __name__ == "__main__":
    main()
