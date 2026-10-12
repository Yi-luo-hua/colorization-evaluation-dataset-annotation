# Antigravity 视觉审核交接协议 v1

模型由主人在 Antigravity 中选择 `gemini-3.8-flash-high`。本工具不调用模型、不改 IDE 配置。`reviewer` 字段是过程自报元数据，不构成模型身份验证。

## 输入和六组看板

只读取本批次 `review_request.json` 和其列出的 `sheets/sheet_*.png`。每张大图六行，每行依次为 GT、生成图、双向彩度差；尾张可少于六组。根据行首完整 sample_key 逐一记录，禁止跨行配对或用上一组观察代替下一组。不要读取 manifest.json 中用于导出继承的旧评分/旧缺陷，也不要读取历史标注作为答案。

每组先检查 GT 与生成图完整画面，再使用彩度图导航。ΔC*=C*_生成−C*_GT，正红/品红、负蓝/青、近零黑色；显示色不是物体色。黑色不能证明无错色；红蓝不能直接判 E1/E2。所有组都须检查，不因 CV 无预警放行。

## 标签边界

- A：全图灰阶或单一色调造成颜色结构整体丢失；GT 本身低彩度不构成缺色。单色集中也可能只是强偏色，不跟随 CV 候选自动熔断。A 为唯一缺陷，severity=""。
- B：颜色越过具体物体边界侵染相邻物体；边缘色差不等于溢色。
- C：具体物体颜色相对 GT 错配；颜色符合常识也可以存在 C。
- D：不同物体/背景共同偏移；单个大物体换色不直接归 D。CV 共同向量只是辅助，网格不是物体。
- E1/E2：具体物体相对 GT 浓艳/褪色。区分色相变化、共同偏移和真正彩度异常。允许不同物体分别命中。
- F：颜色与物体、材质、光照、场景常识冲突；不因为与 GT 不同、或已存在其他缺陷而自动追加 F。

明确写出物体名称、位置、GT 色、生成色、观察证据。当前严重度尚未人工锚定，不能猜测：非 A 的 severity 可以为 null，但这类结果无法导出完整候选。不要编造 CV 数值或未看见的物体。

## 输出

从 review_template.json 另存为 reviews_gemini.json，不覆盖模板。每个 sample_key 恰好一条。检查完七类后 checked_categories=["A","B","C","D","E1","E2","F"]，inspection_complete=true。

decision 为 defects/no_defects/uncertain。defects 的对象格式：

```json
{"id":"C","object":"木门","location":"画面右侧","gt_color":"棕色","generated_color":"蓝紫色","severity":null,"evidence":"木纹门板整体从棕色变成蓝紫色，GT对照可见"}
```

不同物体同类缺陷分别记录。证据不足时 decision="uncertain"，写 uncertainties；需要放大时 needs_crops 写 sample_key 与归一化 bbox=[x1,y1,x2,y2]。不要把待复核写成无缺陷。

放大裁剪由 workflow.py crop 按需生成 GT+生成图二联，不默认增加其他参考图。

区域导航可能同时提供compact_bbox_normalized（高差异紧范围）与expanded_bbox_normalized（扩展范围）。这是同一数值候选的两种视野，不是两个物体；bbox_normalized是推荐视野。JPEG生成图优先紧范围，避免扩展被压缩差异连接到背景；可根据原图观察请求另一视野。区域不构成物体识别或缺陷标签。

## 回传和完成门槛

import-reviews 检查完整覆盖、样本对应、字段和 A 熔断约束；保留不确定项，状态仍待解决。export-candidate 要求所有不确定项和裁剪请求已解决、所有非 A 严重度有效，输出仅位于实验目录。

如需再审，建立新 run 保留旧审核记录。元数据 human_review.completed_by=0 表示外部 AI，不能称为主人或 Label Studio 的真人审核。正式发布/合并单独处理。
