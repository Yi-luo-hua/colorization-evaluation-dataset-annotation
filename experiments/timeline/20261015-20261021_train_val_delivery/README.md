# 2026-10-15 至 10-21｜Train/Val 试标与三轮交付

从两阶段试标起步，恢复 5000 条批次后扩展到 Train/Val 全量。对二次空标签增加独立三次复核，最终交付 22,768 条，其中 22,656 条走视觉流程，112 条复用冻结人工 A。结果来自旧口径。

| 工作目录或证据 | 内容 |
|---|---|
| [交付项目说明](../../../annotation_delivery/train_val_v1_20261015/README.md) | 流程、规则、准备和运行入口。 |
| [准备数据](../../../annotation_delivery/train_val_v1_20261015/data) | 清单和样本映射，含退役的 01 版本及后续 02 版本。 |
| [主运行目录](../../../annotation_delivery/train_val_v1_20261015/runtime/recovery5000_20261016_01) | 从 5000 条扩大到全量后继续沿用目录名。查 state.sqlite3、尝试记录、读图凭证和原始结果。 |
| [最终统计](../../../annotation_delivery/train_val_v1_20261015/exports/final_statistics_20261021/REPORT.md) | 阶段计数、空标签变化及最终统计。 |
| [训练交付 JSON](../../../annotation_delivery/train_val_v1_20261015/exports/training_train_val_20261021) | LCAD、UniColor 各自的 Train 和 Val 共四份。 |
| [训练包 ZIP](../../../annotation_delivery/train_val_v1_20261015/exports/training_train_val_20261021.zip) | 同版交付打包文件。 |
| [10 月 20 日初版成品](../../../annotation_delivery/train_val_v1_20261015/exports/final_train_val_20261020) | 保留用于版本追溯。 |
| [100 张抽查](../../../annotation_delivery/train_val_v1_20261015/exports/random_spotcheck100_20261021/README.md) | 交付后的小批抽查资料。 |

## 10 月 15 日准备、试标及 48 张对照

- [before_NR_v2](../../../annotation_delivery/train_val_v1_20261015/runtime/before_NR_v2)
- [docs_before_01](../../../annotation_delivery/train_val_v1_20261015/runtime/docs_before_01)
- [no_overlay_20261015_01](../../../annotation_delivery/train_val_v1_20261015/runtime/no_overlay_20261015_01)
- [pilot_384_20261015_01](../../../annotation_delivery/train_val_v1_20261015/runtime/pilot_384_20261015_01)
- [rerun48_detail_20261015_01](../../../annotation_delivery/train_val_v1_20261015/runtime/rerun48_detail_20261015_01)
- [secondary_review_correction_20261015_01](../../../annotation_delivery/train_val_v1_20261015/runtime/secondary_review_correction_20261015_01)
- [secondary_review_trial48_20261015_01](../../../annotation_delivery/train_val_v1_20261015/runtime/secondary_review_trial48_20261015_01)
- [starter_01](../../../annotation_delivery/train_val_v1_20261015/runtime/starter_01)
- [starter_02](../../../annotation_delivery/train_val_v1_20261015/runtime/starter_02)

## 10 月 16 日恢复、Medium 试验和诊断

- [autonomous_pipeline_v1](../../../annotation_delivery/train_val_v1_20261015/runtime/autonomous_pipeline_v1)
- [batch5000_8sheets_20261016_01](../../../annotation_delivery/train_val_v1_20261015/runtime/batch5000_8sheets_20261016_01)
- [empty_label_audit_20261016_01](../../../annotation_delivery/train_val_v1_20261015/runtime/empty_label_audit_20261016_01)
- [high_medium_fresh24_20261016_01](../../../annotation_delivery/train_val_v1_20261015/runtime/high_medium_fresh24_20261016_01)
- [medium_prompt_20261016_02](../../../annotation_delivery/train_val_v1_20261015/runtime/medium_prompt_20261016_02)
- [quota_dependencies](../../../annotation_delivery/train_val_v1_20261015/runtime/quota_dependencies)
- [recovery5000_20261016_01](../../../annotation_delivery/train_val_v1_20261015/runtime/recovery5000_20261016_01)
- [trial100_8sheets_20261016_01](../../../annotation_delivery/train_val_v1_20261015/runtime/trial100_8sheets_20261016_01)
- [trial100_no_overlay_20261016_01](../../../annotation_delivery/train_val_v1_20261015/runtime/trial100_no_overlay_20261016_01)

## 10 月 17 日补充入栈和工程核查

- [browser_guard_verification_20261017](../../../annotation_delivery/train_val_v1_20261015/runtime/browser_guard_verification_20261017)
- [completed_integrity_review_20261017](../../../annotation_delivery/train_val_v1_20261015/runtime/completed_integrity_review_20261017)
- [throughput_review_20261017_1415_1615](../../../annotation_delivery/train_val_v1_20261015/runtime/throughput_review_20261017_1415_1615)
- [tier1_train_lcad_remaining_20261017_01](../../../annotation_delivery/train_val_v1_20261015/runtime/tier1_train_lcad_remaining_20261017_01)
- [tier2_val_all_2840_20261017_01](../../../annotation_delivery/train_val_v1_20261015/runtime/tier2_val_all_2840_20261017_01)

主运行的 attempts、旧 5000 任务包和退役预备包 01 中的编号看板已清理。任务头、样本映射、结果及读图凭证仍在原处。
