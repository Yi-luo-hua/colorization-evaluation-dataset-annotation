# 图像上色评价：实验与自动标注

2026-10-13，第15/16轮完成：采用A/E2短CV证据，真实图位置提示未采用。第14轮GT清单仍冻结：14,285张中弃用57张，剩余14,228张；两模型保留28,456例，尚未完成全量新标注或正式交付。

当前默认：**GT先过滤 → CV9辅助（数值沿用CV8，新增A/E2短证据） → 六组看板 → Gemini 3.8 Flash High自读PNG、自写compact JSON → 滚动汇聚/校验/实验候选**。速度第一，允许微量不完美，0补图，不查单张原图。

## 文档与入口

| 文件 | 用途 |
|---|---|
| [STATUS](docs/STATUS.md) | 当前成果、数量与未解决问题 |
| [PLAN](docs/PLAN.md) | 已完成、下一步、暂缓与取消任务 |
| [DESIGN](docs/DESIGN.md) | 当前工作流、算法分工与结果契约 |
| [活动工具索引](experiments/cv_workflow/README.md) | 各脚本职责与归档边界 |
| [AGENTS](AGENTS.md) | 执行规则；用户最新要求优先 |
| [EXPERIMENTS](docs/EXPERIMENTS.md) | 第1～16轮证据与决策 |
| [A/E2实验报告](docs/experiments/ae_round15_20261013.md) | CV物理控制、提示词对照与预留GT确认 |
| [真实图定位实验](docs/experiments/object_round16_20261013.md) | 位置提示未采用、跨划分流程与未打分源处理 |
| [GT筛查报告](docs/experiments/gt_quality_round14_20261013.md) | 57张GT清单、恢复过程及证据边界 |
| [目录整理记录](docs/ORGANIZATION.md) | 当前目录职责与清理记录 |

## 运行新的标注批次

原任务池不重排。config.json已绑定冻结GT弃用清单，prepare在读取生成图做CV之前过滤两模型对应样本；输入范围仍指原任务序号。

```powershell
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 experiments/cv_workflow/workflow.py prepare --model both --split val --start 1 --end 12 --run-id my_batch
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 experiments/cv_workflow/run_sheet_workers.py --batch LS_lcad_reviewer/intermediate/experiments/my_batch
```

请求最多24例；实际保留数由GT清单决定，看板每张最多6组，尾张可少于6。默认2看板/任务、整个队列上限16，完成一个就补位；各批自己完成便导出。

```powershell
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 experiments/cv_workflow/run_sheet_workers.py --batch LS_lcad_reviewer/intermediate/experiments/batchA LS_lcad_reviewer/intermediate/experiments/batchB --queue-run-id my_queue
```

结果在各run/exports/：reviewed_candidate.json、tasks_reviewed_stream.json、provenance.json、excluded_GT.json。原评分/模型/时间戳继承；新缺陷标注不等于已完成离线重评分。正式exports、SQLite与原图不因实验覆盖。

未打分源会保存完整visual_reviews.json与source_metadata_pending.json，旧候选导出延期；无需重跑模型，不填造原评分/元数据。测试集当前属于此情况。

## GT筛查与IDE协作

现有[冻结清单](LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/excluded_GT.json)和[六份过滤任务池](LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/filtered_tasks_pool)可直接使用，不需要每批重做全量筛查。扩充或重筛数据时，按[工具索引](experiments/cv_workflow/README.md)调用gt_quality_gate.py；新清单确认后更新config.exclude_manifest。

不可信GT直接弃用，不做B/F回退或无参考评价。GT阶段只确认候选；标注阶段对全部保留样本视觉审查。GT看板两列三行，标注看板六行三列，均6组/张，只有匿名G/S编号，没有原图位置。

IDE协作另prepare新批次，将START_HERE.md和ANTIGRAVITY_HANDOFF.md交给Gemini；它自读请求列出的看板，直接填reviews_gemini.json。程序再执行workflow.py import-reviews与export-candidate；同一批选择IDE或agy一种执行方式。

## 历史与归档

当前代码在experiments/cv_workflow；一次性旧实验脚本在[archive/rounds_01_14](experiments/cv_workflow/archive/rounds_01_14/README.md)，冻结基线在baselines。旧BF/NR/full字段生成入口已停用，历史结果仍可读取。继续新标注应重新prepare当前批次。

第12/13轮旧候选是历史对照，未按第14轮GT清单重导，不直接当当前清洁交付。LS_lcad_reviewer/core_pipeline及根兼容入口属于历史V4工具；当前自动流程不调用其旧分流/放行规则，只复用正式schema校验。

Git管理源码、参数与报告，忽略本地图像、任务JSON、环境、数据库和实验大产物；本次未提交或推送。
