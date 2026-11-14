# 2026-11-04 至 11-11｜A 快审、彩度分析与 141 张复核

先从开发范围构建另一组 600 张 A/非 A 快审，探索彩度阈值。11 月 10 日另统计 Train/Val/Test 全量 28,570 张的均匀彩度分布，原图表保存在当时聊天。11 月 11 日从 Train/Val 筛出 141 张近灰候选，模型复核和主人复核分别保存。

| 工作目录或证据 | 内容 |
|---|---|
| [A 快审工具](../../a_chroma_reviewer_20261104/README.md) | 快审和两参数校准方法，属于历史筛查工作。 |
| [600 张 A 快审清单](../../a_chroma_reviewer_20261104/local/manifest.json) | 与七类人工标准集分开保存。 |
| [快审人工判断库](../../a_chroma_reviewer_20261104/local/judgments.sqlite3) | 人工 A、非 A、待定及事件。 |
| [阈值拟合快照](../../a_chroma_reviewer_20261104/local/fits) | 探索性的历史候选拟合。 |
| [600 张仅看生成图的复核](../../a_chroma_reviewer_20261104/local/no_gt_20261111) | 单独的模型复核记录。 |
| [22,856 张 Train/Val 筛查](../../a_chroma_reviewer_20261104/local/train_val_A_scan) | 全 Train/Val 计算汇总及 141 张候选表。 |
| [141 张复核目录](../../a_chroma_reviewer_20261104/local/train_val_A_review) | 模型输出、复核页面、来源对照和人审结果。 |
| [141 张人工判断](../../a_chroma_reviewer_20261104/local/train_val_A_review/human_review_20261111.json) | 主人完成这次候选复核后的导出。 |
| [GT 复核证据](../../a_chroma_reviewer_20261104/local/train_val_A_review/gt_no_defects_recheck_20261111.json) | 两张 GT 的整图无缺陷准入复核。 |
