package pipelines

// ── Schema ──
#Step: {
	name!:    string
	command!: string
	input?:   string
	output?:  string
}

#Pipeline: {
	name!:        string
	description?: string
	steps!: [...#Step]
}

// ── 流水线定义 ──

// CSV 标准化：校验 → 增强
csvStandard: #Pipeline & {
	name: "csv-standard"
	description: "CSV 格式校验 → 元数据注入 → 空值分析"

	steps: [{
		name:    "validate"
		command: "./bin/processor.py"
	}, {
		name:    "enrich"
		command: "./bin/enricher.py"
	}]
}

// 数据标注（预留）
annotation: #Pipeline & {
	name: "annotation"
	description: "LLM 辅助数据标注"

	steps: [{
		name:    "preprocess"
		command: "./bin/processor.py"
	}]
}

// SEC 信贷协议识别：解析 Exhibit → 抽取证据 → LLM 分类
secCredit: #Pipeline & {
	name: "sec-credit"
	description: "从 8-K 附件中分类筛选 Credit Agreement"

	steps: [{
		name:    "parse-exhibit"
		command: "./experiments/sec-credit/parse_exhibit.py"
	}, {
		name:    "extract-evidence"
		command: "./experiments/sec-credit/classifier.py"
	}, {
		name:    "llm-classify"
		command: "./experiments/sec-credit/llm_classify.py"
	}]
}
