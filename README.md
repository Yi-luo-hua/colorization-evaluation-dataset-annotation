# 图像上色评价与数据集标注

本项目维护上色缺陷标准、批量标注工作流和人工复核记录。以下入口按任务选择，进度和执行参数以各工作流自己的记录为准。

| 要找什么 | 入口 |
|---|---|
| V5 单图标注规则、模型读本、两轮派发 | [V5 无 GT 标注工作区](V5_无GT标注工作区/README.md) |
| 近期 V5 试跑、人工样例与复审 | [V5 试跑索引](experiments/timeline/20261121-20261124_v5_annotation/README.md) |
| Train/Val 三轮交付、恢复入口与状态 | [交付项目](annotation_delivery/train_val_v1_20261015/README.md) · [STATUS](annotation_delivery/train_val_v1_20261015/STATUS.md) · [`pipeline.py`](pipeline.py) |
| 七类人工标准集和早期审阅 | [人工标准集](experiments/human_standard_600_20261102/README.md) · [V4 分批报告](LS_lcad_reviewer/reports/) |
| CV、三模型证据复核和历次实验 | [实验入口](experiments/README.md) · [实验时间线](experiments/timeline/README.md) |
| 目录、术语与版本管理 | [目录职责](docs/ORGANIZATION.md) · [项目术语](CONTEXT.md) · [Git 维护说明](docs/GIT_WORKFLOW.md) |

## 文件存放

- `V5_无GT标注工作区/` 保存 V5 代码、规则和固定读本，运行结果在其 `local/` 下。
- `annotation_delivery/` 保存交付代码。任务包、运行库和导出在交付项目的 `data/`、`runtime/`、`exports/` 下。
- `experiments/` 保存独立研究项目。一次性查样脚本和临时预览放在 `scratch/`，本地截图与构建产物放在各自的输出目录。
- 原始数据目录、人工标注、正式导出和运行证据留在本机。在新机器使用工作流时，按各入口说明恢复所需输入。

项目操作约定见 [AGENTS.md](AGENTS.md)。旧首页保存在[历史入口](docs/archive/root_readme_20261124.md)。
