# 当前状态（2026-10-12）

## 真实边界先导（最新）

新版CV已扫描真实验证集2,856组：A候选12、D候选508，尚非真实标签。六种数值选样组各3张GT，两模型对应，共36样本/6张六组看板；除已检查的滑雪者锚点外其余17张GT排除之前实验样本。先导取每组1张GT：12样本/2张看板。

下一步需要主人在Antigravity执行`LS_lcad_reviewer/intermediate/experiments/real_boundary_pilot_20261012/START_HERE.md`，保存reviews_gemini.json。严重度可留null，不确定项保留；收到后先做分歧分析，再请主人核对重点A/D参考项。未生成真实审核结果，未改变CV阈值。

选样与回传流程见[真实边界小试报告](experiments/real_boundary_pilot_20261012.md)。review_boundaries.py compare只有收到明确人工参考后才计算相应误报/漏报，未知项不计负例。

## 第四轮更新（当前有效）

活动配置为cv_workflow_candidate_4，production_ready=false，严重度未校准。下方第三轮内容保留作历史背景。

- A加入亮度条件下的颜色结构与GT原色保留比例，排除灰阶GT和仍保留结构的严重欠饱和。
- D结合平移、像素覆盖及编码/线性RGB通道增益，排除能被统一曝光解释的变化。
- C/E导航最长边512，保留紧框与扩展框，JPEG优先紧框，修复分位数平台丢失。
- 开发24张GT、新留出48张GT：2,880例全局干预、2,160例ROI；随后另一批48张新GT固定确认：2,256例全局干预、1,440例ROI。两类确认共享这48张GT，不能称为96张独立样本。
- 新确认集A检出185/192、误报0/2,064；D检出806/816、误报5/1,248（排除真A）。A→D串联D误报9例，额外4例来自漏检A。
- ROI主框平均IoU从0.8096升至0.9108，IoU≥0.5检出率从86.88%升至97.43%。这是合成框定位，不是物体分割精度。
- 6项新数值测试及5项原工作流测试；按GT聚类bootstrap、运行源码哈希及快照已整理。

当前交接包：LS_lcad_reviewer/intermediate/experiments/antigravity_val_1_12_cv4_ready。24个真实样本、4张六组看板，状态awaiting_external_visual_review，未调用Antigravity模型。请求保留方向、覆盖率、拟合残差与ROI，旧评分/旧缺陷不提供给盲审。

完整结果和限制见[第四轮报告](experiments/cv_models_v4_20261012.md)。下一步建立真实A/D边界参考集，配合Antigravity盲审、辅助信息A/B及逐物体严重度校准；合成结果不能代表真实标注精度。正式exports、任务池和SQLite未改。

## 已完成

- 根Git仓库main分支及原源码基线；数据、环境和SQLite不纳入Git。
- 活动实验目录experiments/cv_workflow，第一轮源码与成果保留原路径。
- Antigravity的gemini-3.8-flash-high交接配置、提示词、完整结果检查与候选导出接口。未调用模型或调整IDE。
- 六组大看板（1560×2580），GT/生成图/双向彩度差三列。12组GT、两个模型共24个样本生成4张看板；状态awaiting_external_visual_review，尚无视觉结果。
- 连通数值区域导航：彩度增加/降低及色相分量，最多每类2个；不是物体分割或正式标签。
- GT 11,428张本底、真实验证对照2,856组；两轮原实验完成。
- 第三轮增加方向、不规则形状、90%覆盖局部变化及RGB白平衡增益：72张GT、2,376例干预，其中48张新GT留出（排除之前144张）。
- 5项数值/端到端契约测试：偏色向量、等彩度换色、正负渲染、小区域导航、六组布局、完整覆盖、待定等级拦截、源图改变拦截、逐物体候选与原分数继承。

## 第三轮发现

同一新留出集，D原v2规则精确率93.18%、召回率96.81%、F1=0.9496；增加像素活动覆盖候选（开发集选0.95）后精确率99.56%、召回率95.00%、F1=0.9723。90%宽条局部变化误报从48/48降至0/48，但白平衡增益漏报从每方向6/48增至13/48和12/48。因为真实标签及取舍尚未确认，候选阈值不自动替换活动配置，活动接口保留活动像素比例供复核。

A去掉单色集中度的自动分支，只保留原相对彩度/结构收缩候选；单色集中度进入review_only。在第三轮新留出，灰阶48/48检出、固定色调29/48检出、其他干预0误报。尚不能宣称所有单色失败都可自动判定。

这些是合成干预机制结果，不是实际标注精度。严重度未校准，B/F未新增CV分类器，真实ROI精度与独立视觉A/B尚未验证。

## 入口

- `experiments/cv_workflow/workflow.py`：prepare / verify / crop / import-reviews / export-candidate。
- `experiments/cv_workflow/engine.py`：浮点Lab指标、保守A候选、D候选、区域导航、双向图。
- `experiments/cv_workflow/config.json`：外部模型、数据路径、算法及显示参数；production_ready=false。
- `experiments/cv_workflow/evaluate.py`：第三轮实验，可用--run-id另建运行，现有运行不覆盖。
- `LS_lcad_reviewer/intermediate/experiments/antigravity_val_1_12/`：现成六组交接包。
- `LS_lcad_reviewer/intermediate/experiments/cv_geometry_v3_20261012/report.md`：完整第三轮结果。

## 待协作阶段

先用真实参考案例确认A/D边界与同图局部C/E，再由Antigravity读六组看板返回物体级JSON。校准严重度和盲审效果后，才考虑整合进正式工具链；当前输出仅为实验候选，不覆盖历史交付。
