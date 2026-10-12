import json
import sys

def inspect_batch(batch_num, start_sheet=1, end_sheet=20):
    plan_path = "LS_lcad_reviewer/intermediate/audits/remaining_visual_audit_plan_50_batches.json"
    with open(plan_path, "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    batches = {b["batch_no"]: b for b in plan["batches"]}
    if batch_num not in batches:
        print(f"Error: Batch {batch_num} not found")
        return
    tasks = batches[batch_num]["items"]
    
    start_idx = (start_sheet - 1) * 6
    end_idx = min(end_sheet * 6, len(tasks))
    
    print(f"=== Batch {batch_num:02d} (Sheets {start_sheet:02d} to {end_sheet:02d}, Tasks {start_idx+1} to {end_idx}) ===")
    for i in range(start_idx, end_idx):
        t = tasks[i]
        sheet_no = i // 6 + 1
        slot_no = i % 6 + 1
        tid = t.get("task_id")
        score = t.get("original_gpt_score")
        defects = t.get("current_defects", [])
        def_strs = [f"{d.get('id')}-{d.get('severity','')}:{d.get('name','')}" for d in defects]
        def_str = ", ".join(def_strs) if def_strs else "None"
        note = t.get("current_review_note", "")
        img = t.get("image_id", "")
        print(f"Task #{tid} [S{sheet_no:02d}-{slot_no}] Score: {score} | Defects: [{def_str}] | Img: {img} | Note: {note[:30]}")

if __name__ == "__main__":
    b = int(sys.argv[1]) if len(sys.argv) > 1 else 38
    s1 = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    s2 = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    inspect_batch(b, s1, s2)
