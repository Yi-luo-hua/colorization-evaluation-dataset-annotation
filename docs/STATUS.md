# 当前状态

2026-10-15最新看板调整：已按主人要求移除黄／橙色荧光候选轮廓，渲染代码、共享配置、提示词、规则同步。原同48的无轮廓8板已离线重建并切为后续输入，GT／生成列及77条原BCDF底稿保持；0模型调用，旧41条试标和地区访问全停保持。详见交付STATUS顶部及runtime/no_overlay_20261015_01/packets/verification.json。

2026-10-15最新纠正试运行：主人要求再次试跑同48张，NR_secondary_preserve_20261015_04实际返回41/48可复核结果，已流式导入Label Studio项目19（41任务／41预测／0人工提交）。65条原B/C/D/F逐项审核：保留61、纠正2、删除2；另新增4条非E，E1/E2重点重标56条。3次调用显式复用同一会话；补正剩余7条时再次实际返回FAILED_PRECONDITION/code400/User location is not supported，已立即全停、0在途，不自动恢复。原指定reviewed成品哈希未变、旧结果保留、不计新增覆盖、不启动其余336或全量。

这是供主人检查的试标预测，不是质量合格交付。主控抽查绿色餐盒被保留为C-L2仍缺乏单图语义依据；另12条描述含原本／应有等颜色历史或预期措辞候选，须语义复核，不能用格式通过代替准确性。具体见运行目录QUALITY_REVIEW_NOTES.md、description_review_candidates.json、verification.json及交付STATUS。此段替代下文正在运行／0调用／只补旧25条等历史状态。

最新纠正：主人要求二次重点E1/E2、review原B/C/D/F，先前自由重标＋六类全覆盖实现偏离要求。现已改为原非E标签逐P编号默认保留、明确纠错才修改／删除且留理由，程序据底稿合并；同48已离线重备77条原BCDF，新规则完成0。旧48和详细23均只保留历史，原指定成品哈希未变。访问仍阻塞、0新调用；详见交付STATUS顶部和纠正说明。

2026-10-15最新：主人要求详细标注并确认High恢复，NR_detail_20261015_03提示已替换保守／互斥式提醒，重跑原48条终标。同一会话实际23条通过并导入[项目18](http://localhost:8080/projects/18/data?labeling=1)，同23条旧6项→新82项（数量不代表准确率），六类观察记录齐全；另25条未完成。High持续地区不支持，主人确认连接恢复后实际续接仍被拒，已立即全停、0在途。原48条和旧项目17保留、不计新增覆盖，完整状态见[交付STATUS](../annotation_delivery/train_val_v1_20261015/STATUS.md)。

## 2026-10-15：训练集／验证集两阶段交付准备

最新主线见[交付项目](../annotation_delivery/train_val_v1_20261015/README.md)和[当前状态](../annotation_delivery/train_val_v1_20261015/STATUS.md)，契约train_val_two_stage_NR_legacy_only_v2。按生成图可见质量及原始类别／分级判断，description为无GT比较、无对象／等级标题的自然句；C语义、区域／全图D已恢复。只有指定reviewed_1_10000_clean.json可作待二次底稿，实验AI标签和重跑全部退出。测试集暂缓，固定人工A保持。

当前02清单共22,768条：112条固定A、9,923条唯一旧成品待完整二次审核、12,733条先RGB初标；1,476个阶段任务及依赖已建，实验AI标签使用数0。旧成品同样存在GT比较／缺描述／旧A问题，不直接计完成。活动目录为preparation_02／starter_02；01保留但退役，禁止恢复。原成品哈希未变。

主人授权384试标后，固定角色16槽位运行器、显式会话续接、逐样本验收／阶段推进、网络与额度全停、部分导出已实现并实跑。当前48条六类终标、另48条仅初标；High明确RESOURCE_EXHAUSTED后已全停，0在途，剩余336条终标未完成。48条完整预测已导入新[Label Studio项目17](http://localhost:8080/projects/17/data?labeling=1)，实际核验48任务／48预测／0人工提交及图片／描述显示。完整断点见交付项目STATUS。额度恢复仍待主人确认，自动化保持暂停，不恢复旧实验队列；4—8轮长会话及缓存收益尚未验证。

## 以下为2026-10-14 CV13历史状态（保留追溯）

更新于2026-10-14，当前CV13。优化重点是提示词与CV，宁可漏标或可靠宽泛描述，不要错标。流程见[DESIGN](DESIGN.md)，任务见[PLAN](PLAN.md)，历史见[EXPERIMENTS](EXPERIMENTS.md)。

## 真实批次

| 批次 | 实际完成 | 状态 |
|---|---:|---|
| annotation_real_val192_20261013_01 | 192/192 | 标签、候选及任务包已保存；不重跑 |
| annotation_real_val192_20261014_02 | 192/192 | 初次96、恢复24+72；完整汇聚到同名前缀_completed目录 |
| annotation_real_val192_20261014_03 | 192/192 | CV13，16调用全部SUCCESS、0待定 |
| annotation_real_val192_20261014_04 | 192/192 | 新灰阶候选提示实跑，16调用全部SUCCESS、0待定/补跑，229.98秒 |
| annotation_real_val192_20261014_05 | 192/192 | 本次串行恢复补60条；完整汇聚至同名前缀_completed目录 |
| annotation_real_val96_20261014_06 | 96/96 | 相对浓淡措辞；3路滚动、8调用全SUCCESS、438.95秒 |
| annotation_real_val192_20261014_07 | 24/192 | High个人配额耗尽；11调用ERROR，其中2份实际完整；余5任务未启动 |

历史High完整文件覆盖1,080唯一样本，保留、不重复调用；第七批原缺168条已按源身份重新prepare为annotation_real_val168_v4_20261014_01：1条固定A已保存、167条六类视觉待额度恢复，28张看板、0新调用。旧v2恢复包不再调用，原24条成功结果和失败现场保留。当前无运行队列；High配额恢复须主人确认，期间不预检/重试，恢复临时共享≤4路、配置上限16。

[问题重跑差异](../LS_lcad_reviewer/intermediate/experiments/annotation_issue_rerun_setup_20261014_01/comparison_annotation_issue_rerun22_20261014_01_completed.json)与[相对措辞差异](../LS_lcad_reviewer/intermediate/experiments/annotation_relative_colour_setup_20261014_01/comparison.json)保留，已完成22+2+2条不重复。两条包/屏幕疑点已重新prepare为annotation_multicolor_grounding2_v4_20261014_01（1张板、2条六类任务、0调用）；旧草稿/包保留但不再调用。待额度恢复后按源身份另存差异，不计新增覆盖。

[第四批完整标签](../LS_lcad_reviewer/intermediate/experiments/annotation_real_val192_20261014_04/visual_reviews.json)及候选保留；A/B均0、两个近灰阶标E2，无人工真值。树木颜色归属错误已在定向重跑中去掉，不回填整批。

[第六批标签](../LS_lcad_reviewer/intermediate/experiments/annotation_real_val96_20261014_06/visual_reviews.json)及候选完整，0待定；C48、E2 35、D4为缺陷项数。抽看一张六组板，主要颜色差异可对应，公交车色概括偏粗；不是准确率。第五/六批B标签与CV候选均0，暂不改阈值。

CV12色相残差、低彩度降权和橙轮廓保留。第七批2个私有B候选未确认跨界；新增受染远侧原色保留降权，水域候选退出，屏幕候选仍略超阈值；不抬阈值凑退出，无真实正例验证，B导航关闭。新项仅用于后续prepare，第七批冻结证据不改。D参数不变，A改为冻结人工名单直接标签，见[优化记录](real_annotation_optimization_20261014.md)。

全量统计修订已完成：C/B低彩度参照3.523679→4.299005（14,228有效GT各图P20中位数），热图上限51.238564→51.783686（28,302非A视觉图对逐图abs(ΔC*) P95的跨图P95）。出处审查和待补依据项见[统计记录](../LS_lcad_reviewer/intermediate/experiments/full_GT_reference_calibration_20261014_01/README.md)；D/B判别阈值及其他参数保留，154固定A不做CV，仅后续prepare生效，已备包不改，0新调用。

主人授权的C单参数分档已完成：[人工选择入口](../LS_lcad_reviewer/intermediate/experiments/C_parameter_preview_all_20261014_01/index.html)。全量28,302非A样本，P90/P95/P98平均选区4.722%/2.298%/0.938%、候选图片均99.943%；面积4/8/16仅小范围变化。已保存4张六组并排PNG（每参数12例），待主人选档；主配置仍P95/面积8，无合成或新模型调用，标签和既有包保留。

A已正式接入v4分流：可用154条（train97/val15/test42）只标A命中、severity=""、评分1.0，无CV/看板/模型调用；16条上游GT排除不回流。独立[A直接标签](../LS_lcad_reviewer/intermediate/experiments/A_workflow_cleanup_20261014_01/A_direct_annotations.json)及[A任务流](../LS_lcad_reviewer/intermediate/experiments/A_workflow_cleanup_20261014_01/A_tasks_reviewed_stream.json)已保存，不向正式池/SQLite导入。154人工A与历史High覆盖可能重叠，不相加。旧A判断提示/阈值已从当前入口移除并归档。

近灰占比1个百分点统计及[折线图](../LS_lcad_reviewer/intermediate/experiments/gray_fraction_distribution_20261014_01/gray_fraction_distribution.png)已保存；全量28,570张，含各split及两模型分项CSV，≥99%/95%/90%/85%分别32/86/104/126张。这是像素占比分布及候选量，不是A标签数。

主人已审完近灰占比≥50%的490张生成图：[原看板入口](../LS_lcad_reviewer/intermediate/experiments/A_manual_gray50_490_20261014_01/index.html)及编号映射保留。1—240列非A、其余A；241—490列A、其余非A。154条可用人工A直接复用，不重复生成或AI审看；320条非A后续检查其他类别，16条上游排除不回流。

本对话30分钟接续自动化cv当前为PAUSED（保留状态）；提示同步v4分流及配额等待。问题重跑已完成不重复，主人停止时不继续。

## 流程与范围

冻结GT过滤 → 固定人工A直接结果／其余非A CV+匿名六组看板 → High只标B/C/D/E1/E2/F → 程序汇聚全部输入。

GT资格只在上游判定，冻结57 GT弃用、0待定。两模型保留28,456样本：154条固定A直接标签，28,302条六类视觉范围（train19,831/val2,825/test5,646）。入标注GT作参考，不复审资格；固定A是主人明确的分流，不由AI决定样本去留。全量六类尚未完成。

默认High、compact、fast_single_pass，6组/张、2张/任务、最多16路滚动补位，各批独立汇聚。不查原图、不裁剪、不补图、不增加复核回合。原图、原池、SQLite、正式导出及历史输出保留。

契约post_screened_GT_frozen_human_A_six_visual_v4；旧v2/v3只读完成文件/离线汇聚，新调用禁止旧A提示。六类CV候选不自动写标签；A直接来自人工确认，D仍严格全图整体偏色，severity临时、production_ready=false。

首批审查的18条修订另存诊断包，不计新增标注或算法收益。候选在LS_lcad_reviewer/intermediate/experiments；未打分源保留完整标签及source_metadata_pending.json，不造评分/时间戳。
