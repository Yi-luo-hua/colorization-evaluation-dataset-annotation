# 第18轮：A仅全图黑白无上色

2026-10-13，主人明确A仅生成图全图黑白、一点颜色都没上。统一泛黄、其他统一单色、局部留色均不属于A；非A不自动归E2。当前配置为CV11，annotation_contract=post_screened_GT_generated_only_A_grayscale_v2。

## 代码与工作流

generated_color.py在解码生成图的原分辨率RGB上统计逐像素max(R,G,B)-min(R,G,B)，输出最大通道差、非灰像素数及比例、测量尺寸。默认maximum_gray_channel_spread=0，全部像素R=G=B才进入灰阶A候选。此规则只用生成图，不要求颜色还原GT，也不要求物体间保留颜色区分。

workflow.prepare和screen_real在缩图/对齐之前测量生成图，之后D/C/E证据仍使用原来的分析分辨率。没有面积下限或百分位截断，防止局部颜色被全图均值、缩图或GT原色匹配条件抹掉。

旧A结构残差、GT原色保留、缩放竞争分类与A/E2结构提示已经移出下游代码及配置。global_models只提供D所需RGB增益解释，color_curve_residual继续供独立上游GT初筛调用。D、区域、显示、GT过滤和六组布局参数不变；12个真实图像对的D候选及局部区域与上一轮完全一致。

compact提示改为简短生成图RGB证据，明确非零通道差未必肉眼可见，不能自动标E2。IDE START_HERE和Antigravity协议同步新A。CV仍只提供候选，Gemini检查全部七类并写实际JSON；A唯一、severity=""、评分1.0保持。

新契约隔离旧A定义批次，不能只改旧包版本号续跑；重新prepare。旧观察、评分和历史统计不回填，历史统一单色A控制不作为新A依据。

## 物理与codec诊断

灰阶0～255梯度分别经PNG和JPEG质量50/75/90/95/100编码解码，6个codec控制最大RGB通道差均为0，支持当前等通道零容差。不是人眼可见阈值，也不是已经拟合的噪声容差。

取第17轮6张历史GT锚点，每张做7种PNG控制：灰阶、统一暖色、亮度关联有色、8%颜色保留、局部错误颜色、一像素一级通道差、恒等。共42例：6灰阶全部进入A候选，36有色均未进入。相同控制按新定义回查旧A算法，有23个非A误候选。

一像素控制仅验证原分辨率测量避免缩图丢色，不能当作“肉眼可辨颜色”的真值。6张GT不是独立留出，控制结果不外推真实准确率。容差1/2的敏感性也保留，未因此放宽默认：它们会吞掉某些微弱有色控制。

## 实际High与回归

12个第17轮真实图像锚点重新prepare，空模板，不复制旧标签；train/test各6例、各一张六组看板，2个独立High原生agy会话。模型自读本地PNG、自写reviews_gemini.json；无原图/base64输入、无裁剪、无GT复审。

| 批次 | 结果 | 调用耗时 | 批次墙钟 |
|---|---|---:|---:|
| train6 | 6/6七类完整，候选/流包各6条，正式Schema通过 | 95.92秒 | 96.86秒 |
| test6 | 6/6七类完整，完整标签保存，源旧分数缺失所以严格候选延期 | 84.45秒 | 85.27秒 |

共享队列96.86秒，12/12完整，0uncertain，0下游剔除，0个A。test S003滑雪图仍有颜色，上轮A这次变为天空E2 L3，符合新的A边界。其他C/E等标签亦有变化，未逐项认定正确；不把单次复测或墙钟变化当准确率/速度收益。本批没有已知真A正例，真实视觉正例和微弱有色边界还要独立确认。

38项不同软件检查通过：37项完整套件后，新增原分辨率prepare回归，再通过最终16项工作流检查。覆盖GT无关、有色单色、局部错色、缩图丢色、旧契约拒绝、七类覆盖、A唯一性、滚动汇聚和未打分源处理。

126个既有受保护源池/GT清单/正式导出/历史实验文件SHA不变。代码前快照、日志和核验只写新实验目录，未提交/推送。production_ready=false。

## 入口与后续

- [控制诊断及图片](../../LS_lcad_reviewer/intermediate/experiments/A_grayscale_round18_controls_20261013)
- [修改前快照、软件日志及核验](../../LS_lcad_reviewer/intermediate/experiments/A_grayscale_revision_20261013)
- [训练真实回归](../../LS_lcad_reviewer/intermediate/experiments/A_grayscale_round18_train6_20261013)
- [测试真实回归](../../LS_lcad_reviewer/intermediate/experiments/A_grayscale_round18_test6_20261013)
- [原生共享队列](../../LS_lcad_reviewer/intermediate/experiments/A_grayscale_round18_queue_20261013)

下一步先在固定CV11和标签规则下测试每任务2/4/8/12/16张看板；容量实验加入明确灰阶A正例、有色单色及微弱/局部留色非A对照。仅任务看板数可直接调整；每张3/6/8组实验还需实现动态renderer并单独验证，当前默认仍6组。

若后续需要容忍解码噪声，必须用单独的噪声/微弱留色控制验证，不能重新扩大A到统一有色图，也不能以GT原色保留作为条件。
