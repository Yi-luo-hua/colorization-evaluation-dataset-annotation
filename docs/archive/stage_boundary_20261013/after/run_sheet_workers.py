"""Rolling High queue across batches; independent files and per-batch completion."""
import argparse
import importlib.util
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from run_harness_trial import prepare_trial
from workflow import BASE,OUTPUT,read_json,write_json,utc,validate_reviews,import_reviews,export_candidate,verify_sources,require_annotation_contract
import engine


def combine_queue(queue_dir,inputs):
    exports=[out/'exports' for out,_,_ in inputs]
    annotations=[r for directory in exports for r in read_json(directory/'reviewed_candidate.json')['annotations']]
    if len({r['image_id'] for r in annotations})!=len(annotations):raise ValueError('Combined dataset requires distinct image IDs')
    destination=queue_dir/'exports';destination.mkdir()
    target=destination/'reviewed_candidate.json'
    write_json(target,{'meta':{'exported_at':utc(),'total_images':len(annotations),'needs_rescoring':True},'annotations':annotations})
    spec=importlib.util.spec_from_file_location('export_contract_validator',BASE/'core_pipeline/validate_export_schema.py')
    validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    if not validator.validate_file(target):raise ValueError('Combined candidate failed official schema validation')
    write_json(destination/'tasks_reviewed_stream.json',[r for directory in exports for r in read_json(directory/'tasks_reviewed_stream.json')])
    write_json(destination/'provenance.json',{'experimental_candidate_only':True,
        'parent_batches':[{'batch':str(out),'candidate_sha256':engine.sha256(out/'exports/reviewed_candidate.json'),
                           'provenance':read_json(out/'exports/provenance.json')} for out,_,_ in inputs]})
    return str(target)


def finish_batch(out,manifest,results,failures,started,workers,sheets_per_job,jobs):
    call_dir=out/'agy_calls/parallel';call_dir.mkdir(parents=True,exist_ok=True)
    wall=round(time.monotonic()-started,2)
    results.sort(key=lambda item:item[0].name)
    common={'elapsed_seconds':wall,'workers':workers,'sheets_per_job':sheets_per_job,
            'jobs':jobs,'samples':len(manifest['records']),'sheets':len(manifest['sheets']),
            'worker_calls':[result for _,result in results],'finished_at':utc()}
    if failures:
        result={**common,'state':'workers_incomplete','failures':failures}
        write_json(call_dir/'result.json',result);return result
    rows=[r for child,_ in results for r in read_json(child/'visual_reviews.json')['reviews']]
    payload={'schema_version':'visual_review_v1','reviewer':manifest['configuration']['external_reviewer'],
             'reviews':rows,'completion_fields_source':'merged board-group compact files edited by Gemini'}
    validate_reviews(manifest,payload);write_json(out/'reviews_merged.json',payload)
    import_reviews(argparse.Namespace(batch=out,reviews=out/'reviews_merged.json'))
    resolved=all(r['decision']!='uncertain' and not r['uncertainties'] and not r['needs_crops']
                 and all(d['severity'] is not None for d in r['defects']) for r in rows)
    exported=export_candidate(argparse.Namespace(batch=out)) if resolved else False
    usage={k:sum(result['usage'].get(k,0) for _,result in results) for k in results[0][1]['usage']}
    events=[(r['scheduler_timing']['start_offset_seconds'],1) for _,r in results]+[(r['scheduler_timing']['end_offset_seconds'],-1) for _,r in results]
    active=peak=0
    for _,delta in sorted(events):active+=delta;peak=max(peak,active)
    result={**common,'state':'candidate_exported' if exported else 'observations_saved_without_source_scores' if resolved else 'observations_saved_with_uncertainty',
            'model':manifest['configuration']['external_reviewer']['model'],
            'elapsed_seconds':round(time.monotonic()-started,2),'worker_phase_wall_seconds':wall,
            'timing':'shared queue start through this batch import/validation/export; includes waiting for a queue slot',
            'peak_active_runner_processes':peak,'harness':'compact_sheet_workers',
            'annotation_output':'Gemini edits independent local JSON files; host merges them','usage':usage}
    write_json(call_dir/'result.json',result);return result


def main():
    p=argparse.ArgumentParser();source=p.add_mutually_exclusive_group(required=True)
    source.add_argument('--baseline',type=Path,help='Frozen source to clone for a new experiment')
    source.add_argument('--batch',type=Path,nargs='+',help='Prepared batches sharing one rolling queue')
    p.add_argument('--run-id',help='Required when cloning --baseline')
    p.add_argument('--queue-run-id',help='Required for multiple batches; saves global queue timing')
    p.add_argument('--no-combined-export',action='store_true',help='Keep paired experiment conditions separate, with independent per-batch exports')
    p.add_argument('--workers',type=int);p.add_argument('--timeout',type=int)
    p.add_argument('--sheets-per-job',type=int)
    args=p.parse_args()
    if args.batch:
        inputs=[(path.resolve(),verify_sources(path.resolve()),path.resolve()) for path in args.batch]
    else:
        if not args.run_id:p.error('--baseline requires --run-id')
        out=OUTPUT/args.run_id;inputs=[(out,prepare_trial(args.baseline,out,'compact'),args.baseline)]
    if len({out for out,_,_ in inputs})!=len(inputs):p.error('Batch directories must be distinct')
    for _,manifest,_ in inputs:require_annotation_contract(manifest['configuration'])
    if len(inputs)>1 and not args.queue_run_id:p.error('Multiple batches require --queue-run-id')
    scheduler=inputs[0][1]['configuration']['visual_harness'].get('parallel_scheduler',{})
    if args.workers is None:args.workers=scheduler.get('workers',16)
    if args.sheets_per_job is None:args.sheets_per_job=scheduler.get('sheets_per_job',2)
    if args.workers<1 or args.sheets_per_job<1:p.error('Workers and sheets-per-job must be positive')
    queue_dir=OUTPUT/args.queue_run_id if args.queue_run_id else None
    if queue_dir:queue_dir.mkdir()
    states={};batches=[]
    for out,manifest,baseline in inputs:
        timeout=args.timeout or manifest['configuration']['visual_harness'].get('model_timeout_seconds',300)
        parts=out/'parts';parts.mkdir();children=[]
        for start in range(0,len(manifest['sheets']),args.sheets_per_job):
            child=parts/f'job_{len(children)+1:03d}'
            selected=[s['path'] for s in manifest['sheets'][start:start+args.sheets_per_job]]
            prepare_trial(baseline,child,'compact',selected_sheets=selected);children.append(child)
        write_json(out/'parallel_plan.json',{'workers':args.workers,'sheets_per_job':args.sheets_per_job,'timeout':timeout,
            'jobs':[{'path':str(c.relative_to(out)),'sample_keys':[r['sample_key'] for r in verify_sources(c)['records']]} for c in children],
            'same_boards_and_CV':True,'no_old_labels_copied':True,'queue_run_id':args.queue_run_id})
        (out/'parallel_runner_source.py').write_bytes(Path(__file__).read_bytes())
        states[out]={'manifest':manifest,'jobs':len(children),'results':[],'failures':[],'processed':0}
        batches.extend((out,child,timeout) for child in children)
    if queue_dir:
        write_json(queue_dir/'queue_plan.json',{'workers':args.workers,'sheets_per_job':args.sheets_per_job,
            'batches':[str(out) for out,_,_ in inputs],'jobs':[{'batch':str(out),'job':child.name} for out,child,_ in batches],
            'scheduling':'work-conserving FIFO; one free slot starts the next job, no wave or batch barrier'})
        (queue_dir/'parallel_runner_source.py').write_bytes(Path(__file__).read_bytes())
    started=time.monotonic()
    def run(out,child,timeout):
        command=[sys.executable,str(Path(__file__).with_name('agy_runner.py')),'--batch',str(child),'--harness','compact','--timeout',str(timeout)]
        offset=round(time.monotonic()-started,3);process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print(f'{out.name}/{child.name}: started runner PID {process.pid}, offset {offset}s',flush=True)
        stdout,stderr=process.communicate()
        timing={'runner_pid':process.pid,'start_offset_seconds':offset,'end_offset_seconds':round(time.monotonic()-started,3),'exit_code':process.returncode}
        write_json(child/'worker_timing.json',timing)
        (child/'worker_stdout.txt').write_bytes(stdout);(child/'worker_stderr.txt').write_bytes(stderr)
        if process.returncode:raise RuntimeError(f'{out.name}/{child.name} failed; see worker_stderr.txt')
        result=read_json(next(child.glob('agy_calls/*/result.json')));result['scheduler_timing']=timing
        return child,result
    completed={}
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(run,out,child,timeout):(out,child) for out,child,timeout in batches}
        for future in as_completed(futures):
            out,child=futures[future];state=states[out]
            try:
                child,result=future.result();state['results'].append((child,result))
                print(f"{out.name}/{child.name}: {result['elapsed_seconds']}s, {result['state']}",flush=True)
            except RuntimeError as error:state['failures'].append(str(error));print(str(error),flush=True)
            state['processed']+=1
            if state['processed']==state['jobs']:
                completed[out.name]=finish_batch(out,state['manifest'],state['results'],state['failures'],started,args.workers,args.sheets_per_job,state['jobs'])
                print(f"Batch complete: {out.name}, {completed[out.name]['state']}, {completed[out.name]['elapsed_seconds']}s",flush=True)
    elapsed=round(time.monotonic()-started,2)
    if queue_dir:
        calls=[r for state in states.values() for _,r in state['results']]
        combined=combine_queue(queue_dir,inputs) if not args.no_combined_export and all(r['state']=='candidate_exported' for r in completed.values()) else None
        elapsed=round(time.monotonic()-started,2)
        write_json(queue_dir/'queue_result.json',{'elapsed_seconds':elapsed,'workers':args.workers,'jobs':len(batches),'combined_candidate':combined,'combined_export_requested':not args.no_combined_export,
            'samples':sum(len(m['records']) for _,m,_ in inputs),'batches':completed,
            'failures':[f for state in states.values() for f in state['failures']],
            'usage':{k:sum(r['usage'].get(k,0) for r in calls) for k in calls[0]['usage']} if calls else {},
            'timing':'whole shared queue wall clock including per-batch merge/export; excludes preparation','finished_at':utc()})
    print(f'Queue complete: {len(batches)} jobs, {elapsed}s',flush=True)
    if any(state['failures'] for state in states.values()):raise SystemExit('Incomplete batches retained; successful batches exported independently')


if __name__=='__main__':main()
