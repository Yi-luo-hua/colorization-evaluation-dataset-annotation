# 训练集／验证集初版交付

当前执行入口为仓库根`pipeline.py`，状态事实源为`runtime/recovery5000_20261016_01/state.sqlite3`。最新运行与部署见[STATUS顶部](STATUS.md)，最新规则见[AGENTS](AGENTS.md)。下文各日期的试标数量、初期配置和“尚未启动”等陈述仅保留历史；`ACTIVE_PREPARATION.json`也不是实时进度接口。版本管理边界见[Git维护说明](../../docs/GIT_WORKFLOW.md)。

看板“停止派发，等待在途结束”会停止领取新批次，让已领取任务（含必要的原会话补试）自然结束，核对结果、保存断点后暂停。等待期间不能继续调度或续接中断会话；仍可用“安全保存”立即终止调用，真实额度耗尽也仍优先全停。暂停后可手动继续。“安全保存”本身会终止在途调用，不是等待完成。CLI等价入口为根`pipeline.py drain`。旧执行器未加载此功能时按钮禁用并显示说明，下次启动执行器后生效；不为升级中断当前调用。

当前额度查询已内置工作流看板服务，无需Codex定时任务。`python -X utf8 pipeline.py dashboard`启动看板时一并启动后台原生`agy /usage`查询，间隔10分钟，独立会话、只写quota元数据；标注暂停时仍可查询，服务退出时一起关闭，不因额度恢复自动标注。旧heartbeat `agy`已停用。依赖安装：`python -m pip install --target annotation_delivery/train_val_v1_20261015/runtime/quota_dependencies -r annotation_delivery/train_val_v1_20261015/requirements-quota.txt`。最新状态见[STATUS](STATUS.md)，下文旧数量和仅准备状态为历史。

**2026-10-16当前：** [修复与续跑说明](RECOVERY_20261016.md)、[实时看板](http://localhost:8899)。5000条重新完整校验：保留2301（回收47）、待续2699（打回203），旧100另审100通过。统一执行器与事务状态已接通，当前仅准备，0次新High标注。以下旧状态保留追溯。

最新看板调整：已移除黄／橙色荧光候选轮廓，只保留纯差分。当前同48的[无轮廓离线包核验](runtime/no_overlay_20261015_01/packets/verification.json)及[示例看板](runtime/no_overlay_20261015_01/packets/T0009/sheets/sheet_001.png)已生成；提示词与后续试跑入口同步。原41条仍可在项目19查看，但属于调整前结果；本次没有模型调用，访问全停保持。实际进度以STATUS为准。

最新规则NR_secondary_preserve_20261015_04：重点重标E1/E2，原B/C/D/F逐P编号review、默认保留；明确纠错／删除留依据，描述自然化不等于删除标签。新合并机制已实现，同48离线新包保留77条原B/C/D/F，旧48及详细23仅历史，新规则完成0。服务访问仍阻塞，未新调用。[纠正说明](runtime/secondary_review_correction_20261015_01/CORRECTION.md)。

最新提示NR_detail_20261015_03：详细覆盖、清晰L1保留、多类多对象共存、极其谨慎无缺陷，description仍为无GT比较的自然句。主人确认恢复后重跑原48条，实际23条通过并导入[新版项目18](http://localhost:8080/projects/18/data?labeling=1)，剩余25条遭High地区访问拒绝，确认连接恢复后续接仍同错，已全停。当前断点runtime/rerun48_detail_20261015_01；不重跑已通过23条，不自动继续其余336或全量。旧结果及新旧差异保留，数量变化不代表准确率。

2026-10-15，当前契约`train_val_two_stage_NR_legacy_only_v2`。标签按生成图自身可见质量，采用主人原始类别／分级；description只用自然语言，无GT比较、无“外套（L2）：…”式标题。测试集暂缓，固定人工A复用。只允许指定历史成品进入待二次池，实验AI标签全部退出；其余样本先RGB初标，再彩度差二次。主人授权384试标已实跑，48条终标已导入[Label Studio](http://localhost:8080/projects/17/data?labeling=1)，另48条仅初标；High额度耗尽，已全停并保存断点，等待主人确认恢复。

- [完整规则](RULES.md)：阶段、类别、看板、会话复用、失败回池、网络全停、断点与交付。
- [实际状态](STATUS.md)：全量盘点、首批准备和未完成项。
- [执行约束](AGENTS.md)、[配置](config.json)、[提示词](prompts/session.md)。

## 文件职责

| 路径 | 内容 |
|---|---|
| scripts/prepare.py | 盘点真实train/val、冻结GT/A与唯一历史成品；不读取实验AI标签，产生全量阶段队列及旧描述候选问题索引 |
| scripts/prepare_packets.py | 从ready队列按split/model轮换选首批任务，生成两类本地大图、空结果、匿名旧标签及首轮／续接提示 |
| scripts/verify_preparation.py | 校验源哈希、固定A范围、唯一覆盖、阶段依赖、任务包完整性和匿名映射；不调用模型 |
| scripts/pilot_runner.py | 限384试标的16槽位固定角色运行器、显式会话续接、逐样本验收／依赖／全停和断点恢复 |
| scripts/review_contract.py | 校验实际模型文件及自然语言字面格式；不作语义自动改标 |
| scripts/export_pilot.py、verify_pilot_import.py | 只导出终标预测并只读核验项目17实际导入 |
| runtime/pilot_384_20261015_01 | 384试标实际尝试、断点、48终标流式包及导入核验；额度暂停 |
| ACTIVE_PREPARATION.json | 当前契约、活动目录和状态；不得恢复01旧包 |
| data/preparation_02/inventory.jsonl | 源身份、输入哈希、唯一底稿来源、路由和未完成状态 |
| data/preparation_02/queue.jsonl | 全量阶段任务及依赖；未领取、不占会话 |
| data/preparation_02/fixed_A_final.json | train/val固定人工A直接结果，其他类别不填 |
| data/preparation_02/source_registry.json | 原池、唯一历史成品、冻结清单／CV参照和配置的哈希，不含实验AI标签 |
| data/preparation_02/legacy_format_audit.json | 指定旧文件中的显式GT比较／等级标题／缺描述／旧A候选，非语义自动判决 |
| data/preparation_02/checkpoint.json | 初始断点，0会话、0在途、0调用 |
| runtime/starter_02 | 首批8个初标＋8个二次任务，实际见索引；提示和输出模板均带v2契约 |
| runtime/docs_before_01 | 更新前六份根入口文档的原字节及哈希 |
| runtime/before_NR_v2 | 本次改版前18份源码／文档／提示原字节 |
| data/preparation_01、runtime/starter_01 | 退役旧口径，只追溯，不启动／导入 |

任务包中的prompt_first.txt用于新会话首轮，prompt_continue.txt用于明确同角色会话的后续轮。request.json供主控使用，manifest_private.json含源身份仅供主控，不能交给模型。模型只接收提示中列出的PNG、结果路径及二次任务的匿名prior_reviews.json。reviews_gemini.json仍全为null时表示尚未标注。

## 已存在底稿的选择

唯一旧AI底稿为主人指定的`LS_lcad_reviewer/exports/reviewed_1_10000_clean.json`。冻结GT过滤、人工A分流后，9,923条非A全部进二次，包括12条旧A-only及35条缺描述记录，均须按单图标准完整重审六类。旧A不交给模型，匿名旧标签空列表也不表示新标准无缺陷。

experiments真实High、成功Worker、定向重跑和诊断标签全部取消底稿资格，使用数为0，原文件只保留追溯；其样本与其余未被指定文件覆盖的非A共12,733条从RGB初标开始。任务池原模型预标注也不作完成依据。GT／人工A清单、CV代码和统计参照继续复用。

指定旧文件中的比较式描述不能靠删词修复：二次标注需先判断生成图是否真有缺陷，再决定删除／新增／改类／改级，并写成自然句。保留结构化id、severity和object，不在description中重复对象标题或等级。

## 离线重现

在仓库根目录运行；默认输出已存在时会停止，防止覆盖准备结果。需要重新准备时同时指定新的data和runtime目录。

```powershell
python -B -X utf8 annotation_delivery/train_val_v1_20261015/scripts/prepare.py --output annotation_delivery/train_val_v1_20261015/data/preparation_03
python -B -X utf8 annotation_delivery/train_val_v1_20261015/scripts/prepare_packets.py --inventory annotation_delivery/train_val_v1_20261015/data/preparation_03 --output annotation_delivery/train_val_v1_20261015/runtime/starter_03 --jobs-per-stage 8
python -B -X utf8 annotation_delivery/train_val_v1_20261015/scripts/verify_preparation.py --inventory annotation_delivery/train_val_v1_20261015/data/preparation_03 --packets annotation_delivery/train_val_v1_20261015/runtime/starter_03
```

使用本机已有Python、NumPy、OpenCV、Pillow及微软雅黑字体；没有新增依赖安装。工具会读原数据并在新输出目录写派生产物，不调用agy、不改原图、任务池、SQLite或正式exports。

## 后续

1. 主人检查已导入的48条，文件完整性不代表语义准确率。
2. 明确确认High额度恢复后，只运行`python -B -X utf8 annotation_delivery/train_val_v1_20261015/scripts/pilot_runner.py --resume`恢复同一384范围；现不执行、不预检。
3. 保留完成文件，只补实际未完成；不启动全量或自动化，不为凑会话4—8轮扩大试标。

这次不新增实验矩阵／合成控制／测试套件，不以源完整性校验替代视觉检查或准确率结论。不承诺缓存命中或节省比例；实际usage和缓存字段能取得时如实记录。
