# Label Studio：可选抽检入口

本项目当前默认是[GT过滤后的自动实验工作流](../README.md)，并非重新人工审核原10,000条任务。旧人工SOP与失效03_export_lcad.cmd已逐字节放入[历史目录](legacy_archive/workflow_cleanup_20261013)。

## 查看实验结果

1. 已有Python/Label Studio环境可直接运行02_start_lcad.cmd；只在缺环境时使用01_install_lcad.cmd。
2. 打开http://localhost:8080，导入当前实验run/exports/tasks_reviewed_stream.json作按需抽检。不要用原全量任务文件替代过滤后的抽检包。
3. 界面配置使用interface_dual_v4.xml。GT/模型图由本地文件服务加载；启动脚本把项目根目录设为图片根，SQLite存于data/。

自动标注不依赖人工抽检或补图。当前候选由experiments/cv_workflow/workflow.py导入/导出，正式字段校验复用core_pipeline/validate_export_schema.py。旧core_pipeline分流、旧人工导出和SQLite合并均不是新实验主线。

人工修改的新版回流属于待接入任务；需要融合时单独对齐批次与来源，不直接覆盖当前候选或原任务池。数据与历史正式exports保留原路径。
