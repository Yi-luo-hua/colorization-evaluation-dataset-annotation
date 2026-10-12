# 当前状态（2026-10-12）

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
