import json

with open("intermediate/audits/scan_metrics_pass_4501_5000.json", "r", encoding="utf-8") as f:
    tasks = json.load(f)

tasks = sorted(tasks, key=lambda x: x["score"], reverse=True)

for i, t in enumerate(tasks):
    sheet_idx = (i // 6) + 1
    pos = (i % 6) + 1
    anom_str = ", ".join(t.get("anomalies", [])) if t.get("anomalies") else "CLEAN"
    print(f"Sheet {sheet_idx:02d} Pos {pos}: Task #{t['task_idx']} ({t['image_id']}) score={t['score']} [{anom_str}]")
