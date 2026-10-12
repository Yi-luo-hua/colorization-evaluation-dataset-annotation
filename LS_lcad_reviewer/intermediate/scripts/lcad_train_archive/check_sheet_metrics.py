import json

with open("intermediate/audits/audit_pass_3501_4000.json", "r", encoding="utf-8") as f:
    pass_tasks = json.load(f)

with open("intermediate/audits/scan_metrics_pass_3501_4000.json", "r", encoding="utf-8") as f:
    metrics = {m["task_idx"]: m for m in json.load(f)}

print(f"Total pass tasks: {len(pass_tasks)}")
for i, t in enumerate(pass_tasks):
    sheet_idx = (i // 6) + 1
    pos = (i % 6) + 1
    if sheet_idx >= 7:
        tid = t["task_idx"]
        m = metrics.get(tid, {})
        alerts = []
        if m.get("red_loss", 0) > 0.40:
            alerts.append(f"RedLoss={m['red_loss']:.2f}")
        if m.get("max_peak", 0) > 0.20:
            alerts.append(f"Peak={m['max_peak']:.2f}")
        if m.get("r_sat", 1.0) < 0.45 or m.get("r_sat", 1.0) > 1.60:
            alerts.append(f"R_sat={m['r_sat']:.2f}")
        if m.get("delta_c", 0) > 0.12:
            alerts.append(f"DeltaC={m['delta_c']:.2f}")
        alert_str = ", ".join(alerts) if alerts else "CLEAN"
        print(f"Sheet {sheet_idx:02d} Pos {pos}: Task #{tid} ({t['image_id']}) score={t['score']} [{alert_str}]")
