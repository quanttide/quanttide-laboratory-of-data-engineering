# QuantTide Laboratory of Data Engineering

数据工程实验田。

## qtdata-cli — 数据处理流程编排实验

模拟上层 CLI 串联 `qtcloud-data-cli` 完成完整的数据处理流程：

```mermaid
flowchart LR
    A[客户数据] -->|receive| B[原始数据]
    B -->|处理| C[处理结果]
    C -->|send| D[分享链接]
```

### 快速演示（无需真实凭证）

```bash
chmod +x bin/qtdata-cli
./bin/qtdata-cli demo
```

### 完整流程（需配置 qtcloud-data CLI 凭证）

```bash
export QTDATA_CLI=qtcloud-data
./bin/qtdata-cli process ABC-001 "https://dropbox.com/s/xxx/data.csv"
```

### 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `QTDATA_CLI` | `qtcloud-data` | CLI 命令路径 |
| `PROCESSOR` | `./bin/processor.py` | 处理脚本路径 |
| `WORKDIR` | `./work` | 工作目录 |
