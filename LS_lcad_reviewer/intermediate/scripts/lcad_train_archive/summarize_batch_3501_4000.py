import json
from pathlib import Path

FILE_PATH = Path("LS_lcad_reviewer/exports/reviewed_3501_4000_20260930_114314.json")
STREAM_PATH = Path("LS_lcad_reviewer/streams/tasks_lcad_3501_4000_stream.json")
AUDIT_PATH = Path("LS_lcad_reviewer/intermediate/audits/audit_needs_grounding_3501_4000.json")

with open(FILE_PATH, "r", encoding="utf-8") as f:
    export_data = json.load(f)

with open(STREAM_PATH, "r", encoding="utf-8") as f:
    stream_tasks = json.load(f)

with open(AUDIT_PATH, "r", encoding="utf-8") as f:
    audits = json.load(f)

anns = export_data["annotations"]
total = len(anns)

# 统计原分数分布
orig_5_count = sum(1 for a in anns if a["original_gpt_score"] >= 4.9)
orig_low_count = sum(1 for a in anns if a["original_gpt_score"] <= 2.0)
orig_mid_count = total - orig_5_count - orig_low_count

# 统计改判与放行
# 在 stream 中，review_tag: "洛熙视觉改判" vs "洛熙物理修正" vs "初审核验通过"
stream_tags = {t["data"]["image_id"]: t["data"].get("review_tag") for t in stream_tasks}
grounded_count = sum(1 for a in anns if stream_tags.get(a["image_id"]) == "洛熙视觉改判")
cv_refined_count = sum(1 for a in anns if stream_tags.get(a["image_id"]) == "洛熙物理修正")
pass_count = sum(1 for a in anns if stream_tags.get(a["image_id"]) == "初审核验通过")

# 统计缺陷项频次
defect_counts = {}
severity_counts = {"L1": 0, "L2": 0, "L3": 0, "熔断": 0}
bias_directions = {}

for a in anns:
    for d in a["defects"]:
        did = d["id"]
        defect_counts[did] = defect_counts.get(did, 0) + 1
        sev = d.get("severity", "")
        if sev in severity_counts:
            severity_counts[sev] += 1
        elif did == "A":
            severity_counts["熔断"] += 1
        if did == "D":
            desc = d.get("description", "")
            for b in ["偏暖红黄调", "偏冷青蓝调", "偏洋红紫调", "偏黄绿暖调"]:
                if b in desc:
                    bias_directions[b] = bias_directions.get(b, 0) + 1
                    break

print("=== 批次 3501-4000 最终统计摘要 ===")
print(f"总任务数: {total}")
print(f"原始 5.0 满分拦截数: {orig_5_count}")
print(f"原始低分 (<=2.0) 数: {orig_low_count}")
print(f"原始中等分数数: {orig_mid_count}")
print(f"自洽放行数: {pass_count}")
print(f"视觉具象定物改判数: {grounded_count}")
print(f"物理指标直接修正数: {cv_refined_count}")
print("\n缺陷项分布:")
for k, v in sorted(defect_counts.items()):
    print(f"  {k}: {v}")
print("\n严重度分布:")
for k, v in severity_counts.items():
    print(f"  {k}: {v}")
print("\n偏色向量分布:")
for k, v in sorted(bias_directions.items(), key=lambda x: x[1], reverse=True):
    print(f"  {k}: {v}")
