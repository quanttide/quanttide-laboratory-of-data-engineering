# SEC 信贷协议识别 — 分类实验

验证 `data/profile/sec-credit/blueprint.cue` 定义的分类策略。

## 样本

| # | 文件 | 预期类型 | 来源 |
|---|---|---|---|
| 1 | `enviri_amendment` | credit_agreement_amendment | ENVIRI Corp 8-K EX-10.1 |
| 2 | `goodyear_amendment` | credit_agreement_amendment | Goodyear 10-Q EX-10.2 |
| 3 | `centerpoint_extension` | credit_agreement_extension | CenterPoint Energy 8-K EX-10.1 |
| 4 | `oge_letter` | credit_agreement_related_letter | OGE Energy 8-K EX-10.01 |
| 5 | `ford_indenture` | indenture_or_notes（负例） | Ford Credit 8-K EX-4.1 |

## 分类策略

1. **证据抽取**：从 title + text_head 中提取角色实体、条款术语、章节主题
2. **规则引擎**：强正/强负特征组合判断（Borrower + Admin Agent vs Indenture Trustee）
3. **子类型**：标题模式匹配（Amendment / Extension / Letter / Original）
4. **优先级**：强负 → Letter → Amendment → Extension → Original

## 运行

```bash
./run.sh
```

## 实验结果

当前 5/5 样本通过，验证了 blueprint 的核心分类逻辑。
