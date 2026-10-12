import json

def extract_batch_49():
    plan = json.load(open('LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json', 'r', encoding='utf-8'))
    b49 = plan['batches'][48]  # index 48 is batch 49
    
    items = []
    qualifies_count = 0

    for it in b49['items']:
        idx = it['task_id']
        orig_score = it['original_gpt_score']
        metrics = it.get('metrics', {})
        delta_c = metrics.get('delta_c', 0.0)
        delta_rg = metrics.get('delta_rg', 0.0)
        delta_yb = metrics.get('delta_yb', 0.0)
        r_sat = metrics.get('r_sat', 1.0)
        bias_dir = metrics.get('bias_direction', '')
        
        # Dual-threshold pass candidate qualification
        qualifies = (orig_score >= 4.5 and delta_c < 0.08)
        if qualifies:
            qualifies_count += 1
            
        items.append({
            'task_id': idx,
            'image_id': it['image_id'],
            'orig_score': orig_score,
            'delta_c': delta_c,
            'delta_rg': delta_rg,
            'delta_yb': delta_yb,
            'bias_direction': bias_dir,
            'sat_ratio': r_sat,
            'qualifies': qualifies,
            'current_review_note': it.get('current_review_note', ''),
            'current_defects': it.get('current_defects', [])
        })

    out_file = 'LS_lcad_reviewer/intermediate/scripts/batch_49_meta_summary.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({
            'batch_no': 49,
            'total_tasks': len(items),
            'qualifies_count': qualifies_count,
            'items': items
        }, f, indent=2, ensure_ascii=False)

    print(f"Batch 49 metadata extraction complete: {len(items)} tasks total, {qualifies_count} qualify as pass candidates (orig_score >= 4.5 & delta_c < 0.08)")

if __name__ == '__main__':
    extract_batch_49()
