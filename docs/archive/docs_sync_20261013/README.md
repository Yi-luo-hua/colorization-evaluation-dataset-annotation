# 图像上色评价：CV实验与外部视觉审核

当前阶段：优化CV与快速工作流，默认视觉模型`gemini-3.8-flash-high`。本机agy CLI已实测自行读取本地六组看板；当前Gemini直接填写指定结果JSON文件，只回复保存确认，agy_runner.py读取文件并后处理。

当前CV为第八版候选：保留缺色/全图偏色与可靠色相导航，新增GT参考适用范围。GT没有有效彩色参考时只评B/F；CV按训练GT分布标出低彩度候选，AI看GT确认，白灰自然场景不自动跳过。新24例原六行High全流程148秒；两列三行、区域框和分模型上下文对照均未满足速度要求，不设默认。新规则12例通过导出校验，见[第九轮报告](docs/experiments/board_round9_20261013.md)。默认仍High、六组三列看板、E2优先、本地JSON一次保存，原图路径留在内部manifest。

第十三轮完成96例总色度距离图对照，Turbo/单橙色均未达到采用条件，原双向彩度图保持。GT参考、A误报和主要物体颜色误述仍需改进，详见[热图实验](docs/experiments/ab_heatmap_round13_20261013.md)。配对实验可用--no-combined-export保留两个条件各自候选，避免汇总重复图像。

第十二轮扩大至96/192例，真实多进程和独立会话：同192例八路353.55秒、十六路245.70秒，全部完成。默认新prepare批次采用最多十六路、每任务两张看板、跨批次滚动补位；High、CV8和标签规则保持。新增288例已汇总为一个实验候选数据集；标注分歧仍存在，提速不代表准确率提高，详见[放大与滚动队列实验](docs/experiments/parallel_scale_round12_20261013.md)。下一批先prepare新run，再运行：

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\run_sheet_workers.py --batch .\LS_lcad_reviewer\intermediate\experiments\my_cv8_batch
```

每任务的保存确认、耗时和原始JSON保存在parts/job_*/；Gemini只读自己列出的本地看板并直接写reviews_gemini.json，程序合并到reviews_merged.json，不解析回复中的标注JSON。并发配置在config.json的visual_harness.parallel_scheduler，--workers/--sheets-per-job可覆盖。agy_calls/parallel/result.json记录实际墙钟与逐任务耗时。完整有效结果自动导出实验候选；某任务失败时保留已完成文件和失败日志，不伪造完整结果。已有parts不覆盖。

多批次共享滚动队列：空位立即补后续任务，任一批次自身完成即独立导出；--workers限制所有批次合计并发。全部成功后，queue_run/exports/也汇总完整候选JSON和抽检流包。

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\run_sheet_workers.py --batch .\LS_lcad_reviewer\intermediate\experiments\batchA .\LS_lcad_reviewer\intermediate\experiments\batchB --queue-run-id queue_run
```

## 目录

| 目录 | 用途 |
|---|---|
| `experiments/cv_workflow/` | 当前实验代码、参数、六组看板和Antigravity交接协议 |
| `docs/` | 设计、当前状态、整理记录 |
| `LS_lcad_reviewer/core_pipeline/` | 既有工具链，保留供历史批次使用 |
| `LS_lcad_reviewer/intermediate/experiments/` | 新实验运行产物，Git忽略 |
| `LS_lcad_reviewer/intermediate/scripts/cv_workflow_experiments/` | 第一轮冻结实验源码，保留原路径可复现 |
| `LS_lcad_reviewer/intermediate/audits/` / `inspection_sheets/` | 历史审计和第一轮实验成果 |
| `LS_lcad_reviewer/legacy_archive/` | 历史脚本、整理前根入口备份 |
| `references/agentflow/paper/` | 原agentflow论文，原文件保留 |
| 三个原数据目录 | 原图、模型图、旧标签；路径不变、Git忽略 |
| `tasks_pool/`、`data/`、`exports/`、`streams/` | 原任务池、Label Studio数据库及交付成果；路径不变、Git忽略 |

Git用于源码、配置、提示词和报告版本管理，不纳入图片数据、运行环境、SQLite、任务大JSON或论文PDF；本地初始化不等于已推送或发布。

## 开始一批六组看板

从项目根目录运行：

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py prepare --model both --split val --start 1 --end 12 --run-id my_cv8_batch
```

生成24个样本、4张看板，每张6组，每组GT+生成图+双向彩度差。尾张可以少于6组。已有run不会覆盖。

把该run的`ANTIGRAVITY_HANDOFF.md`交给Antigravity，按`review_request.json`读取看板，从模板另存结果。原评分/旧缺陷仅在manifest里保留用于导出继承，不提供给盲审。

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py verify --batch .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12_cv4_ready
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py import-reviews --batch .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12_cv4_ready --reviews .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12_cv4_ready\reviews_gemini.json
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py export-candidate --batch .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12_cv4_ready
```

未完成视觉审核、缺样本、未解决疑问/裁剪请求或缺少严重度，都会阻止候选导出。导出仍留在实验run，遵循正式JSON字段契约；不会写入原正式exports或SQLite。候选流包支持Label Studio，但同类多物体在界面里汇总显示最高级别，逐物体等级保留在描述与正式候选JSON。

## 验证和CV实验

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\check_workflow.py
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\check_models.py
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\summarize_models.py
```

现成新版交接包为antigravity_val_1_12_cv4_ready。prepare使用新run名称，已有run不会覆盖。第四轮优化和新GT确认见[实验报告](docs/experiments/cv_models_v4_20261012.md)。summarize_models读取已完成运行，复核源码哈希并按GT聚类统计。evaluate/optimize需要第一轮GT统计及之前manifest，重跑须新run；历史分数需使用baselines对应源码。verify_regions/stress_models是本轮固定实验脚本，下一轮须新建运行入口。参数是候选而非已确认标签阈值，严重度锚点尚未确定。
