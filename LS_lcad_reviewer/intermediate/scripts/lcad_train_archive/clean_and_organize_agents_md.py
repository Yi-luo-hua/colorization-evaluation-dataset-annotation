# -*- coding: utf-8 -*-
"""
脚本：整理与精炼 AGENTS.md
职责：
1. 清理 20 个历史批次累计 13,000+ 字符的冗余流水账（已完整归档至 archive_historical_reviews_summary.md）
2. 保持 AGENTS.md 结构紧凑、规范整洁、重点突出，包含 50 批次专项攻坚大表与完整 SOP
"""

CONTENT = """# 图像上色评价数据集标注与人机协同审核工作流规范 (AGENTS.md)

本文件是 AI 代理（洛熙）执行「图像上色质量评估（V4 标准体系）」全流程的唯一操作基准（SOP）。即使在没有任何历史对话记忆的情况下，遵循本文档可独立、零歧义地完成任意批次的处理与交付。

---

## 一、工作区架构与环境索引

* **根目录**：`d:\\学业文件\\MCL\\上色评价_数据集标注`
* **GT 彩色真值图**：`9_14_10000GT_V1\\image\\<image_id>.jpg`
* **LCAD 模型生成图**：`9_14_10000GT_V1\\model\\lcad\\<image_id>.png`
* **全量任务源文件**：`LS_lcad_reviewer\\tasks_lcad_10000.json`（共 10,000 个任务）
* **Python 执行环境**：`LS_lcad_reviewer\\.venv\\Scripts\\python`（内置 PIL、NumPy、sqlite3、Label Studio）

### 1. 目录架构与职责划分（严禁将中间产物散落至根目录）
* **正式交付目录**：`LS_lcad_reviewer\\exports\\`（交付成品 `reviewed_{start}_{end}_{timestamp}.json`，JSON Schema 严格以 `exports/reviewed_20260930_084839.json` 为唯一权威基准）
* **流式抽检包目录**：`LS_lcad_reviewer\\streams\\`（供 Label Studio 抽检的 `tasks_lcad_{start}_{end}_stream.json`）
* **精要审查报告目录**：`LS_lcad_reviewer\\reports\\`（批次精要报告与归档文档）
* **过程与中间产物目录**：`LS_lcad_reviewer\\intermediate\\`
  * 审计与定物数据：`LS_lcad_reviewer\\intermediate\\audits\\`（初筛 JSON、定物映射 JSON）
  * 高清对比看板：`LS_lcad_reviewer\\intermediate\\inspection_sheets\\`（并排三联对比图）
  * 辅助批处理脚本：`LS_lcad_reviewer\\intermediate\\scripts\\`

### 2. 核心执行工具链与脚本索引
* **CV 物理初筛与分流**：`LS_lcad_reviewer\\cv_anomaly_detector.py`
* **通用看板生成**：`LS_lcad_reviewer\\generate_inspection_sheets.py`
* **攻坚专项看板生成**：`LS_lcad_reviewer\\intermediate\\scripts\\render_remaining_batch_sheets.py`
* **批次流包通用构建**：`LS_lcad_reviewer\\build_stream_batch.py`
* **官方合规导出**：`LS_lcad_reviewer\\export_final_batch.py`
* **基准契约校验（强校验）**：`LS_lcad_reviewer\\validate_export_schema.py`
* **主人抽检增量融合**：`LS_lcad_reviewer\\merge_master_reviews.py`

### 3. 全量历史交付归档概览（1 ~ 10,000）
前期已完成全量 10,000 条任务的阶段性初审与 20 批次 Double Check 复核交付。详细改判实录与历史明细已完整迁移归档至：
👉 [历史批次审核与深度复核改判成果归档](file:///d:/学业文件/MCL/上色评价_数据集标注/LS_lcad_reviewer/reports/archive_historical_reviews_summary.md)

* **全量最终交付成品索引**：
  * **纯净交付版 (推荐交付·清空审校备注)**：`LS_lcad_reviewer/exports/reviewed_1_10000_clean.json`（9.84 MB，全量 10,000 条记录保留 `review_note: ""`，与权威基准模版 100% 吻合）
  * **完整过程版 (保留审校历史记录)**：`LS_lcad_reviewer/exports/reviewed_1_10000_all.json`（10.50 MB，包含完整人工审核与改判推导过程）
  * **基准指标状态**：10,000 条任务 100% 覆盖，0 Pending，0 伪满分，格式契约 100% 通过。

---

## 二、工作流拓扑架构（主线直出 + 旁路可选抽检）

全流程严格遵循 **“主线自动化全量审校直出成品，旁路可选抽检增量合入”** 的解耦架构。主线完成后**直接产出正式交付成品**；主人的 Label Studio 抽检属于独立旁路分支，可做可不做：

```mermaid
flowchart TD
    %% 主线主干流程 (洛熙全自动基准与交付)
    subgraph MAINLINE["🟢 主线流程：AI + CV 全量审校与成品直出 (洛熙主干)"]
        direction TB
        A["分批原始任务池 (tasks_*.json)"] --> S1["阶段一: CV 物理指标初筛与逻辑核验"]
      
        subgraph S1_BOX["CV 算法与逻辑核验引擎"]
            direction TB
            C1["底层色度检测 (饱和度比 / 色差 Delta_C / 偏色向量唯一确定)"]
            C2["色域转移与局部特征 (红脱色率 / 蓝天绿化 / 4x4局部色偏)"]
            C3["边缘溢色算子 (Canny边缘色差突变 / 溢出比 R_bleed)"]
            C4["逻辑校验 (E1/E2互斥、A熔断) + 满分(>=4.9)全量强制拦截"]
            C1 --> C2 --> C3 --> C4
        end
        S1 --> S1_BOX
      
        %% 第一级分流: 根据 CV 处理结果分流
        S1_BOX --> DECIDE_PASS{"CV 处理结果判定"}

        %% 分支 1: 审核无误
        DECIDE_PASS -->|"审核无误 (指标自洽且无报警)"| PASS["🟢 物理自洽放行 (采信原评测基准)"]

        %% 分支 2: 需要修改
        DECIDE_PASS -->|"需要修改 (命中报警/逻辑冲突/满分待验)"| DECIDE_ENTITY{"是否需明确具体视觉实体？"}

        %% 分支 2A: 不需要明确具体视觉实体
        DECIDE_ENTITY -->|"否 (纯色差/色温修正)"| CV_FIX["⚙️ CV 物理指标直接修正 (更新偏色向量/色阶)"]

        %% 分支 2B: 需要明确具体视觉实体
        DECIDE_ENTITY -->|"是 (需具体定物语义)"| S2["阶段二: 自动生成 6 组/张高清看板与视觉具象定物"]
      
        subgraph S2_BOX["AI 视觉直审与具象定物引擎"]
            direction TB
            V1["自动渲染并排对比看板 (6组/张 · GT + LCAD + 2x差分图)"]
            V2["AI 多模态视觉直审 (锁定受损部位真实物体/服饰/建筑背景)"]
            V3["具体实体定物描述 (彻底消灭抽象代词，注入精准物品名称)"]
            V1 --> V2 --> V3
        end
        S2 --> S2_BOX
      
        %% Double Check 增强分支:
        PASS -.->|"Double Check 增强 (专属看板全量二次直审)"| S2

        %% 汇聚到输出阶段
        PASS --> S3["阶段三: 结果汇聚与格式校验"]
        CV_FIX --> S3
        S2_BOX --> S3
      
        subgraph S3_BOX["正式交付输出与契约断言"]
            direction TB
            O1["生成标准流式包 (tasks_*_stream.json)"]
            O2["一键导出交付成品 (reviewed_*.json)"]
            O3["自动化基准断言 (validate_export_schema.py)"]
            O1 --> O2 --> O3
        end
        S3 --> S3_BOX
        S3_BOX --> DELIVER["🏆 正式成品就绪 (0 Pending · 100% 达标)"]
    end

    %% 旁路独立分支: 主人可选抽检
    subgraph SIDELINE["🔵 旁路分支: 主人随时按需抽检 (可选)"]
        direction TB
        M1["主人导入 streams/tasks_*_stream.json 至 Label Studio"] --> M2["仅对标记为'洛熙视觉改判'的重点任务快速抽检"]
        M2 --> M3["有异议直接修改评语并提交至 SQLite"]
        M3 --> M4["运行 merge_master_reviews.py 执行增量融合"]
        M4 --> M5["自动更新已交付的 reviewed_*.json (主人修改100%覆盖)"]
    end

    DELIVER -.->|"可选: 随时提供抽检包"| SIDELINE
```

---

## 三、批次处理执行 SOP（Step-by-Step）

执行新批次（如 $N \sim M$）时，按顺序执行以下主线步骤：

### Step 1：切片与 CV 物理指标初筛（两级分流）

从 `LS_lcad_reviewer\tasks_lcad_10000.json` 切取对应批次，加载真值图与生成图，执行色度计算：

1. **核心色度算法与阈值**：
   * **满分强制拦截**：凡 `gpt_score >= 4.9`（准满分/满分）**100% 拦截全检**，杜绝脱离 GT 的“孤立真实感”幻觉；
   * **饱和度比值**：
     $$R_{\text{sat}} = \frac{\text{mean}(S_{\text{gen}}) + 10^{-4}}{\text{mean}(S_{\text{GT}}) + 10^{-4}}$$
     - $R_{\text{sat}} < 0.25$ 或 $\text{mean}(S_{\text{gen}}) < 0.04$：疑似漏报 `A 缺色` 或 `E2-L3 严重欠饱和`；
     - $R_{\text{sat}} > 1.70$ 且 $\text{mean}(S_{\text{gen}}) > 0.35$：疑似漏报 `E1 过饱和`；
   * **色彩对立空间偏色向量与唯一方向确定**：
     - 在色彩对立空间计算偏色距离 $\Delta C = \sqrt{(\Delta a)^2 + (\Delta b)^2}$；$\Delta C > 0.12$ 触发报警；
     - **唯一偏色方向锁定**：计算符号色差 $\Delta RG = RG_{\text{gen}} - RG_{\text{gt}}$、$\Delta YB = YB_{\text{gen}} - YB_{\text{gt}}$：
       - $\Delta RG > 0, \Delta YB > 0$：严格定性为“偏暖红黄调”；
       - $\Delta RG < 0, \Delta YB < 0$：严格定性为“偏冷青蓝调”；
       - **绝对禁止使用“偏暖黄或泛青冷”等模糊二选一套话**；
   * **轮廓边缘色差溢出算子（Edge-Guided Bleed Detection）**：
     - 提取 GT 灰度图 Canny 边缘轮廓，沿轮廓进行 $5 \times 5$ 膨胀构建边缘窄带 $\Omega_{\text{edge}}$；
     - 计算边缘色差相对全局色差的溢出比率：$R_{\text{bleed}} = \frac{\text{mean}(\Delta C_{\text{edge}})}{\text{mean}(\Delta C_{\text{global}}) + 10^{-4}}$，并提取边缘色差 90 分位数 $P_{90}$；
     - **$R_{\text{bleed}} > 1.40$ 且 $P_{90} > 30.0$**：触发**疑似漏报 `B 溢色`** 报警，强制拦截送入阶段二；
   * **深度语义色度转移分析**：
     - 红色脱色率（Red Loss）$> 0.60$：拦截红色服饰/招牌褪色为纯灰白；
     - 蓝天草绿化（Blue to Green）$> 0.25$：拦截蓝天被常识性误涂为草绿（常识错色 C-L3）；
     - 局部 $4 \times 4$ 网格色偏峰值 $> 0.25$：拦截局部恶性荧光伪色；
   * **逻辑冲突检验**：
     - `gpt_score <= 2.0` 但 defects 为空者报警；
     - 同一任务同时标注矛盾的 E1（过饱和）与 E2（欠饱和）者报错；
     - 熔断项 A 出现 L1~L3 细分者报错。
2. **第一级分流（CV 初筛判定）**：
   * **审核无误（Pass）**：指标自洽且无任何报警，原评分与扣分项合理，直接标记 `review_status: "已核验"`，纯净标注“审查通过”（defects=[]），写入交付成品池；
   * **需要修改（Needs Revision）**：命中报警或逻辑冲突，转入第二级分流。
3. **第二级分流（定物需求判定）**：
   * **无需明确具体实体**：直接依据 CV 偏色向量与物理色阶修正标签与描述，写入交付成品池；
   * **需明确具体视觉实体**：收集待修改任务元数据，导出中间列表至 `LS_lcad_reviewer/intermediate/audits/audit_needs_grounding_{start}_{end}.json`，进入 Step 2。

---

### Step 2：生成看板与 AI 视觉具象实体定物（6 组/张）

1. **自动生成三联并排高清看板**：
   批量生成看板图片（每张包含 6 组卡片，每组包含 **GT + LCAD + 2x 差分热力图**），存入 `intermediate/inspection_sheets/`：
   ```bash
   # 生成待改判高危看板 (--min-suspicion 5.0，提取高危样本约 130~145 组，对应 22~24 张看板)
   .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\generate_inspection_sheets.py --audit-file LS_lcad_reviewer\\intermediate\\audits\\audit_needs_grounding_{start}_{end}.json --out-dir LS_lcad_reviewer\\intermediate\\inspection_sheets\\inspection_sheets_{start}_{end} --chunk-size 6 --min-suspicion 5.0
   ```
2. **多模态视觉直审与查阅**：
   AI 代理直接调用 `view_file` 查阅看板图片，借助 2x 差分图高亮区快速定位画面受损部位。
3. **具象实体定物写作准则**：
   * **彻底消灭抽象代词**：严禁在描述中使用“局部关键区域”、“关键主体或背景”、“局部配饰与边缘区域”等空泛占位符；
   * **具象物体精确命名**：必须明确写出具体真实物体名称（例如：“红砖墙”、“深蓝风衣外套”、“电视机屏幕”、“木质餐桌表面”、“网球拍拍面”、“网球运动员荧光黄T恤”）；
   * **标准输出格式**：`[具体物体/背景名称] + [受损表现与色偏特征] + (缺陷代号与严重度)`。
     - *错色示例*：“网球场上运动员身穿的鲜艳荧光黄绿色运动T恤被彻底错涂为纯灰白色（严重错色 C-L3）。”
     - *溢色示例*：“网球拍边框明黄色漆料越界严重渗透侵染透明网线拍面（轻度溢色 B-L1）。”
4. **产出具象定物字典（纯 JSON）**：
   保存为纯净 JSON 文件：`LS_lcad_reviewer/intermediate/audits/grounding_reviews_{start}_{end}.json`，以 `task_idx` 为键，包含 `score`、`severities`、`descriptions` 与定物 `note`。

---

### Step 3：构建流式抽检包与正式成品交付

主线流程完成 Step 1 与 Step 2 后，**直接输出最终交付成果，无需等待人工抽检**：

1. **运行通用脚本构建流式抽检包**：
   ```bash
   .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\build_stream_batch.py --start {start} --end {end}
   ```
   * 自动将 100% 核验后的结果写入 `predictions[0].result`；
   * 标注 `review_tag: "洛熙视觉改判"`（若有修改）或 `"初审核验通过"`；
   * 统一输出至 `LS_lcad_reviewer/streams/tasks_lcad_{start}_{end}_stream.json`。
2. **运行一键正式交付导出脚本**：
   ```bash
   .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\export_final_batch.py streams/tasks_lcad_{start}_{end}_stream.json
   ```
3. **review_note 双轨制规范（抽检包 vs 成品数据集）**：
   * **配套流式抽检包**：供 Label Studio 交互界面抽检使用，保留提示性前缀供快速过目；
   * **正式交付成品**：供下游模型评测使用，未修改部分统一纯净标注为 **`"审查通过"`**；修改部分直接陈述具象物体受损与改动原因，**严禁带有 `【...】` 等交互标签前缀**。
4. **正式交付成品 JSON 架构与字段规范（严格以 `exports/reviewed_20260930_084839.json` 为基准）**：

   #### （1）权威基准数据结构示例
   ```json
   {
     "meta": {
       "exported_at": "2026-09-30T00:48:39.851108+00:00",
       "total_images": 500,
       "needs_rescoring": true
     },
     "annotations": [
       {
         "image_id": "lcad/000000000009.png",
         "file_path": "lcad/000000000009.png",
         "source_dataset": "coco",
         "role": "lcad",
         "defects": [
           {
             "id": "E1",
             "name": "过饱和",
             "severity": "L2",
             "description": "餐盒的粉红与绿色、蔬菜绿色及食物暖色均过于浓艳，整体饱和度明显偏高。"
           }
         ],
         "gpt_score": 2.43,
         "labeling_model": "gpt-5.6-sol",
         "labeling_timestamp": "2026-09-20T14:56:47.366876+00:00",
         "original_gpt_score": 2.43,
         "review_status": "已核验",
         "review_note": "审查通过",
         "reviewed_score": null,
         "needs_rescoring": true,
         "human_review": {
           "task_id": 1,
           "annotation_id": 1,
           "completed_by": 1,
           "updated_at": "2026-09-28T14:21:10.161861Z"
         }
       }
     ]
   }
   ```

   #### （2）顶级 `meta` 元数据对象契约（严格限定 3 个字段，严禁增删）
   | 字段名 | 数据类型 | 取值规范与约束 |
   | :--- | :---: | :--- |
   | `exported_at` | `string` | ISO 8601 UTC 时间戳（如`"2026-09-30T00:48:39.851108+00:00"`） |
   | `total_images` | `integer` | 当前交付批次的总图像记录数（严格为整型） |
   | `needs_rescoring` | `boolean` | 固定为布尔值 `true` |

   #### （3）`annotations[*]` 任务记录契约（严格限定 14 个字段，严禁增删）
   | 序号 | 字段名 | 数据类型 | 规范说明与取值约束 |
   | :--: | :--- | :---: | :--- |
   | 1 | `image_id` | `string` | 图像相对路径，形如 `"lcad/000000000009.png"` |
   | 2 | `file_path` | `string` | 图像相对路径，与 `image_id` 保持严格一致 |
   | 3 | `source_dataset` | `string` | 来源数据集标识，固定为 `"coco"` |
   | 4 | `role` | `string` | 评测模型角色，固定为 `"lcad"` |
   | 5 | `defects` | `array` | 缺陷项列表。放行项为纯净空列表 `[]`；改判项为缺陷对象列表 |
   | 6 | `gpt_score` | `number` | 原始评分。**严格保持源数据不变，审核阶段严禁篡改** |
   | 7 | `labeling_model` | `string` | 原始打分模型标识，固定为 `"gpt-5.6-sol"` |
   | 8 | `labeling_timestamp` | `string` | 原始打分时间戳（严格继承原数据） |
   | 9 | `original_gpt_score` | `number` | 原始初始 GPT 打分（严格与 `gpt_score` 一致） |
   | 10 | `review_status` | `string` | 核验状态，必须 100% 为 `"已核验"` |
   | 11 | `review_note` | `string` | 审核评语：未修改放行项统一定格为 `"审查通过"`；修改项直接陈述受损原因 |
   | 12 | `reviewed_score` | `number \| null` | 命中缺色 A 时为 `1.0`；其余情况严格为 `null`（交下游离线重算） |
   | 13 | `needs_rescoring` | `boolean` | 命中缺色 A 时为 `false`；其余情况固定为 `true` |
   | 14 | `human_review` | `object` | 包含 `task_id`, `annotation_id`, `completed_by`, `updated_at` |

   #### （4）`defects[*]` 缺陷对象子契约（严格限定 4 个字段）
   | 字段名 | 数据类型 | 取值约束与要求 |
   | :--- | :---: | :--- |
   | `id` | `string` | 缺陷标准代号：`"A"`, `"B"`, `"C"`, `"D"`, `"E1"`, `"E2"`, `"F"` |
   | `name` | `string` | 缺陷标准中文名：`"缺色"`, `"溢色"`, `"错色"`, `"偏色"`, `"过饱和"`, `"欠饱和"`, `"视觉自然度"` |
   | `severity` | `string` | 严重级别：A 项必须为 `""`；非 A 缺陷必须且只能为 `"L1"`, `"L2"`, `"L3"` 之一 |
   | `description` | `string` | 遵循「具象实体定物」规范的精准受损陈述，消灭抽象代词 |

   #### （5）`human_review` 审计对象子契约（严格限定 4 个字段）
   | 字段名 | 数据类型 | 取值说明 |
   | :--- | :---: | :--- |
   | `task_id` | `integer` | 任务序号（整型数字，如 `1`） |
   | `annotation_id` | `integer` | 标注唯一 ID（整型数字，如 `1` 或 `900001`） |
   | `completed_by` | `integer` | 审核员 ID（通常为 `1`） |
   | `updated_at` | `string` | 审核提交 ISO 8601 时间戳 |

5. **交付成品格式契约自动化核验**：
   运行字段契约断言脚本，确保与权威基准文件 100% 镜像一致：
   ```bash
   .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\validate_export_schema.py LS_lcad_reviewer\\exports\\reviewed_{start}_{end}_{timestamp}.json
   ```
   必须输出 `[PASS] 100% Schema Compliant` 方可确认交付完成。

---

### Step 4：生成批次精要审查报告（500 组/篇）

每完成一个 500 组大批次，在 `LS_lcad_reviewer/reports/` 目录下生成一份精要审查报告：
* **命名规范**：`LS_lcad_reviewer/reports/review_report_{start}_{end}.md`
* **报告内容**：交付成果清单、分流统计、满分强检分析、具象定物典型改判案例、防错红线核验结果。

---

## 四、可选分支：主人抽检与增量打补丁（Merge SOP）

该步骤为**独立可选分支（可做可不做）**。若主人选择抽检，使用以下流程合入修改：

### 1. 主人抽检操作
1. 主人进入 Label Studio 网页端，导入 `tasks_lcad_{start}_{end}_stream.json`；
2. 筛选 `review_tag: "洛熙视觉改判"`，仅对重点样本快速过目；
3. 有异议时直接修改选项与评语并提交（数据自动实时保存在 `LS_lcad_reviewer/data/label_studio.sqlite3`）。

### 2. 运行增量融合补丁脚本 (`merge_master_reviews.py`)
```bash
# 自动寻找最新成品数据集并执行合并 (自动备份原文件为 .json.bak)
.\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\merge_master_reviews.py

# 或显式指定成品数据集路径
.\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\merge_master_reviews.py LS_lcad_reviewer\\exports\\reviewed_{start}_{end}_{timestamp}.json
```
* **绝对优先权**：主人人工修改的项目 100% 覆盖初审；
* **元数据自动更新**：自动重新计算并写入 `meta.manual_reviews_count` 与 `meta.last_master_merge_at`；
* **零副作用**：未被主人修改的任务保持原有审核结果完好无损。

---

## 五、V4 缺陷评测标准与防错红线速查

| 缺陷代号 | 缺陷名称 | 严重分级 | 核心判别规则与防错要点 |
| :---: | :---: | :---: | :--- |
| **A** | **缺色** | **未命中 / 命中** | **熔断项**。全域上色失败（纯灰阶、单色未渲染）。命中后总分直接锁定为 **1.0 分**，严禁细分 L1~L3。 |
| **B** | **溢色** | 无 / L1 / L2 / L3 | 颜色越界扩散。注意网球拍拍面、窗框等网格缝隙的填充污染。 |
| **C** | **错色** | 无 / L1 / L2 / L3 | 语义违背常理或与 GT 错配（如红苹果变绿苹果、蓝天变草绿、红球衣变灰白）。 |
| **D** | **偏色** | 无 / L1 / L2 / L3 | 全图系统性色温/色调偏移（全图泛暖黄、泛青冷灰）。**不可把暖色偏色误标为欠饱和！** |
| **E1** | **过饱和** | 无 / L1 / L2 / L3 | 浓艳刺眼、高光溢出。生成图饱和度显著高于 GT 时判定。 |
| **E2** | **欠饱和** | 无 / L1 / L2 / L3 | 严重发灰褪色、丧失活力。**仅在真正褪色泛灰时使用，GT 本身低饱和时严禁扣罚！** |
| **F** | **视觉自然度** | 无 / L1 / L2 / L3 | 整体视觉可信度评价。有违和色斑、边缘不自然时扣罚。 |

### 必须坚决遵守的五大防错红线：
1. **严禁脱离 GT 的“孤立真实感”幻觉**：看起来像自然照片但关键颜色相对 GT 严重错配或丢失，绝不可打 5.0 满分；
2. **严禁混淆色偏（D）与欠饱和（E2）**：泛黄褐、泛冷绿是色调偏移（D），发灰脱色才是欠饱和（E2）；
3. **严禁互斥标签共存**：同一主体不可同时标注 E1（过饱和）与 E2（欠饱和）；
4. **严禁低饱和真值惩罚**：阴天、夜景、黑西装等原本低饱和画面，上色图还原为低饱和是忠实表现，不可扣罚 E2；
5. **语言质量红线**：
   - **绝对禁止使用模棱两可与二选一表达**：必须依据物理色偏向量明确唯一的偏色方向；
   - **绝对禁止使用抽象代词**：必须通过多模态视觉直审明确具体的物品名称（如“大理石吧台”、“红色卫衣”）。

---

## 六、批次极简交付与审计要求

每批次执行完成后，工作区严格规范产物存储，根目录保持干净整洁，仅产出以下三项标准产物：
1. **🏆 正式交付成果**：`LS_lcad_reviewer/exports/reviewed_{start}_{end}_{timestamp}.json`（下游模型评测使用）；
2. **📦 配套流式抽检包**：`LS_lcad_reviewer/streams/tasks_lcad_{start}_{end}_stream.json`（供主人随时按需抽检）；
3. **📋 精要审查报告**：`LS_lcad_reviewer/reports/review_report_{start}_{end}.md`（独立复盘与深度分析报告）。

所有过程产物（初筛 JSON、定物映射、高清看板等）一律限制在 `LS_lcad_reviewer/intermediate/` 子目录下。

---

## 七、全量视觉大图直审全覆盖专项攻坚规划（5,944 例待具象定物任务 · 50 批次）

### 1. 专项攻坚背景与升级标准
* **背景与排查深化**：在全量 10,000 条任务中，前期已完成了 3,958 条深层视觉具象定物样本与 98 条零缺陷放行样本。
* **排查发现的盲区**：早期批次及 CV 物理修正池中，存在部分评语仍残留“场景物体轮廓边缘”、“核查发现局部缺陷”、“全图轻微偏冷青蓝调”等抽象代词或机械模板的伪定物样本。
* **升级口径**：全面升级筛选逻辑，严格以**「是否真正具备真实物体具象实体描述（彻底消灭抽象代词）」**为唯一判定红线！
* **攻坚目标**：将全量筛出的 **5,944 条** 缺乏具体实体定物的任务，严格按照 **1 批 = 20 张高清三联大图看板（120 组任务）** 的标准规格，分批全量生成看板（GT + LCAD + 2x 差分热力图），逐图开展 AI 多模态视觉直审与具象定物标注，彻底消灭所有机械模板词，达成 **10,000 条任务 100% 真正视觉大图标注覆盖率**。

---

### 2. 批次规划总览（50 个攻坚批次 · 991 张大图看板）

5,944 条任务按 Task ID 自然序严格分块，划分为 **50 个连续批次（Batch 01 ~ Batch 50）**：
* **Batch 01 ~ Batch 49**：每批严格对应 **20 张三联大图看板（120 组任务/批）**，涵盖 5,880 条任务；
  * **Batch 01 重点**：涵盖 Task #2 ~ #210，其中主人特别核验的 `lcad/000000001841.png`（Task #30）位于 **Sheet 03 第 5 组卡片**，重点核查女子肩膀青蓝溢色光晕(B-L2, F-L2)与肤色偏黄发绿(D-L2)；
* **Batch 50**：收官批次，包含 **11 张大图看板（64 组任务）**；
* **总计看板规模**：累计 **991 张高清大图看板**（GT + LCAD + 2x 差分热力图，6 组/张）。

---

### 3. 攻坚批次任务调度总表（Batch 01 ~ Batch 50 全景索引）

| 批次编号 | 任务数量 | 看板张数 | Task ID 范围 | 看板存储目录 | 审核改判产物 | 进度状态 |
| :---: | :---: | :---: | :---: | :---| :---| :---: |
| **Batch 01** | 120 | 20 | [2 ~ 210] | `intermediate/inspection_sheets/remaining_batch_01/` | `grounding_remaining_batch_01.json` | 🟢 看板已就绪·待直审 (含Task #30) |
| **Batch 02** | 120 | 20 | [213 ~ 404] | `intermediate/inspection_sheets/remaining_batch_02/` | `grounding_remaining_batch_02.json` | ⚪ 待渲染 |
| **Batch 03** | 120 | 20 | [405 ~ 945] | `intermediate/inspection_sheets/remaining_batch_03/` | `grounding_remaining_batch_03.json` | ⚪ 待渲染 |
| **Batch 04** | 120 | 20 | [947 ~ 1117] | `intermediate/inspection_sheets/remaining_batch_04/` | `grounding_remaining_batch_04.json` | ⚪ 待渲染 |
| **Batch 05** | 120 | 20 | [1118 ~ 1251] | `intermediate/inspection_sheets/remaining_batch_05/` | `grounding_remaining_batch_05.json` | ⚪ 待渲染 |
| **Batch 06** | 120 | 20 | [1252 ~ 1376] | `intermediate/inspection_sheets/remaining_batch_06/` | `grounding_remaining_batch_06.json` | ⚪ 待渲染 |
| **Batch 07** | 120 | 20 | [1377 ~ 1510] | `intermediate/inspection_sheets/remaining_batch_07/` | `grounding_remaining_batch_07.json` | ⚪ 待渲染 |
| **Batch 08** | 120 | 20 | [1513 ~ 1760] | `intermediate/inspection_sheets/remaining_batch_08/` | `grounding_remaining_batch_08.json` | ⚪ 待渲染 |
| **Batch 09** | 120 | 20 | [1761 ~ 1982] | `intermediate/inspection_sheets/remaining_batch_09/` | `grounding_remaining_batch_09.json` | ⚪ 待渲染 |
| **Batch 10** | 120 | 20 | [1984 ~ 2232] | `intermediate/inspection_sheets/remaining_batch_10/` | `grounding_remaining_batch_10.json` | ⚪ 待渲染 |
| **Batch 11** | 120 | 20 | [2233 ~ 2453] | `intermediate/inspection_sheets/remaining_batch_11/` | `grounding_remaining_batch_11.json` | ⚪ 待渲染 |
| **Batch 12** | 120 | 20 | [2454 ~ 2672] | `intermediate/inspection_sheets/remaining_batch_12/` | `grounding_remaining_batch_12.json` | ⚪ 待渲染 |
| **Batch 13** | 120 | 20 | [2673 ~ 2903] | `intermediate/inspection_sheets/remaining_batch_13/` | `grounding_remaining_batch_13.json` | ⚪ 待渲染 |
| **Batch 14** | 120 | 20 | [2906 ~ 3122] | `intermediate/inspection_sheets/remaining_batch_14/` | `grounding_remaining_batch_14.json` | ⚪ 待渲染 |
| **Batch 15** | 120 | 20 | [3124 ~ 3350] | `intermediate/inspection_sheets/remaining_batch_15/` | `grounding_remaining_batch_15.json` | ⚪ 待渲染 |
| **Batch 16** | 120 | 20 | [3351 ~ 3578] | `intermediate/inspection_sheets/remaining_batch_16/` | `grounding_remaining_batch_16.json` | ⚪ 待渲染 |
| **Batch 17** | 120 | 20 | [3580 ~ 3794] | `intermediate/inspection_sheets/remaining_batch_17/` | `grounding_remaining_batch_17.json` | ⚪ 待渲染 |
| **Batch 18** | 120 | 20 | [3796 ~ 4004] | `intermediate/inspection_sheets/remaining_batch_18/` | `grounding_remaining_batch_18.json` | ⚪ 待渲染 |
| **Batch 19** | 120 | 20 | [4007 ~ 4238] | `intermediate/inspection_sheets/remaining_batch_19/` | `grounding_remaining_batch_19.json` | ⚪ 待渲染 |
| **Batch 20** | 120 | 20 | [4240 ~ 4474] | `intermediate/inspection_sheets/remaining_batch_20/` | `grounding_remaining_batch_20.json` | ⚪ 待渲染 |
| **Batch 21** | 120 | 20 | [4475 ~ 4689] | `intermediate/inspection_sheets/remaining_batch_21/` | `grounding_remaining_batch_21.json` | ⚪ 待渲染 |
| **Batch 22** | 120 | 20 | [4690 ~ 4905] | `intermediate/inspection_sheets/remaining_batch_22/` | `grounding_remaining_batch_22.json` | ⚪ 待渲染 |
| **Batch 23** | 120 | 20 | [4908 ~ 5099] | `intermediate/inspection_sheets/remaining_batch_23/` | `grounding_remaining_batch_23.json` | ⚪ 待渲染 |
| **Batch 24** | 120 | 20 | [5102 ~ 5283] | `intermediate/inspection_sheets/remaining_batch_24/` | `grounding_remaining_batch_24.json` | ⚪ 待渲染 |
| **Batch 25** | 120 | 20 | [5284 ~ 5462] | `intermediate/inspection_sheets/remaining_batch_25/` | `grounding_remaining_batch_25.json` | ⚪ 待渲染 |
| **Batch 26** | 120 | 20 | [5463 ~ 5625] | `intermediate/inspection_sheets/remaining_batch_26/` | `grounding_remaining_batch_26.json` | ⚪ 待渲染 |
| **Batch 27** | 120 | 20 | [5627 ~ 5792] | `intermediate/inspection_sheets/remaining_batch_27/` | `grounding_remaining_batch_27.json` | ⚪ 待渲染 |
| **Batch 28** | 120 | 20 | [5793 ~ 5961] | `intermediate/inspection_sheets/remaining_batch_28/` | `grounding_remaining_batch_28.json` | ⚪ 待渲染 |
| **Batch 29** | 120 | 20 | [5962 ~ 6138] | `intermediate/inspection_sheets/remaining_batch_29/` | `grounding_remaining_batch_29.json` | ⚪ 待渲染 |
| **Batch 30** | 120 | 20 | [6139 ~ 6323] | `intermediate/inspection_sheets/remaining_batch_30/` | `grounding_remaining_batch_30.json` | ⚪ 待渲染 |
| **Batch 31** | 120 | 20 | [6325 ~ 6496] | `intermediate/inspection_sheets/remaining_batch_31/` | `grounding_remaining_batch_31.json` | ⚪ 待渲染 |
| **Batch 32** | 120 | 20 | [6498 ~ 6667] | `intermediate/inspection_sheets/remaining_batch_32/` | `grounding_remaining_batch_32.json` | ⚪ 待渲染 |
| **Batch 33** | 120 | 20 | [6668 ~ 6841] | `intermediate/inspection_sheets/remaining_batch_33/` | `grounding_remaining_batch_33.json` | ⚪ 待渲染 |
| **Batch 34** | 120 | 20 | [6842 ~ 7013] | `intermediate/inspection_sheets/remaining_batch_34/` | `grounding_remaining_batch_34.json` | ⚪ 待渲染 |
| **Batch 35** | 120 | 20 | [7015 ~ 7200] | `intermediate/inspection_sheets/remaining_batch_35/` | `grounding_remaining_batch_35.json` | ⚪ 待渲染 |
| **Batch 36** | 120 | 20 | [7202 ~ 7381] | `intermediate/inspection_sheets/remaining_batch_36/` | `grounding_remaining_batch_36.json` | ⚪ 待渲染 |
| **Batch 37** | 120 | 20 | [7382 ~ 7564] | `intermediate/inspection_sheets/remaining_batch_37/` | `grounding_remaining_batch_37.json` | ⚪ 待渲染 |
| **Batch 38** | 120 | 20 | [7565 ~ 7748] | `intermediate/inspection_sheets/remaining_batch_38/` | `grounding_remaining_batch_38.json` | ⚪ 待渲染 |
| **Batch 39** | 120 | 20 | [7749 ~ 7943] | `intermediate/inspection_sheets/remaining_batch_39/` | `grounding_remaining_batch_39.json` | ⚪ 待渲染 |
| **Batch 40** | 120 | 20 | [7944 ~ 8137] | `intermediate/inspection_sheets/remaining_batch_40/` | `grounding_remaining_batch_40.json` | ⚪ 待渲染 |
| **Batch 41** | 120 | 20 | [8139 ~ 8326] | `intermediate/inspection_sheets/remaining_batch_41/` | `grounding_remaining_batch_41.json` | ⚪ 待渲染 |
| **Batch 42** | 120 | 20 | [8328 ~ 8524] | `intermediate/inspection_sheets/remaining_batch_42/` | `grounding_remaining_batch_42.json` | ⚪ 待渲染 |
| **Batch 43** | 120 | 20 | [8525 ~ 8714] | `intermediate/inspection_sheets/remaining_batch_43/` | `grounding_remaining_batch_43.json` | ⚪ 待渲染 |
| **Batch 44** | 120 | 20 | [8717 ~ 8901] | `intermediate/inspection_sheets/remaining_batch_44/` | `grounding_remaining_batch_44.json` | ⚪ 待渲染 |
| **Batch 45** | 120 | 20 | [8903 ~ 9088] | `intermediate/inspection_sheets/remaining_batch_45/` | `grounding_remaining_batch_45.json` | ⚪ 待渲染 |
| **Batch 46** | 120 | 20 | [9090 ~ 9276] | `intermediate/inspection_sheets/remaining_batch_46/` | `grounding_remaining_batch_46.json` | ⚪ 待渲染 |
| **Batch 47** | 120 | 20 | [9277 ~ 9473] | `intermediate/inspection_sheets/remaining_batch_47/` | `grounding_remaining_batch_47.json` | ⚪ 待渲染 |
| **Batch 48** | 120 | 20 | [9474 ~ 9685] | `intermediate/inspection_sheets/remaining_batch_48/` | `grounding_remaining_batch_48.json` | ⚪ 待渲染 |
| **Batch 49** | 120 | 20 | [9689 ~ 9887] | `intermediate/inspection_sheets/remaining_batch_49/` | `grounding_remaining_batch_49.json` | ⚪ 待渲染 |
| **Batch 50** | 64 | 11 | [9888 ~ 9993] | `intermediate/inspection_sheets/remaining_batch_50/` | `grounding_remaining_batch_50.json` | ⚪ 待渲染 |
| **合计** | **5,944** | **991** | **[2 ~ 10000]** | — | — | **总进度: 0/50 完成** |

---

### 4. 自动化渲染与执行工具链

* **全量规划元数据**：`LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json`
* **一键渲染脚本**：`LS_lcad_reviewer/intermediate/scripts/render_remaining_batch_sheets.py`
  ```bash
  # 渲染指定批次 (例如渲染 Batch 01，生成 20 张高清三联大图看板)
  .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\intermediate\\scripts\\render_remaining_batch_sheets.py --batch 1

  # 渲染全量 50 个批次全部 991 张看板
  .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\intermediate\\scripts\\render_remaining_batch_sheets.py --all
  ```
* **单批审查定物落地与同步流程（SOP）**：
  1. 调用 `view_file` 查阅对应批次目录（如 `remaining_batch_01/sheet_01.jpg` ~ `sheet_20.jpg`）；
  2. 针对 2x 差分热力图高亮区，消灭抽象代词，锁定真实物体名称（如服饰、车辆、建筑、特定家具等），判定受损表现与缺陷级别（C-L1~L3, D-L1~L2, E1/E2, B 等）；
  3. 保存定物 JSON 至 `LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_{batch_no:02d}.json`；
  4. 执行增量合入，同步更新正式交付文件 `exports/reviewed_1_10000_all.json` 与 `exports/reviewed_1_10000_clean.json`；
  5. 运行 `validate_export_schema.py` 确保 100% 格式契约合规。
"""

if __name__ == '__main__':
    with open('AGENTS.md', 'w', encoding='utf-8') as f:
        f.write(CONTENT.strip() + '\n')
    print("Successfully organized and cleaned AGENTS.md!")
