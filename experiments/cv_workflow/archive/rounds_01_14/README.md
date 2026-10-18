# 已完成实验脚本归档

2026-10-13从活动目录逐字节移入28个文件，路径/哈希与原因见[整理清单](../../../../docs/archive/workflow_cleanup_20261013/cleanup_manifest.json)。这些文件仅供研究追溯，不是当前运行入口；未加入新模型调用或重新写历史标签。

| 类别 | 文件 |
|---|---|
| 早期数值干预/选参 | evaluate.py、optimize.py、stress_models.py、verify_regions.py、evaluation_config.json、optimization_config.json |
| 第5～8轮物理确认 | experiment_d_groups.py、confirm_d_groups.py、confirm_a_round8.py、evaluate_hue_regions.py、d_group_config.json |
| 已完成显示/布局/上下文对照 | evaluate_ce_maps.py、experiment_ce_sheets.py、experiment_ab_heatmap.py、experiment_tiled_sheets.py、experiment_roi_overlay.py、experiment_batch_order.py、experiment_model_batches.py、roi_overlay_config.json |
| 历史统计/比较 | compare_harness.py、summarize_d_groups.py、summarize_layout_trial.py、summarize_models.py、summarize_parallel.py、summarize_scale.py、profile_gt_reference.py |
| 已取消GT无参考方向 | experiment_gt_reference.py、gt_reference_round14_config.json |

依赖、相对路径及命令保留当时源文本，未改写成当前版本。复现时使用对应实验run的源码快照/Git版本与冻结配置，不能将本目录直接视为可运行的当前工具链。活动工具见[入口索引](../../README.md)，各轮结论见[实验索引](../../../../docs/EXPERIMENTS.md)。
