"""Gemini reads local sheets and edits local JSON; the host postprocesses that file."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import time

from workflow import read_json,write_json,utc,verify_sources,validate_reviews,import_reviews,export_candidate,require_annotation_contract,ANNOTATION_CONTRACT
import compact_harness


def normalize_review(payload):
    """Translate observed syntax aliases, preserving labels/evidence/severity exactly."""
    result=copy.deepcopy(payload)
    for r in result['reviews']:
        r['decision']={'pass':'no_defects','defect':'defects'}.get(r['decision'],r['decision'])
        for d in r['defects']:
            if 'id' not in d and 'category' in d:d['id']=d.pop('category')
    return result


def load_completed_file(manifest,target,envelope):
    if envelope.get('status')!='SUCCESS' and not Path(target).exists():
        raise ValueError(envelope.get('error') or 'agy call did not complete')
    raw=read_json(target)
    payload=compact_harness.expand(manifest,raw) if raw.get('schema_version')=='visual_review_compact_v1' else normalize_review(raw)
    validate_reviews(manifest,payload)
    return raw,payload


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--batch',type=Path,required=True)
    parser.add_argument('--timeout',type=int,default=None)
    parser.add_argument('--harness',choices=['compact'],default=None)
    parser.add_argument('--effort',choices=['low','medium','high','xhigh','max'],default=None,
                        help='Optional CLI effort experiment; omission preserves the existing model default')
    parser.add_argument('--agy',type=Path,default=Path.home()/'AppData/Local/agy/bin/agy.exe')
    args=parser.parse_args();run=args.batch.resolve();manifest=verify_sources(run)
    require_annotation_contract(manifest['configuration'])
    if manifest['configuration']['annotation_contract']!=ANNOTATION_CONTRACT:
        raise SystemExit('Historical requests are read-only for file recovery. Prepare v4 before any new model call.')
    request=read_json(run/'review_request.json')
    if not request['samples']:
        print('No visual tasks; frozen human A-only results already saved. No agy call.');return
    if args.timeout is None:args.timeout=manifest['configuration']['visual_harness'].get('model_timeout_seconds',300)
    target=run/'reviews_gemini.json'
    if target.exists():raise ValueError('Reviews already exist; preserve this run and use a new batch')
    harness=args.harness or manifest['configuration']['visual_harness'].get('output_contract','full')
    if harness!='compact':raise ValueError('Full-field generation is archived; prepare a current compact batch. Historical file reading remains supported.')
    if harness=='compact':
        initial=compact_harness.template(request)
        target.write_text(json.dumps(initial,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
        prompt=compact_harness.build_prompt(request,target)
        if manifest['configuration']['visual_harness'].get('cv_navigation',False):
            prompt+=compact_harness.cv_hint_text(manifest)
    stamp=utc().replace(':','-');out=run/'agy_calls'/stamp;out.mkdir(parents=True)
    (out/'prompt.txt').write_text(prompt,encoding='utf-8')
    (out/'runner_source.py').write_bytes(Path(__file__).read_bytes())
    write_json(out/'launch.json',{'started_at':utc(),'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'cli_effort':args.effort,
               'image_input':'Gemini reads local sheet files through its tools; no image/base64 embedded in prompt',
               'annotation_output':'Gemini edits local reviews_gemini.json; CLI response is only an acknowledgement'})
    if harness=='compact':(out/'compact_harness_source.py').write_bytes(Path(compact_harness.__file__).read_bytes())
    model=manifest['configuration']['external_reviewer']['model']
    command=[str(args.agy),'-p',prompt,'--model',model,'--mode','accept-edits','--dangerously-skip-permissions',
             '--output-format','json','--print-timeout',f'{args.timeout}s','--log-file',str(out/'client.log')]
    if args.effort:command+=['--effort',args.effort]
    started=time.monotonic();envelope={}
    try:
        process=subprocess.Popen(command,cwd=run,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        launch=read_json(out/'launch.json');launch.update(agy_pid=process.pid,agy_spawned_at=utc());write_json(out/'launch.json',launch)
        try:
            stdout,stderr=process.communicate(timeout=args.timeout+20)
        except subprocess.TimeoutExpired:
            process.kill();stdout,stderr=process.communicate()
            (out/'stdout.json').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
            raise
        (out/'stdout.json').write_bytes(stdout);(out/'stderr.txt').write_bytes(stderr)
        envelope=json.loads(stdout.decode('utf-8-sig'))
        raw,payload=load_completed_file(manifest,target,envelope)
        write_json(out/'raw_reviews.json',raw)
    except (subprocess.TimeoutExpired,ValueError) as error:
        write_json(out/'result.json',{'state':'model_call_incomplete','model':model,'cli_effort':args.effort,
                   'elapsed_seconds':round(time.monotonic()-started,2),'error':str(error),
                   'native_status':envelope.get('status'),'native_error':envelope.get('error')})
        raise SystemExit(f'No labels imported: {error}')
    normalized=out/'normalized_reviews.json';write_json(normalized,payload)
    import_reviews(argparse.Namespace(batch=run,reviews=normalized))
    resolved=all(r['decision']!='uncertain' and not r['uncertainties'] and not r['needs_crops']
                 and all(d['severity'] is not None for d in r['defects']) for r in payload['reviews'])
    exported=export_candidate(argparse.Namespace(batch=run)) if resolved else False
    state='candidate_exported' if exported else 'observations_saved_without_source_scores' if resolved else 'observations_saved_with_uncertainty'
    write_json(out/'result.json',{'state':state,
               'model':model,'cli_effort':args.effort,'agy_pid':process.pid,'elapsed_seconds':round(time.monotonic()-started,2),
               'samples':len(payload['reviews']),'sheets':len(manifest['sheets']),
               'annotation_output':'local_file_edited_by_gemini','harness':harness,
               'prompt_characters':len(prompt),'model_result_file_bytes':len(json.dumps(raw,ensure_ascii=False).encode('utf-8')),
               'conversation_id':envelope.get('conversation_id'),'num_turns':envelope.get('num_turns'),'usage':envelope.get('usage') or {},
               'native_status':envelope.get('status'),'native_error':envelope.get('error'),
               'file_completed_despite_native_error':envelope.get('status')!='SUCCESS'})
    print(out/'result.json')


if __name__=='__main__':main()
