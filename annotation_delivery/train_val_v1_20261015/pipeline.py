"""Unified CLI. Preparation never launches model calls."""
import argparse
import json
from pathlib import Path
import sys

PROJECT = Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT/'scripts'))
from pipeline_store import Store, OwnerLock
from pipeline_engine import DEFAULT_RUN, LEGACY_BATCH, Executor, migrate_batch, load_inventory, preflight, recover_interrupted, snapshot
import pipeline_delivery


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','check','status','reconcile','run','resume','pause','drain','dashboard','export','sync','load'])
    parser.add_argument('--run-dir',type=Path,default=DEFAULT_RUN)
    parser.add_argument('--batch-dir',type=Path,default=LEGACY_BATCH)
    parser.add_argument('--inventory',type=Path)
    parser.add_argument('--verify-images',action='store_true')
    parser.add_argument('--workers',type=int,default=16)
    parser.add_argument('--model',choices=['gemini-3.8-flash-high','gemini-3.8-flash-medium'])
    parser.add_argument('--maximum-batches',type=int,help='Bounded one-worker trial; never starts the full queue')
    parser.add_argument('--sample-scope',type=Path,help='JSON list of allowed sample identities for a scoped trial')
    parser.add_argument('--port',type=int,default=8899)
    parser.add_argument('--execute-authorized-run',action='store_true',help='Explicitly enable actual model calls')
    parser.add_argument('--continue-blocked',action='store_true',help='Manually continue preserved failed conversations in their original packets')
    parser.add_argument('--resume-workers',nargs='+',help='Resume only lanes interrupted by a controlled implementation update')
    parser.add_argument('--resume-retry-offsets',type=json.loads,help='Preserve per-lane retry indices during that handover')
    args = parser.parse_args()
    if args.command in ['run','resume']:
        if not args.execute_authorized_run:
            parser.error('run/resume requires --execute-authorized-run; no model was called')
        store = Store(args.run_dir)
        try:
            allowed=json.loads(args.sample_scope.read_text(encoding='utf-8')) if args.sample_scope else None
            Executor(store,args.workers,model=args.model,maximum_batches=args.maximum_batches,sample_scope=allowed,
                continue_blocked=args.continue_blocked,resume_workers=args.resume_workers,
                resume_retry_offsets=args.resume_retry_offsets).run(authorized=True)
        except Exception as exc:
            for command in store.pending_commands():
                if command['action']=='start':
                    store.ack(command['id'],'failed',str(exc))
            raise
        return
    if args.command=='dashboard':
        from dashboard_server import serve
        serve(args.run_dir,args.port)
        return
    store = Store(args.run_dir)
    if args.command=='status':
        result = store.summary()
    elif args.command in ['pause','drain']:
        state=store.summary()
        if args.command=='drain' and (not state['engine_alive'] or
                state.get('dispatch_control')!={'version':1,'owner_pid':state.get('owner_pid')}):
            parser.error('drain requires a running executor with dispatch_control version 1; no command was sent')
        identifier = store.command('drain' if args.command=='drain' else 'stop')[0]
        if not store.summary()['engine_alive']:
            store.ack(identifier,detail='没有在运行的执行器')
        result = {'command_id':identifier}
    else:
        with OwnerLock(args.run_dir):
            if args.command=='prepare':
                store = migrate_batch(args.run_dir,args.batch_dir)
            elif args.command=='load':
                if not args.inventory:
                    parser.error('load requires --inventory')
                store = load_inventory(args.run_dir,args.inventory)
            elif args.command=='reconcile':
                recover_interrupted(store)
                pipeline_delivery.export(store)
            elif args.command=='export':
                pipeline_delivery.export(store)
            elif args.command=='sync':
                pipeline_delivery.export(store)
                pipeline_delivery.sync(store)
            if args.command in ['prepare','check','load','reconcile']:
                preflight(store,args.verify_images)
            snapshot(store)
            result = store.summary()
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
