import sys
import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
AGENTS_FILE = WORKSPACE_ROOT / "AGENTS.md"
PLAN_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "remaining_visual_audit_plan_50_batches.json"

with open(PLAN_FILE, "r", encoding="utf-8") as f:
    plan = json.load(f)

batches = plan["batches"]
total_tasks = plan["total_remaining_tasks"]
total_sheets = plan["total_sheets"]

with open(AGENTS_FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

cut_idx = None
for idx, line in enumerate(lines):
    if "## 七、全量视觉大图直审全覆盖专项攻坚规划" in line:
        cut_idx = idx - 1  # Before the ---
        break

if cut_idx is None:
    print("Error: section 7 marker not found!")
    sys.exit(1)

clean_head = lines[:cut_idx]

# Build table rows
table_rows = []
for b in batches:
    bno = b["batch_no"]
    tcnt = b["task_count"]
    scnt = b["sheet_count"]
    trange = f"[{b['task_id_range'][0]} ~ {b['task_id_range'][1]}]"
    dir_name = f"`intermediate/inspection_sheets/remaining_batch_{bno:02d}/`"
    out_name = f"`grounding_remaining_batch_{bno:02d}.json`"
    status = "🟢 看板已就绪·待直审 (含Task #30)" if bno == 1 else "⚪ 待渲染"
    table_rows.append(f"| **Batch {bno:02d}** | {tcnt} | {scnt} | {trange} | {dir_name} | {out_name} | {status} |")

table_content = "\n".join(table_rows)

section_seven = f"""
---

## 七、全量视觉大图直审全覆盖专项攻坚规划（{total_tasks:,} 例待具象定物任务 · 50 批次）

### 1. 专项攻坚背景与升级标准

* **背景与排查深化**：在全量 10,000 条任务中，前期已完成了 3,958 条深层视觉具象定物样本与 98 条零缺陷放行样本。
* **暴露出的系统性盲区**：通过对典型样本（如 `lcad/000000001841.png`，Task #30）的深度溯源核查，发现早期批次及 CV 物理修正池中，存在大量虽然生成过粗筛看板或经过了公式修正、但**实际评语仍残留了“场景物体轮廓边缘”、“核查发现局部缺陷”、“全图轻微偏冷青蓝调”等抽象代词或机械模板**的伪定物样本。
* **升级口径**：全面升级筛选逻辑，不再仅按“文件名是否生成过”粗筛，而是严格以**「是否真正具备真实物体具象实体描述（彻底消灭抽象代词）」**为唯一判定红线！
* **攻坚目标**：将全量筛出的 **{total_tasks:,} 条** 缺乏具体实体定物的任务，严格按照 **1 批 = 20 张高清三联大图看板（120 组任务）** 的标准规格，分批全量生成看板（GT + LCAD + 2x 差分热力图），逐图开展 AI 多模态视觉直审与具象定物标注，彻底消灭所有机械模板词，达成 **10,000 条任务 100% 真正视觉大图标注覆盖率**。

---

### 2. 批次规划总览（50 个攻坚批次 · {total_sheets} 张大图看板）

{total_tasks:,} 条任务按 Task ID 自然序严格分块，划分为 **50 个连续批次（Batch 01 ~ Batch 50）**：
* **Batch 01 ~ Batch 49**：每批严格对应 **20 张三联大图看板（120 组任务/批）**，涵盖 5,880 条任务；
  * **Batch 01 重点**：涵盖 Task #2 ~ #210，其中主人特别核验的 `lcad/000000001841.png`（Task #30）位于 **Sheet 03 第 5 组卡片**，重点核查女子肩膀刺目青蓝溢色光晕(B-L2, F-L2)与肤色严重偏黄发绿(D-L2)；
* **Batch 50**：收官批次，包含 **11 张大图看板（64 组任务）**；
* **总计看板规模**：累计 **{total_sheets} 张高清大图看板**（GT + LCAD + 2x 差分热力图，6 组/张）。

---

### 3. 攻坚批次任务调度总表（Batch 01 ~ Batch 50 全景索引）

| 批次编号 | 任务数量 | 看板张数 | Task ID 范围 | 看板存储目录 | 审核改判产物 | 进度状态 |
| :---: | :---: | :---: | :---: | :---| :---| :---: |
{table_content}
| **合计** | **{total_tasks:,}** | **{total_sheets}** | **[2 ~ 10000]** | — | — | **总进度: 0/50 完成** |

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
  3. 保存定物 JSON 至 `LS_lcad_reviewer/intermediate/audits/grounding_remaining_batch_{{batch_no:02d}}.json`；
  4. 执行增量合入，同步更新正式交付文件 `exports/reviewed_1_10000_all.json` 与 `exports/reviewed_1_10000_clean.json`；
  5. 运行 `validate_export_schema.py` 确保 100% 格式契约合规。
"""

new_content = "".join(clean_head).rstrip() + "\n" + section_seven

with open(AGENTS_FILE, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Successfully updated AGENTS.md with 50-batch plan! New line count: {len(new_content.splitlines())}")
