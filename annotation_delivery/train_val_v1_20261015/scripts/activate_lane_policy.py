"""One-time non-interrupting handover from an already running global-stop executor."""
import argparse
import json
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from prepare import read,write
from pipeline_store import Store,pid_alive,now
from pipeline_engine import Executor,MANUAL_SESSION_FAULTS,DEFAULT_RUN


def classify_workers(workers,attempts):
    """Only collateral cancellations with no native fault may resume automatically."""
    healthy=[];faulted={}
    for worker_id,worker in workers.items():
        pending=worker.get('pending_resume')
        directory=Path(pending['attempt']) if pending else attempts.get(worker_id)
        if not directory or not (directory/'native_result.json').exists():
            continue
        native=read(directory/'native_result.json')
        reason=native.get('session_error')
        if reason in MANUAL_SESSION_FAULTS:
            faulted[worker_id]=(str(directory),reason,native.get('conversation_id'))
        elif pending and native.get('started') and not reason and pending.get('conversation_id'):
            healthy.append(worker_id)
    return healthy,faulted


def activate(store,old_owner):
    # A fully written result may still accompany a real native fault and leave no pending packet.
    attempts={};latest={}
    for row in store.rows():
        native=row.get('provenance') or {}
        worker_id=native.get('worker_id');finished=native.get('finished_at','')
        if worker_id and native.get('result_path') and finished>latest.get(worker_id,''):
            latest[worker_id]=finished;attempts[worker_id]=Path(native['result_path']).parent
    while pid_alive(old_owner):
        state=store.summary()
        if state.get('owner_pid') not in [old_owner,None]:
            store.update_meta(policy_activation={'status':'superseded','at':now()});return
        for worker_id,worker in state['workers'].items():
            if worker.get('current_task'):
                attempts[worker_id]=store.run_dir/'attempts'/worker['current_task']
        time.sleep(2)
    state=store.summary()
    if (state.get('owner_pid') not in [None,old_owner] or state.get('stop_reason') not in MANUAL_SESSION_FAULTS
            or (state.get('last_command') or {}).get('action')=='stop'):
        store.update_meta(policy_activation={'status':'ready_next_start','at':now(),
            'detail':'旧执行器自然结束或人工停止；未自动恢复'});return
    healthy,faulted=classify_workers(state['workers'],attempts)
    for worker_id,(directory,reason,conversation) in faulted.items():
        worker=state['workers'][worker_id]
        if not worker.get('pending_resume'):
            worker['pending_resume']={'attempt':directory,'conversation_id':conversation,'keys':[],
                'reason':reason,'stopped_at':now()}
        worker['pending_resume']['reason']=reason
        worker.update(status='awaiting_continue',last_session_error=reason)
        store.worker(worker_id,worker)
    report={'status':'activated' if healthy else 'ready_next_start','at':now(),
        'old_owner':old_owner,'collateral_sessions_resumed':healthy,'faulted_sessions_kept_paused':list(faulted)}
    write(store.run_dir/'lane_policy_handover_20261017.json',report)
    store.update_meta(policy_activation=report)
    if healthy:
        # Preserve original packets/CIDs; known failures are explicitly excluded.
        Executor(store,workers=state.get('worker_limit',16),resume_workers=healthy).run(authorized=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir',type=Path,default=DEFAULT_RUN)
    parser.add_argument('--old-owner',type=int,required=True)
    args=parser.parse_args()
    activate(Store(args.run_dir),args.old_owner)
