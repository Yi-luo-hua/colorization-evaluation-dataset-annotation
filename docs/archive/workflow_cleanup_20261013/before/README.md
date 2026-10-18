# 图像上色评价数据集：CV实验与自动视觉标注

当前已完成第十四轮全划分GT筛查（2026-10-13）：14,285张GT中剔除57张，后续自动排除两模型对应114个样本。工作目标是速度优先的轻量标注和快速迭代；允许少量不完美，不穷举模糊细节。活动配置为 **GT筛除清单 + CV8 + Gemini 3.8 Flash High + 十六路跨批次滚动队列 + 六组双向彩度看板**。标注输出仍是实验候选，严重度尚未校准。

## 文档入口

| 文件 | 职责 |
|---|---|
| [当前状态](docs/STATUS.md) | 当前默认、完成进度、现有成果与未解决问题 |
| [下一步计划](docs/PLAN.md) | 待执行实验、顺序、对照方式与采用依据 |
| [活动设计](docs/DESIGN.md) | 各标签算法、CV/视觉分工、文件契约与调度 |
| [实验索引](docs/EXPERIMENTS.md) | 第1～14轮证据、采用/未采用决策及详细报告 |
| [执行规范](AGENTS.md) | 用户要求、标签边界与代理操作约束 |
| [视觉交接协议](experiments/cv_workflow/ANTIGRAVITY_HANDOFF.md) | 提供给Antigravity的轻量标注指令 |
| [目录整理记录](docs/ORGANIZATION.md) | 目录职责及历史文件保留方式 |

配置与实际代码是运行事实来源；STATUS只保留当前快照，历史结果查EXPERIMENTS和各轮报告。docs/archive中的旧SOP/文档快照仅供追溯。

最新[GT筛查报告](docs/experiments/gt_quality_round14_20261013.md)与[过滤后的六份任务池](LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/filtered_tasks_pool)。默认prepare仍读取原任务池，按config.exclude_manifest先过滤，保留原任务序号。

## 当前默认

- 每张六行三列：GT、生成图、双向彩度差；尾张允许少于六组。
- 每个独立agy会话处理两张看板、最多12例；整个队列最多16任务同时运行，空位立即补任务。
- Gemini用工具自读本地看板，直接修改各任务reviews_gemini.json，只回复保存确认。
- 模型只接收匿名S编号、看板与中性信息；原图路径、源ID、旧评分/标签留在内部manifest。
- 原版彩度图保持；Turbo总色度、单橙色总色度、区域框等只作为未采用实验保留。
- 主要褪色优先E2；不可信GT在实验阶段直接筛除，不做B/F回退或无参考评价；数值候选不自动等于低质量。
- fast_single_pass、0补图；CV只生成候选证据，全体样本经看板，不使用旧分数决定放行。

## 自动运行一批

从项目根目录依次执行，run-id使用新名称：

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py prepare --model both --split val --start 1 --end 12 --run-id my_cv8_batch
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\run_sheet_workers.py --batch .\LS_lcad_reviewer\intermediate\experiments\my_cv8_batch
```

上述范围生成两模型共24例、4张六组看板。新prepare批次读取当前config.json；已prepare批次保留冻结配置，可用--workers/--sheets-per-job覆盖调度。

多个已prepare批次共享一个总并发上限，逐批自己完成就独立导出：

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\run_sheet_workers.py --batch .\LS_lcad_reviewer\intermediate\experiments\batchA .\LS_lcad_reviewer\intermediate\experiments\batchB --queue-run-id queue_run
```

成功任务保留原始模型文件；程序合并reviews_merged.json、检查完整覆盖与契约，导出各批exports/中的候选JSON、抽检流包和provenance。全部成功且图像身份互不重复时，队列目录也汇总候选。配对实验使用--no-combined-export，分别保留条件结果。失败/未解决项不会被伪装成完整候选；已有run/parts不覆盖。

## Antigravity IDE协作

另prepare一个新的手工执行批次，把该目录START_HERE.md和ANTIGRAVITY_HANDOFF.md交给IDE。Gemini读取review_request.json列出的看板，直接填写本地reviews_gemini.json。完成后由程序导入并导出：

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py import-reviews --batch .\LS_lcad_reviewer\intermediate\experiments\my_cv8_manual_batch --reviews .\LS_lcad_reviewer\intermediate\experiments\my_cv8_manual_batch\reviews_gemini.json
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py export-candidate --batch .\LS_lcad_reviewer\intermediate\experiments\my_cv8_manual_batch
```

手工IDE与自动agy选一种执行同一批。需要主人配合时会说明具体操作；默认全流程不依赖人工补图或逐图确认。

## 目录与成果

活动源码/参数在experiments/cv_workflow；新运行在LS_lcad_reviewer/intermediate/experiments；历史工具保留LS_lcad_reviewer/core_pipeline。任务池、原图、正式exports和SQLite保持原路径。

近期可直接读取的[288例汇总候选](LS_lcad_reviewer/intermediate/experiments/scale_round12_288_candidate_20261013/exports/reviewed_candidate.json)来自第十二轮，包含配套流包及来源记录。第十三轮的96例多条件输出用于实验对照，不重复当新增数据或正式交付。

Git管理源码、配置、提示词和报告，排除图像、大JSON、环境和数据库。本地管理、候选校验、真实准确率验收和公开发布是不同状态。
