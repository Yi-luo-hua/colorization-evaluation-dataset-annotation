import json
from pathlib import Path

streams_dir = Path("LS_lcad_reviewer/streams")
stream_files = sorted(list(streams_dir.glob("*.json")))

print(f"Found {len(stream_files)} stream files to patch.")

for sf in stream_files:
    with open(sf, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    modified = False
    for t in tasks:
        data = t.get("data", {})
        if "original_gpt_info" not in data or "review_note_display" not in data:
            orig = data.get("original_record", {})
            score = orig.get("gpt_score", "未知")
            defects = orig.get("defects", [])

            if not defects:
                orig_info = f"原始评分: {score} 分 (无扣分缺陷)"
            else:
                parts = [f"原始评分: {score} 分 | 原始检出 {len(defects)} 项缺陷:"]
                for d in defects:
                    d_id = d.get("id", "")
                    sev = d.get("severity", "")
                    name = d.get("name", "")
                    desc = d.get("description", "")
                    tag = f"[{d_id}-{sev}]" if sev else f"[{d_id}]"
                    parts.append(f"• {tag} {name}: {desc}")
                orig_info = "\n".join(parts)

            note = data.get("review_note", "")
            if not note:
                note = "审查通过"

            data["original_gpt_info"] = orig_info
            data["review_note_display"] = note
            modified = True

    if modified:
        with open(sf, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
        print(f"Patched: {sf.name}")
    else:
        print(f"Already up-to-date: {sf.name}")

print("All stream files updated successfully.")
