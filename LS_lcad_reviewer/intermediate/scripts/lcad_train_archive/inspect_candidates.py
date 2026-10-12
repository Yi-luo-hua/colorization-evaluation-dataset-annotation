import json

candidate_ids = [
    3580, 3653, 3754, 3819, 3925, 3963, 3690, 3876, 3970, 3982,
    3624, 3638, 3657, 3699, 3830,
    3883, 3510, 3532, 3820, 3583, 3995, 3682, 3780, 3832, 3916, 3584, 3895, 3522, 3613, 3600
]

with open("exports/reviewed_3501_4000_20260930_121202.json", "r", encoding="utf-8") as f:
    data = json.load(f)

annotations = data["annotations"]

lines = []
for cid in candidate_ids:
    idx = cid - 3501
    ann = annotations[idx]
    defects = [f"{d.get('name')}: {d.get('description','')}" for d in ann.get('defects', [])]
    lines.append(f"Task #{cid} | Image: {ann['image_id']} | Score: {ann.get('gpt_score')} | Status: {ann.get('review_status')}\n  Defects: {'; '.join(defects)}\n  Note: {ann.get('review_note')}\n")

with open("intermediate/audits/inspect_candidates_utf8.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Saved to intermediate/audits/inspect_candidates_utf8.txt")
