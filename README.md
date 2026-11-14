# 图像上色评价：训练集与验证集初版交付

按日期查找旧实验、运行目录、人工复核和 V5 案例资料，请打开[实验阶段索引](experiments/timeline/README.md)。

当前统一入口是根目录`pipeline.py`，实现位于[两阶段交付项目](annotation_delivery/train_val_v1_20261015/README.md)。实时状态以该项目的SQLite和[STATUS顶部](annotation_delivery/train_val_v1_20261015/STATUS.md)为准，下方试标数量、暂停原因和旧命令均为历史记录。

当前策略为High、共享16路、每轮4板，原CID显式续接；任务完整验收后按80,000输入token轮换，缺计量时8轮兜底。普通故障每20秒原会话最多5次补试；额度暂停与恢复、人工停止及手动范围导入按[最新执行规范](AGENTS.md)处理。

本仓库管理源码、配置、提示、检查和历史文档；数据集、标注结果、运行数据库与认证凭据留在本机。Git提交与运行版本的区别、归档字节保护及安全检查见[Git维护说明](docs/GIT_WORKFLOW.md)。

## 历史试标与迁移记录

最新二次职责已纠正：E1/E2重点重标，指定reviewed底稿的B/C/D/F逐项默认保留审核，仅明确错误可修改／删除并留依据。程序按原底稿＋显式决定合并，不再六类自由重标覆盖。旧48／详细23仅作历史，新规则完成0；同48的新结构包已备，访问仍阻塞。见[纠正说明](annotation_delivery/train_val_v1_20261015/runtime/secondary_review_correction_20261015_01/CORRECTION.md)。

最新详细提示NR_detail_20261015_03已按主人要求启用，原48条重跑目前23条有效结果导入[新版审核项目18](http://localhost:8080/projects/18/data?labeling=1)，其余25条因High持续地区访问拒绝保存断点、0在途。同一23条旧6项→新82项；数量不是准确率，待主人复核。原结果和差异保留，具体以[交付状态](annotation_delivery/train_val_v1_20261015/STATUS.md)顶部为准。

2026-10-15，当前为[训练集／验证集两阶段交付项目](annotation_delivery/train_val_v1_20261015/README.md)，契约train_val_two_stage_NR_legacy_only_v2。按生成图自身可见质量和原始类别／分级判断，描述使用无GT比较、无对象／等级标题的自然语言。只有指定reviewed_1_10000_clean.json可作待二次底稿，且须完整审核；实验AI标签全部退出。其他样本RGB初标B/C/D/F，再彩度二次重标E1/E2并审核其余四类。固定人工A复用、测试集暂缓。

会话16路复用策略和断点约定见[交付规则](annotation_delivery/train_val_v1_20261015/RULES.md)，实际进度见[交付状态](annotation_delivery/train_val_v1_20261015/STATUS.md)。384试标已实跑：48条终标已导入[Label Studio项目17](http://localhost:8080/projects/17/data?labeling=1)，另48条仅初标；High额度耗尽，已全停并保存断点，剩余336条终标未完成。主人确认额度恢复前不预检／调用，自动化保持暂停。

## 以下为旧CV13实验入口（保留追溯）

2026-10-14，当前CV13，A已由人工确认并冻结：154条可用直接A命中，其余28,302条只做六类AI标注。GT初筛已完成：14,285 GT弃用57、保留14,228；两模型保留28,456样本。尚未完成全量新标注或正式交付。

**冻结GT过滤 → 人工A直接写标签／其余样本CV+六组看板 → High只检查B/C/D/E1/E2/F → 全部输入汇聚。** 下游GT直接作有效参考，不复审资格、不弃用样本、不缩减类别。快速单次标注、0补图，优先避免错标，允许漏标或宽泛可靠描述。

| 入口 | 用途 |
|---|---|
| [STATUS](docs/STATUS.md) | 当前事实与限制 |
| [PLAN](docs/PLAN.md) | 当前真实标注与优化任务 |
| [DESIGN](docs/DESIGN.md) | 阶段/算法/契约 |
| [AGENTS](AGENTS.md) | 执行规范 |
| [工具索引](experiments/cv_workflow/README.md) | 活动与历史入口 |
| [EXPERIMENTS](docs/EXPERIMENTS.md) | 第1～22轮记录 |
| [固定A分流与六类工作流](LS_lcad_reviewer/intermediate/experiments/A_workflow_cleanup_20261014_01/operation.json) | 当前分流数量和实际准备情况 |
| [阶段边界整改](docs/experiments/stage_boundary_round17_20261013.md) | 删除旧GT下游分支与验证 |

当前直接推进真实数据，每30分钟自动接续；不新增合成控制或条件矩阵。正常样本不重复标，检查出问题可按优化工作流定向重跑，保留原结果并另存差异，不计新增覆盖。最新改动见[优化记录](docs/real_annotation_optimization_20261014.md)，历史实验查EXPERIMENTS；默认2张/任务、6组/张、最多16路。

## 新批次

CV12留色色相残差/低彩度降权和稀疏轮廓继续使用。CV13收紧B为明确源颜色跨界，B数值原型仍有真实误候选，默认不传给AI；旋转D提示也关闭。当前批次与实际完成量查STATUS。

config.gt_filter引用[冻结上游清单](LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/excluded_GT.json)。范围仍指原任务序号，输入过滤后数量可减少；进入标注后记录不再减少。

```powershell
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 experiments/cv_workflow/workflow.py prepare --model both --split val --start 1 --end 12 --run-id my_batch
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 experiments/cv_workflow/run_sheet_workers.py --batch LS_lcad_reviewer/intermediate/experiments/my_batch
```

每张6组，GT/生成/双向彩度差；High自读本地PNG、自写compact JSON。默认每任务2张，上限16，滚动补位；多批可同传--batch，指定--queue-run-id。相同样本的实验条件不能合并交付，使用--no-combined-export。

run内visual_reviews.json是完整标签；正常exports含候选、抽检流包、provenance。未打分源（当前test池）保存完整标签及source_metadata_pending.json，旧严格候选延期，不造元数据、不重复视觉调用。正式exports/SQLite不覆盖。

现有GT清单无需逐批重做；新增/重筛数据才独立调用gt_quality_gate.py，命令见工具索引。IDE协作用新prepare包的START_HERE.md和ANTIGRAVITY_HANDOFF.md；模型直接填reviews_gemini.json，程序import-reviews/export-candidate。

旧GT资格或旧A定义契约不能直接续跑或克隆到当前标注器；重新prepare才能新实验。第15/16轮原结果保持，只作为旧流程开发历史。源码/配置/报告进入Git，大图/任务池/环境/运行产物不入Git；本次未提交/推送。
