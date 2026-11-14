# 2026-10-26 至 10-28｜JSON 流程改进与工作台

先用小批样本检查提示、输出格式、补写和模型传输，后来改为两轮初标先按批合并、三模型复核、Gemini 定向修改该批 JSON。独立脚本 v6 留有离线校验，工作台所做的真实试跑另有运行记录。

| 工作目录或证据 | 内容 |
|---|---|
| [改进项目及接续记录](../../workflow_refinement_20261026/CURRENT_CONTEXT.md) | 阶段决定、旧方案诊断、样本范围和结果限制。 |
| [分组与试跑输入](../../workflow_refinement_20261026/data) | 冻结样本分配和各版本的准备数据。 |
| [工程流程首次试跑](../../workflow_refinement_20261026/runtime/engineering24) | 工程链路记录。 |
| [格式试验运行目录](../../workflow_refinement_20261026/runtime) | 含多版 format_pilot、轻量版、自然文案版和原始输出。 |
| [自然文案试跑](../../workflow_refinement_20261026/runtime/natural_v2_trial24) | 保留中间整理出现误映射的诊断。 |
| [原文至最终 JSON 试跑](../../workflow_refinement_20261026/runtime/raw_final_json24) | 结果与后续空标重查均在该目录。 |
| [v6 离线检查](../../workflow_refinement_20261026/runtime/json_delta_v6_offline/verification.json) | 离线两批模拟的合并、增量修订和汇总验证。 |
| [可视化工作台及状态](../../../workflow_studio/STATUS.md) | React Flow 编排、真实通道验证和双模板。 |
| [工作台真实试跑](../../../workflow_studio/.local/runs/aad4ed1bc322) | 2 张已曝光图片的真实工程链路。 |
| [旧三轮回放](../../../workflow_studio/.local/runs/5e9297f5472b) | 24 张使用冻结历史结果的回放。 |
| [旧三轮模板](../../../workflow_studio/legacy/production_20261021/README.md) | 10 月 28 日接入，版本名指 10 月 21 日生产快照。 |

### 试跑目录对照

| 运行目录 | 用途 |
|---|---|
| [`format_pilot24`](../../workflow_refinement_20261026/runtime/format_pilot24/) | 24 张格式试点，查结构约束和补写问题。 |
| [`format_v3_pilot24`](../../workflow_refinement_20261026/runtime/format_v3_pilot24/)、[`format_v4_pilot24`](../../workflow_refinement_20261026/runtime/format_v4_pilot24/) | 后续两版格式与补写验证。 |
| [`light_interface8`](../../workflow_refinement_20261026/runtime/light_interface8/)、[`light_prompt_v2`](../../workflow_refinement_20261026/runtime/light_prompt_v2/) | 轻量接口小批测试及对应提示迭代。 |
| [`raw_v3_offline`](../../workflow_refinement_20261026/runtime/raw_v3_offline/) | 原文流程的离线核验。 |
| [`control`](../../workflow_refinement_20261026/runtime/control/) | 运行控制记录。 |
