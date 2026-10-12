import json
from pathlib import Path

plan_file = Path("LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json")
with open(plan_file, "r", encoding="utf-8") as f:
    plan = json.load(f)

b14 = next(b for b in plan["batches"] if b["batch_no"] == 14)
items = b14["items"]

print(f"Batch 14 items count: {len(items)}")
print(f"Task ID range: {items[0]['task_id']} ~ {items[-1]['task_id']}")

chunk_size = 6
for s_idx in range((len(items) + chunk_size - 1) // chunk_size):
    chunk = items[s_idx * chunk_size : (s_idx + 1) * chunk_size]
    print(f"\n=== Sheet {s_idx + 1:02d} ===")
    for it in chunk:
        tid = it["task_id"]
        sc = it.get("original_gpt_score", "N/A")
        dc = it.get("metrics", {}).get("delta_c", 0.0)
        peak = it.get("metrics", {}).get("max_local_peak", 0.0)
        defs = it.get("current_defects", [])
        def_str = ",".join([f"{d.get('id')}-{d.get('severity','')}" for d in defs]) if defs else "无"
        img = it["image_id"]
        print(f"  #{tid:4d} | sc:{sc} | dC:{dc:.3f} | peak:{peak:.2f} | defs:{def_str:12s} | {img}")
