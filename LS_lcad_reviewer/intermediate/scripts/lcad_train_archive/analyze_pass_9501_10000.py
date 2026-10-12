"""Audit analysis script for 9501-10000 pass tasks."""
import json
from pathlib import Path

WORKSPACE_ROOT = Path(r"d:\学业文件\MCL\上色评价_数据集标注")
PASS_FILE = WORKSPACE_ROOT / "LS_lcad_reviewer" / "intermediate" / "audits" / "audit_pass_9501_10000.json"

with open(PASS_FILE, "r", encoding="utf-8") as f:
    tasks = json.load(f)

print(f"Loaded {len(tasks)} tasks.")

# Let's inspect tasks by ID and find their specifics
high_red_loss = [t for t in tasks if t['metrics'].get('red_loss', 0) > 0.20]
low_sat = [t for t in tasks if t['metrics'].get('r_sat', 1.0) < 0.65]
high_delta_c = [t for t in tasks if t['metrics'].get('delta_c', 0) > 0.07]
high_score = [t for t in tasks if t['orig_score'] >= 4.0]

print(f"High red loss (>0.20): {len(high_red_loss)}")
print(f"Low saturation (<0.65): {len(low_sat)}")
print(f"High delta_c (>0.07): {len(high_delta_c)}")
print(f"High score (>=4.0): {len(high_score)}")
