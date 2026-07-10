package blueprints

// ── Schema ──

#Contract: {
	schema:  string // schema 文件路径（YAML 或 CUE）
	format?: string // csv / json / parquet（默认 csv）
}

#Acceptance: {
	rules!: [...string]
}

#Blueprint: {
	name!:        string
	description?: string
	contract: {
		input!:  #Contract
		output!: #Contract
	}
	pipeline!:    string  // 引用 pipelines/ 中的名称
	acceptance!:  #Acceptance
}

// ── 问卷清洗 Blueprint ──
questionnaireCleaning: #Blueprint & {
	name: "问卷清洗"
	description: "问卷数据清洗：格式校验 → 空值处理 → 质量评分"

	contract: {
		input: {
			schema: "../data/profile/questionnaire_cleaning/catelog/contract/source-contract.yaml"
			format: "csv"
		}
		output: {
			schema: "../data/profile/questionnaire_cleaning/catelog/contract/output-contract.yaml"
			format: "csv"
		}
	}

	pipeline: "csv-standard"

	acceptance: {
		rules: [
			"所有字段非空率 >= 95%",
			"输出行数 <= 输入行数（只减不增）",
			"每行有唯一 _row_id",
			"无 _quality = poor 的记录",
		]
	}
}

// ── CSV 数据标准化 Blueprint ──
csvStandardization: #Blueprint & {
	name: "CSV 数据标准化"
	description: "通用 CSV 标准化：校验 → 元数据注入 → 空值分析"

	contract: {
		input: {
			schema: "inline: 首行为列名，每行列数一致"
			format: "csv"
		}
		output: {
			schema: "inline: 追加 _row_id / _processed_at / _record_hash / _null_count / _quality"
			format: "csv"
		}
	}

	pipeline: "csv-standard"

	acceptance: {
		rules: [
			"所有行 _row_id 不重复",
			"所有行 _processed_at 格式为 ISO 8601",
			"所有行 _record_hash 长度 12",
			"_quality 仅包含 clean / minor / poor",
		]
	}
}
