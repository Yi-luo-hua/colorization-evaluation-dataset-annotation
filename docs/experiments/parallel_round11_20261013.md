# 第十一轮：agy多进程与独立会话并发

> 已完成阶段的历史记录。当前任务与默认流程查[STATUS](../STATUS.md)和[PLAN](../PLAN.md)；旧命令保留当时文本，一次性脚本现位于[归档索引](../../experiments/cv_workflow/archive/rounds_01_14/README.md)，不作为当前运行入口。

采用最多四路并发、每任务两张六组看板（最多12例）作为速度优先的实验默认。High、CV8、彩度图、单次自读本地PNG与直接写文件契约保持。新48例同四任务，墙钟二路313.28秒、四路164.31秒，减少47.6%，约1.91倍；各48例全部完成，零失败、零未解决项，候选通过正式格式与逻辑校验。

## 对照和计时

| 条件 | 样本 / 任务 | 并发数 | 耗时 | 完成 |
|---|---|---:|---:|---|
| 第十轮顺序调用参考 | 旧24 / 2×12 | 1 | 243.60秒 | 24/24 |
| 相同旧24、两任务同时调用 | 旧24 / 2×12 | 2 | 158.91秒 | 24/24 |
| 相同旧24、拆成四任务 | 旧24 / 4×6 | 4 | 157.06秒 | 24/24 |
| 新48、固定四任务 | 新48 / 4×12 | 2 | 313.28秒 | 48/48 |
| 相同新48、固定四任务 | 新48 / 4×12 | 4 | 164.31秒 | 48/48 |

顺序参考243.60秒是两次真实模型调用的耗时之和，排除Codex分析停顿；其余是调度开始到任务汇聚、检查和候选导出的实际墙钟，不是调用时长相加。计时不包括生成CV/看板及分区准备，因此这些值表示视觉调度阶段。旧24二路相对顺序调用减少34.8%；旧24四路同时改变任务大小，不能作为纯并发度对照。

新样本排除412张历史GT，选取24张新GT×两模型共48例、8张看板；六个诊断分层各4张GT，选择用旧CV筛选指标，实际看板重新计算CV8。不是代表全量分布的准确率样本。二路与四路的四个子任务逐项匹配S编号、内部来源映射、GT/生成哈希、全部CV指标/候选、PNG字节与顺序，旧模型标注未复制。

新48二路调用时长159.56、114.27、100.03、151.78秒；四路131.75、147.61、163.25、128.44秒。每条件只测一次，服务端负载、缓存和随机生成均可能影响耗时；没有测六路/八路或持续限流，不把本轮结果外推为稳定吞吐上限。

## 真实并发与文件隔离

run_sheet_workers.py的线程池只调度原生进程，每任务启动独立Python运行器及agy CLI，独立会话，不使用continue。逐任务保存runner PID、实际agy PID、开始/结束偏移和conversation_id；四任务会话ID全部不同。旧24四路的live_process_snapshot.json也记录同一时刻四个原生agy进程。初次旧24二路尚未增加agy PID记录，但已有两runner重叠区间及不同会话ID；不把PID缺失解释为没有并发。

每任务parts/job_*/只给Gemini自己的S编号和两张看板列表；低彩度候选、模板键也同步过滤，避免模型误填别的任务。Gemini使用工具自行读取本地PNG，直接填写各自reviews_gemini.json，仅回复保存确认。程序读取实际文件，保留原始模型文件，合并成reviews_merged.json，检查没有遗漏、重复或额外S编号后导出实验候选。

某任务失败时保留成功文件与失败日志，保存workers_incomplete，不把未完成任务当无缺陷或伪造完整候选。超时300秒保持，超时仅停止本运行器启动的agy子进程。没有修改全局登录、模型配置或历史结果。

## 标签观察与资源

四组并发实验共144个输出全部完整，四个候选均通过结构/逻辑契约；这说明调用与合并可用，不说明语义准确。旧24两个并发条件均保持S013/S014两个A、S010/S022两个B/F-only，仍存在物体错漏。

新48二路/四路的标签集合与参考范围相同31/48；这是两个AI结果之间的诊断一致性，不是准确率。二路A四例、B/F-only两例；四路A五例、B/F-only一例。抽看相同看板：S037生成图仍有肤色及荧光黄绿色局部，四路却标全图A，属于明显过度归类；二路把有棕色猫毛和木窗参考的S044当B/F-only，属于过度跳过。两个条件各有误判，不能据这些差异断言并发本身改变质量，也没有手动回填结果。

新48二路usage total_tokens=200,891、四路250,915；input/output分别135,692/65,199与191,695/59,220，thinking分别61,104与55,551。CLI缓存字段单独保留，total不是所有字段机械相加，usage也不是计费金额。四路更快并不意味着资源更少；以主人速度第一的要求选择四路。

## 当前入口与下一步

config.json的visual_harness.parallel_scheduler设workers=4、sheets_per_job=2。新prepare批次使用：

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\run_sheet_workers.py --batch .\LS_lcad_reviewer\intermediate\experiments\my_cv8_batch
```

--workers与--sheets-per-job可覆盖；--baseline与--run-id用于复制冻结输入开展新对照。已有parts不覆盖。每worker单次完成；父批无需再调用Gemini重审。四路是实验默认，production_ready和severity_anchors_ready仍为false。

下一项回到CV差分呈现对照，在相同任务/并发度下测试总色度差图对等彩度换色及主要物体识别的帮助。暂不需要主人逐图参与或补图。

## 文件和验证

源码：experiments/cv_workflow/run_sheet_workers.py、run_harness_trial.py、agy_runner.py、summarize_parallel.py。实际单任务文件契约相关6项检查通过，真实--batch入口已完成四路48例；四组输入来源哈希、结果完整性、正式候选格式均通过。

产物均在LS_lcad_reviewer/intermediate/experiments/：

- parallel2_12_round11_20261013、parallel4_6_round11_20261013：旧24两个并发条件。
- parallel_round11_fresh_selection_20261013、parallel_round11_fresh48_source_20261013：新48选择和未标注输入。
- parallel2_12_fresh48_round11_20261013、parallel4_12_fresh48_round11_20261013：固定四任务对照。
- parallel_summary_round11_20261013/results.json：实际计时、会话、PID、usage和标签统计；quality_differences.json：逐S编号标签/范围分歧。

每run的parts/job_*保存独立模型原文件与日志，agy_calls/parallel/result.json保存墙钟和逐任务记录。配置/源码快照随运行保留；结果仍只在实验目录，原图、任务池、正式exports和SQLite不改。未提交、推送或发布。
