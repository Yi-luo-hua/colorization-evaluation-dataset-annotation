import json
from pathlib import Path

plan_file = Path("LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json")
with open(plan_file, "r", encoding="utf-8") as f:
    plan = json.load(f)

b11 = next(b for b in plan["batches"] if b["batch_no"] == 11)
items = b11["items"]
print(f"Batch 11 items count: {len(items)}")
print(f"Task ID range: {items[0]['task_id']} ~ {items[-1]['task_id']}")

low_score = [x for x in items if x.get("original_gpt_score", 5.0) < 4.0]
high_dc = [x for x in items if x.get("metrics", {}).get("delta_c", 0.0) >= 0.08]
eligible_pass = [x for x in items if x.get("original_gpt_score", 0) >= 4.5 and x.get("metrics", {}).get("delta_c", 1.0) < 0.08]

print(f"Original score < 4.0: {len(low_score)}")
print(f"Delta_C >= 0.08: {len(high_dc)}")
print(f"Potentially eligible for pass (Score >= 4.5 AND Delta_C < 0.08): {len(eligible_pass)}")

# Group by sheets (6 items per sheet)
chunk_size = 6
for s_idx in range((len(items) + chunk_size - 1) // chunk_size):
    chunk = items[s_idx * chunk_size : (s_idx + 1) * chunk_size]
    print(f"\n--- Sheet {s_idx + 1:02d} ---")
    for it in chunk:
        tid = it["task_id"]
        img = it["image_id"]
        sc = it.get("original_gpt_score", "N/A")
        dc = it.get("metrics", {}).get("delta_c", 0.0)
        peak = it.get("metrics", {}).get("max_local_peak", 0.0)
        cur_note = it.get("current_review_note", "")
        defs = it.get("current_defects", [])
        def_str = ",".join([f"{d.get('id')}-{d.get('severity','')}" for d in defs]) if defs else "无"
        print(f"  Task #{tid:4d} | Score: {sc} | dC: {dc:.3f} | peak: {peak:.2f} | defs: {def_str:10s} | {cur_note[:40]}")
