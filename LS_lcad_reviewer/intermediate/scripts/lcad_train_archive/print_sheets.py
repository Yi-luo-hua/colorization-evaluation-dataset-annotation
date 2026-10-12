import json

tasks = json.load(open('LS_lcad_reviewer/intermediate/scripts/batch_43_meta_summary.json', encoding='utf-8'))

for i in range(8):
    sheet_num = i + 1
    sub = tasks[i*6 : (i+1)*6]
    print(f"=== Sheet {sheet_num:02d} ===")
    for t in sub:
        defs_str = " | ".join(t['defects']) if t['defects'] else "None"
        print(f"#{t['task_id']} | Score: {t['score']:.2f} | Defs: {defs_str}")
