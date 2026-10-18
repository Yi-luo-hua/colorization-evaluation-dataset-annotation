"""Workflow-owned native /usage reader. Never submits model prompts or annotation work."""
from contextlib import contextmanager
import os
from pathlib import Path
import queue
import re
import sys
import threading
import time
import uuid

from batch_auth import batch_environment

from pipeline_store import Store, now
from update_quota_snapshot import record
from quota_control import observe_quota

PROJECT = Path(__file__).resolve().parents[1]
DEPENDENCIES = PROJECT/'runtime/quota_dependencies'
INTERVAL_SECONDS = 600


def parse_gemini(text):
    group = text.split('GEMINI MODELS',1)[-1] if 'GEMINI MODELS' in text else ''
    group = re.split(r'\n\s*(?:CLAUDE|GPT|OPENAI|OTHER)[ A-Z/&-]*MODELS',group)[0]
    result = {}
    for name,key in [('Five Hour','five_hour'),('Weekly','weekly')]:
        match = re.search(name+r' Limit Remaining\s+[^\n]*?(\d+(?:\.\d+)?)%\s+(?:Refreshes in\s+([^\n]+)|(Quota available))',group)
        if not match:
            raise ValueError('Gemini quota page is incomplete: '+name)
        value = float(match[1])
        if not 0<=value<=100:
            raise ValueError('Invalid Gemini quota percentage')
        result[key] = value
        result['five_reset' if key=='five_hour' else 'weekly_reset'] = (match[2] or match[3]).strip()
    return result


class NativeTerminal:
    def __init__(self, stop, cwd=None):
        sys.path.insert(0,str(DEPENDENCIES))
        import pyte
        from winpty import PtyProcess
        agy = Path.home()/'AppData/Local/agy/bin/agy.exe'
        checks=PROJECT/'runtime/recovery5000_20261016_01/quota_checks'
        checks.mkdir(parents=True,exist_ok=True)
        self.auth_marker=checks/('auth_guard_'+uuid.uuid4().hex+'.json')
        self.proc = PtyProcess.spawn([str(agy),'--model','gemini-3.8-flash-high'],
            cwd=str(cwd or PROJECT.parents[1]),env=batch_environment(self.auth_marker),dimensions=(40,120))
        self.stop = stop
        self.screen = pyte.Screen(120,40)
        self.stream = pyte.Stream(self.screen)
        self.output = queue.Queue()
        self.reader = threading.Thread(target=self._read,daemon=True,name='quota-pty-reader')
        self.reader.start()

    def _read(self):
        try:
            while self.proc.isalive():
                self.output.put(self.proc.read(16384))
        except (EOFError,OSError):
            pass
        finally:
            self.output.put(None)

    def send(self, text):
        self.proc.write(text)

    def wait_for(self, predicate, timeout=30):
        deadline = time.monotonic()+timeout
        while time.monotonic()<deadline:
            if self.stop.is_set():
                raise InterruptedError('Quota monitor is closing')
            if self.auth_marker.exists():
                raise RuntimeError('auth_browser_blocked: 后台额度查询认证失败，已阻止打开登录页；请手动登录 agy 后重试')
            try:
                chunk = self.output.get(timeout=0.1)
            except queue.Empty:
                continue
            if chunk is None:
                raise RuntimeError('Native quota session exited before observation')
            self.stream.feed(chunk)
            text = '\n'.join(self.screen.display)
            if re.search(r'\bGenerating\b',text,re.I):
                self.send('\x1b')
                raise RuntimeError('Unexpected model generation; cancelled quota query')
            if predicate(text):
                return text
        raise TimeoutError('Timed out waiting for native quota UI')

    def close(self):
        # Separate key events: never combine ESC, slash-command text and Enter.
        for key in ['\x1b','\x03','\x03']:
            if not self.proc.isalive():
                break
            self.send(key)
            time.sleep(0.35)
        deadline = time.monotonic()+3
        while self.proc.isalive() and time.monotonic()<deadline:
            time.sleep(0.1)
        self.proc.close(force=True)  # only this owned PTY, never other agy processes
        self.reader.join(timeout=2)


def query_native(stop, terminal_factory=NativeTerminal):
    terminal = terminal_factory(stop)
    try:
        text = terminal.wait_for(lambda s:'for shortcuts' in s or 'esc to' in s.lower())
        if 'for shortcuts' not in text:
            terminal.send('\x1b')
            terminal.wait_for(lambda s:'for shortcuts' in s)
        terminal.send('/usage')
        terminal.wait_for(lambda s:re.search(r'/usage\s+View model quota usage',s) is not None)
        terminal.send('\r')
        terminal.wait_for(lambda s:'Models & Quota' in s and 'GEMINI MODELS' in s)
        terminal.screen.reset()
        terminal.send('\x0c')
        def complete(text):
            try:
                parse_gemini(text)
                return True
            except ValueError:
                return False
        return parse_gemini(terminal.wait_for(complete))
    finally:
        terminal.close()


@contextmanager
def monitor_lock(directory):
    # Separate from executor.lock: quota metadata never owns the annotation executor.
    with (directory/'quota_monitor.lock').open('a+b') as handle:
        handle.seek(0);handle.write(b'0');handle.flush();handle.seek(0)
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield


class QuotaMonitor:
    def __init__(self, store, query=query_native, interval=INTERVAL_SECONDS):
        self.store,self.query,self.interval = store,query,interval
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run,daemon=True,name='workflow-native-quota')

    def metadata(self, **fields):
        with self.store.tx() as db:
            row=db.execute("SELECT value FROM meta WHERE key='quota_monitor'").fetchone()
            import json
            value=json.loads(row[0]) if row else {}
            value.update(fields)
            Store.put_meta(db,'quota_monitor',value)

    def check_once(self):
        try:
            values = self.query(self.stop)
            observation=record(self.store,**values)
        except Exception as exc:
            if not self.stop.is_set():
                record(self.store,error=type(exc).__name__+': '+str(exc))
            return
        try:
            observe_quota(self.store,observation)
        except Exception as exc:
            self.store.event('quota_control_error',error=str(exc))

    def run(self):
        try:
            with monitor_lock(self.store.run_dir):
                self.metadata(mode='workflow_builtin',owner_pid=os.getpid(),enabled=True,
                    automation_id=None,schedule_active=False,interval_minutes=self.interval/60,
                    started_at=now(),next_check_at=now())
                try:
                    while not self.stop.is_set():
                        self.check_once()
                        from datetime import datetime,timedelta,timezone
                        self.metadata(next_check_at=(datetime.now(timezone.utc)+timedelta(seconds=self.interval)).isoformat())
                        self.stop.wait(self.interval)
                finally:
                    self.metadata(enabled=False,owner_pid=None,next_check_at=None)
        except OSError:
            # Another dashboard already owns this runtime's quota monitor.
            return

    def start(self):
        self.thread.start()

    def close(self):
        self.stop.set()
        self.thread.join(timeout=10)

