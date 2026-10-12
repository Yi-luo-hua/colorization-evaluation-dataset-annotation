import json
import re
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
POOL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "cv_physical_pool_all.json"
ALL_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_1_10000_all.json"
AUDITS_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits"

with open(ALL_FILE, "r", encoding="utf-8") as f:
    all_anns = json.load(f)["annotations"]
all_map = {ann["human_review"]["task_id"]: ann for ann in all_anns}

with open(POOL_FILE, "r", encoding="utf-8") as f:
    pool = json.load(f)

# 加载所有 batch 的初筛 audit metrics（包含 max_local_peak, delta_c, blue_to_green 等）
audit_metrics_map = {}
for af in AUDITS_DIR.glob("audit_needs_grounding_*.json"):
    try:
        with open(af, "r", encoding="utf-8") as f:
            alist = json.load(f)
            for a in alist:
                audit_metrics_map[a["task_idx"]] = a.get("metrics", {})
    except Exception:
        pass

print(f"Loaded audit metrics for {len(audit_metrics_map)} tasks.")

# 识别已完成过视觉具象定物审查的样本（避免重复审查）
reviewed_set = set()
for ann in all_anns:
    note = ann.get("review_note", "")
    tid = ann["human_review"]["task_id"]
    # 如果已经有具体物体或者 Double Check / 看板改判
    if any(k in note for k in ["核查发现：", "原5.0满分严重漏检，核查发现：", "Double Check", "看板", "具象"]):
        reviewed_set.add(tid)

print(f"Already firmly grounded tasks: {len(reviewed_set)}")

suspicious_items = []

for item in pool:
    tid = item["task_id"]
    if tid in reviewed_set:
        continue

    ann = all_map[tid]
    defs = ann.get("defects", [])
    note = ann.get("review_note", "")
    orig_score = item["original_gpt_score"]
    
    # 提取缺陷类型列表
    d_ids = [d["id"] for d in defs]
    is_single_d1 = (len(defs) == 1 and d_ids == ["D"] and defs[0].get("severity") == "L1")
    is_single_e2 = (len(defs) == 1 and d_ids == ["E2"])
    
    metrics = audit_metrics_map.get(tid, {})
    local_peak = metrics.get("max_local_peak", 0.0)
    delta_c = metrics.get("delta_c", 0.0)
    b_to_g = metrics.get("blue_to_green", 0.0)
    r_sat = metrics.get("r_sat", 1.0)

    suspicion_score = 0.0
    reasons = []

    # 规则 1：原 5.0 满分，但仅被粗暴判定为单一 D-L1
    if orig_score >= 4.9 and is_single_d1:
        suspicion_score += 4.0
        reasons.append("原5.0满分仅判定为单一D-L1")
        if local_peak >= 0.20:
            suspicion_score += 2.0
            reasons.append(f"局部色偏峰值显著(peak={local_peak:.2f})")
        if b_to_g >= 0.15:
            suspicion_score += 1.5
            reasons.append(f"蓝绿通道突变高危(b2g={b_to_g:.2f})")

    # 规则 2：原打分较低 (< 3.2)，但仅被判定为单一 D-L1 或单一 E2
    elif orig_score < 3.2 and (is_single_d1 or is_single_e2):
        suspicion_score += 4.5
        reasons.append(f"原低分({orig_score})被大幅降级均摊为单一{d_ids[0]}")
        if local_peak >= 0.20:
            suspicion_score += 2.0
            reasons.append(f"局部色偏峰值显著(peak={local_peak:.2f})")

    # 规则 3：局部色差峰值极大 (peak >= 0.28)，但最终只有全局宏观标签
    elif local_peak >= 0.28 and not any(did in ["C", "B"] for did in d_ids):
        suspicion_score += 3.5
        reasons.append(f"局部色差峰值极高(peak={local_peak:.2f})但无局部错色/溢色标签")

    # 规则 4：反向饱和度风险 (严重褪色却标 E1 或 反之)
    elif r_sat < 0.60 and "E1" in d_ids:
        suspicion_score += 4.0
        reasons.append("物理实测欠饱和但被误标为过饱和E1")

    if suspicion_score >= 3.5:
        suspicious_items.append({
            "task_id": tid,
            "image_id": item["image_id"],
            "original_gpt_score": orig_score,
            "current_defects": defs,
            "review_note": note,
            "local_peak": local_peak,
            "delta_c": delta_c,
            "suspicion_score": suspicion_score,
            "reasons": reasons
        })

# 按可疑度从高到低严格排序
suspicious_items.sort(key=lambda x: -x["suspicion_score"])
print(f"Total highly suspicious items filtered: {len(suspicious_items)}")

# 划分审查轮次（每轮 20 张大图，每张 6 组，共 120 组）
ROUND_SIZE = 120
num_rounds = (len(suspicious_items) + ROUND_SIZE - 1) // ROUND_SIZE
print(f"Can be organized into {num_rounds} rounds of 20 sheets (120 tasks/round).")

plan_file = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "cv_physical_audit_plan.json"
with open(plan_file, "w", encoding="utf-8") as f:
    json.dump({
        "total_suspicious": len(suspicious_items),
        "round_size": ROUND_SIZE,
        "num_rounds": num_rounds,
        "items": suspicious_items
    }, f, ensure_ascii=False, indent=2)

print(f"Audit plan saved to: {plan_file.name}")
