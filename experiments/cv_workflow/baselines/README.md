# 数值基线快照

本目录只保留冻结源码/配置，不作为当前运行入口。已完成的一次性驱动与旧搜索配置另见[脚本归档](../archive/rounds_01_14/README.md)，当前工具见[活动索引](../README.md)。

- engine_v3.py：从Git提交5322885保存的第三轮数值算法；仅导入纯数值函数，不使用其ROOT执行文件操作。
- global_models_v4_calibration.py、region_models_v4_calibration.py、optimization_config_v4.json：第四轮校准时的源码/配置原字节快照，供核验运行manifest中的SHA256。运行后补充了灰阶参考排除、曝光解释、严重欠饱和结构保留，以及区域紧范围保留。
- engine_v4_stress.py：固定规则压力验证启动时的数值入口。当前engine.py只多了供视觉请求读取的中性摘要字段；快照SHA256与压力验证manifest一致。
- optimize_v4_calibration.py：第四轮优化入口原字节快照。当前入口识别匿名版manifest并排除其真实GT，历史SHA256对应此快照。

校准分数和后续固定规则确认分开记录，不把后续修正后的算法冒充校准时的版本。快照不作为当前工作流入口。

compact_harness_grounded_round8.py、config_v6_round8.json、config_v7_round9.json保留当时的提示/标签/参数边界；B/F回退与NR方向已取消，新调用以当前config.json及compact_harness.py为准。
