#!/usr/bin/env bash
# sec-credit 分类实验 — 通过 pipeline 编排
set -euo pipefail
cd "$(dirname "$0")"

echo "══════════════════════════════════════════════"
echo "  SEC 信贷协议识别 — Pipeline 验证"
echo "══════════════════════════════════════════════"
echo ""

# 1. 解析 Exhibit（从 samples JSON → CSV）
echo "▶ Step 1/3: 解析 Exhibit"
python3 parse_exhibit.py "" /tmp/sec_credit_01_exhibits.csv
echo ""

# 2. 证据抽取 + 规则引擎
echo "▶ Step 2/3: 抽取证据 + 规则引擎"
python3 classifier.py /tmp/sec_credit_01_exhibits.csv /tmp/sec_credit_02_evidence.csv
echo ""

# 3. LLM 分类 + 验收
echo "▶ Step 3/3: LLM 分类 + 规则验收"
python3 llm_classify.py /tmp/sec_credit_02_evidence.csv /tmp/sec_credit_03_final.csv
echo ""

# 结果汇总
echo "────────────────────────────────────────────"
echo "  最终结果"
echo "────────────────────────────────────────────"
column -t -s, /tmp/sec_credit_03_final.csv 2>/dev/null || cat /tmp/sec_credit_03_final.csv
echo ""

passed=$(grep -c 'True' /tmp/sec_credit_03_final.csv || true)
echo "✓ 目标文件: $passed"
