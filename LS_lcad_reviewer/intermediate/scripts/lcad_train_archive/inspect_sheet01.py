# -*- coding: utf-8 -*-
import json

with open('LS_lcad_reviewer/intermediate/audits/suspect_detailed_cv_diff.json', encoding='utf-8') as f:
    stats = {x['task_id']: x for x in json.load(f)}

for tid in [142, 277, 283, 295, 302, 336]:
    s = stats[tid]
    print(f"Task #{tid}: orig={s['orig_score']}, dC={s['delta_c']:.3f}, diff_mean={s['diff_mean']:.1f}, p95={s['diff_p95']:.1f}, reasons={s['reasons']}")
