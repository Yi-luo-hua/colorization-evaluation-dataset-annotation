"""One-off documentation sync audit; not a workflow entrypoint."""
from pathlib import Path

root=Path(__file__).resolve().parents[3]
updates={
'README.md':'''# 图像上色评价：实验与自动标注

2026-10-13，第14轮GT筛查已完成。14,285张GT中弃用57张，剩余14,228张；LCAD/UniColor各排除57例，共保留28,456个模型样本。尚未给全部保留样本完成新标注或正式交付。

当前默认：**GT先过滤 → CV8辅助 → 六组看板 → Gemini 3.8 Flash High自读PNG、自写compact JSON → 滚动汇聚/校验/实验候选**。速度第一，允许微量不完美，0补图，不查单张原图。

## 文档与入口

| 文件 | 用途 |
|---|---|
| [STATUS](docs/STATUS.md) | 当前成果、数量与未解决问题 |
| [PLAN](docs/PLAN.md) | 已完成、下一步、暂缓与取消任务 |
| [DESIGN](docs/DESIGN.md) | 当前工作流、算法分工与结果契约 |
| [活动工具索引](experiments/cv_workflow/README.md) | 各脚本职责与归档边界 |
| [AGENTS](AGENTS.md) | 执行规则；用户最新要求优先 |
| [EXPERIMENTS](docs/EXPERIMENTS.md) | 第1～14轮历史证据与决策 |
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

## GT筛查与IDE协作

现有[冻结清单](LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/excluded_GT.json)和[六份过滤任务池](LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/filtered_tasks_pool)可直接使用，不需要每批重做全量筛查。扩充或重筛数据时，按[工具索引](experiments/cv_workflow/README.md)调用gt_quality_gate.py；新清单确认后更新config.exclude_manifest。

不可信GT直接弃用，不做B/F回退或无参考评价。GT阶段只确认候选；标注阶段对全部保留样本视觉审查。GT看板两列三行，标注看板六行三列，均6组/张，只有匿名G/S编号，没有原图位置。

IDE协作另prepare新批次，将START_HERE.md和ANTIGRAVITY_HANDOFF.md交给Gemini；它自读请求列出的看板，直接填reviews_gemini.json。程序再执行workflow.py import-reviews与export-candidate；同一批选择IDE或agy一种执行方式。

## 历史与归档

当前代码在experiments/cv_workflow；一次性旧实验脚本在[archive/rounds_01_14](experiments/cv_workflow/archive/rounds_01_14/README.md)，冻结基线在baselines。旧BF/NR/full字段生成入口已停用，历史结果仍可读取。继续新标注应重新prepare当前批次。

第12/13轮旧候选是历史对照，未按第14轮GT清单重导，不直接当当前清洁交付。LS_lcad_reviewer/core_pipeline及根兼容入口属于历史V4工具；当前自动流程不调用其旧分流/放行规则，只复用正式schema校验。

Git管理源码、参数与报告，忽略本地图像、任务JSON、环境、数据库和实验大产物；本次未提交或推送。
''',
'docs/STATUS.md':'''# 当前状态

同步日期：2026-10-13。第14轮GT筛查完成；本次统一任务/工作流文档并归档旧脚本，没有新模型标注或重新拟合数值阈值。

## 当前数据

| 划分 | 原GT | 弃用GT | 保留GT / 每模型样本 |
|---|---:|---:|---:|
| train | 10,000 | 36 | 9,964 |
| val | 1,428 | 8 | 1,420 |
| test | 2,857 | 13 | 2,844 |
| 合计 | 14,285 | 57 | 14,228 |

两模型共排除114例，保留28,456例。57张中54黑白、3异常整体色偏，占原GT约0.399%；待定0。GT全量CV、922候选加诊断控制共933个独立GT完成视觉判定，非候选暂保留，不等于全量视觉认证。

[冻结清单与过滤任务池](../LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013)已绑定config.exclude_manifest。真实prepare请求6例、跳过同GT两模型2例，只测量/渲染4例；原任务序号保留。源池、原图、正式交付及SQLite不覆盖。

## 当前工作流

- GT先过滤：不可信直接弃用，不标生成图，不做B/F或NR回退。
- 标注数值版本CV8；原版signed_chroma双向彩度差；六行三列6组/张。
- High自读本地PNG、自写compact JSON；匿名编号，无原图路径，0补图、单次主要缺陷审查。
- 上限16路，2看板/任务，跨批次滚动补位，各批自己完成便导出。
- 保留样本检查A/B/C/D/E1/E2/F；纯褪色优先E2，明显换色相才C；旧分数不作放行门槛。
- 原评分/模型/时间戳继承，completed_by=0；严重度仍临时近似，production_ready=false。

## 已完成与历史产物

第12轮确定16路滚动队列，第13轮保留原版显示，第14轮确定GT直接弃用与标注前过滤。详情查[实验索引](EXPERIMENTS.md)。

第12轮288例包、第13轮72个新增模型观察及重复条件均是历史证据，未按最新GT清单重导；不称当前清洁交付或人工金标准。全部保留28,456例尚未完成新缺陷标注，也尚未统一重评分。

## 未解决与下一步

1. A/E2：严重褪色但仍有物体颜色时，AI可能过判A。
2. 物体定位：GT颜色误述、包装等主要物体漏项、相邻对象描述混用。
3. GT保守筛查仍可能漏掉混合颜色偏移；6个合成GT排除4个、保留2个；部分环境光误排经快速诊断保守纠正。
4. 同输入模型输出有波动，严重度缺少稳定锚点；Schema通过不等于语义准确。

按[任务列表](PLAN.md)先在保留GT上做A/E2对照，再做必要CV证据及物体定位，最后新GT确认。无需主人逐图配合；本次未调用agy检查外部服务实时状态。
''',
'docs/PLAN.md':'''# 任务列表与下一步实验

2026-10-13。当前基线：冻结GT弃用清单 + CV8 + High + 16路滚动队列 + 6组看板 + compact。只在保留GT上推进后续标注，旧观察不冒称新留出。

## 已完成

- [x] train/val/test全部14,285张GT CV扫描；候选及控制933个独立GT完成视觉判定。
- [x] 冻结57张GT弃用清单，同GT两模型114例退出；六份过滤任务池齐全，待定0。
- [x] prepare在生成图CV前过滤、保留原任务序号；导出同步去掉弃用记录与抽检项。
- [x] High自读本地看板、自写JSON、匿名编号、0补图；16路跨批次滚动补位。
- [x] 本次文档/入口整理：旧实验驱动归档，GT筛查不再依赖取消的B/F试验，筛选工具应用现行GT清单。

## 按顺序推进

| 顺序 | 任务 | 本轮要回答的问题 | 状态 / 预期产物 |
|---|---|---|---|
| 1 | 有效GT上的A/E2诊断对照 | 全图灰阶/单色失败与严重局部褪色如何区分，残余肤色/衣物颜色是否足够明确 | 待准备：匿名六组诊断包、固定CV/提示对照及短报告 |
| 2 | 最小CV证据优化 | 哪一个结构/颜色保留信号能减少A过判，且不增加主要缺陷漏报或读图耗时 | 待第1步定位原因；配置化参数搜索、物理控制、冻结后新GT确认 |
| 3 | 主要物体及GT/生成颜色定位 | 如何减少GT颜色误述、包装漏项与相邻对象串用 | 待准备：先改最小必要提示，再判断是否需要额外字段 |
| 4 | 新GT全流程确认 | 改动在新GT、两模型与不同划分上是否仍快速、完整、可追溯 | 待值得采用的候选；独立任务入同一滚动队列 |

选择样本先应用现行弃用清单。复用第12/13轮作为开发诊断时先排除坏GT，按GT身份分组，同GT两模型及全部干预属于同一开发/留出区；不重新称为未见GT。新筛选入口screen_real.py与select_boundaries.py。

对照优先覆盖：完整灰阶/单色失败、明显残余彩色的严重褪色、局部褪色与单个物体换色、多物体共同偏移，以及包装等容易漏掉的主要对象。坏GT案例只用于GT筛选诊断，绝不送入缺陷标注。

## 采用依据

- 参数放配置；由统计/物理干预确定范围，冻结后另选新GT确认，不靠样本ID或旧标签写算法。
- 每次只改一个主要因素；保持样本、顺序、模型、任务拆分和队列上限，报告调用/墙钟、失败与恢复分别耗时。
- 物理控制、Codex/其他AI诊断、主人参考分开；AI一致性和Schema通过不当作准确率。
- 速度第一，明确主要缺陷即可，允许少量不完美；不重复全批追求一致，不增加查原图、补图、长报告或人工逐项批准。

## 暂缓与取消

GT混合偏色漏筛、严重度锚点、可选人工抽检回流作为后续独立任务，不阻塞当前轻量实验。新版人工修改自动融合尚未接入，不把历史SQLite合并器当当前默认。

已取消：不可信GT的B/F回退、NR标签扩展。未采用为默认：Medium、布局/区域框/长提示、Turbo/单橙总色差。旧一次性脚本只读归档，不能以旧配置继续新标注。

进入IDE协作或外部服务确实需要主人操作时说明具体事项；当前没有需要主人立即执行的操作。
''',
'LS_lcad_reviewer/使用说明_lcad师弟.md':'''# Label Studio：可选抽检入口

本项目当前默认是[GT过滤后的自动实验工作流](../README.md)，并非重新人工审核原10,000条任务。旧人工SOP与失效03_export_lcad.cmd已逐字节放入[历史目录](legacy_archive/workflow_cleanup_20261013)。

## 查看实验结果

1. 已有Python/Label Studio环境可直接运行02_start_lcad.cmd；只在缺环境时使用01_install_lcad.cmd。
2. 打开http://localhost:8080，导入当前实验run/exports/tasks_reviewed_stream.json作按需抽检。不要用原全量任务文件替代过滤后的抽检包。
3. 界面配置使用interface_dual_v4.xml。GT/模型图由本地文件服务加载；启动脚本把项目根目录设为图片根，SQLite存于data/。

自动标注不依赖人工抽检或补图。当前候选由experiments/cv_workflow/workflow.py导入/导出，正式字段校验复用core_pipeline/validate_export_schema.py。旧core_pipeline分流、旧人工导出和SQLite合并均不是新实验主线。

人工修改的新版回流属于待接入任务；需要融合时单独对齐批次与来源，不直接覆盖当前候选或原任务池。数据与历史正式exports保留原路径。
'''
}

for relative,text in updates.items():
    (root/relative).write_text(text,encoding='utf-8')
print('Synchronized',len(updates),'documents')
