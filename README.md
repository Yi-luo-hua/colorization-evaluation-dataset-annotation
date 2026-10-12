# 图像上色评价：CV实验与外部视觉审核

当前阶段：先优化CV与工作流，再由主人使用Antigravity中的`gemini-3.8-flash-high`进行视觉实验。模型名称按主人指定记录；此仓库没有配置IDE或调用其模型API。

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
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py prepare --model both --split val --start 1 --end 12 --run-id antigravity_val_1_12
```

生成24个样本、4张看板，每张6组，每组GT+生成图+双向彩度差。尾张可以少于6组。已有run不会覆盖。

把该run的`ANTIGRAVITY_HANDOFF.md`交给Antigravity，按`review_request.json`读取看板，从模板另存结果。原评分/旧缺陷仅在manifest里保留用于导出继承，不提供给盲审。

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py verify --batch .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py import-reviews --batch .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12 --reviews .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12\reviews_gemini.json
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\workflow.py export-candidate --batch .\LS_lcad_reviewer\intermediate\experiments\antigravity_val_1_12
```

未完成视觉审核、缺样本、未解决疑问/裁剪请求或缺少严重度，都会阻止候选导出。导出仍留在实验run，遵循正式JSON字段契约；不会写入原正式exports或SQLite。候选流包支持Label Studio，但同类多物体在界面里汇总显示最高级别，逐物体等级保留在描述与正式候选JSON。

## 验证和CV实验

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\check_workflow.py
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\evaluate.py
```

evaluate需要第一轮GT统计及分区记录，默认运行目录不会覆盖；再次实验用`--run-id`另建运行。初步结论与限制见`docs/STATUS.md`。参数是候选而非已确认标签阈值，严重度锚点尚未确定。
