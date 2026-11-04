"""Local human A-review server; independent SQLite decisions and append-only history."""
import argparse
from contextlib import contextmanager,closing
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import sqlite3
import threading
from urllib.parse import urlparse,parse_qs

from fit import fit_model
from prepare_candidates import HERE,ROOT,LOCAL,write,sha


class ReviewStore:
    def __init__(self,folder,manifest_path=None):
        self.folder = Path(folder); self.folder.mkdir(exist_ok=True,parents=True)
        self.manifest_path = Path(manifest_path or LOCAL/'manifest.json')
        self.manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
        self.records = {r['id']:r for r in self.manifest['records']}
        self.lock = threading.RLock()
        self.db = self.folder/'judgments.sqlite3'
        with self.connect() as c:
            c.execute('create table if not exists judgments (id text primary key,label text not null,updated_at text not null)')
            c.execute('create table if not exists events (revision integer primary key autoincrement,at text not null,body text not null)')
            c.execute('create table if not exists meta (key text primary key,value text not null)')
            digest = sha(self.manifest_path)
            old = c.execute("select value from meta where key='manifest_sha256'").fetchone()
            if old and old[0]!=digest: raise ValueError('Review queue changed; keep the existing human judgments with their original manifest.')
            c.execute('insert or ignore into meta values (?,?)',('manifest_sha256',digest))

    @contextmanager
    def connect(self):
        with closing(sqlite3.connect(self.db,timeout=20)) as connection:
            with connection:
                yield connection

    def state(self):
        with self.connect() as c:
            labels = {i:{'label':label,'updated_at':at} for i,label,at in c.execute('select id,label,updated_at from judgments')}
            revision = c.execute('select coalesce(max(revision),0) from events').fetchone()[0]
        counts = {k:sum(r['label']==k for r in labels.values()) for k in ['A','not_A','unsure']}
        counts.update(total=len(self.records),pending=len(self.records)-len(labels),reviewed=len(labels))
        return {'labels':labels,'revision':revision,'counts':counts}

    def decide(self,ids,label):
        if label not in ['A','not_A','unsure'] or not ids or len(ids)>100:
            raise ValueError('请选择1—100张并指定A、非A或待定')
        if len(ids)!=len(set(ids)) or any(i not in self.records for i in ids):
            raise ValueError('候选编号无效')
        at = datetime.now(timezone.utc).isoformat()
        with self.lock,self.connect() as c:
            before = {i:(c.execute('select label from judgments where id=?',(i,)).fetchone() or [None])[0] for i in ids}
            c.executemany('insert or replace into judgments values (?,?,?)',[(i,label,at) for i in ids])
            cur = c.execute('insert into events (at,body) values (?,?)',(at,json.dumps({'kind':'decision','before':before,'after':label})))
            rev = cur.lastrowid
        self.backup()
        return {**self.state(),'undo_revision':rev}

    def undo(self,revision):
        with self.lock,self.connect() as c:
            latest = c.execute('select revision,body from events order by revision desc limit 1').fetchone()
            if not latest or latest[0]!=revision: raise ValueError('记录已变化，请刷新后查看最新状态')
            event = json.loads(latest[1])
            if event['kind']!='decision': raise ValueError('最近记录已撤销')
            at = datetime.now(timezone.utc).isoformat()
            for i,label in event['before'].items():
                if label is None: c.execute('delete from judgments where id=?',(i,))
                else: c.execute('insert or replace into judgments values (?,?,?)',(i,label,at))
            c.execute('insert into events (at,body) values (?,?)',(at,json.dumps({'kind':'undo','target':revision})))
        self.backup()
        return self.state()

    def backup(self):
        # SQLite is the source of truth; snapshots provide a simple portable copy.
        with self.lock:
            write(self.folder/'judgments_backup.json',self.state())

    def fit(self):
        with self.lock:
            state = self.state()
            result = fit_model(self.manifest,state['labels'],state['revision'])
            result['manifest_sha256'] = sha(self.manifest_path)
            result['input_labels_sha256'] = __import__('hashlib').sha256(json.dumps(state['labels'],sort_keys=True).encode()).hexdigest()
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            (self.folder/'fits').mkdir(exist_ok=True)
            write(self.folder/'fits'/f'fit_{stamp}.json',result)
            write(self.folder/'latest_fit.json',result)
            return result


def handler_for(store):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args): pass

        def send(self,value,status=200,content_type='application/json; charset=utf-8'):
            raw = json.dumps(value,ensure_ascii=False).encode() if isinstance(value,(dict,list)) else value
            self.send_response(status)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self'; frame-ancestors 'self'")
            self.end_headers(); self.wfile.write(raw)

        def do_GET(self):
            route = urlparse(self.path)
            if route.path=='/': return self.send((HERE/'index.html').read_bytes(),content_type='text/html; charset=utf-8')
            if route.path=='/favicon.ico': return self.send(b'',204,'image/x-icon')
            if route.path=='/api/state':
                # Numerical feature/tier/holdout details are hidden from the default review view.
                order = {'core':0,'near':1,'boundary':2,'contrast':3}
                prioritized = sorted(store.manifest['records'],key=lambda r:(order[r['tier']],r['id']))
                records = [{k:r[k] for k in ['id','model','split','source_sample_key']} for r in prioritized]
                return self.send({**store.state(),'records':records,'scan':{k:v for k,v in store.manifest.items() if k in ['scanned','source_rows','candidate_bucket_counts','evaluation_partition_excluded']}})
            if route.path=='/api/features':
                return self.send([{k:r[k] for k in ['id','mean_C','var_ab']} for r in store.manifest['records']])
            if route.path=='/api/export':
                return self.send({'manifest_sha256':sha(store.manifest_path),'scope':store.manifest['review_role'],**store.state()})
            if route.path=='/api/model':
                path = store.folder/'latest_fit.json'
                return self.send(json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'status':'awaiting_human_labels','thresholds':None})
            if route.path=='/image':
                query = parse_qs(route.query); key = query.get('id',[''])[0]; kind = query.get('kind',['generated'])[0]
                if key not in store.records or kind not in ['generated','GT']: return self.send({'error':'图片不存在'},404)
                rec = store.records[key]
                path = (ROOT/rec['model_path' if kind=='generated' else 'gt_path']).resolve()
                if not path.is_relative_to(ROOT.resolve()): return self.send({'error':'路径无效'},400)
                if not path.exists(): return self.send({'error':'原图不可用'},404)
                return self.send(path.read_bytes(),content_type=mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
            return self.send({'error':'页面不存在'},404)

        def do_POST(self):
            origin = self.headers.get('Origin')
            if origin and origin not in [f'http://{self.headers.get("Host")}']:
                return self.send({'error':'仅接受本页面请求'},403)
            if not self.headers.get('Content-Type','').startswith('application/json'):
                return self.send({'error':'需要JSON请求'},415)
            length = int(self.headers.get('Content-Length','0'))
            if length>100000: return self.send({'error':'请求过大'},413)
            try:
                body = json.loads(self.rfile.read(length))
                if self.path=='/api/decide': return self.send(store.decide(body['ids'],body['label']))
                if self.path=='/api/undo': return self.send(store.undo(int(body['revision'])))
                if self.path=='/api/fit': return self.send(store.fit())
                return self.send({'error':'接口不存在'},404)
            except (ValueError,KeyError,TypeError) as exc:
                return self.send({'error':str(exc)},400)
    return Handler


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port',type=int,default=8092)
    p.add_argument('--data-dir',type=Path,default=LOCAL)
    p.add_argument('--manifest',type=Path)
    args = p.parse_args()
    store = ReviewStore(args.data_dir,args.manifest)
    print(f'A review ready at http://localhost:{args.port}/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),handler_for(store)).serve_forever()


if __name__=='__main__': main()
