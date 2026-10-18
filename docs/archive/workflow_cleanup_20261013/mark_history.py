"""Preserve old report commands while identifying history and fixing moved source links."""
import re
from pathlib import Path
import json

root=Path(__file__).resolve().parents[3]
audit=Path(__file__).parent
plan=json.loads((audit/'cleanup_manifest.json').read_text(encoding='utf-8'))
(audit/'before/historical_reports').mkdir(exist_ok=True)
count=0
for path in (root/'docs/experiments').glob('*.md'):
    text=path.read_text(encoding='utf-8-sig')
    (audit/'before/historical_reports'/path.name).write_bytes(path.read_bytes())
    chunks=re.split(r'(```[\s\S]*?```)',text)
    for index,chunk in enumerate(chunks):
        if chunk.startswith('```'):continue
        for item in plan['archive_files']:
            chunk=chunk.replace(item['source'],item['destination'])
        chunks[index]=chunk
    text=''.join(chunks)
    note='\n> 已完成阶段的历史记录。当前任务与默认流程查[STATUS](../STATUS.md)和[PLAN](../PLAN.md)；旧命令保留当时文本，一次性脚本现位于[归档索引](../../experiments/cv_workflow/archive/rounds_01_14/README.md)，不作为当前运行入口。\n'
    first,rest=text.split('\n',1)
    path.write_text(first+'\n'+note+rest,encoding='utf-8');count+=1
print('Marked',count,'completed reports as history; source bytes saved before edits')
