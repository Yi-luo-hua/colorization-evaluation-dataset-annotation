# 2026-10-12目录整理记录

- 建立根Git仓库，main分支，先保存原有源码基线；未配置远端或推送。
- 原始三个数据目录、Python环境、Label Studio数据库、任务池、正式交付和历史看板不移动。
- 活动代码与配置进入experiments/cv_workflow；新运行进入LS_lcad_reviewer/intermediate/experiments，生成物不进入Git。
- 第一轮实验代码及成果保留原路径，避免破坏已记录的来源哈希与复现命令。
- agentflow整个目录移至references/agentflow，论文文件保留；AGENTS.md.bak移至LS_lcad_reviewer/legacy_archive/AGENTS_preexisting_20261012.md.bak。
- LS_lcad_reviewer根目录六份重复工具替换为兼容命令入口，统一执行core_pipeline版本；原文件逐字另存本地legacy_archive/root_entrypoints_20261012（Git忽略重复备份），Git基线亦可恢复。
- 根showcase保留为历史成果展示；图片与PDF保留本地但不进入Git。

这是本地源码管理和目录整理，不代表已有实验通过真实标注验收或正式发布。
