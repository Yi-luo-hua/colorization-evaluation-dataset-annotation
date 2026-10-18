# 第十二轮：更高并发与跨批次滚动队列

> 已完成阶段的历史记录。当前任务与默认流程查[STATUS](../STATUS.md)和[PLAN](../PLAN.md)；旧命令保留当时文本，一次性脚本现位于[归档索引](../../experiments/cv_workflow/archive/rounds_01_14/README.md)，不作为当前运行入口。

采用十六路作为新prepare批次的实验默认，每任务仍两张六组看板、最多12例。新192例相同16任务，八路353.55秒、十六路245.70秒，减少30.5%，吞吐32.58→46.89例/分钟；全部成功、无未解决项。新增144张GT×两模型共288个独立样本已汇总为候选数据集，重复对照不重计。

## 实际结果

| 样本 / 固定任务 | 调度 | 墙钟 | 完成 | 失败 / 未解决 |
|---|---|---:|---:|---:|
| 新96例 / 8×12 | 四路，同批内滚动 | 304.45秒 | 96/96 | 0 / 0 |
| 相同96例 / 8×12 | 八路 | 277.11秒 | 96/96 | 0 / 0 |
| 另192例 / 16×12 | 八路，两个96例批次共享队列 | 353.55秒 | 192/192 | 0 / 0 |
| 相同192例 / 16×12 | 十六路，两个批次共享队列 | 245.70秒 | 192/192 | 0 / 0 |

相同输入比较逐项验证任务内容、S编号、GT/生成图哈希、CV指标/候选、看板PNG字节和任务顺序。High、CV8阈值、看板与轻量提示词规则不变，模型自读本地图片、自写独立JSON；旧标注未提供给模型。

墙钟从调度启动到任务完成、逐批检查及候选导出，不是模型调用时长相加；CV/看板和分区准备不计入。十六路245.70秒还包含自动汇总192例，逐批导出完成时间245.58秒。八路汇总功能在测量后接入，其353.55秒止于逐批导出；汇总192例随后单独完成，不把操作间分析停顿加入基准。

96例四→八路只减少9.0%，八路一个任务用了275.53秒，成为尾部瓶颈。192例十六路约1.44倍提速，单任务平均却136.84→165.08秒、最大220.95→243.58秒；更多并发有吞吐收益，也增加单任务耗时，不据本轮外推32路。四个条件均只测一次。按主人要求推进准备与执行重叠，96例八路期间准备下一192例；因此本轮记录实际运行收益，不能视为完全隔离主机负载的稳定性能测量。

## 无轮次与跨批次屏障

主人指出独立任务不必等待整轮，已扩展run_sheet_workers.py：多个已prepare目录共享一个有界FIFO线程池，线程仅调度独立原生agy进程；任一任务完成，立即补下一个，包括后续批次。--workers是整个队列总上限，各批次自己的任务全部结束后立即检查、合并及导出，失败批次不取消其他批次。

实际八路：第二批第131.391秒启动，第一批最后任务第168.797秒结束、169.50秒导出。实际十六路：第二批189.09秒独立导出，第一批245.58秒才完成。证明后续批次不等待前批全部结束，批次输出也不等待全队列结束。

快照捕获同一时刻8个及16个本运行启动的agy原生进程；逐任务保存实际agy PID、runner PID、会话ID及开始/结束偏移，会话全部不同。每任务只收到自己的看板/S编号/候选/模板，直接修改自己的reviews_gemini.json；程序保留原文件并合并。没有共享同一模型结果文件或复用对话。

每批候选通过正式结构与逻辑校验。全队列全部成功后自动合并queue目录exports/reviewed_candidate.json、tasks_reviewed_stream.json和provenance.json，原字段原样继承，逐批来源哈希与B/F-only范围保留。某批未完成则保留该批失败日志和成功任务，其他批继续独立导出，不伪造完整汇总。

## 样本和标签观察

96例取48张新GT，排除436张历史GT；另192例取96张新GT，排除484张历史GT。两组GT无重叠，每组六个诊断分层，每层分别8/16张GT，均覆盖LCAD和Unicolor。旧CV只用于选择，实际特征重新按CV8计算。诊断抽样不用于推断全量缺陷比例或真实准确率。

96例四路/八路标签集合与参考范围一致70/96；192例八路/十六路一致131/192（64+67）。均是AI对AI诊断，不是人工准确率，原结果不回填。结构完整与语义正确分开记录；下一步继续CV差分呈现、主要物体识别和A/GT参考边界优化。

192例八路total_tokens=736,899，十六路915,999；这是CLI usage，不是费用，更高并发没有减少资源用量。完整input/output/thinking/cache字段保存在结果文件。

## 入口与交付

新prepare批次config.json的parallel_scheduler设workers=16、sheets_per_job=2；300秒单任务超时保持。旧已prepare批次仍使用冻结配置，可显式--workers 16覆盖。CV版本仍为cv_workflow_candidate_8，production_ready和severity_anchors_ready保持false。

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\run_sheet_workers.py --batch .\LS_lcad_reviewer\intermediate\experiments\batchA .\LS_lcad_reviewer\intermediate\experiments\batchB --queue-run-id queue_run --workers 16
```

本轮选用96例八路和192例十六路的成功结果，汇总288个不同图像记录：

LS_lcad_reviewer/intermediate/experiments/scale_round12_288_candidate_20261013/exports/

- reviewed_candidate.json：288例实验候选，正式14字段契约与逻辑校验通过。
- tasks_reviewed_stream.json：对应288例抽检流包。
- provenance.json：逐批审核模型、源候选哈希与参考排除范围；bundle_manifest.json在上级目录记录来源条件。

原图、任务池、正式exports、SQLite及历史运行未覆盖；没有提交、推送或发布。

## 复现和检查

源码：run_sheet_workers.py（滚动调度、逐批/队列汇聚）、run_harness_trial.py（子任务输入过滤）、summarize_scale.py（同输入与调度核对）。check_sheet_workers.py两个检查确认慢批次不挡后批导出、失败不取消其他批次；check_agy_runner.py六项文件契约检查通过。真实两次192例运行验证共享队列、逐批完成与完整汇聚，288例最终候选也通过正式契约。

所有过程文件位于LS_lcad_reviewer/intermediate/experiments/：parallel_round12_fresh96_selection_20261013、parallel_round12_fresh96_source_20261013、parallel4_12_fresh96_round12_20261013、parallel8_12_fresh96_round12_20261013；parallel_round12_fresh192_selection_20261013、parallel_round12_fresh192_source_20261013；rolling8_fresh192_round12_20261013_part1/part2及queue；rolling16_fresh192_round12_20261013_part1/part2及queue。

parallel_scale_summary_round12_20261013/results.json包含来源核验、各条件完整覆盖、同输入比较、进程/会话、实际墙钟、usage、逐S标签分歧与跨批次时间证据。每run/queue保存运行源码快照；新默认不会改写已冻结实验。
