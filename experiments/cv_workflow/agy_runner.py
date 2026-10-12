"""One agy call per batch: sheet vision → JSON → existing candidate postprocessing."""
import argparse
import json
from pathlib import Path
import subprocess
import time

from workflow import read_json,write_json,utc,verify_sources,import_reviews,export_candidate


def decode_response(envelope):
    # agy may return SUCCESS with an empty partial response at its print timeout.
    if envelope.get('status')!='SUCCESS' or not envelope.get('response','').strip():
        raise ValueError(envelope.get('error') or 'agy returned no completed response')
    text=envelope['response'].strip()
    if text.startswith('```'):
        text=text.split('\n',1)[1].rsplit('```',1)[0].strip()
    return json.loads(text)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch',type=Path,required=True)
    parser.add_argument('--timeout',type=int,default=180)
    parser.add_argument('--agy',type=Path,default=Path.home()/'AppData/Local/agy/bin/agy.exe')
    args=parser.parse_args();run=args.batch.resolve();manifest=verify_sources(run)
    target=run/'reviews_gemini.json'
    if target.exists():raise ValueError('Reviews already exist; preserve this run and use a new batch')
    request=read_json(run/'review_request.json');template=read_json(run/'review_template.json')
    protocol=(run/'ANTIGRAVITY_HANDOFF.md').read_text(encoding='utf-8')
    prompt=('你是快速看板标注器。所有说明与元数据已内嵌，不需读取其他文本文件。'
            '唯一允许的工具操作是按清单各打开一次六组看板；不要读源码、原图、目录或运行命令。'
            '不要写文件或作总结，直接在最终回复返回完整JSON，程序负责存盘与后处理。\n'
            +protocol+'\nINPUT\n'+json.dumps(request,ensure_ascii=False)
            +'\nOUTPUT TEMPLATE\n'+json.dumps(template,ensure_ascii=False))
    stamp=utc().replace(':','-');out=run/'agy_calls'/stamp;out.mkdir(parents=True)
    (out/'prompt.txt').write_text(prompt,encoding='utf-8')
    model=manifest['configuration']['external_reviewer']['model']
    command=[str(args.agy),'-p',prompt,'--model',model,'--mode','plan','--dangerously-skip-permissions',
             '--output-format','json','--print-timeout',f'{args.timeout}s','--log-file',str(out/'client.log')]
    started=time.monotonic()
    try:
        process=subprocess.run(command,cwd=run,capture_output=True,timeout=args.timeout+20)
        (out/'stdout.json').write_bytes(process.stdout);(out/'stderr.txt').write_bytes(process.stderr)
        envelope=json.loads(process.stdout.decode('utf-8-sig'));payload=decode_response(envelope)
    except (subprocess.TimeoutExpired,ValueError) as error:
        write_json(out/'result.json',{'state':'model_call_incomplete','model':model,'elapsed_seconds':round(time.monotonic()-started,2),'error':str(error)})
        raise SystemExit(f'No labels imported: {error}')
    write_json(target,payload)
    import_reviews(argparse.Namespace(batch=run,reviews=target))
    resolved=all(r['decision']!='uncertain' and not r['uncertainties'] and not r['needs_crops']
                 and all(d['severity'] is not None for d in r['defects']) for r in payload['reviews'])
    if resolved:export_candidate(argparse.Namespace(batch=run))
    write_json(out/'result.json',{'state':'candidate_exported' if resolved else 'observations_saved_with_uncertainty',
               'model':model,'elapsed_seconds':round(time.monotonic()-started,2),
               'samples':len(payload['reviews']),'sheets':len(manifest['sheets']),
               'conversation_id':envelope.get('conversation_id'),'num_turns':envelope.get('num_turns'),'usage':envelope.get('usage')})
    print(out/'result.json')


if __name__=='__main__':main()
