# -*- coding: utf-8 -*-
import json
from pathlib import Path

def main():
    p = Path('LS_lcad_reviewer/intermediate/audits/suspect_detailed_cv_diff.json')
    with open(p, 'r', encoding='utf-8') as f:
        stats = json.load(f)

    print(f"Total suspects: {len(stats)}")
    
    # Check distribution
    stats_sorted = sorted(stats, key=lambda x: x['diff_mean'], reverse=True)
    print("--- Top 10 highest diff_mean (Severe Discrepancies) ---")
    for s in stats_sorted[:10]:
        print(f"Task #{s['task_id']} ({s['sheet']} pos {s['pos']}): orig={s['orig_score']}, dC={s['delta_c']:.3f}, diff_mean={s['diff_mean']:.1f}, p95={s['diff_p95']:.1f}, reasons={s['reasons']}")

    print("\n--- Bottom 10 lowest diff_mean (Potential True Passes) ---")
    for s in stats_sorted[-10:]:
        print(f"Task #{s['task_id']} ({s['sheet']} pos {s['pos']}): orig={s['orig_score']}, dC={s['delta_c']:.3f}, diff_mean={s['diff_mean']:.1f}, p95={s['diff_p95']:.1f}, reasons={s['reasons']}")

    # Breakdown by violation type
    dc_ge_08 = [s for s in stats if s['delta_c'] >= 0.08]
    score_lt_40 = [s for s in stats if s['orig_score'] < 4.0]
    score_40_45 = [s for s in stats if 4.0 <= s['orig_score'] < 4.5 and s['delta_c'] < 0.08]
    score_ge_45_high_peak_or_sat = [s for s in stats if s['orig_score'] >= 4.5 and s['delta_c'] < 0.08]
    
    print("\n--- Breakdown ---")
    print(f"ΔC >= 0.08: {len(dc_ge_08)}")
    print(f"orig_score < 4.0: {len(score_lt_40)}")
    print(f"4.0 <= orig_score < 4.5 (and dC < 0.08): {len(score_40_45)}")
    print(f"orig_score >= 4.5 but sat/peak flagged: {len(score_ge_45_high_peak_or_sat)}")

if __name__ == '__main__':
    main()
