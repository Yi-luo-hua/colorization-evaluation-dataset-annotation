# 活动入口与阶段职责

当前CV13/v4：冻结人工A直接写A命中，其余样本只做B/C/D/E1/E2/F视觉标注。参数在config.json，状态/计划见docs/STATUS.md与PLAN.md。

| 入口 | 职责 |
|---|---|
| gt_quality_gate.py / gt_quality_screen_config.json | 独立上游GT筛查、候选GT六组看板、冻结清单/过滤池；不是生成图标注分支 |
| workflow.py / config.json | 冻结GT过滤 → 人工A直接结果／非A CV+看板 → 分支导入/完整汇聚 |
| compact_harness.py / agy_runner.py | High自读本地看板、自写六类JSON；禁止模型写A，禁止新调用旧契约 |
| run_sheet_workers.py | 跨批有界滚动并发，各批独立汇聚；缺旧分数不算模型失败 |
| real_batch_progress.py | 汇聚原真实批次与恢复任务的实际完整文件；生成缺失恢复包或新完整交付目录，不重跑已齐标签 |
| run_harness_trial.py | 复用当前契约看板、生成独立空模板恢复包；历史对照保留，不把旧包改版本号续跑 |
| review_boundaries.py | 当前六类START_HERE提示；旧A诊断只留archive |
| experiment_capacity.py / summarize_capacity.py | 第19轮同输入任务容量初测与实际文件/位置/吞吐诊断；控制数据仅实验用 |
| experiment_capacity_round20.py / summarize_round20.py / spatial_hint.py | 第20轮固定四路4/8容量及中性色相中心对照；第20轮已完成，坐标不采用默认，8继续容量候选 |
| experiment_layout.py | 第21轮3/6/8组布局对照，固定24样本/任务及8路；同冻结输入、不复制标签 |
| experiment_cd.py / global_rotation.py | 第22轮v1整体/局部干预与旋转证据；v1仅追溯，不采用为默认 |
| global_rotation_supported.py / experiment_cd_supported.py / check_rotation.py | 第22轮留色加权旋转模型、720控制、正候选提示及可选入口检查；默认不启用 |
| bleed_probe.py / experiment_bleed.py | 当前B私有诊断：正向侵染、双侧稳定、同色相深浅降权；不传AI、不自动标B。旧控制驱动已停止，无真实B正例金标准 |
| summarize_round22.py | 实际完整文件、共同完成样本对照和调用统计；完整恢复包另存，原失败输出保留 |
| calibrate_full_GT_references.py | 复用冻结GT/A名单，全量有效GT低彩度参照及非A视觉图对热图尺度统计；不写标签，不直接修改配置 |
| preview_C_parameters.py | 主人授权的真实全量C橙轮廓单参数分档，输出比例/并排图及人工选择页；不改主配置、不写标签或调用模型 |
| color_evidence.py | CV12同色相缩放残差、低彩度降权、差分列稀疏候选轮廓；不直接判C/E/B |
| recover_file_results.py | 旧完成文件离线恢复，保留原native错误；新运行器已直接接收完整合法的ERROR文件 |
| ANTIGRAVITY_HANDOFF.md | 当前生成图标注协议 |

engine/global_models/d_color_groups/color_evidence/region_models只生成非A的CV证据，候选不是标签。固定A不做CV、不进看板/Worker。只执行实际运行必需校验，不新增测试套件。旧A算法/阈值/提示、筛查/人工看板/灰阶绘图工具在archive/A_visual_before_frozen_20261014，不作为当前入口。

旋转D提示默认关闭。CV13 B测量已接入私有manifest，增加正向侵染与双侧稳定性；仍有真实误候选，b_boundary_evidence默认关闭，不在看板或提示中暗示B答案。最新诊断见[优化记录](../../docs/real_annotation_optimization_20261014.md)，旧实验见EXPERIMENTS。

现有57张上游清单可直接复用。新增/重筛GT作为独立上游任务：

```powershell
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py scan --run-id GT_screen_new
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py prepare --run-id GT_screen_new
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py run --run-id GT_screen_new --workers 16
# 只恢复未完成的上游GT候选：
.\LS_lcad_reviewer\.venv\Scripts\python.exe -B experiments/cv_workflow/gt_quality_gate.py retry --run-id GT_screen_new --workers 4 --timeout 300
```

确认上游新清单后更新gt_filter.exclude_manifest；日常标注命令见根README。GT阶段两列三行、匿名G；生成图阶段默认六行三列、匿名S、六组。每任务4/8/12/16张容量可通过run_sheet_workers.py --sheets-per-job对照；第19轮初测/单并发确认已完成，8列扩量候选，尚未替换默认。每张3/6/8组计划通过sheet.groups_per_sheet配置，renderer/请求/提示/IDE已支持，第21轮固定24样本对照已完成，默认保留6组、3/8可选；默认不变。任务及Gemini建议采用状态详见PLAN。

第1～14轮旧驱动在[archive/rounds_01_14](archive/rounds_01_14/README.md)，第15/16轮在[archive/rounds_15_16](archive/rounds_15_16/README.md)。历史原输出保留，包括旧统一单色A结果；不能由当前标注器续跑；新实验重新prepare。过程产物只在LS_lcad_reviewer/intermediate/experiments，不覆盖源池或正式交付。
