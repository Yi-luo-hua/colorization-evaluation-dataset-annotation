"""Read-only live status; sample-wide dashboard statistics refresh separately."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import sqlite3
import threading

from pipeline_store import now, pid_alive


class DashboardState:
    def __init__(self, store):
        self.store = store
        self.stopped = threading.Event()
        self.metrics = None
        self.metrics_error = None
        self.refresh_metrics()

    @contextmanager
    def read(self):
        db = sqlite3.connect(self.store.path.as_uri()+'?mode=ro', uri=True)
        try:
            db.row_factory = sqlite3.Row
            db.execute('BEGIN')
            yield db
        finally:
            db.close()

    def refresh_metrics(self):
        with self.read() as db:
            found = db.execute("SELECT value FROM meta WHERE key='state_updated_at'").fetchone()
            revision = json.loads(found[0]) if found else None
            if self.metrics and self.metrics['revision'] == revision:
                return
            retries = completed = empty = defects = 0
            progress, productions = {}, {}
            for state, body in db.execute('SELECT state,body FROM samples'):
                row = json.loads(body)
                retries += row.get('qa_failures', 0)
                stages = []
                if state == 'completed':
                    completed += 1
                    defects += len(row.get('defects', []))
                    empty += not row.get('defects', [])
                    native = row.get('provenance', {})
                    stages.append(('secondary', native, native.get('result_path') or native.get('packet_id')))
                if row.get('initial_defects') is not None:
                    native = row.get('initial_provenance', {})
                    packet = row.get('record', {}).get('baseline', {}).get('source', {}).get('attempt')
                    stages.append(('initial', native, packet or native.get('packet_id') or native.get('finished_at')))
                for stage, native, packet in stages:
                    worker = native.get('worker_id')
                    if worker:
                        progress.setdefault(worker, {'initial': 0, 'secondary': 0})[stage] += 1
                    conversation = native.get('conversation_id')
                    if conversation and packet:
                        productions.setdefault(conversation, set()).add((stage, packet))
        self.metrics = {'revision': revision, 'qa_retries': retries, 'worker_progress': progress,
            'productions': {key: len(value) for key, value in productions.items()},
            'quality_cache': {'completed': completed, 'empty_count': empty,
                'empty_rate': round(empty / completed * 100, 2) if completed else 0.0,
                'total_defects': defects, 'avg_defects': round(defects / completed, 2) if completed else 0.0,
                'cached_at': now()}}
        self.metrics_error = None

    def start(self):
        def refresh():
            while not self.stopped.wait(1):
                try:
                    self.refresh_metrics()
                except (sqlite3.Error, ValueError, TypeError) as exc:
                    self.metrics_error = str(exc)
        self.thread = threading.Thread(target=refresh, name='dashboard-statistics', daemon=True)
        self.thread.start()

    def close(self):
        self.stopped.set()
        self.thread.join(timeout=2)

    def summary(self):
        with self.read() as db:
            data = {r['key']: json.loads(r['value']) for r in db.execute(
                "SELECT * FROM meta WHERE key NOT IN ('legacy_source_files','code_fingerprint')")}
            counts = dict(db.execute('SELECT state,count(*) FROM samples GROUP BY state'))
            workers = {r['key']: json.loads(r['body']) for r in db.execute('SELECT * FROM workers')}
            command = db.execute('SELECT * FROM commands ORDER BY id DESC LIMIT 1').fetchone()
        alive = pid_alive(data.get('owner_pid'))
        heartbeat = data.get('heartbeat_at')
        age = (datetime.now(timezone.utc)-datetime.fromisoformat(heartbeat)).total_seconds() if heartbeat else None
        healthy = alive and age is not None and age < 15
        phase = data.get('phase', 'unprepared')
        if phase in ['running', 'pausing', 'starting', 'draining'] and not healthy:
            phase = 'unresponsive' if alive else 'interrupted'
        metrics = self.metrics
        for worker in workers.values():
            worker['active'] = bool(healthy and worker.get('status') == 'running' and pid_alive(worker.get('pid')))
            worker['productive_rounds'] = metrics['productions'].get(worker.get('conversation_id'), 0)
        data.update(phase=phase, engine_alive=alive, heartbeat_healthy=healthy, heartbeat_age_seconds=age,
            observed_at=now(), workers=workers, last_command=dict(command) if command else None,
            active_calls=sum(w['active'] for w in workers.values()),
            stats={'total': sum(counts.values()), 'completed': counts.get('completed', 0),
                'fixed_a': counts.get('fixed_a', 0), 'secondary_ready': counts.get('secondary_chroma_ready', 0),
                'initial_ready': counts.get('initial_rgb_ready', 0),
                'running': sum(v for k, v in counts.items() if k.endswith('_running')),
                'needs_manual': counts.get('needs_manual', 0), 'qa_retries': metrics['qa_retries'],
                'program_validated': counts.get('completed', 0)+counts.get('fixed_a', 0), 'states': counts},
            quality_cache=metrics['quality_cache'], worker_progress=metrics['worker_progress'],
            statistics={'updated_at': metrics['quality_cache']['cached_at'],
                'refreshing': metrics['revision'] != data.get('state_updated_at'), 'error': self.metrics_error})
        if isinstance(data.get('export'), dict):
            data['export'] = {k: v for k, v in data['export'].items() if k != 'keys'}
        return data
