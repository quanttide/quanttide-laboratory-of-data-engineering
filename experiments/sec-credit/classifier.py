#!/usr/bin/env python3
"""SEC 信贷协议识别分类器实验

基于 blueprint.cue 定义的分类策略：
1. 解析 Exhibit metadata + text_head
2. 抽取 evidence（title / role / section / term）
3. 规则引擎判断 document_type
4. 输出结构化结果 + confidence
"""

import json
import re
import sys
from pathlib import Path


# ── 强正/负特征模式 ──

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
    "credit_agreement_original": [
        r"^Credit Agreement$",
        r"^Loan Agreement$",
        r"Amended and Restated Credit Agreement",
        r"First Lien Credit Agreement",
    ],
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
    "indenture_or_notes": [
        r"^INDENTURE$",
        r"Indenture$",
    ],
}


def extract_evidence(text: str) -> dict:
    """抽取可解释证据"""
    evidence = {
        "title_evidence": [],
        "role_evidence": [],
        "section_topic_evidence": [],
        "term_evidence": [],
        "negative_evidence": [],
    }

    # Title evidence
    lines = text.split("\n")
    title = lines[0].strip() if lines else ""
    for doc_type, patterns in TITLE_PATTERNS.items():
        for p in patterns:
            if re.search(p, title, re.IGNORECASE):
                evidence["title_evidence"].append(f"title matches {doc_type}: {p}")

    # Role evidence
    for name, pattern in POSITIVE_PATTERNS.items():
        if re.search(pattern, text):
            evidence["role_evidence"].append(f"found positive: {name}")

    # Negative evidence
    for name, pattern in NEGATIVE_PATTERNS.items():
        if re.search(pattern, text):
            evidence["negative_evidence"].append(f"found negative: {name}")

    # Term evidence
    term_patterns = {
        "interest_rate": r"\bInterest Rate\b",
        "maturity_date": r"\bMaturity Date\b",
        "revolving_credit": r"\bRevolving Credit\b",
        "term_sofr": r"\bTerm SOFR\b",
    }
    for name, pattern in term_patterns.items():
        if re.search(pattern, text):
            evidence["term_evidence"].append(f"found term: {name}")

    return evidence


def classify(evidence: dict) -> dict:
    """规则引擎：基于 evidence 判断 document_type"""
    title_evidence = " ".join(evidence["title_evidence"]).lower()
    pos_count = len(evidence["role_evidence"])
    neg_count = len(evidence["negative_evidence"])
    has_term = len(evidence["term_evidence"]) > 0

    result = {
        "document_type": "other",
        "is_target": False,
        "confidence": 0.0,
        "positive_evidence": evidence["role_evidence"] + evidence["term_evidence"],
        "negative_evidence": evidence["negative_evidence"],
    }

    # 强负：INDENTURE + Trustee + The Notes
    if any("indenture" in e.lower() for e in evidence["negative_evidence"]):
        if any("trustee" in e.lower() for e in evidence["negative_evidence"]):
            result["document_type"] = "indenture_or_notes"
            result["is_target"] = False
            result["confidence"] = 0.9
            return result

    # 根据标题判断子类型（letter 优先于 extension）
    for ev in evidence["title_evidence"]:
        el = ev.lower()
        if "letter" in el:
            result["document_type"] = "credit_agreement_related_letter"
            break
        if "amendment" in el:
            result["document_type"] = "credit_agreement_amendment"
            break
        if "extension" in el:
            result["document_type"] = "credit_agreement_extension"
            break
        if "original" in el:
            result["document_type"] = "credit_agreement_original"
            break

    # 如果标题判断为其他，但证据充分
    if result["document_type"] == "other":
        # 检查是否有 letter 特征
        if any("letter" in e.lower() for e in evidence["title_evidence"]):
            result["document_type"] = "credit_agreement_related_letter"
        elif pos_count >= 3 and has_term:
            result["document_type"] = "credit_agreement_original"

    # 计算 confidence
    if result["document_type"] != "other":
        total = pos_count + neg_count
        if total > 0:
            result["confidence"] = round(pos_count / (pos_count + neg_count), 2)
        result["is_target"] = not result["document_type"].startswith("indenture")

    return result


def run_exhibit(exhibit: dict) -> dict:
    """处理单个 exhibit"""
    text = f"{exhibit.get('title', '')}\n{exhibit.get('text_head', '')}\n"
    text += "\n".join(exhibit.get("metadata", {}).values())

    evidence = extract_evidence(text)
    result = classify(evidence)
    result["file_name"] = exhibit.get("file_name", "")
    result["expected"] = exhibit.get("expected_type", "")
    return result


def main():
    samples_dir = Path(__file__).parent / "samples"
    results = []

    for f in sorted(samples_dir.glob("*.json")):
        with open(f) as fh:
            exhibit = json.load(fh)
        result = run_exhibit(exhibit)
        results.append(result)

        status = "✓" if result["document_type"] == result["expected"] else "✗"
        print(f"{status} {result['file_name']}")
        print(f"  预期: {result['expected']}")
        print(f"  实际: {result['document_type']} (conf={result['confidence']})")
        if result["positive_evidence"]:
            print(f"  正证据: {result['positive_evidence'][:2]}")
        if result["negative_evidence"]:
            print(f"  负证据: {result['negative_evidence'][:2]}")
        print()

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["document_type"] == r["expected"])
    print(f"{'='*40}")
    print(f"结果: {passed}/{total} 通过 ({passed/total*100:.0f}%)")
    if passed == total:
        print("🎉 全部通过")
    else:
        print(f"⚠  {total - passed} 个未通过")
        sys.exit(1)


if __name__ == "__main__":
    main()
