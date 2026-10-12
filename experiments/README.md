# 实验区

当前活动实验为cv_workflow/，先改进CV与文件交接协议，视觉阶段由主人使用Antigravity。

- 源码/config/提示词：本目录，Git版本管理。
- 新运行产物：LS_lcad_reviewer/intermediate/experiments/{run_id}/，不覆盖旧运行。
- 第一轮冻结源码：LS_lcad_reviewer/intermediate/scripts/cv_workflow_experiments/，保留原路径。
- 当前进度和实验结果：docs/STATUS.md、docs/experiments/。

实验不得改写原图片、旧模型标签、SQLite或正式交付。CV候选与最终视觉标签分开记录；每张看板6组，最终完成状态必须经过结果覆盖和证据检查。
