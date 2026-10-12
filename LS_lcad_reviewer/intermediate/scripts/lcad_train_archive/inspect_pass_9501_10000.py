import json

tasks = json.load(open("LS_lcad_reviewer/intermediate/audits/audit_pass_9501_10000.json", encoding="utf-8"))
print(f"Total pass tasks: {len(tasks)}")
alarm_tasks = [t for t in tasks if t["alarms"]]
clean_tasks = [t for t in tasks if not t["alarms"]]
print(f"Tasks with alarms: {len(alarm_tasks)}")
print(f"Tasks clean: {len(clean_tasks)}")

print("\n--- Clean tasks ---")
for t in clean_tasks:
    m = t["metrics"]
    print(f"#{t['task_id']} ({t['basename']}) score={t['score']} orig={t['orig_score']} delta_c={m.get('delta_c')} r_sat={m.get('r_sat')} red_loss={m.get('red_loss')}")
