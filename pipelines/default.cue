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
