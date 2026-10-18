"""Local dashboard: read authoritative state and enqueue acknowledged commands."""
import argparse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlparse, parse_qs

PROJECT = Path(__file__).resolve().parent
sys.path.insert(0,str(PROJECT/'scripts'))
from pipeline_store import Store, pid_alive
from dashboard_state import DashboardState
from pipeline_engine import DEFAULT_RUN
import pipeline_delivery


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self,*args,store,snapshot=None,launcher=subprocess.Popen,**kwargs):
        self.store,self.launcher = store,launcher
        self.snapshot = snapshot or DashboardState(store)
        super().__init__(*args,directory=str(PROJECT/'web'),**kwargs)

    def reply(self,status,value):
        body = json.dumps(value,ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path)
        try:
            if route.path=='/favicon.ico':
                self.send_response(204);self.end_headers();return
            if route.path.startswith('/api/action/'):
                return self.reply(405,{'error':'Controls require POST'})
            if route.path=='/api/status':
                state=self.snapshot.summary()
                state.update(dashboard_contract='sqlite_runtime_dashboard_v1',run_id=self.store.run_dir.name)
                return self.reply(200,state)
            if route.path=='/api/samples':
                query = parse_qs(route.query)
                value = lambda k,d:query.get(k,[d])[0]
                return self.reply(200,self.store.page(int(value('page',1)),int(value('size',50)),value('state','all'),value('query','')))
            if route.path=='/api/import-preview':
                query=parse_qs(route.query)
                selection={k:v[0] for k,v in query.items() if k in ['split','model','start','end']}
                return self.reply(200,pipeline_delivery.select_rows(self.store,selection)[1])
            if route.path.startswith('/api/'):
                return self.reply(404,{'error':'Unknown endpoint'})
            return super().do_GET()
        except ValueError as exc:
            self.reply(400,{'error':str(exc)})
        except Exception as exc:
            self.reply(503,{'error':type(exc).__name__+': '+str(exc)})

    def do_POST(self):
        origin = self.headers.get('Origin')
        host = self.headers.get('Host')
        if host not in [f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}'] or (origin and urlparse(origin).netloc!=host):
            return self.reply(403,{'error':'Local same-origin controls only'})
        action = urlparse(self.path).path.removeprefix('/api/action/')
        if self.path!='/api/action/'+action or action not in ['start','stop','drain','continue-blocked','import']:
            return self.reply(404,{'error':'Unknown control'})
        try:
            state = self.snapshot.summary()
            draining=bool(state.get('dispatch_hold',{}).get('active'))
            if action=='drain':
                capability=state.get('dispatch_control',{})
                if not state['engine_alive']:
                    return self.reply(409,{'error':'当前没有运行中的执行器'})
                if capability.get('version')!=1 or capability.get('owner_pid')!=state.get('owner_pid'):
                    return self.reply(409,{'error':'当前执行器尚未加载等待结束功能；下次启动后生效，未打断当前调用'})
                identifier,created=self.store.command('drain')
                return self.reply(202,{'command_id':identifier,'created':created,'status':'已停止派发，等待在途结束'})
            if action in ['start','continue-blocked'] and state['engine_alive'] and draining:
                return self.reply(409,{'error':'已停止派发，正在等待在途结束；结束后可继续'})
            if action=='import':
                length=int(self.headers.get('Content-Length','0'))
                if length>4096:
                    return self.reply(400,{'error':'导入范围请求过大'})
                selection=json.loads(self.rfile.read(length) or b'{}')
                preview=pipeline_delivery.queue_import(self.store,selection)
                return self.reply(202,{'status':'queued','selection':preview})
            if action in ['start','continue-blocked']:
                if state['engine_alive']:
                    if action=='continue-blocked':
                        if state.get('session_fault_policy') not in ['pause_faulted_lane_manual_continue_v2','continue_three_then_pool_v3','continue_five_then_pool_v4']:
                            return self.reply(409,{'error':'当前执行器仍为旧策略，等待本轮结束后再续接；未打断运行'})
                        if not any(w.get('pending_resume') and not w.get('active') and w.get('status')!='retry_wait' for w in state['workers'].values()):
                            return self.reply(409,{'error':'当前没有等待手动继续的异常会话'})
                        identifier,created=self.store.command('continue-blocked')
                        return self.reply(202,{'command_id':identifier,'created':created,'status':'queued; healthy lanes keep running'})
                    return self.reply(409,{'error':'Executor already exists; inspect heartbeat before restarting'})
                if not state.get('preflight',{}).get('ready') or not state['stats']['total']:
                    return self.reply(409,{'error':'Prepare and check the run first'})
                if not (state['stats']['secondary_ready']+state['stats']['initial_ready']+state['stats']['running']):
                    return self.reply(409,{'error':'No resumable samples'})
                pending=[w for w in state['workers'].values() if w.get('pending_resume')]
                reserved={key for w in pending for key in w['pending_resume']['keys']}
                dispatchable=any(r['state'].endswith('_ready') and r['source_sample_key'] not in reserved for r in self.store.rows())
                if action=='start' and pending and not dispatchable:
                    return self.reply(409,{'error':'异常会话已保留，请点击“继续异常会话”'})
                if action=='continue-blocked' and not pending:
                    return self.reply(409,{'error':'当前没有等待手动继续的异常会话'})
                identifier,created = self.store.command('start')
                if created:
                    try:
                        with (self.store.run_dir/'executor.log').open('ab') as log:
                            command=[sys.executable,'-X','utf8',str(PROJECT/'pipeline.py'),'resume',
                                '--run-dir',str(self.store.run_dir),'--execute-authorized-run']
                            if action=='continue-blocked':
                                command+=['--continue-blocked']
                            proc = self.launcher(command,
                                cwd=str(PROJECT),stdout=log,stderr=log,
                                creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
                        self.store.event('executor_spawn_requested',pid=proc.pid,command_id=identifier)
                    except Exception:
                        self.store.ack(identifier,'failed','Executor could not be launched')
                        raise
            else:
                identifier,created = self.store.command('stop')
                if not state['engine_alive']:
                    self.store.ack(identifier,detail='当前没有执行器；没有修改任何标注状态')
            self.reply(202,{'command_id':identifier,'created':created,'status':'queued; await executor acknowledgment'})
        except ValueError as exc:
            self.reply(400,{'error':str(exc)})
        except Exception as exc:
            self.reply(503,{'error':type(exc).__name__+': '+str(exc)})

    def log_message(self,*args):
        pass


def serve(run_dir=DEFAULT_RUN,port=8899):
    from native_quota_monitor import QuotaMonitor
    store = Store(run_dir)
    snapshot = DashboardState(store)
    snapshot.start()
    server = ThreadingHTTPServer(('127.0.0.1',port),partial(DashboardHandler,store=store,snapshot=snapshot))
    quota = QuotaMonitor(store)
    quota.start()
    print(f'Dashboard http://127.0.0.1:{port} | {Path(run_dir).resolve()}',flush=True)
    try:
        server.serve_forever()
    finally:
        quota.close()
        snapshot.close()
        server.server_close()


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,default=DEFAULT_RUN)
    parser.add_argument('--port',type=int,default=8899)
    args = parser.parse_args()
    serve(args.run_dir,args.port)
