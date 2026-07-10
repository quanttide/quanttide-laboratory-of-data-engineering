#!/usr/bin/env python3
"""Pipeline Step 2: 抽取证据 + 规则引擎分类

Input CSV:  file_name, title, form_type, exhibit_type, text_head
Output CSV: file_name, document_type, is_target, confidence, evidence_json
"""

import csv
import json
import re
import sys


POSITIVE_PATTERNS = {
    "borrower": r"\bBorrower\b",
    "lender": r"\bLender[s]?\b",
    "admin_agent": r"\bAdministrative Agent\b",
    "credit_agreement": r"\bCredit Agreement\b",
    "commitment": r"\bCommitment[s]?\b",
    "credit_facility": r"\bCredit Facility\b",
    "maturity_date": r"\bMaturity Date\b",
    "revolving_credit": r"\bRevolving Credit\b",
}

NEGATIVE_PATTERNS = {
    "indenture": r"\bINDENTURE\b",
    "trustee": r"\bIndenture Trustee\b",
    "issuer": r"\bIssuer\b",
    "noteholder": r"\bNoteholder\b",
    "the_notes": r"\bThe Notes\b",
    "trust_indenture_act": r"\bTrust Indenture Act\b",
}

TITLE_PATTERNS = {
    "credit_agreement_related_letter": [
        r"Consent Letter",
        r"Extension Consent",
    ],
    "credit_agreement_amendment": [
        r"Amendment No\.\s*\d+",
        r"^First Amendment$",
        r"Amended Credit Agreement",
    ],
    "credit_agreement_extension": [
        r"Extension Agreement",
        r"Commitment Extension",
        r"Maturity Date Extension",
    ],
    "credit_agreement_original": [
        r"^Credit Agreement$",
        r"^Loan Agreement$",
        r"Amended and Restated Credit Agreement",
        r"First Lien Credit Agreement",
    ],
    "indenture_or_notes": [
        r"^INDENTURE$",
        r"Indenture$",
    ],
}


def extract_evidence(text: str) -> dict:
    evidence = {"title_evidence": [], "role_evidence": [], "negative_evidence": [], "term_evidence": []}
    lines = text.split("\n")
    title = lines[0].strip() if lines else ""
    for doc_type, patterns in TITLE_PATTERNS.items():
        for p in patterns:
            if re.search(p, title, re.IGNORECASE):
                evidence["title_evidence"].append(f"title matches {doc_type}")
    for name, pattern in POSITIVE_PATTERNS.items():
        if re.search(pattern, text):
            evidence["role_evidence"].append(name)
    for name, pattern in NEGATIVE_PATTERNS.items():
        if re.search(pattern, text):
            evidence["negative_evidence"].append(name)
    term_patterns = {"interest_rate": r"\bInterest Rate\b", "maturity_date": r"\bMaturity Date\b",
                     "revolving_credit": r"\bRevolving Credit\b", "term_sofr": r"\bTerm SOFR\b"}
    for name, pattern in term_patterns.items():
        if re.search(pattern, text):
            evidence["term_evidence"].append(name)
    return evidence


def classify(evidence: dict) -> dict:
    title_evidence = evidence["title_evidence"]
    pos_count = len(evidence["role_evidence"])
    neg_count = len(evidence["negative_evidence"])
    result = {"document_type": "other", "is_target": False, "confidence": 0.0}

    # 强负
    if any("indenture" in e for e in evidence["negative_evidence"]) and \
       any("trustee" in e for e in evidence["negative_evidence"]):
        result["document_type"] = "indenture_or_notes"
        result["is_target"] = False
        result["confidence"] = 0.9
        return result

    # 标题匹配（letter 优先）
    for e in title_evidence:
        el = e.lower()
        if "letter" in el:
            result["document_type"] = "credit_agreement_related_letter"; break
        if "amendment" in el:
            result["document_type"] = "credit_agreement_amendment"; break
        if "extension" in el:
            result["document_type"] = "credit_agreement_extension"; break
        if "original" in el:
            result["document_type"] = "credit_agreement_original"; break

    if result["document_type"] == "other":
        if "letter" in str(title_evidence).lower():
            result["document_type"] = "credit_agreement_related_letter"
        elif pos_count >= 3 and len(evidence["term_evidence"]) > 0:
            result["document_type"] = "credit_agreement_original"

    if result["document_type"] != "other":
        total = pos_count + neg_count
        result["confidence"] = round(pos_count / (pos_count + neg_count), 2) if total > 0 else 0.5
        result["is_target"] = not result["document_type"].startswith("indenture")

    return result


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else "/dev/stdin"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "/dev/stdout"

    rows = []
    with open(input_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = f"{row.get('title', '')}\n{row.get('text_head', '')}\n"
            evidence = extract_evidence(text)
            result = classify(evidence)
            row["document_type"] = result["document_type"]
            row["is_target"] = str(result["is_target"])
            row["confidence"] = str(result["confidence"])
            row["evidence"] = json.dumps(evidence)
            rows.append(row)

    with open(output_path, "w", newline="") as f:
        fields = ["file_name", "document_type", "is_target", "confidence", "evidence",
                   "title", "form_type", "exhibit_type", "text_head"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    summary = sum(1 for r in rows if r["document_type"] != "other")
    print(f"  分类完成: {len(rows)} 个, {summary} 个为目标文件", file=sys.stderr)


if __name__ == "__main__":
    main()
