# 真实样本边界小试准备

2026-10-12；未获得Antigravity视觉结果，尚未建立人工真值。本轮不调整CV分类阈值。

## 数值扫描与选样

使用cv_workflow_candidate_4对验证集1,428张GT × 两个模型共2,856组重新提取指标；任务文件只读取图像身份，不把旧评分/旧缺陷当真值。A候选12例，D候选508例；这些数量不等于缺陷发生率或准确率。

诊断集按以下六组数值特征各选3张GT，同时保留LCAD/Unicolor对应图，共18张GT、36样本、6张六组看板。

|选样组|排序目的|
|---|---|
|A边界|优先颜色结构/彩度收缩，观察灰阶失败与强欠饱和|
|D与局部差异冲突|D候选同时全局增益拟合残差大，检验局部错色与背景偏移|
|模型分歧|同GT两模型A/D候选不同，再比较变化幅度差|
|同图彩度增减|正负彩度尾部同时显著，观察不同物体E1/E2与C|
|低彩度对照|GT自身彩度最低，检验比值被小分母放大|
|随机对照|固定哈希排序，与以上定向选样对照|

除000000000785作为之前已看过的明确锚点，其余17张GT排除此前合成开发/留出及准备过的看板样本。锚点不是新留出。选样是诊断用途，不代表验证集分布，不能用其命中比例声称总体准确率。

每组取第一张GT做先导，共6张GT、12模型样本、2张六组看板。先导与36样本诊断集重叠，不能合并计算独立样本数。两张先导看板已检查六组排布、图像配对、文字和差分方向；未写入任何正式人工标注。

## 已准备的文件

- LS_lcad_reviewer/intermediate/experiments/real_boundary_screen_20261012：manifest、全量records、选样清单、选样理由与SHA256。
- LS_lcad_reviewer/intermediate/experiments/real_boundary_pilot_20261012：12样本先导；START_HERE.md是给Antigravity的可直接执行任务。
- LS_lcad_reviewer/intermediate/experiments/real_boundary_full_20261012：36样本完整诊断包，保留供先导之后扩展。

prepare新增--selection，支持非连续model/task_idx，并校验split、任务身份和选样文件哈希。连续范围入口仍可用，原数据/正式交付不修改。

## 主人现在配合的动作

在Antigravity使用gemini-3.8-flash-high，让它执行先导目录的START_HERE.md，保存reviews_gemini.json，完成后告诉洛熙。暂不需要全量人工标注或严重度打分。未知非A严重度可为null；不确定观察保留uncertain/needs_crops。

收到结果后，先校验完整12样本、标签约束和源图哈希，再列CV与视觉分歧和需要裁剪的样本。主人之后只核对这些重点A/D案例，填写人工参考模板（其余保留null）。严重度与正式候选导出仍留待后续。

```powershell
& .\LS_lcad_reviewer\.venv\Scripts\python.exe -B -X utf8 .\experiments\cv_workflow\review_boundaries.py compare --batch .\LS_lcad_reviewer\intermediate\experiments\real_boundary_pilot_20261012 --reviews .\LS_lcad_reviewer\intermediate\experiments\real_boundary_pilot_20261012\reviews_gemini.json
```

人工参考：从master_reference_template.json另存master_reference.json。A/D只能是true/false/null；回答项必须inspected=true并写证据。A=true不允许D=true。compare可加--reference路径，未知项不纳入误报/漏报统计。AI与CV的一致只作为分歧导航，不自动生成真值；诊断集不用于估计总体性能。

## 验证

新增非连续选样身份与错误映射拦截测试；新增未知参考不当负例、AI不确定不当无缺陷测试。原完整审核覆盖、同类多物体、原评分继承、候选格式等检查保留。候选模型与官方导出流程尚未因本轮调整。
