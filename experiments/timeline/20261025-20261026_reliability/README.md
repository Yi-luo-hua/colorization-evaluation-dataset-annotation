# 2026-10-25 至 10-26｜可靠性试点与联合复核

先离线核查 101 条早期人工参考，再使用另一批冻结的 192 张做可靠性比较。Gemini R1/R2、DeepSeek、GPT-6 Luna 构成四组独立重标。随后在同一 192 张上做三组联合看板与 Critic–Refiner。七组模型结果汇入独立审核项目，报告记录程序验收和模型分歧。

| 工作目录或证据 | 内容 |
|---|---|
| [101 条人工参考核查](../../human_reference_audit_20261025/REPORT.md) | 早期人工记录的来源、覆盖和与模型结果的差异。 |
| [样本清单](../../reliability_refine_pilot_20261025/sample_manifest.json) | 192 张身份与划分，含开发和封存评测。 |
| [Gemini R1](../../reliability_refine_pilot_20261025/runtime/R1) | 第一遍独立运行。 |
| [Gemini R2](../../reliability_refine_pilot_20261025/runtime/R2) | 第二遍独立运行。 |
| [DeepSeek](../../reliability_refine_pilot_20261025/runtime/API_deepseek) | API 对照运行。 |
| [GPT-6 Luna](../../reliability_refine_pilot_20261025/runtime/API_gpt6_luna) | API 对照运行。 |
| [联合复核报告](../../reliability_refine_pilot_20261025/joint_cr_v1_20261025/REPORT.md) | 575 条通过结构与完整性验收，另 1 条待人审。 |
| [联合复核运行](../../reliability_refine_pilot_20261025/joint_cr_v1_20261025/runtime) | 三模型的联合流程现场。 |
| [综合分析](../../reliability_refine_pilot_20261025/reliability_analysis_20261026) | 定量分析、审阅图和论文材料。 |
| [Label Studio 对比](../../reliability_refine_pilot_20261025/labelstudio_comparison_20261026/README.md) | 七组输出、历史来源及项目 31 的导入记录。 |
