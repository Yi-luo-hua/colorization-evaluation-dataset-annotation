import json
import sys

def show_phase(start_idx, end_idx):
    data = json.load(open('LS_lcad_reviewer/intermediate/scripts/batch_50_meta_summary.json', encoding='utf-8'))
    for i in range(start_idx, min(end_idx, len(data['items']))):
        it = data['items'][i]
        q = "PASS-CANDIDATE" if it['qualifies'] else "INTERCEPTED"
        print(f"Task #{it['task_id']} (idx {i+1}) | orig={it['orig_score']} | dC={it['delta_c']:.3f} | {q} | bias={it['bias_direction']} | sat={it['sat_ratio']:.2f}")

if __name__ == '__main__':
    s = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    e = int(sys.argv[2]) if len(sys.argv) > 2 else 36
    show_phase(s, e)
