# 活动工具与文件职责

当前默认：GT弃用清单 + CV9（数值CV8、短A/E2证据） + Gemini 3.8 Flash High + compact + 16路滚动队列。参数由config.json和gt_quality_screen_config.json提供，状态/任务查[STATUS](../../docs/STATUS.md)与[PLAN](../../docs/PLAN.md)。

## 日常入口

| 文件 | 职责 |
|---|---|
| gt_quality_gate.py / gt_quality_screen_config.json | 全划分GT CV筛查、候选六组GT看板、独立调用、失败恢复、弃用清单/过滤池 |
| workflow.py / config.json | 原任务切片，先过滤GT，再CV/看板、导入、候选与抽检包导出 |
| run_sheet_workers.py | 跨批次有界并发、完成即补位、每批独立导出 |
| agy_runner.py / compact_harness.py | High自行读本地PNG、自写JSON；只生成compact，旧full/BF/NR只能读取历史 |
| ANTIGRAVITY_HANDOFF.md | IDE协作协议；不让模型查原图、补图或反复验证 |
| screen_real.py / select_boundaries.py | 过滤后的验证集CV诊断与分层选择；保留原任务序号，区分已见/新GT |
| ae_diagnostic.py / ae_round15_config.json | 第15轮物理干预、同看板提示对照/预留GT确认与统计；仅实验驱动，见报告，不用于日常标注 |
| object_diagnostic.py / object_round16_config.json | 第16轮train/test真实图对照、完整文件后处理恢复与统计；仅本轮实验，不是通用断点恢复器 |
| review_boundaries.py | 交接文本和CV/视觉诊断统计，不把未知/排除项当负例 |
| run_harness_trial.py | 同看板对照的输入克隆；旧废弃策略不能继续调用模型，需重新prepare |

GT筛查默认仅使用本次数据候选，不再依赖已取消B/F实验。需要物理控制时，可显式给gt_quality_gate.py prepare传--diagnostics <CV handoff manifest>；它是可选实验输入，不是生产依赖。

新增/重筛数据使用新run-id；已完成的清单无需逐批重算：

```powershell
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py scan --run-id GT_screen_new
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py prepare --run-id GT_screen_new
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py run --run-id GT_screen_new --workers 16
# 有失败时，只恢复尚未完成的GT：
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py retry --run-id GT_screen_new --workers 4 --timeout 300
```

汇聚生成excluded_GT.json及filtered_tasks_pool；未完成候选先隔离，不伪称已确认坏GT。确认新清单后将config.gt_reference.exclude_manifest指向该清单；当前仍使用第14轮冻结版本。普通标注命令见根README。

## 数值模块与检查

engine.py为Lab测量/热图；global_models.py为A/D结构解释；d_color_groups.py为共同方向；region_models.py为局部区域。数值参数本次整理未改变。

check_workflow.py、check_agy_runner.py、check_sheet_workers.py检查文件/范围/调度契约；check_models.py、check_boundaries.py、check_ab_heatmap.py检查数值及诊断。根据改动运行所需检查，不默认反复调用Gemini。

## 历史资料

[archive/rounds_01_14](archive/rounds_01_14/README.md)保存已完成的一次性驱动、统计脚本和旧搜索配置；[baselines](baselines/README.md)保存冻结数值/提示快照。两者不作为当前运行入口。历史命令需结合对应运行源码快照/Git版本，不能把旧阈值或旧GT回退恢复成默认。

原图、任务池、SQLite、正式交付和历史实验大产物保持原路径；新生成物只在LS_lcad_reviewer/intermediate/experiments。
