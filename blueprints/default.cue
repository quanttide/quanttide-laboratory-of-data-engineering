package blueprints

#ContractSchema: {
	schema:  string // schema 文件路径（YAML / CUE）或 inline 描述
	format?: string // csv / json / parquet（默认 csv）
	rules?:  [...string] // 验收规则：输出数据必须满足的约束
}

#Blueprint: {
	name!:        string
	description?: string
	contract: {
		input!:  #ContractSchema
		output!: #ContractSchema & {
			rules!: [...string] // 验收规则在 output 中必填
		}
	}
	pipeline!: string // 引用 pipelines/ 中的名称
}

// ── 问卷清洗 ──
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
			rules: [
				"所有字段非空率 >= 95%",
				"输出行数 <= 输入行数",
				"每行有唯一 _row_id",
				"无 _quality = poor 的记录",
			]
		}
	}

	pipeline: "csv-standard"
}

// ── CSV 数据标准化 ──
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
			rules: [
				"所有行 _row_id 不重复",
				"所有行 _processed_at 格式为 ISO 8601",
				"所有行 _record_hash 长度 12",
				"_quality 仅包含 clean / minor / poor",
			]
		}
	}

	pipeline: "csv-standard"
}
