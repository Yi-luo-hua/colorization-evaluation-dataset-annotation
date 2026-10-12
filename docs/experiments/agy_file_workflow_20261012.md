# agy本地看板与直接文件输出实测

默认High，速度优先，允许微量不完美；Gemini自行读取本地六组看板，直接填写指定标注JSON，CLI只返回保存确认。

## 调用链修复

恢复登录后，view_file被googlecloudtools.datacloud_telemetry前置hook拦截：CLI把脚本路径两端引号当作文件名字符。实际脚本存在，修复仅去掉该路径两端引号，插件仍启用，其余配置不变。

- 配置：C:/Users/丁家宝/.gemini/config/plugins/googlecloudtools.datacloud_telemetry/hooks.json。
- 原配置备份：同目录hooks.json.bak-20261012-200655。
- 修复记录：real_boundary_full_fast_20261012/agy_probe/hook_path_fix.json。

随后High正确识别了整张六行看板，能力验证通过。没有把图片/Base64直接嵌入提示词，图片由Gemini的本地文件工具读取。

## 已完成实验

|运行|档位/输出方式|样本/看板|调用耗时|结果|
|---|---|---|---:|---|
|real_boundary_full_fast_20261012|High，旧stdout JSON|36/6|157.70秒|36条候选通过官方契约；28有缺陷、8无缺陷|
|real_boundary_low6_20261012|Low，旧stdout JSON|6/1|31.97秒|小样本对照，候选通过|
|real_boundary_low6_file_20261012|Low，直接写本地JSON|6/1|57.86秒|回复仅“文件已保存”；程序读文件并导出候选|

High的缓存审计记录6张图片，每张匹配一张1560×2580看板的缩放版本，未发现单张原图缓存；审计文件agy_image_read_audit.json。后台只统一了defect/pass决策别名与category/id字段名，保留模型标签、证据和等级；没有为格式问题重看图片或重跑模型。

High与CV：A候选/观察分歧0，D分歧13（CV有而视觉未报11、视觉有而CV无2）。诊断集定向选样，AI不是人工真值，不用这些数字宣称真实准确率。Low文件输出与High前6样本的完整标签集合一致3/6，仍保持High为默认。样本量、批次规模、工具次数与缓存状态不同，以上时间不能直接证明某档位或输出方式普遍更快。

## 当前生效的文件工作流

prepare创建六组看板、匿名请求和模板；agy_runner把模板初始化为reviews_gemini.json。提示词只允许读指定看板与读写这个结果文件，禁止原图查找、源码读取、命令执行、补图和长总结。模型整批一次保存，不在回复中返回标注JSON。程序读取文件、做字段别名统一和一次后处理，完整结果自动导出实验候选；核心评分/原始时间戳保持不变。

输出方式已按主人最新指令改为本地文件；旧stdout实验仅保留作追溯。4项调用器测试覆盖非JSON保存确认、未填写模板不冒充完成、字段别名不改语义及提示词读写范围。历史正式exports/SQLite不覆盖，严重度仍是临时视觉近似。
