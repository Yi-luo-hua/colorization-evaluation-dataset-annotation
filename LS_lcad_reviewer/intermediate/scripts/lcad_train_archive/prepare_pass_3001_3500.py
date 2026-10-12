import json
from pathlib import Path

WORKSPACE_ROOT = Path("d:/学业文件/MCL/上色评价_数据集标注")
TASKS_10000_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "tasks_lcad_10000.json"
REVIEWED_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "exports" / "reviewed_3001_3500_20260929_221929.json"
OUT_PASS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_3001_3500.json"

tasks_10000 = json.loads(TASKS_10000_FILE.read_text(encoding="utf-8"))
reviewed_data = json.loads(REVIEWED_FILE.read_text(encoding="utf-8"))

batch_tasks = tasks_10000[3000:3500]
reviewed_map = {a["image_id"]: a for a in reviewed_data["annotations"]}

pass_list = []
a_missed = []
high_score_pass = []

for idx, t in enumerate(batch_tasks, start=3001):
    rec = t.get("data", {}).get("original_record", {})
    img_id = rec.get("image_id") or t.get("data", {}).get("image_id")
    rev = reviewed_map.get(img_id, {})
    
    is_passed = (rev.get("review_note") == "审查通过" or len(rev.get("defects", [])) == 0)
    
    # 检查是否有原打分 1.0 的缺色 A 被误判放行
    orig_score = rec.get("gpt_score", 0.0)
    orig_defects = rec.get("defects", [])
    has_orig_a = any(d.get("id") == "A" for d in orig_defects) or orig_score <= 1.0
    
    if is_passed:
        if has_orig_a:
            a_missed.append((idx, img_id, orig_score))
        if orig_score >= 4.0:
            high_score_pass.append((idx, img_id, orig_score))
            
        pass_list.append({
            "task_idx": idx,
            "image_id": img_id,
            "basename": Path(img_id).name,
            "score": orig_score,
            "suspicion": 10.0 if orig_score >= 4.0 else (5.0 if has_orig_a else 0.0),
            "reasons": ["A熔断漏检疑似" if has_orig_a else ("高分均摊疑似" if orig_score >= 4.0 else "物理指标自洽(全量视觉复审核验)")],
            "defects": orig_defects
        })

# 排序：A 熔断疑似与高分疑似排在最前，便于集中优先深度直审
pass_list.sort(key=lambda x: (x["suspicion"], x["score"]), reverse=True)

OUT_PASS_FILE.write_text(json.dumps(pass_list, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Total passed tasks in batch 3001-3500: {len(pass_list)}")
print(f"A熔断漏检疑似 (orig_score<=1.0 or orig has A): {len(a_missed)}")
for m in a_missed:
    print(f"  Task #{m[0]}: {m[1]}, score={m[2]}")
print(f"High score passed (orig_score >= 4.0): {len(high_score_pass)}")
for h in high_score_pass[:10]:
    print(f"  Task #{h[0]}: {h[1]}, score={h[2]}")
if len(high_score_pass) > 10:
    print(f"  ... and {len(high_score_pass) - 10} more high score tasks")
print(f"Saved pass audit list to: {OUT_PASS_FILE}")
