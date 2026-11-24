# 实验区

按日期查询各阶段的目标、工作目录与留存证据，见[实验阶段索引](timeline/README.md)。

| 实验方向 | 入口 |
|---|---|
| V5 无 GT 单图标注 | [执行工作区](../V5_无GT标注工作区/README.md) · [11 月试跑](timeline/20261121-20261124_v5_annotation/README.md) |
| 人工标准集与 A 类快审 | [七类标准集](human_standard_600_20261102/README.md) · [A 类快审](a_chroma_reviewer_20261104/README.md) |
| 三模型证据复核 | [工作流记录](timeline/20261026-20261028_workflow_refinement/README.md) |
| CV 第 1～22 轮及 CV13 | [CV 工具](cv_workflow/README.md) · [逐轮沿革](../docs/EXPERIMENTS.md) |

本机一次性查样脚本和预览位于 `scratch/`，其中 `scratch/e2-case-search/` 汇集原先散放在实验区顶层的 13 个脚本。从仓库根目录执行，保留其相对数据路径。

## CV13 历史说明

- 源码、配置和提示词在本目录，Git管理；运行产物只进LS_lcad_reviewer/intermediate/experiments/{run_id}，不覆盖旧运行。
- 当前事实查[STATUS](../docs/STATUS.md)，任务和改进方向查[PLAN](../docs/PLAN.md)，第1～22轮沿革查[EXPERIMENTS](../docs/EXPERIMENTS.md)。
- A仅全图黑白无上色，生成图原分辨率RGB候选与GT无关；CV候选和视觉标签分开。
- 默认6组/张、2张/任务、16路滚动；第19/20轮容量已初测，8张列候选；第21轮动态3/6/8组已实现并对照，默认保留6组。
- 旋转D提示关闭；CV13收紧B源颜色跨界提示，双侧窄带测量仅存私有诊断，不向AI提供不可靠B导航。
- 上游GT清单已冻结；日常生成图标注不复审GT、不缩减七类、不删除输入记录。
- 原图片、旧标签、SQLite及正式交付保持；汇聚从实际结果文件读取，未打分源标签保存不造元数据。

第一轮冻结源码仍在LS_lcad_reviewer/intermediate/scripts/cv_workflow_experiments，历史驱动/快照只供追溯，不是当前标注入口。
