"""Transactional runtime state; dashboard commands never overwrite annotation state."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sqlite3
import threading


def now():
    return datetime.now(timezone.utc).isoformat()


def pid_alive(pid):
    if not pid:
        return False
    if os.name == 'nt':
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        handle = kernel.OpenProcess(0x1000, False, int(pid))
        if not handle:
            return False
        code = wintypes.DWORD()
        ok = kernel.GetExitCodeProcess(handle, ctypes.byref(code))
        kernel.CloseHandle(handle)
        return bool(ok and code.value == 259)
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False


class Store:
    def __init__(self, run_dir):
        self.run_dir = Path(run_dir).resolve()
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.run_dir/'state.sqlite3'
        self.lock = threading.RLock()
        with self.tx() as db:
            db.executescript('''
              CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS samples(key TEXT PRIMARY KEY, state TEXT NOT NULL,
                role TEXT NOT NULL, group_id TEXT NOT NULL, ready_at TEXT NOT NULL, body TEXT NOT NULL);
              CREATE INDEX IF NOT EXISTS sample_queue ON samples(state,ready_at,group_id);
              CREATE TABLE IF NOT EXISTS workers(key TEXT PRIMARY KEY, body TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS commands(id INTEGER PRIMARY KEY, action TEXT NOT NULL,
                created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', detail TEXT);
              CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, created_at TEXT NOT NULL,
                kind TEXT NOT NULL, body TEXT NOT NULL);
            ''')

    @contextmanager
    def tx(self):
        with self.lock:
            db = sqlite3.connect(self.path, timeout=30)
            db.row_factory = sqlite3.Row
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA busy_timeout=30000')
            try:
                db.execute('BEGIN IMMEDIATE')
                yield db
                db.commit()
            except BaseException:
                db.rollback()
                raise
            finally:
                db.close()

    @staticmethod
    def put_sample(db, row):
        db.execute('INSERT OR REPLACE INTO samples VALUES(?,?,?,?,?,?)',
            (row['source_sample_key'],row['state'],row['stage'],row['group_id'],
             row.get('ready_at',now()),json.dumps(row,ensure_ascii=False)))

    @staticmethod
    def put_meta(db, key, value):
        db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)',(key,json.dumps(value,ensure_ascii=False)))

    def meta(self):
        with self.tx() as db:
            return {r['key']:json.loads(r['value']) for r in db.execute('SELECT * FROM meta')}

    def update_meta(self, **values):
        with self.tx() as db:
            for k,v in values.items():
                self.put_meta(db,k,v)

    def worker(self, key, value=None):
        with self.tx() as db:
            if value is not None:
                db.execute('INSERT OR REPLACE INTO workers VALUES(?,?)',(key,json.dumps(value,ensure_ascii=False)))
            r = db.execute('SELECT body FROM workers WHERE key=?',(key,)).fetchone()
            return json.loads(r[0]) if r else {'worker_id':key,'status':'idle','role':'secondary_chroma',
                'conversation_id':None,'rounds':0,'pid':None,'current_task':None,'history':[]}

    def event(self, kind, **body):
        with self.tx() as db:
            db.execute('INSERT INTO events(created_at,kind,body) VALUES(?,?,?)',
                (now(),kind,json.dumps(body,ensure_ascii=False)))

    def rows(self):
        with self.tx() as db:
            return [json.loads(r[0]) for r in db.execute('SELECT body FROM samples ORDER BY key')]

    def productive_rounds(self,conversation):
        if not conversation:
            return 0
        with self.tx() as db:
            return db.execute("""
                SELECT count(DISTINCT coalesce(json_extract(body,'$.provenance.result_path'),
                    json_extract(body,'$.provenance.packet_id')))
                FROM samples WHERE state='completed' AND json_extract(body,'$.provenance.conversation_id')=?
            """,(conversation,)).fetchone()[0]+db.execute("""
                SELECT count(DISTINCT coalesce(json_extract(body,'$.record.baseline.source.attempt'),json_extract(body,'$.initial_provenance.packet_id'),
                    json_extract(body,'$.initial_provenance.finished_at')))
                FROM samples WHERE json_extract(body,'$.initial_defects') IS NOT NULL
                    AND json_extract(body,'$.initial_provenance.conversation_id')=?
            """,(conversation,)).fetchone()[0]

    def claim(self, role, worker_id, prefer_full=False, allowed_keys=None):
        with self.tx() as db:
            if self.dispatch_held(db):
                return []
            where,params = 'state=?',[role+'_ready']
            reserved = {key for body, in db.execute('SELECT body FROM workers')
                for key in json.loads(body).get('pending_resume',{}).get('keys',[])}
            if reserved:
                where+=' AND key NOT IN ('+','.join('?' for _ in reserved)+')'
                params+=sorted(reserved)
            if allowed_keys is not None:
                if not allowed_keys:return []
                where+=' AND key IN ('+','.join('?' for _ in allowed_keys)+')'
                params+=list(allowed_keys)
            query = 'SELECT group_id FROM samples WHERE '+where+(
                ' GROUP BY group_id ORDER BY count(*) DESC,min(ready_at) LIMIT 1'
                if prefer_full else ' ORDER BY ready_at,key LIMIT 1')
            first = db.execute(query,params).fetchone()
            if not first:
                return []
            rows = [json.loads(r[0]) for r in db.execute(
                'SELECT body FROM samples WHERE '+where+' AND group_id=? ORDER BY key LIMIT 24',
                params+[first[0]])]
            for row in rows:
                row.update(state=role+'_running',worker_id=worker_id)
                self.put_sample(db,row)
            return rows

    def claim_resume(self, worker):
        """Only reclaim this conversation's unfinished packet, never another lane's work."""
        rows=[]
        with self.tx() as db:
            if self.dispatch_held(db):
                return []
            for key in worker.get('pending_resume',{}).get('keys',[]):
                found=db.execute('SELECT body FROM samples WHERE key=?',(key,)).fetchone()
                if not found:
                    continue
                row=json.loads(found[0])
                if row['state']!=row['stage']+'_ready':
                    continue
                row.update(state=row['stage']+'_running',worker_id=worker['worker_id'])
                self.put_sample(db,row);rows.append(row)
        return rows

    @staticmethod
    def dispatch_held(db):
        found=db.execute("SELECT value FROM meta WHERE key='dispatch_hold'").fetchone()
        return bool(found and json.loads(found[0]).get('active'))

    def command(self, action):
        with self.tx() as db:
            if action in ['stop','drain']:
                found=db.execute("SELECT value FROM meta WHERE key='quota_guard'").fetchone()
                guard=json.loads(found[0]) if found else {}
                if guard.get('waiting_for_recovery'):
                    guard.update(manual_hold=True,manual_hold_at=now())
                    self.put_meta(db,'quota_guard',guard)
            if action=='drain':
                # The gate and command commit together, before another claim can succeed.
                self.put_meta(db,'dispatch_hold',{'active':True,'requested_at':now()})
                self.put_meta(db,'phase','draining')
            if action in ['start','continue-blocked','drain']:
                pending = db.execute("SELECT id FROM commands WHERE action=? AND status='pending'",(action,)).fetchone()
                if pending:
                    return pending[0], False
            cur = db.execute('INSERT INTO commands(action,created_at) VALUES(?,?)',(action,now()))
            return cur.lastrowid, True

    def ack(self, command_id, status='acknowledged', detail=''):
        with self.tx() as db:
            db.execute('UPDATE commands SET status=?,detail=? WHERE id=?',(status,detail,command_id))

    def pending_commands(self):
        with self.tx() as db:
            return [dict(r) for r in db.execute("SELECT * FROM commands WHERE status='pending' ORDER BY id")]

    def summary(self):
        with self.tx() as db:
            data = {r['key']:json.loads(r['value']) for r in db.execute('SELECT * FROM meta')}
            counts = {r[0]:r[1] for r in db.execute('SELECT state,count(*) FROM samples GROUP BY state')}
            retries = sum(json.loads(r[0]).get('qa_failures',0) for r in db.execute('SELECT body FROM samples'))
            workers = {r['key']:json.loads(r['body']) for r in db.execute('SELECT * FROM workers')}
            command = db.execute('SELECT * FROM commands ORDER BY id DESC LIMIT 1').fetchone()
            synced = db.execute("SELECT count(*) FROM samples WHERE state IN ('completed','fixed_a')").fetchone()[0]
            # 增量轻量质量缓存：仅当有新样本入库（state_updated_at变动）或缓存缺失时重算并落盘
            qc = data.get('quality_cache')
            state_updated_at = data.get('state_updated_at')
            if not qc or getattr(self, '_last_quality_state_time', None) != state_updated_at:
                c_rows = db.execute("SELECT body FROM samples WHERE state='completed'").fetchall()
                t_c = len(c_rows)
                e_c = sum(1 for r in c_rows if len(json.loads(r[0]).get('defects', [])) == 0)
                tot_d = sum(len(json.loads(r[0]).get('defects', [])) for r in c_rows)
                qc = {
                    'completed': t_c,
                    'empty_count': e_c,
                    'empty_rate': round(e_c / t_c * 100, 2) if t_c else 0.0,
                    'total_defects': tot_d,
                    'avg_defects': round(tot_d / t_c, 2) if t_c else 0.0,
                    'cached_at': now()
                }
                self.put_meta(db, 'quality_cache', qc)
                self._last_quality_state_time = state_updated_at
                data['quality_cache'] = qc
        alive = pid_alive(data.get('owner_pid'))
        heartbeat = data.get('heartbeat_at')
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(heartbeat)).total_seconds() if heartbeat else None
        healthy = alive and age is not None and age < 15
        phase = data.get('phase','unprepared')
        if phase in ['running','pausing','starting','draining'] and not healthy:
            phase = 'unresponsive' if alive else 'interrupted'
        for w in workers.values():
            w['active'] = bool(healthy and w.get('status')=='running' and pid_alive(w.get('pid')))
        data.update(phase=phase,engine_alive=alive,heartbeat_healthy=healthy,heartbeat_age_seconds=age,
            observed_at=now(),workers=workers,last_command=dict(command) if command else None,
            active_calls=sum(w['active'] for w in workers.values()),
            stats={'total':sum(counts.values()),'completed':counts.get('completed',0),
                'fixed_a':counts.get('fixed_a',0),'secondary_ready':counts.get('secondary_chroma_ready',0),
                'initial_ready':counts.get('initial_rgb_ready',0),'running':sum(v for k,v in counts.items() if k.endswith('_running')),
                'needs_manual':counts.get('needs_manual',0),'qa_retries':retries,
                'program_validated':synced,'states':counts})
        if isinstance(data.get('export'),dict):
            data['export'] = {k:v for k,v in data['export'].items() if k!='keys'}
        data.pop('legacy_source_files',None)
        data.pop('code_fingerprint',None)
        return data

    def page(self, page=1, size=50, state='all', query=''):
        size = min(max(size,1),100)
        where,params = [],[]
        if state == 'requeued':
            where.append("json_extract(body,'$.qa_failures')>0 AND state NOT IN ('completed','fixed_a')")
        elif state != 'all':
            where.append('state=?'); params.append(state)
        if query:
            where.append('instr(lower(key),lower(?))>0'); params.append(query)
        clause = ' WHERE '+' AND '.join(where) if where else ''
        with self.tx() as db:
            total = db.execute('SELECT count(*) FROM samples'+clause,params).fetchone()[0]
            page = max(1,min(page,max(1,(total+size-1)//size)))
            rows = [json.loads(r[0]) for r in db.execute('SELECT body FROM samples'+clause+
                ' ORDER BY key LIMIT ? OFFSET ?',params+[size,(page-1)*size])]
        # Image paths, baselines and previous model output stay off the polling endpoint.
        fields = ['source_sample_key','sample_key','state','stage','qa_failures','attempt_count','last_feedback','defects']
        return {'page':page,'size':size,'total':total,'items':[{k:r.get(k) for k in fields} for r in rows]}


class OwnerLock:
    def __init__(self, run_dir):
        self.path = Path(run_dir)/'executor.lock'
        self.stream = None

    def __enter__(self):
        self.stream = self.path.open('a+b')
        self.stream.seek(0); self.stream.write(b'0'); self.stream.flush(); self.stream.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(self.stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(self.stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise RuntimeError('This run already has an executor')
        return self

    def __exit__(self,*args):
        self.stream.close()
