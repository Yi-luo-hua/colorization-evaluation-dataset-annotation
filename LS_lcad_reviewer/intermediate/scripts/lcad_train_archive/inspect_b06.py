import json

def main():
    all_data = json.load(open('LS_lcad_reviewer/exports/reviewed_1_10000_all.json', encoding='utf-8'))['annotations']
    plan = json.load(open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', encoding='utf-8'))['batches'][5]
    tids = plan['task_ids']
    task_map = {a['human_review']['task_id']: a for a in all_data if a['human_review']['task_id'] in tids}
    print(f"Batch 06 total tasks: {len(tids)}, found in all: {len(task_map)}")
    for i, tid in enumerate(tids):
        sheet_idx = i // 6 + 1
        a = task_map[tid]
        defs = [f"{d['id']}-{d.get('severity','')}" for d in a['defects']]
        print(f"Sheet {sheet_idx:02d} | Task #{tid:4d} | gpt={a['gpt_score']} | defs={defs} | note={a['review_note'][:35]}")

if __name__ == '__main__':
    main()
