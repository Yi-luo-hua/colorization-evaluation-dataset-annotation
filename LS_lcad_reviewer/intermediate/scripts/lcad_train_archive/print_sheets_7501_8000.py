import json
from pathlib import Path

meta_file = Path("LS_lcad_reviewer/intermediate/audits/sheets_meta_7501_8000.json")
out_file = Path("LS_lcad_reviewer/intermediate/audits/sheets_analysis_7501_8000.txt")

with open(meta_file, "r", encoding="utf-8") as f:
    items = json.load(f)

lines = []
for i in range(0, len(items), 6):
    sheet_idx = i // 6 + 1
    chunk = items[i:i+6]
    lines.append(f"\n================ SHEET {sheet_idx:02d} ({len(chunk)} items) ================")
    for m in chunk:
        idx = m["task_idx"]
        base = m["basename"]
        score = m["score"]
        susp = m["suspicion"]
        reasons = "; ".join(m["reasons"])
        bias = m["metrics"].get("bias_direction", "无")
        dc = m["metrics"].get("delta_c", 0.0)
        lines.append(f"  Task {idx} | {base} | Orig: {score} | Susp: {susp} | Bias: {bias}(dC={dc:.2f}) | {reasons}")

out_file.write_text("\n".join(lines), encoding="utf-8")
print(f"Written analysis to {out_file}")
