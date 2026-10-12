import json

def main():
    with open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8') as f:
        plan = json.load(f)
    
    with open('LS_lcad_reviewer/exports/reviewed_1_10000_all.json', 'r', encoding='utf-8') as f:
        all_data = json.load(f)
    
    ann_map = {item['human_review']['task_id']: item for item in all_data['annotations']}
    
    batch_02 = plan['batches'][1] # batch_no: 2
    items = batch_02['items']
    
    for s_idx in range(20):
        sheet_items = items[s_idx*6 : (s_idx+1)*6]
        print(f"=== SHEET {s_idx+1:02d} ===")
        for pos, it in enumerate(sheet_items):
            tid = it['task_id']
            ann = ann_map.get(tid, {})
            score = ann.get('original_gpt_score', ann.get('gpt_score'))
            defects = ann.get('defects', [])
            def_str = "; ".join([f"{d['id']}-{d['severity']}({d['name']}): {d['description']}" for d in defects])
            note = ann.get('review_note', '')
            print(f"  [{pos+1}] Task #{tid} | {it['image_id']} | Score: {score} | Note: {note}")
            print(f"      Defects: {def_str if def_str else '[] (放行或无缺陷)'}")

if __name__ == '__main__':
    main()
