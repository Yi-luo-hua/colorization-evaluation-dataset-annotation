"""Global quota pause; native five-hour recovery may resume, weekly exhaustion requires a human."""
import json
import re
import subprocess

from pipeline_store import Store,now,pid_alive
from prepare import ROOT


def explicit_exhaustion(text):
    # HTTP 429 alone may be throttling rather than a depleted allowance.
    return bool(re.search(r'RESOURCE_EXHAUSTED|Individual quota reached|exhausted your capacity|quota exceeded',text,re.I))


def zero_windows(snapshot):
    return [name for name in ['five_hour','weekly']
        if isinstance(snapshot.get(name+'_remaining_percent'),(float,int))
        and snapshot[name+'_remaining_percent']==0]


def recovered(meta,guard):
    snapshot=meta.get('quota_snapshot') or {}
    monitor=meta.get('quota_monitor') or {}
    return bool(snapshot.get('source')=='native agy /usage' and not monitor.get('last_error')
        and snapshot.get('checked_at','')>guard.get('last_exhaustion_at',guard.get('triggered_at',''))
        and all(isinstance(snapshot.get(k+'_remaining_percent'),(float,int))
            and snapshot[k+'_remaining_percent']>0 for k in ['five_hour','weekly']))


def pause_for_quota(store,evidence,source,force=False):
    with store.tx() as db:
        meta={k:json.loads(v) for k,v in db.execute('SELECT key,value FROM meta')}
        guard=meta.get('quota_guard') or {'enabled':True}
        if not guard.get('enabled',True):return False
        active=pid_alive(meta.get('owner_pid'))
        if not active and not guard.get('waiting_for_recovery') and not force:
            return False  # Observing quota must not restart an independently paused workflow.
        windows=zero_windows(evidence)
        first=not guard.get('waiting_for_recovery')
        if first:
            workers={k:json.loads(v) for k,v in db.execute('SELECT key,body FROM workers')}
            interrupted={k:w for k,w in workers.items() if w.get('status') in ['running','retry_wait']}
            for key in ['recovery_observed_at','resuming_at','resumed_executor_pid','last_resume_error']:
                guard.pop(key,None)
            guard.update(waiting_for_recovery=True,triggered_at=now(),manual_hold=False,weekly_manual_hold=False,
                trigger_snapshot=evidence if evidence.get('source')=='native agy /usage' else None,
                zero_windows=windows,
                resume_workers=list(interrupted),resume_retry_offsets={
                    k:w.get('retry_count',0) for k,w in interrupted.items() if w.get('retry_count',0)>0})
        guard.update(enabled=True,source=source,evidence=evidence,observed_at=now(),
            last_exhaustion_at=now(),auto_resume=True,
            five_hour_resume='automatic_after_native_recovery',weekly_resume='manual_account_switch')
        if 'weekly' in windows:guard['weekly_manual_hold']=True
        guard['zero_windows']=windows or guard.get('zero_windows',[])
        if active and first:
            command=db.execute("INSERT INTO commands(action,created_at) VALUES('quota-stop',?)",(now(),))
            guard['quota_stop_command_id']=command.lastrowid
        elif not active:
            Store.put_meta(db,'phase','quota_waiting')
            Store.put_meta(db,'stop_reason','quota_exhausted')
        Store.put_meta(db,'quota_guard',guard)
    if first:store.event('quota_global_pause',source=source,evidence=evidence)
    return True


def cancel_automatic_resume(store):
    with store.tx() as db:
        found=db.execute("SELECT value FROM meta WHERE key='quota_guard'").fetchone()
        guard=json.loads(found[0]) if found else {}
        if guard.get('waiting_for_recovery'):
            guard.update(manual_hold=True,manual_hold_at=now())
            Store.put_meta(db,'quota_guard',guard)


def allow_requested_start(store):
    """Only a requested start may release a weekly/manual hold, after fresh native confirmation."""
    meta=store.meta();guard=meta.get('quota_guard') or {'enabled':True}
    if not guard.get('enabled',True):return True
    if guard.get('waiting_for_recovery'):
        if recovered(meta,guard):
            guard.update(waiting_for_recovery=False,weekly_manual_hold=False,manual_hold=False,
                manually_released_at=now())
            store.update_meta(quota_guard=guard)
            for command in store.pending_commands():
                if command['action']=='quota-stop':
                    store.ack(command['id'],detail='额度暂停已完成；新额度已由原生查询确认')
            return True
        guard['manual_hold']=False  # A new request permits five-hour recovery, never weekly auto-resume.
        store.update_meta(quota_guard=guard)
    elif not zero_windows(meta.get('quota_snapshot') or {}):
        return True
    pause_for_quota(store,meta.get('quota_snapshot') or {},'requested_start',force=True)
    for command in store.pending_commands():
        if command['action']=='start':store.ack(command['id'],detail='额度仍不可用；保留任务等待原生额度恢复')
    return False


def observe_quota(store,observation,launcher=None):
    """Called only after /usage. Never submits a model prompt to probe recovery."""
    if observation.get('error') or not observation.get('snapshot'):return
    snapshot=observation['snapshot']
    if zero_windows(snapshot):
        pause_for_quota(store,snapshot,'native agy /usage')
        return
    with store.tx() as db:
        meta={k:json.loads(v) for k,v in db.execute('SELECT key,value FROM meta')}
        guard=meta.get('quota_guard') or {}
        if meta.get('dispatch_hold',{}).get('active'):return
        if not guard.get('waiting_for_recovery') or not recovered(meta,guard):return
        guard.update(recovery_observed_at=snapshot['checked_at'])
        Store.put_meta(db,'quota_guard',guard)
    if guard.get('weekly_manual_hold') or guard.get('manual_hold') or not guard.get('auto_resume',True):return
    if pid_alive(meta.get('owner_pid')):return
    workers=store.summary()['workers']
    if any(pid_alive(w.get('pid')) for w in workers.values()):return
    for command in store.pending_commands():
        if command['action']=='stop':return
    resume=[k for k,w in workers.items() if w.get('pending_resume') and (
        k in guard.get('resume_workers',[]) or w['pending_resume'].get('reason')=='quota_exhausted')]
    offsets={k:n for k,n in guard.get('resume_retry_offsets',{}).items() if k in resume and n>0}
    command=[__import__('sys').executable,'-X','utf8',str(ROOT/'pipeline.py'),'resume',
        '--run-dir',str(store.run_dir),'--execute-authorized-run']
    if resume:command+=['--resume-workers',*resume]
    if offsets:command+=['--resume-retry-offsets',json.dumps(offsets)]
    with store.tx() as db:
        current={k:json.loads(v) for k,v in db.execute('SELECT key,value FROM meta')}
        latest=current.get('quota_guard') or {}
        if current.get('dispatch_hold',{}).get('active'):return
        if not latest.get('waiting_for_recovery') or latest.get('manual_hold') or latest.get('weekly_manual_hold'):return
        if not recovered(current,latest):return
        guard=latest
        guard.update(waiting_for_recovery=False,resuming_at=now())
        Store.put_meta(db,'quota_guard',guard)
        Store.put_meta(db,'phase','starting')
    identifier=store.command('start')[0]
    for pending in store.pending_commands():
        if pending['action']=='quota-stop':
            store.ack(pending['id'],detail='全部调用已退出，额度已恢复')
    try:
        with (store.run_dir/'executor.log').open('ab') as log:
            proc=(launcher or subprocess.Popen)(command,cwd=str(ROOT),stdout=log,stderr=log,
                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        with store.tx() as db:
            latest=json.loads(db.execute("SELECT value FROM meta WHERE key='quota_guard'").fetchone()[0])
            if latest.get('resuming_at')==guard.get('resuming_at') and not latest.get('waiting_for_recovery'):
                latest['resumed_executor_pid']=proc.pid
            Store.put_meta(db,'quota_guard',latest)
        store.event('quota_recovery_resume_requested',pid=proc.pid,command_id=identifier,
            resume_workers=resume,check_id=snapshot.get('check_id'))
    except Exception as exc:
        with store.tx() as db:
            latest=json.loads(db.execute("SELECT value FROM meta WHERE key='quota_guard'").fetchone()[0])
            latest.update(waiting_for_recovery=True,last_resume_error=str(exc))
            Store.put_meta(db,'quota_guard',latest)
            Store.put_meta(db,'phase','quota_waiting')
        store.ack(identifier,'failed',str(exc))
        raise
