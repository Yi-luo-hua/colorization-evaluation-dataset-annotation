# 上色评价工作流：当前执行规范

称呼用户主人，日常交流句尾可加喵；JSON标注不加入寒暄。主人最新要求优先：速度第一，允许微量不完美，快速轻量迭代，减少防御性假设。

## 默认流程

全量GT CV筛查 → 候选GT六组看板确认 → 不可信GT及全部模型对应样本剔除 → 保留样本CV/六组看板视觉标注 → 实验候选。GT筛选入口gt_quality_gate.py与gt_quality_screen_config.json；标注入口workflow.py与config.json。过程产物只放LS_lcad_reviewer/intermediate/experiments。

- 每张六行三列：GT、生成图、双向彩度差，尾张可少于六组。
- 看板/视觉请求/结果只用批次匿名S编号。原图ID、路径、原标签和评分留在内部manifest，不提供给视觉模型。
- fast_single_pass为默认：只读六组看板，一次完成。不查单张原图，不读源码/任务池/内部manifest，不补图，不反复验证，不写长篇报告，不等待人工补图或逐项确认。
- 标注明确可见的主要缺陷，跳过难辨的小细节，不穷举小物体。证据一句话即可。只有主要判断也无法成立才用uncertain，默认needs_crops=[]。
- 非A允许临时近似分级：L1轻微局部、L2明显改变物体主要颜色、L3强烈且影响主要主体/大面积。未经校准的等级不称为人工真值。

## 标签边界

|代号|定义|
|---|---|
|A|全图颜色结构失效，灰阶/单色上色失败。唯一缺陷，severity为空字符串，分数规则1.0。GT本身低彩度不罚。|
|B|看得到具体物体颜色越界侵染，模糊小边缘不追查。|
|C|具体物体相对GT错配，即使颜色本身符合常识。|
|D|多个物体/背景共同偏移，不把单个大物体换色直接当全图偏色。|
|E1/E2|具体物体相对GT过艳/褪色，不同物体可并存。|
|F|看板明确可见的颜色常识/材质/光照违和，不因有其他缺陷自动追加。|

主人已明确C/E2边界：主要褪色为浅灰白、没有明显换色相时优先E2；明显换色相才标C。同一物体不因单纯褪色重复追加C。后续批次执行此规则，旧实验结果不回写。

主人最新GT规则：默认信任，拿不准仍使用GT。仅确认黑白且无有效物体颜色，或明显异常整体色偏且跨物体共同污染、正常场景光照不能解释时，判不可信。自然低饱和、白灰物体、阴天/夜景/夕阳、舞台彩灯、雪景、水下环境或单色物体主导不单独触发；仍有明确颜色不能当黑白。不按比例凑排除数量，低彩度数值仅候选。

主人最新决定：不可信GT直接弃用，不做B/F回退，也不做无参考标注。全量扫描train/val/test，CV候选由Gemini自读匿名六组GT看板、直接写GT_decisions.json；黑白或异常整体色偏确认后，同GT全部模型样本从后续任务与交付中剔除。失败待定候选暂不进入标注，不冒称已确认低质量。原图/源任务池/正式交付保持，另存过滤实验任务池和excluded_GT.json。配置exclude_manifest接入当前冻结清单，prepare在生成图CV前跳过，保留原任务序号。

标注阶段发现漏筛坏GT时，compact写`{"exclude_GT":"black_and_white"}`或`{"exclude_GT":"abnormal_global_cast","GT_evidence":"一句场景依据"}`，不标生成图、不用[]表示弃用。程序将同GT全部样本从候选JSON/抽检包剔除，保留独立理由记录；正式字段不扩展。旧BF_only/NR格式只兼容历史读取，不用于新标注。

彩度差ΔC*=C*_生成−C*_GT，正红负蓝；黑色也可能等彩度错色，红蓝不自动等于E1/E2。CV只提供候选，不凭数字写最终视觉结论，不使用旧GPT分数作为放行门槛。

## 模型调用与后处理

主人已授权直接调用本机agy的Gemini 3.8 Flash系列，由本对话控制迭代，无需就已授权调用重复确认。标注模型默认gemini-3.8-flash-high；其他档位实验需记录实际模型。agy_runner.py一次批次调用，内嵌精简元数据；模型自行读本地看板并直接修改指定reviews_gemini.json，只回复文件已保存，不在对话里返回标注JSON。程序读取结果文件后处理，不从模型回复解析标注内容。

默认compact文件：S编号映射中的null代表未看，[]代表保留样本看过且无主要缺陷；缺陷填id/severity/object/description。保留样本检查七类，不可信GT直接exclude_GT弃用；程序补对应元数据与完成字段，不猜颜色或位置，保留Gemini写入的原文件。Medium保留速度候选，不替换默认。

新prepare批次默认run_sheet_workers.py --batch <新prepare目录>：最多十六个agy独立进程/会话同时运行，每任务两张六组看板（最多12例），每个任务单次完成。每个parts/job_*只暴露自己的S编号和看板，Gemini直接写各自reviews_gemini.json；程序合并到reviews_merged.json并检查全量覆盖后导出实验候选。已有parts的运行不覆盖。并发度/看板数由config.json的visual_harness.parallel_scheduler配置，可用--workers/--sheets-per-job覆盖；旧已prepare批次保留冻结配置。实测决策见docs/EXPERIMENTS.md，不宣称并发提速提高标签准确率，失败不冒称全批完成。

多个已prepare批次可一起传给--batch，并指定--queue-run-id。--workers是整个队列的总并发上限；任一任务完成，空位立即启动后续任务，包括后续批次。每批自身完成就独立合并/导出，不等待其他批次；某批失败也继续其余批次。全部成功后，队列目录exports/自动汇总一个候选JSON及抽检流包，逐批provenance保留。所有任务保持独立会话和结果文件。

必要的样本对应、完整覆盖、A约束和JSON结构检查由程序完成，模型不要再自行写验证脚本。保留原评分/时间戳；candidate和provenance留在实验run，不自动覆盖正式exports/SQLite。外部AI审核员completed_by=0，不冒充真人。

## 开发与历史资料

文档分工：根README.md为启动导航；[STATUS](docs/STATUS.md)为当前状态；[DESIGN](docs/DESIGN.md)为活动算法/契约；[PLAN](docs/PLAN.md)为待执行计划；[EXPERIMENTS](docs/EXPERIMENTS.md)为历史决策/报告索引。计划不当作已实现规则，历史阶段默认值不覆盖当前config。只对改动运行必要检查，不扩大测试或反复验证。默认局部补图预算0；可选非fast自动局部看板由程序生成，不依赖人工。

原完整SOP保存在docs/archive/AGENTS_full_sop_20261012.md，仅供历史追溯，不作为新批次的强制门槛，也不需要视觉模型阅读。原数据、正式交付和历史运行保持原路径。
