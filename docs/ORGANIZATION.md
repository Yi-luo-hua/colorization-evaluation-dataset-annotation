# 目录职责与整理记录

## 项目导航与实验时间线

逐阶段的工作目录、报告和样本清单见[实验阶段索引](../experiments/timeline/README.md)。其中列出旧 CV 运行区的全部一级子目录，并记录了 2026-11-14 清理旧看板后的留存范围。

按实际工作的日期查阅。目录名的日期通常是建包或启动日期，后续复核、续跑和导出可能仍写在原目录。日期依据实验文档、运行记录和相关聊天交叉核对。下文的目录数量是盘点时的一级子目录数。

### 根目录

| 位置 | 内容 |
|---|---|
| [`9_14_10000GT_V1`](../9_14_10000GT_V1/)、[`10_5_val_V1`](../10_5_val_V1/)、[`10_5_test_V1`](../10_5_test_V1/) | Train、Val、Test 的 GT、LCAD/UniColor 生成图及随附数据。数字属于数据包命名。 |
| [`LS_lcad_reviewer`](../LS_lcad_reviewer/) | 早期 V4 审阅工具、Label Studio 本机库、任务池、审阅导出，以及后来借用此处存放的 CV 实验产物。 |
| [`annotation_delivery/train_val_v1_20261015`](../annotation_delivery/train_val_v1_20261015/) | 训练集和验证集交付。根 [`pipeline.py`](../pipeline.py) 转入该项目。这里的 `data/` 存准备清单，`runtime/` 存任务与运行库，`exports/` 存成品与统计。 |
| [V5 无 GT 标注工作区](../V5_无GT标注工作区/README.md) | 生成图单图标注的规则、固定读本、两轮派发与校验。`local/` 保存试跑、盲审和回执，入口见 [V5 试跑索引](../experiments/timeline/20261121-20261124_v5_annotation/README.md)。 |
| [`experiments`](../experiments/) | CV 共享实现及独立研究分支。各分支的运行位置见下表。 |
| [`workflow_studio`](../workflow_studio/) | 10 月下旬开发的可视化工作台。代码在 `src/`、`backend/`，草稿、运行与本机库在 `.local/`，历史兼容模板在 `legacy/`。 |
| [`人工标注`](../人工标注/) | 较早的 101 条人工核验记录与来源压缩包，10 月 25 日有单独的离线核查。 |
| [`docs`](./)、[`references`](../references/)、[`showcase`](../showcase/) | 项目文档、外部参考资料和历史成果展示。 |
| `scratch/`、`output/`、`.playwright-cli/` | 本机查样脚本、临时预览、截图和浏览器调试输出。`scratch/e2-case-search/` 保存实验区顶层归拢的查样脚本。 |

### 按时间查找

| 日期（北京时间） | 工作 | 入口与产物 |
|---|---|---|
| 9 月 29 日起，10 月上旬继续 | V4 早期 LCAD 批次复核与交付 | [批次报告](../LS_lcad_reviewer/reports/)、[旧检查图目录](../LS_lcad_reviewer/intermediate/inspection_sheets/)、[历史导出](../LS_lcad_reviewer/exports/)。`inspection_sheets_1_500`、`remaining_batch_*`、`zero_defects_batch_*` 等主要按样本范围或任务目的编号，批量编号看板已清理。 |
| 10 月 12 日 | CV 初期、真实边界和轻量文件输出试点 | [第 1～22 轮总索引](EXPERIMENTS.md)、[首轮原始报告](../LS_lcad_reviewer/intermediate/audits/cv_workflow_experiment_20261012_01/experiment_report.md)。`cv_geometry_v3_*`、`cv_models_v4_*`、`real_boundary_*` 等在旧 CV 运行目录。 |
| 10 月 13 日 | GT 筛查、并发容量、看板布局、A/E2 和 C/D/B 对照 | 旧 CV 运行目录中的 `gt_quality_all_splits_20261013`、`parallel_*`、`capacity_round19_*`、`capacity_round20_*`、`layout_round21_*`、`cd_round22_*`。按 [逐轮报告](experiments/) 查样本和对照条件。 |
| 10 月 14 日 | CV13 真实批次、人工 A 冻结、疑点定向重跑 | 旧 CV 运行目录中的 `annotation_real_*`、`annotation_issue_rerun_*`、`A_frozen_human_20261014_01`。详见 [10 月 14 日优化记录](real_annotation_optimization_20261014.md)。 |
| 10 月 15 日 | 两阶段交付准备、384 张试标、同 48 张重跑和换板 | [交付运行目录](../annotation_delivery/train_val_v1_20261015/runtime/) 中的 `starter_01`、`starter_02`、`pilot_384_20261015_01`、`rerun48_detail_20261015_01`、`secondary_review_*` 和 `no_overlay_*`。旧 CV 运行目录也有 [Label Studio 实验预览](../LS_lcad_reviewer/intermediate/experiments/labelstudio_experiment_review_20261015_01/README.md)。 |
| 10 月 16–21 日 | 5000 条恢复、扩到全量 Train/Val、第三次空标签复核、最终交付 | [主运行目录](../annotation_delivery/train_val_v1_20261015/runtime/recovery5000_20261016_01/) 沿用起步时的名称，`state.sqlite3` 含最终 22,768 条。旧 `batch5000_8sheets_20261016_01` 是恢复来源之一。最终训练包在 [10 月 21 日导出](../annotation_delivery/train_val_v1_20261015/exports/training_train_val_20261021/)，统计在 [最终报告](../annotation_delivery/train_val_v1_20261015/exports/final_statistics_20261021/REPORT.md)。 |
| 10 月 25 日 | 核查 101 条早期人审；在另一组 192 张上运行可靠性试点 | [101 条核查报告](../experiments/human_reference_audit_20261025/REPORT.md) 对应根目录人工标注。192 张试点的 Gemini R1、R2、DeepSeek、GPT-6 Luna 分别在 [可靠性试点 runtime](../experiments/reliability_refine_pilot_20261025/runtime/) 下。 |
| 10 月 25–26 日 | 在同一批 192 张上试验联合看板与 Critic–Refiner | [联合试验](../experiments/reliability_refine_pilot_20261025/joint_cr_v1_20261025/README.md)、[综合分析](../experiments/reliability_refine_pilot_20261025/reliability_analysis_20261026/README.md)、[七组 Label Studio 对比](../experiments/reliability_refine_pilot_20261025/labelstudio_comparison_20261026/README.md)。 |
| 10 月 26–27 日 | 三模型证据复核、提示/格式/传输试跑，转向批内 JSON 增量修订 | [流程改进](../experiments/workflow_refinement_20261026/CURRENT_CONTEXT.md) 的 `runtime/` 有 `engineering24`、`natural_v2_trial24`、`raw_final_json24` 等实跑现场，`json_delta_v6_offline` 是 v6 独立脚本的离线校验。日期也可查同分支的 `data/*_20261027`。 |
| 10 月 27–28 日 | React Flow 工作台试跑、旧三轮兼容回放 | [工作台状态](../workflow_studio/STATUS.md) 和 [运行目录](../workflow_studio/.local/runs/)。[`legacy/production_20261021`](../workflow_studio/legacy/production_20261021/README.md) 的日期指冻结的生产版本，工作台接入在 10 月 28 日。 |
| 11 月 2–4 日，11 日导出 | 600 张七类人工标准集，校准 300、封存评测 300 | [人工标准集](../experiments/human_standard_600_20261102/README.md) 下的 `local/batch_01` 至 `batch_06`、`development/` 与 `sealed_evaluation/`。11 日另存 [600 张身份表](../experiments/human_standard_600_20261102/local/image_ids_600_20261111.json) 和 [前两批 200 条人工定稿](../experiments/human_standard_600_20261102/local/development/human_annotations_200_of_300_20261111.json)。 |
| 11 月 4 日起，10–11 日继续 | 另一组 600 张 A/非 A 快审、彩度阈值探索 | [A 快审工具](../experiments/a_chroma_reviewer_20261104/README.md) 下的 `local/manifest.json`、`judgments.sqlite3`、`fits/`。11 月 11 日仅看生成图的模型复核在 [`local/no_gt_20261111`](../experiments/a_chroma_reviewer_20261104/local/no_gt_20261111/)。11 月 10 日全量均匀彩度统计覆盖 Train/Val/Test 共 28,570 张，图表保存在当时的聊天附件中。 |
| 11 月 11 日 | Train/Val 扫描后单独复核 141 张近灰候选；修订 GT 准入 | 同一 A 工具下的 [扫描](../experiments/a_chroma_reviewer_20261104/local/train_val_A_scan/) 与 [候选复核](../experiments/a_chroma_reviewer_20261104/local/train_val_A_review/)。模型结果和人工导出分开，人工记录见 `human_review_20261111.json`。新版整图无缺陷的 GT 准入见 [AGENTS](../AGENTS.md)，本次两张 GT 的证据见 `gt_no_defects_recheck_20261111.json`。 |

### 旧 CV 目录辨认

[旧 CV 运行目录](../LS_lcad_reviewer/intermediate/experiments/) 有 252 个一级子目录。按名字里的日期统计，10 月 12 日 31 个、13 日 146 个、14 日 71 个、15 日 1 个。另有 3 个无日期的 `antigravity_val_1_12*`，清单里的 `created_at` 均为 10 月 12 日，属于早期验证试点。一个实验会分出多处准备、队列、重跑和汇总目录。

- 同一轮优先按共同前缀和对应报告串起来。比如 `layout_round21_*` 包含准备、3/6/8 组对照和重试，汇总看 [第 21 轮](experiments/layout_round21_20261013.md)。
- CV 公共代码在 [`experiments/cv_workflow`](../experiments/cv_workflow/)，历史驱动与配置见其 `archive/`、`baselines/`。旧运行目录主要提供对应输入、看板、模型结果和汇总。
- 配置仍引用旧运行目录里的 [GT 排除清单](../LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/excluded_GT.json) 和 [人工 A 冻结名单](../LS_lcad_reviewer/intermediate/experiments/A_frozen_human_20261014_01/confirmed_A_manifest.json)。交付配置还引用 [V4 审阅底稿](../LS_lcad_reviewer/exports/reviewed_1_10000_clean.json)。这些历史输入与正式库、冻结清单、人工结果和实验看板具有不同的迁移依赖。

## 历史整理记录

## 2026-10-15独立交付目录

`annotation_delivery/train_val_v1_20261015/`为当前train/val初版交付项目：RULES／AGENTS规则、config、prompts、scripts离线准备。当前为NR_legacy_only_v2：只继承指定历史成品为待重审底稿，实验AI结果取消资格、仅保留追溯。活动数据／任务包为data/preparation_02、runtime/starter_02；01旧包退役。data和runtime由Git忽略。规则改版前源码／文档在runtime/before_NR_v2；更早根文档在runtime/docs_before_01。未启动模型，调度器尚待实现；原实验包、原池和正式成品不移动／覆盖。

以下目录表描述旧CV13入口及仍保留的公共数据职责，当前交付优先看新项目。

## 当前目录

| 路径 | 职责 |
|---|---|
| README / AGENTS / docs/STATUS、PLAN、DESIGN | 当前启动、执行规则、状态、任务与工作流 |
| experiments/cv_workflow | 当前运行器、数值模块、配置、提示与契约检查 |
| experiments/cv_workflow/archive/rounds_01_14 | 28个已完成的一次性驱动、统计及旧搜索配置，只读追溯 |
| experiments/cv_workflow/baselines | 冻结数值/提示快照，不作运行入口 |
| docs/EXPERIMENTS、docs/experiments | 历史决策与完成报告；历史命令不覆盖当前入口 |
| docs/archive/workflow_cleanup_20261013 | 本次整理前源文件、迁移哈希、检查结果和回收站记录 |
| LS_lcad_reviewer/intermediate/experiments | 原始调用、看板、候选、GT清单和过滤任务池；Git忽略大产物 |
| LS_lcad_reviewer/core_pipeline及根兼容脚本 | 历史V4工具；当前主线只复用正式schema校验 |
| LS_lcad_reviewer/legacy_archive | 更早脚本、旧人工说明与导出启动器 |
| 三个数据目录、任务池、正式exports、SQLite | 原始/历史数据保留原路径，不因整理覆盖 |

## 2026-10-13第17轮阶段边界整改（已完成）

- 删除活动harness/配置/校验/导出中的下游GT资格与缩减范围路径；GT只在上游筛查，当时CV10固定评价生成图七类。
- 第15/16轮四个一次性驱动/配置逐字节移入archive/rounds_15_16；25份修改前核心/文档快照在docs/archive/stage_boundary_20261013，历史报告原文另存并添加明显阶段提示。
- 历史模型文件、候选、原池、57张清单和正式交付用126份文件哈希保护，不回填旧标签。
- 38项软件检查与12对新空模板High回归完成；重新编排A/E2、C/D、物体/部位、轻量证据及速度实验。没有提交/推送。

以下整理条目为当时记录；其中旧格式解读兼容/下游GT分支已经由当前阶段边界替代。

## 2026-10-13第14轮后整理（历史）

- 将28个旧实验脚本/配置、失效03_export_lcad.cmd和旧人工SOP共30个文件逐字节归档；更新人工说明为当前可选抽检指引。
- README明确原序号范围与过滤后实际数量；STATUS区分GT筛查完成、保留样本待标注、旧候选未按新清单重导；PLAN按已完成/待做/暂缓/取消列任务。
- GT-only筛查不再硬依赖取消的B/F运行；诊断控制改为显式可选输入。验证集筛查/选择同步应用当前GT清单，修正带额外案例后缀的历史GT身份识别。
- 新模型调用只生成compact，停止BF/NR/full字段生成；保留旧JSON解读兼容。核心CV模块、数值配置及57张弃用清单保持原哈希。
- 16篇完成报告添加历史标识，原文先保存；历史命令代码块保留当时文本。
- 3处可再生__pycache__（24个pyc）送至回收站，确认源路径不存在且有新回收站记录；不清空回收站。
- 23项契约/调度检查通过；普通GT看板准备已验证无需历史B/F依赖；本地文档链接及归档哈希检查见[验证记录](archive/workflow_cleanup_20261013/verification.json)。没有模型调用、重新标注、Git提交/推送或发布。

以下为更早阶段的历史整理记录。

## 2026-10-12初次整理

- 建立根Git仓库，main分支，先保存原有源码基线；未配置远端或推送。
- 原始三个数据目录、Python环境、Label Studio数据库、任务池、正式交付和历史看板不移动。
- 活动代码与配置进入experiments/cv_workflow；新运行进入LS_lcad_reviewer/intermediate/experiments，生成物不进入Git。
- 第一轮实验代码及成果保留原路径，避免破坏已记录的来源哈希与复现命令。
- agentflow整个目录移至references/agentflow，论文文件保留；AGENTS.md.bak移至LS_lcad_reviewer/legacy_archive/AGENTS_preexisting_20261012.md.bak。
- LS_lcad_reviewer根目录六份重复工具替换为兼容命令入口，统一执行core_pipeline版本；原文件逐字另存本地legacy_archive/root_entrypoints_20261012（Git忽略重复备份），Git基线亦可恢复。
- 根showcase保留为历史成果展示；图片与PDF保留本地但不进入Git。

这是本地源码管理和目录整理，不代表已有实验通过真实标注验收或正式发布。

## 2026-10-13文档同步

- README改为启动与文档导航；STATUS只保留当前事实，DESIGN只描述活动算法和文件契约。
- 新建PLAN记录尚未执行的实验顺序/采用依据；EXPERIMENTS统一第1～13轮进度、决策和报告入口。
- 整理前四份主文档按原字节保存在archive/docs_sync_20261013，历史报告和实验产物不移动、不改写。
- 算法、配置、活动视觉提示词保持；本次没有启动新实验，也没有提交/推送或发布。

## 2026-10-13 A定义修正

第18轮CV11移除旧下游A结构/原色保留分类，新增generated_color.py与a_grayscale_diagnostic.py。修改前快照和过程文件位于intermediate/experiments/A_grayscale_revision_20261013及round18目录；历史原输出不改。当前CV13增加color_evidence.py及B私有诊断，最新进度查STATUS；历史详情见[第18轮](experiments/A_grayscale_round18_20261013.md)。

## 2026-10-13 CV11实验总结与任务文档同步

- PLAN按已完成、第T01～T08待执行队列、容量设计、Gemini建议决定、取消/暂缓重排；A代码整改完成与新A视觉确认待做分开。
- STATUS区分第17轮旧A阶段回归与第18轮新A控制/真实锚点回归；38项检查和12样本复测不叠加虚计。
- EXPERIMENTS更新至第18轮，旧A模型/BF-only/下游GT复审在当前决策栏明确退出；历史结果数值及原报告不改写。
- DESIGN修正E类仍提供旧结构支持的过时描述，明确独立文件汇聚及动态组数尚未实现；根入口与工具索引同步。
- 八份修改前文档及本次链接/一致性核验保存于LS_lcad_reviewer/intermediate/experiments/docs_sync_CV11_20261013。仅更新文档，无算法/配置修改、模型调用、Git提交/推送或正式交付覆盖。

## 2026-10-13第19轮容量实验

新增experiment_capacity.py与summarize_capacity.py，workflow提取原交接写入函数及实验匿名标题选项；默认配置未改。所有新包、失败现场、600秒/EOF新尝试和固定单并发确认均独立保存在intermediate/experiments的capacity_round19目录；24次调用、22有效，576条成功观察仍仅96独立输入。8张列扩量候选，源池/正式交付/旧实验不覆盖。详情见[第19轮](experiments/capacity_round19_20261013.md)。

## 2026-10-13第20轮扩量与位置对照

新增experiment_capacity_round20.py、summarize_round20.py、中性坐标spatial_hint.py及旧完成文件恢复recover_file_results.py。84新GT/192输入，三条件各192/192，17调用/576有效观察；4个ERROR文件只恢复后处理，1个null补跑。所有调用结束后再修正agy_runner及检查：实际完整合法文件优先，native错误保留。短坐标未采用，CV参数/默认配置未改。产物/源码/文档快照在capacity_round20_fixed_setup_20261013等新目录；原源池、正式交付、第19轮结果保持。见[第20轮](experiments/capacity_round20_20261013.md)。

## 2026-10-13第21轮组数对照

新增experiment_layout.py，renderer、请求sheet_groups、提示与IDE指引支持动态行数；默认6组。复用192冻结输入，三条件各192/192，32调用/24实际完整，576有效观察；6组8个初次超时/null调用用独立尝试恢复，0新GT。26项检查及7个样本区域像素SHA验证通过；前后快照/保护校验位于layout_round21_setup_20261013，旧输出/正式交付不改。见[第21轮](experiments/layout_round21_20261013.md)。

## 2026-10-13第22轮C/D与B实验

新增整体旋转及留色支持模型、C/D驱动/汇总、B双侧近远原型与检查。engine/workflow/harness增加可选旋转入口，默认config不改。48新GT/v2共720控制、B144控制；High三条件实际24/36、36/36、36/36，14调用/96观察，基线12条四次恢复仍未完成。旋转提示有普通平移漏项，未采用；B未进入标注入口。前后源码/文档及331受保护文件核验在cd_round22_setup_20261013；原池/正式交付/旧结果保持，未提交或推送。见[第22轮](experiments/cd_bleed_round22_20261013.md)。
