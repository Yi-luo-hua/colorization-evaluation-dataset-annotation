# 实验区

活动入口为[cv_workflow](cv_workflow/README.md)，当前CV13。本对话已获授权通过本机原生agy控制实验；Gemini High自己读本地看板、直接写结果JSON，主人需要时可通过Antigravity IDE协作。

- 源码、配置和提示词在本目录，Git管理；运行产物只进LS_lcad_reviewer/intermediate/experiments/{run_id}，不覆盖旧运行。
- 当前事实查[STATUS](../docs/STATUS.md)，任务和改进方向查[PLAN](../docs/PLAN.md)，第1～22轮沿革查[EXPERIMENTS](../docs/EXPERIMENTS.md)。
- A仅全图黑白无上色，生成图原分辨率RGB候选与GT无关；CV候选和视觉标签分开。
- 默认6组/张、2张/任务、16路滚动；第19/20轮容量已初测，8张列候选；第21轮动态3/6/8组已实现并对照，默认保留6组。
- 旋转D提示关闭；CV13收紧B源颜色跨界提示，双侧窄带测量仅存私有诊断，不向AI提供不可靠B导航。
- 上游GT清单已冻结；日常生成图标注不复审GT、不缩减七类、不删除输入记录。
- 原图片、旧标签、SQLite及正式交付保持；汇聚从实际结果文件读取，未打分源标签保存不造元数据。

第一轮冻结源码仍在LS_lcad_reviewer/intermediate/scripts/cv_workflow_experiments，历史驱动/快照只供追溯，不是当前标注入口。
