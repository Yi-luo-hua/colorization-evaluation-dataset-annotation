# -*- coding: utf-8 -*-
import json
from pathlib import Path

audit_p = Path(r"LS_lcad_reviewer/intermediate/audits/suspect_passes_audit.json")
with open(audit_p, "r", encoding="utf-8") as f:
    data = json.load(f)

batch2 = [d for d in data if 121 <= d["idx"] <= 240]
print(f"Batch 2 total: {len(batch2)}")
print(f"Idx range: {batch2[0]['idx']} ~ {batch2[-1]['idx']}")
print(f"Task range: {batch2[0]['task_id']} ~ {batch2[-1]['task_id']}")

genuine_passes_candidates = []
for d in batch2:
    m = d["metrics"]
    if m["diff_mean"] < 8.0 and m["diff_p90"] < 15.0 and m["delta_c"] < 0.05 and m["local_max_diff"] <= 0.04:
        genuine_passes_candidates.append(d)

print(f"\nCandidates with ultra-low diff: {len(genuine_passes_candidates)}")
for c in genuine_passes_candidates:
    print(f"Card [{c['idx']}/371] Task #{c['task_id']} ({c['image_id']}): dC={c['metrics']['delta_c']:.3f}, diff_mean={c['metrics']['diff_mean']:.2f}, peak={c['metrics']['local_max_diff']:.2f}, orig={c['orig_score']}")
