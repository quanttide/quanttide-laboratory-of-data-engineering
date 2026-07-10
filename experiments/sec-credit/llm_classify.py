#!/usr/bin/env python3
"""Pipeline Step 3: LLM 分类 + 规则验收（stub）

Input CSV:  file_name, document_type, is_target, confidence, evidence
Output CSV: + final_type, final_target, final_confidence, review_needed

当前为占位实现：直接透传规则引擎结果。
后续接入 LLM API 后，基于 evidence 做 LLM 判断，规则引擎验收冲突。
"""

import csv
import json
import sys


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "/dev/stdout"

    rows = []
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            evidence = json.loads(row.get("evidence", "{}"))
            neg = evidence.get("negative_evidence", [])

            # 规则验收：LLM 判为目标但有强负特征 → 降级
            doc_type = row.get("document_type", "other")
            if doc_type not in ("indenture_or_notes", "other") and \
               any("indenture" in e for e in neg) and \
               any("trustee" in e for e in neg):
                row["final_type"] = "indenture_or_notes"
                row["final_target"] = "False"
                row["review_needed"] = "True"
                row["conflict_note"] = "LLM 判为 Credit Agreement，但规则发现强负特征"
            else:
                row["final_type"] = doc_type
                row["final_target"] = row.get("is_target", "False")
                row["review_needed"] = "False"
                row["conflict_note"] = ""

            row["final_confidence"] = row.get("confidence", "0")
            rows.append(row)

    with open(output_path, "w", newline="") as f:
        fields = ["file_name", "final_type", "final_target", "final_confidence",
                   "review_needed", "conflict_note", "document_type", "evidence",
                   "title", "is_target", "confidence", "form_type", "exhibit_type", "text_head"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    reviews = sum(1 for r in rows if r.get("review_needed") == "True")
    print(f"  验收完成: {len(rows)} 个, {reviews} 个需人工复核", file=sys.stderr)


if __name__ == "__main__":
    main()
