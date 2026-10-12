# 数值基线快照

- engine_v3.py：从Git提交5322885保存的第三轮数值算法；仅导入纯数值函数，不使用其ROOT执行文件操作。
- global_models_v4_calibration.py、region_models_v4_calibration.py、optimization_config_v4.json：第四轮校准时的源码/配置原字节快照，供核验运行manifest中的SHA256。运行后补充了灰阶参考排除、曝光解释、严重欠饱和结构保留，以及区域紧范围保留。
- engine_v4_stress.py：固定规则压力验证启动时的数值入口。当前engine.py只多了供视觉请求读取的中性摘要字段；快照SHA256与压力验证manifest一致。
- optimize_v4_calibration.py：第四轮优化入口原字节快照。当前入口识别匿名版manifest并排除其真实GT，历史SHA256对应此快照。

校准分数和后续固定规则确认分开记录，不把后续修正后的算法冒充校准时的版本。快照不作为当前工作流入口。
