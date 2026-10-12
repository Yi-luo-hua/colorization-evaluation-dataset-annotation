import sys
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AGENTS_FILE = WORKSPACE_ROOT / "AGENTS.md"

with open(AGENTS_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines currently: {len(lines)}")

# Find the end of line 470
# Line 470 was: "校验通过并输出 `[PASS] 100% Schema Compliant` 即代表该成品文件 100% 符合官方工业级交付标准。\n"
cut_idx = None
for idx, line in enumerate(lines[:500]):
    if "校验通过并输出 `[PASS] 100% Schema Compliant`" in line:
        cut_idx = idx + 1
        break

if cut_idx is None:
    print("Error: cut_idx not found!")
    sys.exit(1)

print(f"Found first cut point at line index: {cut_idx} (line {cut_idx + 1})")

clean_head = lines[:cut_idx]

section_seven = """

---

## 七、全量视觉大图直审全覆盖专项攻坚规划（4,068 例未上大图任务 · 34 批次）

### 1. 专项攻坚背景与目标

* **背景**：在全量 10,000 条任务中，前期通过批次高危初审看板（`inspection_sheets_{start}_{end}`）、自洽放行专属看板（`inspection_sheets_*_pass`）、Deep Fix（Part 1~5）及 CV 物理池审计（Round 1~4）等，累计已有 **5,932 条任务**（占比 59.32%）经过了三联高清看板（6 组/张）的逐图像素级直审与具象实体定物。
* **现状盲区**：剩余 **4,068 条任务**（占比 40.68%）在前期分流中因 `suspicion < 5.0` 归入分支 2A（中轻度 CV 物理指标修正），主要依赖实测色偏向量生成了模板化公式评语（如“原5.0满分严重漏检，核查发现：画面色彩偏暖红黄调(D-L1)；局部色彩欠饱和褪色(E2-L1)”），其中 99.0% 尚未具象定物到真实物体实体（如衣物、车辆、家具、特定背景）。
* **攻坚目标**：将这 4,068 条未上大图的任务，按照 **1 批 = 20 张高清三联大图看板（120 组任务）** 的标准规格，全面渲染高清大图看板（GT + LCAD + 2x 差分热力图），逐图开展 AI 多模态视觉直审与具象定物标注，彻底清洗公式化模板评语，达成 **10,000 条任务 100% 视觉大图标注覆盖率**。

---

### 2. 批次规划总览（34 个攻坚批次 · 678 张大图看板）

4,068 条任务按 Task ID 自然序严格分块，划分为 **34 个连续批次（Batch 01 ~ Batch 34）**：
* **Batch 01 ~ Batch 33**：每批恰好 20 张大图看板（120 组任务/批，共 33 × 20 = 660 张看板，涵盖 3,960 条任务）；
* **Batch 34**：收官批次，18 张大图看板（108 组任务）；
* **总计看板规模**：**678 张高清大图看板**（6 组/张），覆盖全部 4,068 条任务。

---

### 3. 攻坚批次任务调度总表（Batch 01 ~ Batch 34）

| 批次编号 | 任务数量 | 看板张数 | Task ID 范围 | 看板存储目录 | 审核改判产物 | 进度状态 |
| :---: | :---: | :---: | :---: | :---| :---| :---: |
| **Batch 01** | 120 | 20 | [9 ~ 773] | `intermediate/inspection_sheets/remaining_batch_01/` | `grounding_remaining_batch_01.json` | 🟢 看板已就绪·待直审 |
| **Batch 02** | 120 | 20 | [778 ~ 1596] | `intermediate/inspection_sheets/remaining_batch_02/` | `grounding_remaining_batch_02.json` | ⚪ 待渲染 |
| **Batch 03** | 120 | 20 | [1597 ~ 1828] | `intermediate/inspection_sheets/remaining_batch_03/` | `grounding_remaining_batch_03.json` | ⚪ 待渲染 |
| **Batch 04** | 120 | 20 | [1830 ~ 2560] | `intermediate/inspection_sheets/remaining_batch_04/` | `grounding_remaining_batch_04.json` | ⚪ 待渲染 |
| **Batch 05** | 120 | 20 | [2561 ~ 2814] | `intermediate/inspection_sheets/remaining_batch_05/` | `grounding_remaining_batch_05.json` | ⚪ 待渲染 |
| **Batch 06** | 120 | 20 | [2815 ~ 3544] | `intermediate/inspection_sheets/remaining_batch_06/` | `grounding_remaining_batch_06.json` | ⚪ 待渲染 |
| **Batch 07** | 120 | 20 | [3546 ~ 3772] | `intermediate/inspection_sheets/remaining_batch_07/` | `grounding_remaining_batch_07.json` | ⚪ 待渲染 |
| **Batch 08** | 120 | 20 | [3773 ~ 4025] | `intermediate/inspection_sheets/remaining_batch_08/` | `grounding_remaining_batch_08.json` | ⚪ 待渲染 |
| **Batch 09** | 120 | 20 | [4026 ~ 4244] | `intermediate/inspection_sheets/remaining_batch_09/` | `grounding_remaining_batch_09.json` | ⚪ 待渲染 |
| **Batch 10** | 120 | 20 | [4245 ~ 4501] | `intermediate/inspection_sheets/remaining_batch_10/` | `grounding_remaining_batch_10.json` | ⚪ 待渲染 |
| **Batch 11** | 120 | 20 | [4503 ~ 4715] | `intermediate/inspection_sheets/remaining_batch_11/` | `grounding_remaining_batch_11.json` | ⚪ 待渲染 |
| **Batch 12** | 120 | 20 | [4716 ~ 4925] | `intermediate/inspection_sheets/remaining_batch_12/` | `grounding_remaining_batch_12.json` | ⚪ 待渲染 |
| **Batch 13** | 120 | 20 | [4926 ~ 5139] | `intermediate/inspection_sheets/remaining_batch_13/` | `grounding_remaining_batch_13.json` | ⚪ 待渲染 |
| **Batch 14** | 120 | 20 | [5141 ~ 5352] | `intermediate/inspection_sheets/remaining_batch_14/` | `grounding_remaining_batch_14.json` | ⚪ 待渲染 |
| **Batch 15** | 120 | 20 | [5353 ~ 5590] | `intermediate/inspection_sheets/remaining_batch_15/` | `grounding_remaining_batch_15.json` | ⚪ 待渲染 |
| **Batch 16** | 120 | 20 | [5591 ~ 5819] | `intermediate/inspection_sheets/remaining_batch_16/` | `grounding_remaining_batch_16.json` | ⚪ 待渲染 |
| **Batch 17** | 120 | 20 | [5821 ~ 6075] | `intermediate/inspection_sheets/remaining_batch_17/` | `grounding_remaining_batch_17.json` | ⚪ 待渲染 |
| **Batch 18** | 120 | 20 | [6077 ~ 6314] | `intermediate/inspection_sheets/remaining_batch_18/` | `grounding_remaining_batch_18.json` | ⚪ 待渲染 |
| **Batch 19** | 120 | 20 | [6315 ~ 6533] | `intermediate/inspection_sheets/remaining_batch_19/` | `grounding_remaining_batch_19.json` | ⚪ 待渲染 |
| **Batch 20** | 120 | 20 | [6534 ~ 6766] | `intermediate/inspection_sheets/remaining_batch_20/` | `grounding_remaining_batch_20.json` | ⚪ 待渲染 |
| **Batch 21** | 120 | 20 | [6768 ~ 6984] | `intermediate/inspection_sheets/remaining_batch_21/` | `grounding_remaining_batch_21.json` | ⚪ 待渲染 |
| **Batch 22** | 120 | 20 | [6985 ~ 7217] | `intermediate/inspection_sheets/remaining_batch_22/` | `grounding_remaining_batch_22.json` | ⚪ 待渲染 |
| **Batch 23** | 120 | 20 | [7218 ~ 7438] | `intermediate/inspection_sheets/remaining_batch_23/` | `grounding_remaining_batch_23.json` | ⚪ 待渲染 |
| **Batch 24** | 120 | 20 | [7440 ~ 7651] | `intermediate/inspection_sheets/remaining_batch_24/` | `grounding_remaining_batch_24.json` | ⚪ 待渲染 |
| **Batch 25** | 120 | 20 | [7654 ~ 7899] | `intermediate/inspection_sheets/remaining_batch_25/` | `grounding_remaining_batch_25.json` | ⚪ 待渲染 |
| **Batch 26** | 120 | 20 | [7900 ~ 8143] | `intermediate/inspection_sheets/remaining_batch_26/` | `grounding_remaining_batch_26.json` | ⚪ 待渲染 |
| **Batch 27** | 120 | 20 | [8144 ~ 8382] | `intermediate/inspection_sheets/remaining_batch_27/` | `grounding_remaining_batch_27.json` | ⚪ 待渲染 |
| **Batch 28** | 120 | 20 | [8386 ~ 8604] | `intermediate/inspection_sheets/remaining_batch_28/` | `grounding_remaining_batch_28.json` | ⚪ 待渲染 |
| **Batch 29** | 120 | 20 | [8605 ~ 8826] | `intermediate/inspection_sheets/remaining_batch_29/` | `grounding_remaining_batch_29.json` | ⚪ 待渲染 |
| **Batch 30** | 120 | 20 | [8829 ~ 9079] | `intermediate/inspection_sheets/remaining_batch_30/` | `grounding_remaining_batch_30.json` | ⚪ 待渲染 |
| **Batch 31** | 120 | 20 | [9082 ~ 9315] | `intermediate/inspection_sheets/remaining_batch_31/` | `grounding_remaining_batch_31.json` | ⚪ 待渲染 |
| **Batch 32** | 120 | 20 | [9316 ~ 9554] | `intermediate/inspection_sheets/remaining_batch_32/` | `grounding_remaining_batch_32.json` | ⚪ 待渲染 |
| **Batch 33** | 120 | 20 | [9557 ~ 9796] | `intermediate/inspection_sheets/remaining_batch_33/` | `grounding_remaining_batch_33.json` | ⚪ 待渲染 |
| **Batch 34** | 108 | 18 | [9797 ~ 9993] | `intermediate/inspection_sheets/remaining_batch_34/` | `grounding_remaining_batch_34.json` | ⚪ 待渲染 |
| **合计** | **4,068** | **678** | **[9 ~ 9993]** | — | — | **总进度: 0/34 完成** |

---

### 4. 自动化渲染与执行工具链

* **全量规划元数据**：`LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_35_batches.json`
* **一键渲染脚本**：`LS_lcad_reviewer/intermediate/scripts/render_remaining_batch_sheets.py`
  ```bash
  # 渲染指定批次 (例如渲染 Batch 01，生成 20 张高清三联大图看板)
  .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\intermediate\\scripts\\render_remaining_batch_sheets.py --batch 1

  # 渲染全量 34 个批次全部 678 张看板
  .\\LS_lcad_reviewer\\.venv\\Scripts\\python LS_lcad_reviewer\\intermediate\\scripts\\render_remaining_batch_sheets.py --all
  ```
* **单批审查定物落地与同步流程（SOP）**：
  1. 调用 `view_file` 查阅对应批次目录（如 `remaining_batch_01/sheet_01.jpg` ~ `sheet_20.jpg`）；
  2. 针对 2x 差分热力图高亮区，消灭抽象代词，锁定真实物体名称（如服饰、车辆、建筑、特定家具等），判定受损表现与缺陷级别（C-L1~L3, D-L1~L2, E1/E2, B 等）；
  3. 保存定物 JSON 至 `LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_{batch_no:02d}.json`；
  4. 执行增量合入，同步更新正式交付文件 `exports/reviewed_1_10000_all.json` 与 `exports/reviewed_1_10000_clean.json`；
  5. 运行 `validate_export_schema.py` 确保 100% 格式契约合规。
"""

new_content = "".join(clean_head) + section_seven

with open(AGENTS_FILE, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Successfully updated AGENTS.md! New line count: {len(new_content.splitlines())}")
