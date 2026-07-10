#!/usr/bin/env bash
# sec-credit 分类实验
# 验证 blueprint 定义的分类策略在真实样本上的效果

set -euo pipefail
cd "$(dirname "$0")"

echo "══════════════════════════════════════════════"
echo "  SEC 信贷协议识别 — 分类实验"
echo "══════════════════════════════════════════════"
echo ""

# 样本数
total=$(ls samples/*.json 2>/dev/null | wc -l)
echo "样本数: $total"
echo ""

# 运行分类器
python3 classifier.py
