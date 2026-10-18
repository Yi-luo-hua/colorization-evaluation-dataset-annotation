# 目录职责与整理记录

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
