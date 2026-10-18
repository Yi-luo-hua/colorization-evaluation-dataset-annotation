"""One-time activation after an existing executor exits, without cancelling live calls."""
import argparse
from pathlib import Path
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parent))
from pipeline_store import Store,pid_alive,now
from pipeline_engine import Executor,DEFAULT_RUN,SESSION_RETRY_LIMIT
from prepare import read


def activate(store,old_owner):
    attempts={};latest={}
    for row in store.rows():
        native=row.get('provenance') or {}
        worker=native.get('worker_id');finished=native.get('finished_at','')
        if worker and native.get('result_path') and finished>latest.get(worker,''):
            latest[worker]=finished;attempts[worker]=Path(native['result_path']).parent
    while pid_alive(old_owner):
        state=store.summary()
        if state.get('owner_pid') not in [old_owner,None]:
            store.update_meta(retry_policy_activation={'status':'superseded','at':now()});return
        for worker_id,worker in state['workers'].items():
            if worker.get('current_task'):
                attempts[worker_id]=store.run_dir/'attempts'/worker['current_task']
        time.sleep(2)
    state=store.summary()
    if state.get('owner_pid') not in [None,old_owner] or (state.get('last_command') or {}).get('action')=='stop':
        store.update_meta(retry_policy_activation={'status':'ready_next_start','at':now(),'detail':'人工停止或已由其他执行器接管，未自动恢复'});return
    for worker_id,worker in state['workers'].items():
        directory=attempts.get(worker_id)
        if not worker.get('pending_resume') and directory and (directory/'native_result.json').exists():
            native=read(directory/'native_result.json')
            if native.get('session_error') and native.get('conversation_id'):
                worker.update(status='awaiting_continue',pending_resume={'attempt':str(directory),
                    'conversation_id':native['conversation_id'],'keys':[],'reason':native['session_error'],
                    'continue_retries':0,'stopped_at':now()})
                store.worker(worker_id,worker)
    pending=any(w.get('pending_resume') for w in store.summary()['workers'].values())
    store.update_meta(retry_policy_activation={'status':'activated' if pending else 'ready_next_start',
        'at':now(),'old_owner':old_owner,'retry_limit':SESSION_RETRY_LIMIT,'retry_interval_seconds':20})
    if pending:
        Executor(store,workers=state.get('worker_limit',16),auto_resume_pending=True).run(authorized=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old-owner',type=int,required=True)
    parser.add_argument('--run-dir',type=Path,default=DEFAULT_RUN)
    args=parser.parse_args()
    activate(Store(args.run_dir),args.old_owner)
