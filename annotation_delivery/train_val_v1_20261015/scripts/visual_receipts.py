"""Confirm native successful board reads; never infer semantic labels from code."""
import json
import os
from pathlib import Path


def path_key(value):
    if not isinstance(value,str):return ''
    try:
        if value.startswith('"'):value=json.loads(value)
    except ValueError:
        return ''
    return os.path.normcase(os.path.normpath(value))


def read_visual_receipts(conversation_id,sheets,transcript=None):
    expected={path_key(s['path']):s['path'] for s in sheets}
    source=Path(transcript) if transcript else (
        Path.home()/'.gemini/antigravity-cli/brain'/str(conversation_id)/'.system_generated/logs/transcript_full.jsonl')
    seen=set();waiting=[]
    if source.exists():
        with source.open(encoding='utf-8') as stream:
            for line in stream:
                try:step=json.loads(line)
                except ValueError:continue
                if step.get('tool_calls'):
                    waiting=[]
                    for call in step['tool_calls']:
                        args=call.get('args',{})
                        key=path_key(args.get('AbsolutePath') or args.get('ImagePath'))
                        waiting.append(key if call.get('name') in ['view_file','view_image'] and key in expected else None)
                elif waiting and step.get('type')=='GENERIC':
                    key=waiting.pop(0)
                    content=step.get('content','')
                    if key and step.get('status')=='DONE' and isinstance(content,str) and (
                            'entire, complete content of the requested file' in content) and 'Error:' not in content:
                        seen.add(key)
    return {'seen':[expected[key] for key in expected if key in seen],
        'missing':[expected[key] for key in expected if key not in seen],
        'transcript':str(source),'source':'native successful image tool receipts'}
