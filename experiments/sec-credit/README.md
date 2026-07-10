# SEC 信贷协议识别 — Pipeline 实验

验证 `data/profile/sec-credit/blueprint.cue` 定义的分类策略，通过 3 步 Pipeline 编排。

## Pipeline

| Step | 脚本 | 功能 |
|---|---|---|
| parse-exhibit | `parse_exhibit.py` | 从 samples/ JSON 解析为 CSV |
| extract-evidence | `classifier.py` | 抽取证据 + 规则引擎分类 |
| llm-classify | `llm_classify.py` | LLM 判断 + 规则验收（当前为 stub） |

## 注册的 CLI Pipeline

已注册到 `pipelines/default.cue`，可通过 CLI 查看：

```bash
# 查看
qtcloud-data pipeline list
qtcloud-data pipeline show sec-credit
```

## 样本

5 个样本覆盖所有 document_type，含负例 Indenture。

## 运行

```bash
# 方式一：手动逐步执行
./run.sh

# 方式二：通过 qtdata-cli 编排（需配置 credential）
qtdata-cli process sec-credit "experiments/sec-credit/samples/" --pipeline sec-credit
```

## 结果

5/5 全部通过，验证了 CUE pipeline 定义到可执行程序的映射。
