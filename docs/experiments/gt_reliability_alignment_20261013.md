# 保守GT可信性规则与统计对齐

> 已完成阶段的历史记录。当前任务与默认流程查[STATUS](../STATUS.md)和[PLAN](../PLAN.md)；旧命令保留当时文本，一次性脚本现位于[归档索引](../../experiments/cv_workflow/archive/rounds_01_14/README.md)，不作为当前运行入口。

历史阶段记录：后续主人明确不可信GT直接弃用、不进入标注；当前规则及全划分筛查成果以[第14轮](gt_quality_round14_20261013.md)为准，下文B/F回退不再用于新批次。

2026-10-13，依据主人最新要求完成入口规则、harness、过程原因记录及统计。没有调用Gemini或重写历史标注；数值算法仍CV8，不新增自动排除或放行。

默认信任GT，拿不准继续用GT。只允许两种不可信原因：

- `black_and_white`：确为黑白图像，没有有效物体颜色参考；仍有蓝色座椅、肤色或衣物颜色不能当黑白。
- `abnormal_global_cast`：明显异常整体色偏，跨不同物体共同污染，且正常场景光照不能解释；记录一句跨物体证据和排除正常光照的依据。

低饱和、白灰物体、阴天、夜景、夕阳、舞台灯光、雪景、水下环境、单色物体主导均不单独触发。模糊、噪声、压缩质量不加入新的不可信类型。不按固定比例或数量凑排除名单；以高精度保守确认控制规模。

## GT统计

复用原11,428张GT的Lab色度统计（每GT一行，不按两模型重复计数）。P95 C是像素色度95分位数；下面0.5/1/2是统计观察切片，不是新自动排除阈值。

| 划分 | GT总数 | 原均值C<3.5214候选 | P95 C<0.5 | P95 C<1 | P95 C<2 |
|---|---:|---:|---:|---:|---:|
| train | 10,000 | 100 | 2 | 3 | 3 |
| val | 1,428 | 18 | 0 | 0 | 0 |

训练P95 C<1切片仅占0.03%；这不是已确认不可信GT的数量。P95也可能忽略占比很小但有效的颜色，仍须在原六组看板内快速确认。整体色偏不能根据均值a/b或颜色集中度直接确诊，这些数值同时会选中正常特殊场景；本次未报告色偏GT确认数。

[统计快照](../../LS_lcad_reviewer/intermediate/experiments/gt_reliability_alignment_20261013/gt_profile_summary.json)保留来源哈希、配置和切片ID；ID仅供内部实验，不写在视觉看板/请求上。

重现命令（项目根目录）：

```powershell
.\LS_lcad_reviewer\.venv\Scripts\python.exe experiments/cv_workflow/profile_gt_reference.py --profiles LS_lcad_reviewer/intermediate/audits/cv_workflow_experiment_20261012_01/gt_profiles.csv --chroma-probes 0.5 1 2 --out LS_lcad_reviewer/intermediate/experiments/gt_reliability_alignment_20261013/gt_profile_summary.json
```

## 实现与验证边界

config的`gt_reference.reliability`记录独立规则版本`conservative_gt_v1`及两类原因。新prepare将规则送入匿名视觉请求；compact/START_HERE共用规则文本。普通行仍是数组，没有增加额外逐图字段；少量不可信行记录GT_reason，异常整体色偏再记录GT_evidence短句。

expand/validate将理由保留并约束，缺理由、其他泛化原因或整体色偏缺场景依据不能导出；原因仅存过程文件/provenance，正式14字段/缺陷4字段不变。旧冻结配置没有reliability则仍可读原BF_only格式，不回写历史结果。

此阶段不可信GT暂沿用B/F检查范围。生成图自身的A/D/E扩展保留为下一步独立实验，不能将当前输出说成已检查七类。GT入口收紧和无参考评价扩展分开测量，避免无法归因。

工作流12项、agy文件输出6项、滚动调度2项，共20项检查通过，含新理由门槛、色偏证据、旧契约兼容及原正式schema导出。校验通过只证明工程契约，GT误排是否减少仍需小集视觉对照；不把这次规则对齐称为第14轮视觉实验完成。
