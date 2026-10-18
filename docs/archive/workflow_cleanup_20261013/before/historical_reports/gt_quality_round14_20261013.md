# 第14轮：全划分GT筛查与标注前剔除

2026-10-13。主人重新明确不可信GT直接弃用，并要求在实验阶段覆盖所有数据集；不做B/F回退或无参考标注。保守范围仍是黑白、明显异常整体色偏，正常低饱和和特殊光照不单独触发。

## 完成结果

| 划分 | 全量GT | CV候选 | 最终剔除GT | 保留GT | 两模型退出样本 |
|---|---:|---:|---:|---:|---:|
| train | 10,000 | 643 | 36 | 9,964 | 72 |
| val | 1,428 | 85 | 8 | 1,420 | 16 |
| test | 2,857 | 194 | 13 | 2,844 | 26 |
| 合计 | 14,285 | 922 | 57 | 14,228 | 114 |

57张占全量约0.399%，54张归黑白（包括主体没有有效颜色的扫描/单色旧照片），3张为异常整体色偏。统计量不是剔除配额。两模型各保留14,228例，共28,456例；本轮没有生成这些样本的新缺陷标注或宣称正式交付。

CV全量扫描用时96.28秒。922个数据候选加上额外诊断与已知干预，合并相同GT哈希后933个独立GT、156张六组GT看板完成视觉判定（其中6个合成GT，不进入数据任务池）。没有待定GT。全量CV覆盖不等于全量视觉审查：非候选暂保留，不能称全部GT已证明完美。

## 判据与算法

配置[gt_quality_screen_config.json](../../experiments/cv_workflow/gt_quality_screen_config.json)控制所有候选参数；[gt_quality_gate.py](../../experiments/cv_workflow/gt_quality_gate.py)为扫描、看板、独立agy、汇聚/恢复与过滤入口。

- 256最长边的浮点Lab均值彩度、ab(L)交叉拟合P95残差、色相集中度；阈值从训练10,000张GT分布校准，分别取P1/P1/P95。
- 本轮校准值：均值彩度3.5214、曲线残差4.9091、色相集中度0.973676。低均值/低残差/高集中度的并集仅作候选，不自动剔除。
- Gemini High只读取候选GT六组看板（两列三行），直接填写本地GT_decisions.json，普通保留项只写keep。不附图片，不提供原图路径/ID、历史标签/分数，不标生成图。
- 默认保留。确认主体无有效颜色的黑白照片，或不同材质/中性物体共同异常染色且正常光照不能解释时剔除；后者写一句场景依据。夕阳、夜景、舞台彩灯、雪景、水下环境、白灰物体与单色主体不单独触发。

近灰阶P95<1的三张训练GT实际仍有红伞、蓝绿色玩具或衣物有效颜色，本轮保留；说明灰阶占比不能直接替代GT可信性判定。

## 调用、恢复与保守纠正

初始78任务、16路滚动队列耗时469.88秒，73任务正常完成；5任务因容量429、连接/流中断或未完整填写失败。4路补跑235.59秒，再以2路、300秒恢复上限补跑223.02秒。三段为执行墙钟，未包含准备、诊断和调用间人工/代理分析时间，不将其直接称总项目耗时。

共86个原生agy调用，77次完整CLI成功、9次服务/文件不完整记录保留。一次CLI中断前已经写完12个独立GT决定，逐键验证后恢复实际文件数据；不把空模板、缺键或无效决定当保留。后续只请求尚未完成的GT。最终933/933决定齐全。

Gemini原始决定列出68张数据GT剔除。Codex快速检查剔除看板后，按拿不准保留恢复11项（暖冷环境光、雾霾剪影、自然低彩度、颜色对照拼图等），形成57张冻结清单。原模型文件不改写，纠正及依据单独保留；这是AI诊断，不冒充主人或人工真值。提示增加“缺少鲜艳颜色不等于黑白处理”和拼图/环境光边界，适用于后续筛查。

24个独立诊断GT含18个真实观察及6个合成GT。真实诊断的有色低彩度、正常特殊场景和蓝座椅均保留，旧黑白照片剔除；6个已知干预GT剔除4个，保留2个混合颜色色偏控制。这说明保守规则会漏掉部分色偏，且物理干预不自动等于任何场景的语义真值；本轮不报告总体准确率，也不据此放宽所有暖冷场景的剔除。

## 工作流接入与核对

config.gt_reference.policy已改为visual_confirm_exclude，并绑定本轮excluded_GT.json。prepare继续读原任务池，以split/GT ID在生成图CV与渲染前过滤，跨lcad/unicolor一致，原任务序号保留。失败待定候选可隔离，当前待定为0。

若后续视觉阶段发现漏筛GT，compact用exclude_GT弃用，不填空缺陷数组或BF_only/NR；程序从候选JSON及抽检流包移除同GT全部模型样本，meta.total_images按保留数计，独立保留原因，正式字段契约不扩展。

15项工作流、6项agy文件输出、2项滚动调度检查通过。真实双模型prepare请求6例，跳过同坏GT2例，只测量/渲染4例；六份过滤任务池均无57个弃用GT，LCAD源池扫描前后哈希一致，原图/源池/正式exports未覆盖。

## 产物与重现

运行目录：[gt_quality_all_splits_20261013](../../LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013)。

- [冻结筛除清单](../../LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/excluded_GT.json)
- [过滤后六份实验任务池](../../LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/filtered_tasks_pool)
- [数量、来源与真实prepare核验](../../LS_lcad_reviewer/intermediate/experiments/gt_quality_all_splits_20261013/verification.json)
- profiles.json、candidate_selection.json、GT_manifest.json、jobs各次原文件、GT_job_results_attempt*.json与GT_review_corrections.json保留完整过程。

新一轮用新run-id；已有运行只对失败项retry，不覆盖历史调用目录：

```powershell
.\LS_lcad_reviewer\.venv\Scripts\python.exe experiments/cv_workflow/gt_quality_gate.py scan --run-id new_GT_screen
.\LS_lcad_reviewer\.venv\Scripts\python.exe experiments/cv_workflow/gt_quality_gate.py prepare --run-id new_GT_screen
.\LS_lcad_reviewer\.venv\Scripts\python.exe experiments/cv_workflow/gt_quality_gate.py run --run-id new_GT_screen --workers 16
# 仅在存在失败/待定时：
.\LS_lcad_reviewer\.venv\Scripts\python.exe experiments/cv_workflow/gt_quality_gate.py retry --run-id new_GT_screen --workers 4 --timeout 300
```

开始本轮前的BF/NR36例对照已归档：NR36完整，BF24/36完成、一个任务流中断；主人更改要求后不补跑、不采用或混入过滤任务池。后续在保留GT上继续A/E2优化，无参考方向停止。
