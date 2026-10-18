"""Offline regression checks using copied real records and a fake native process. Zero AI calls."""
import copy
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from http.server import ThreadingHTTPServer
import json
import os
import subprocess
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error
import uuid

PROJECT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PROJECT),str(PROJECT/'scripts')]
from prepare import read,write
from pipeline_store import Store,OwnerLock,now
from pipeline_engine import Executor,initialize,LEGACY_BATCH,recover_interrupted,failure_kind,preflight,return_for_review
from review_contract import validate_file,validate_entry
import pipeline_delivery
from dashboard_server import DashboardHandler


class OfflineChecks(unittest.TestCase):
    def setUp(self):
        retry_delay=patch.object(Executor,'RETRY_DELAY_SECONDS',0)
        retry_delay.start();self.addCleanup(retry_delay.stop)
        receipts=patch('pipeline_engine.read_visual_receipts',lambda conv,sheets:{
            'seen':[s['path'] for s in sheets],'missing':[],'source':'offline native read fixture'})
        receipts.start();self.addCleanup(receipts.stop)
        # Never use the real local PAT during simulated executor checks.
        guard=patch.object(pipeline_delivery,'access_token',lambda base:os.environ.get('LABEL_STUDIO_API_KEY'))
        guard.start();self.addCleanup(guard.stop)
        environment=patch.dict(os.environ,{'LABEL_STUDIO_API_KEY':''})
        environment.start();self.addCleanup(environment.stop)

    @classmethod
    def setUpClass(cls):
        cls.root = PROJECT/'runtime'/('verification_20261016_'+uuid.uuid4().hex[:8])
        cls.root.mkdir()
        for packet in read(LEGACY_BATCH/'batch_manifest.json')['packets']:
            directory=Path(packet['dir'])
            mapping=read(directory/'manifest_private.json')['sample_mapping']
            request=read(directory/'request.json')
            try:
                raw=read(directory/'reviews_gemini.json')
                accepted,_=validate_file(raw,request,mapping)
            except (ValueError,TypeError,KeyError):
                continue
            if accepted:
                cls.local=next(s for s,r in mapping.items() if r['source_sample_key'] in accepted)
                cls.record=copy.deepcopy(mapping[cls.local])
                cls.value=copy.deepcopy(raw['reviews'][cls.local])
                cls.checks=copy.deepcopy(raw['category_checks'][cls.local])
                break
        else:
            raise AssertionError('No valid real source fixture')

    def store(self,count=1):
        store=Store(self.root/uuid.uuid4().hex[:8])
        rows=[]
        for i in range(count):
            record=copy.deepcopy(self.record)
            record['source_sample_key']+=f'_offline_fixture_{i}'
            rows.append({'source_sample_key':record['source_sample_key'],'record':record,
                'sample_key':'S001','stage':'secondary_chroma','state':'secondary_chroma_ready',
                'group_id':f'{i:03d}','ready_at':now(),'defects':None,'qa_failures':0,'failure_count':0,
                'attempt_count':0,'last_feedback':None})
        initialize(store,rows,{'offline_fixture':True,'target':count})
        (store.run_dir/'prompts').mkdir()
        for name in ['session.md','initial_rgb.md','secondary_chroma.md']:
            (store.run_dir/'prompts'/name).write_bytes((PROJECT/'prompts'/name).read_bytes())
        return store

    def output(self,directory,bad=False):
        raw=read(directory/'reviews_gemini.json')
        raw['reviews']={s:copy.deepcopy(self.value) for s in raw['reviews']}
        raw['category_checks']={s:None if bad else copy.deepcopy(self.checks) for s in raw['reviews']}
        write(directory/'reviews_gemini.json',raw)

    def factory(self,calls,bad_first=False,always_bad=False,quota=False):
        test=self
        class Finished:
            pid=0
            returncode=1 if quota else 0
            def poll(self):return self.returncode
            def wait(self):return self.returncode
        def launch(command,cwd,stdout,stderr,**kwargs):
            cwd=Path(command[command.index("--log-file")+1]).parent
            calls.append(command)
            test.output(Path(cwd),always_bad or (bad_first and len(calls)==1))
            if quota:
                Path(command[command.index('--log-file')+1]).write_text(
                    'agent executor error: Individual quota reached\n',encoding='utf-8')
            stdout.write(json.dumps({'status':'ERROR' if quota else 'SUCCESS','error':'Individual quota reached' if quota else None,
                'conversation_id':command[command.index('--conversation')+1] if '--conversation' in command else 'fixture-explicit-conversation'+(str(len(calls)) if len(calls)>1 else ''),'usage':{}}).encode())
            stdout.flush()
            return Finished()
        return launch

    def test_01_requeue_feedback_and_conversation(self):
        store=self.store();calls=[]
        Executor(store,1,self.factory(calls,bad_first=True)).run(True)
        row=store.rows()[0]
        self.assertEqual(row['state'],'completed');self.assertEqual(row['qa_failures'],0)
        self.assertEqual(row['attempt_count'],1);self.assertEqual(len(calls),2)
        self.assertNotIn('--conversation',calls[0]);self.assertIn('--conversation',calls[1])
        self.assertIn('fixture-explicit-conversation',calls[1]);self.assertNotIn('--continue',calls[1])
        feedback=read(Path(row['last_attempt'])/'continuation_feedback.json')
        self.assertIn('missing per-category',next(iter(feedback['pending'].values())))
        self.assertEqual(store.summary()['active_calls'],0)
        task=read(store.run_dir/'exports/tasks_stream.json')[0]
        self.assertIn('image',task['data']);self.assertNotIn('score',task['predictions'][0])

    def test_02_complete_file_is_kept_but_quota_stops_next_packet(self):
        store=self.store(2);calls=[]
        Executor(store,1,self.factory(calls,quota=True)).run(True)
        self.assertEqual(len(calls),1)
        self.assertEqual(store.summary()['stats']['completed'],1)
        self.assertEqual(store.summary()['phase'],'quota_waiting')
        self.assertNotIn('pending_resume',store.worker('W01'))
        self.assertEqual(store.rows()[0]['provenance']['ignored_session_error'],'quota_exhausted')

    def test_03_interrupted_late_file_and_duplicate_owner(self):
        store=self.store();engine=Executor(store)
        rows=store.claim('secondary_chroma','W01')
        directory,request,mapping,prompt=engine.materialize(store.worker('W01'),rows)
        self.output(directory)
        rows[0]['last_attempt']=str(directory)
        with store.tx() as db:Store.put_sample(db,rows[0])
        recover_interrupted(store)
        self.assertEqual(store.rows()[0]['state'],'completed')
        self.assertFalse(store.claim('secondary_chroma','W01'))
        with OwnerLock(store.run_dir):
            with self.assertRaises(RuntimeError):
                with OwnerLock(store.run_dir):pass
        with OwnerLock(PROJECT/'runtime'):
            with self.assertRaises(RuntimeError):Executor(self.store(),1,self.factory([])).run(True)

    def test_04_retry_limit_and_classification(self):
        store=self.store();calls=[]
        Executor(store,1,self.factory(calls,always_bad=True)).run(True)
        self.assertEqual(len(calls),6);self.assertEqual(store.rows()[0]['state'],'secondary_chroma_ready')
        self.assertEqual(store.worker('W01')['pending_resume']['continue_retries'],5)
        for text,kind in [('RESOURCE_EXHAUSTED','quota_exhausted'),('User location is not supported','provider_access_rejected'),('connection reset','network_error')]:
            self.assertEqual(failure_kind(text),kind)
        self.assertIsNotNone(validate_entry([{'id':'C','severity':'L2','object':'衣物','description':'衣物原本呈鲜红色，现在色调异常。'}],['C']))
        for malformed in [None,[],0]:
            with self.assertRaises(ValueError):validate_file(malformed,{}, {})
        fixture=self.store();rows=fixture.claim('secondary_chroma','W01')
        directory,request,mapping,_=Executor(fixture).materialize(fixture.worker('W01'),rows)
        self.output(directory)
        raw=read(directory/'reviews_gemini.json');raw['category_checks']=[]
        accepted,pending=validate_file(raw,request,mapping)
        self.assertFalse(accepted);self.assertEqual(len(pending),1)

    def test_05_atomic_claims_and_commands(self):
        store=self.store(30)
        with ThreadPoolExecutor(max_workers=16) as pool:
            batches=list(pool.map(lambda i:store.claim('secondary_chroma',f'W{i:02d}'),range(16)))
        keys=[r['source_sample_key'] for batch in batches for r in batch]
        self.assertEqual(len(keys),len(set(keys)));self.assertEqual(len(keys),16)
        before=store.rows();first,created=store.command('start');second,new=store.command('start')
        self.assertTrue(created);self.assertFalse(new);self.assertEqual(first,second);self.assertEqual(before,store.rows())
        self.assertEqual(store.page(2,7)['page'],2);self.assertEqual(store.page(1,50,query='offline_fixture_0')['total'],1)

    def test_06_labelstudio_idempotent_outbox(self):
        store=self.store();Executor(store,1,self.factory([])).run(True)
        tasks=[];imports=[]
        def api(base,token,path,method='GET',body=None):
            if path.startswith('/api/projects?'):return {'results':[{'id':91,'title':'上色评价_恢复批次_'+store.run_dir.name}]}
            if path.startswith('/api/tasks?'):return {'tasks':tasks}
            if path.endswith('/import'):
                imports.append(body)
                tasks.extend({'id':len(tasks)+i+1,**copy.deepcopy(task)} for i,task in enumerate(body))
                for task in tasks:task['predictions'][0]['id']=10
                return {'task_count':len(body)}
            if path=='/api/tasks/1/':
                if method=='PATCH':tasks[0].update(copy.deepcopy(body));return tasks[0]
                return tasks[0]
            if path=='/api/predictions/10/' and method=='PATCH':
                tasks[0]['predictions'][0].update(copy.deepcopy(body));return tasks[0]['predictions'][0]
            raise AssertionError(path)
        with patch.dict(os.environ,{'LABEL_STUDIO_API_KEY':'offline-fixture-only'}),patch.object(pipeline_delivery,'api',api):
            self.assertEqual(pipeline_delivery.sync(store)['status'],'synced')
            self.assertEqual(pipeline_delivery.sync(store)['status'],'synced')
            original=store.rows()[0]
            return_for_review(store,original['source_sample_key'],'Explicit offline fixture review return')
            self.assertEqual(pipeline_delivery.sync(store)['returned_tasks'],1)
            self.assertIsNone(tasks[0]['data']['pipeline_review']['defects'])
            self.assertIn('returned_pipeline_review',tasks[0]['data'])
            with store.tx() as db:Store.put_sample(db,original)
            self.assertEqual(pipeline_delivery.sync(store)['returned_tasks'],0)
            self.assertNotIn('pipeline_return',tasks[0]['data'])
            self.assertEqual(tasks[0]['predictions'][0]['result'],pipeline_delivery.make_task(original)['predictions'][0]['result'])
        self.assertEqual(len(imports),1)

    def test_07_dashboard_post_commands_no_state_overwrite(self):
        store=self.store();preflight(store)
        launches=[]
        class Launched:pid=0
        def launcher(*args,**kwargs):launches.append(args);return Launched()
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(DashboardHandler,store=store,launcher=launcher))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        try:
            before=store.rows()
            with urllib.request.urlopen(base+'/api/status') as response:
                self.assertEqual(json.load(response)['dashboard_contract'],'sqlite_runtime_dashboard_v1')
            with self.assertRaises(urllib.error.HTTPError) as ctx:urllib.request.urlopen(base+'/api/action/start')
            self.assertEqual(ctx.exception.code,405)
            for i in range(2):
                request=urllib.request.Request(base+'/api/action/start',data=b'{}',method='POST')
                with urllib.request.urlopen(request) as response:self.assertEqual(response.status,202)
            self.assertEqual(len(launches),1);self.assertEqual(before,store.rows())
            request=urllib.request.Request(base+'/api/action/stop',data=b'{}',method='POST')
            urllib.request.urlopen(request).close()
            self.assertEqual(store.summary()['last_command']['status'],'acknowledged')
            request=urllib.request.Request(base+'/api/action/start',data=b'{}',method='POST',headers={'Origin':'https://example.com'})
            with self.assertRaises(urllib.error.HTTPError) as ctx:urllib.request.urlopen(request)
            self.assertEqual(ctx.exception.code,403)
            for command in store.pending_commands():store.ack(command['id'])
            worker=store.worker('W01')
            worker.update(status='awaiting_continue',pending_resume={'attempt':'offline-fixture',
                'conversation_id':'preserved-fixture','keys':[before[0]['source_sample_key']],'reason':'location_unsupported'})
            store.worker('W01',worker)
            request=urllib.request.Request(base+'/api/action/start',data=b'{}',method='POST')
            with self.assertRaises(urllib.error.HTTPError) as ctx:urllib.request.urlopen(request)
            self.assertEqual(ctx.exception.code,409)
            request=urllib.request.Request(base+'/api/action/continue-blocked',data=b'{}',method='POST')
            with urllib.request.urlopen(request) as response:self.assertEqual(response.status,202)
            self.assertIn('--continue-blocked',launches[-1][0])
            for command in store.pending_commands():store.ack(command['id'])
            store.update_meta(owner_pid=os.getpid(),phase='running',heartbeat_at=now(),
                session_fault_policy='pause_faulted_lane_manual_continue_v2')
            launch_count=len(launches)
            request=urllib.request.Request(base+'/api/action/continue-blocked',data=b'{}',method='POST')
            with urllib.request.urlopen(request) as response:self.assertEqual(response.status,202)
            self.assertEqual(len(launches),launch_count)
            self.assertEqual(store.pending_commands()[0]['action'],'continue-blocked')
            with urllib.request.urlopen(base+'/api/import-preview?start=1&end=1') as response:
                self.assertEqual(json.load(response)['selected'],1)
            with patch.object(pipeline_delivery,'queue_import',return_value={'eligible':1}) as queue:
                request=urllib.request.Request(base+'/api/action/import',data=b'{"start":1,"end":1}',method='POST')
                with urllib.request.urlopen(request) as response:self.assertEqual(response.status,202)
                self.assertEqual(queue.call_args.args[1],{'start':1,'end':1})
            self.assertEqual(store.rows(),before)
        finally:
            server.shutdown();server.server_close();thread.join()

    def test_08_eight_round_rotation_and_four_panel_limit(self):
        store=self.store(10);calls=[]
        original=Executor.materialize
        def materialize(engine,worker,rows):
            result=original(engine,worker,rows)
            self.assertLessEqual(len(result[1]['sheets']),4)
            self.assertLessEqual(len(rows),24)
            return result
        with patch.object(Executor,'materialize',materialize):
            Executor(store,1,self.factory(calls)).run(True)
        self.assertEqual(len(calls),10)
        self.assertNotIn('--conversation',calls[8]);self.assertIn('--conversation',calls[9])
        self.assertEqual(store.summary()['stats']['completed'],10)

    def test_09_network_warning_does_not_kill_live_cli(self):
        store=self.store(2);children=[]
        def factory(command,cwd,stdout,stderr,**kwargs):
            cwd=Path(command[command.index("--log-file")+1]).parent
            self.output(Path(cwd))
            stdout.write(b'{"status":"SUCCESS","conversation_id":"network-warning-session"}')
            stdout.flush()
            # Harmless child exits normally despite a recoverable diagnostic warning.
            proc=subprocess.Popen([sys.executable,'-c','import time; time.sleep(.3)'],stdout=stdout,stderr=stderr,**kwargs)
            children.append(proc)
            (Path(cwd)/'client.log').write_text('network error: connection reset',encoding='utf-8')
            return proc
        Executor(store,1,factory).run(True)
        self.assertEqual(len(children),2)
        self.assertTrue(all(proc.poll() is not None for proc in children))
        self.assertIsNone(store.summary()['stop_reason'])
        self.assertEqual(store.summary()['stats']['completed'],2)
        self.assertEqual(store.summary()['stats']['running'],0)

    def test_11_service_fault_restarts_only_failed_session(self):
        for error in ['UNAUTHENTICATED (code 401): invalid authentication credentials',
                'PERMISSION_DENIED','connection reset','unexpected native failure']:
            with self.subTest(error=error):
                store=self.store();calls=[]
                worker=store.worker('W01');worker.update(conversation_id='retired-session',rounds=3,model='gemini-3.8-flash-high')
                store.worker('W01',worker)
                other=store.worker('W02');other.update(conversation_id='unrelated-session',rounds=2)
                store.worker('W02',other)
                success=self.factory(calls)
                class Failed:
                    pid=0;returncode=1
                    def poll(self):return 1
                    def wait(self):return 1
                def factory(command,cwd,stdout,stderr,**kwargs):
                    cwd=Path(command[command.index("--log-file")+1]).parent
                    if not calls:
                        calls.append(command)
                        stdout.write(json.dumps({'status':'ERROR','error':error,
                            'conversation_id':'retired-session'}).encode());stdout.flush()
                        return Failed()
                    return success(command,cwd,stdout,stderr,**kwargs)
                engine=Executor(store,1,factory)
                engine.worker_loop('W01')
                self.assertFalse(engine.stopped.is_set())
                self.assertEqual(len(calls),2)
                self.assertIn('--conversation',calls[0]);self.assertIn('--conversation',calls[1])
                self.assertIn('retired-session',calls[1])
                self.assertEqual(store.rows()[0]['state'],'completed')
                self.assertEqual(store.rows()[0]['qa_failures'],0)
                self.assertEqual(store.rows()[0]['failure_count'],0)
                self.assertEqual(store.worker('W02'),other)
                self.assertEqual(read(Path(store.rows()[0]['last_attempt'])/'native_result.json')['continue_retries'],1)

    def test_12_persistent_fault_isolates_lane_without_losing_samples(self):
        store=self.store();calls=[]
        class Failed:
            pid=0;returncode=1
            def poll(self):return 1
            def wait(self):return 1
        def factory(command,cwd,stdout,stderr,**kwargs):
            cwd=Path(command[command.index("--log-file")+1]).parent
            calls.append(command)
            stdout.write(b'{"status":"ERROR","error":"UNAUTHENTICATED (code 401)","conversation_id":"failed-session"}')
            stdout.flush();return Failed()
        engine=Executor(store,1,factory);engine.run(True)
        self.assertEqual(len(calls),6)
        self.assertNotIn('--conversation',calls[0])
        self.assertTrue(all('--conversation' in command for command in calls[1:]))
        self.assertFalse(engine.stopped.is_set())
        self.assertEqual(store.worker('W01')['status'],'awaiting_continue')
        self.assertEqual(store.summary()['phase'],'needs_attention')
        self.assertEqual(store.summary()['stop_reason'],'sessions_paused')
        self.assertEqual(store.rows()[0]['state'],'secondary_chroma_ready')
        self.assertEqual(store.rows()[0]['qa_failures'],0)
        self.assertEqual(store.rows()[0]['failure_count'],0)

    def test_13_builtin_quota_keys_parser_and_metadata_isolation(self):
        from native_quota_monitor import parse_gemini,query_native,QuotaMonitor,monitor_lock
        screen=('GEMINI MODELS\nWeekly Limit Remaining\n[████░] 90.17%\nRefreshes in 166h 43m\n'
            'Five Hour Limit Remaining\n[███░░] 68.10%\nRefreshes in 3h 43m\n'
            'CLAUDE MODELS\nWeekly Limit Remaining\n[█████] 100%\nRefreshes in 1h')
        observed=parse_gemini(screen)
        self.assertEqual(observed,{'five_hour':68.1,'weekly':90.17,'five_reset':'3h 43m','weekly_reset':'166h 43m'})
        available=screen.replace('68.10%\nRefreshes in 3h 43m','100.00%\nQuota available')
        self.assertEqual(parse_gemini(available)['five_reset'],'Quota available')
        self.assertEqual(parse_gemini(available)['five_hour'],100.0)
        with self.assertRaises(ValueError):parse_gemini(screen.split('CLAUDE MODELS')[1])
        sent=[]
        class Terminal:
            def __init__(self,stop):self.screen=self
            def reset(self):sent.append('redraw')
            def send(self,key):sent.append(key)
            def wait_for(self,predicate):
                text={0:'for shortcuts',1:'/usage  View model quota usage',
                    2:'Models & Quota\nGEMINI MODELS',4:screen}[len(sent)]
                if not predicate(text):raise AssertionError('Wrong quota UI sequence')
                return text
            def close(self):sent.append('closed')
        self.assertEqual(query_native(threading.Event(),Terminal),observed)
        self.assertEqual(sent,['/usage','\r','redraw','\x0c','closed'])
        store=self.store();before=store.rows()
        monitor=QuotaMonitor(store,query=lambda stop:observed)
        monitor.check_once();previous=store.meta()['quota_snapshot']
        def failure(stop):raise TimeoutError('Offline quota fixture')
        monitor.query=failure;monitor.check_once()
        self.assertEqual(store.meta()['quota_snapshot'],previous)
        self.assertEqual(store.meta()['quota_monitor']['status'],'error')
        self.assertEqual(store.rows(),before)
        with monitor_lock(store.run_dir):
            with self.assertRaises(OSError):
                with monitor_lock(store.run_dir):pass
        calls=[]
        monitor=QuotaMonitor(store,query=lambda stop:(calls.append(1) or observed),interval=60)
        monitor.start()
        import time
        deadline=time.monotonic()+5
        while not calls and time.monotonic()<deadline:time.sleep(.05)
        monitor.close()
        self.assertFalse(monitor.thread.is_alive())
        self.assertEqual(len(calls),1)
        self.assertFalse(store.meta()['quota_monitor']['enabled'])
        self.assertEqual(store.rows(),before)

    def test_14_compact_checks_and_empty_success_continue(self):
        from review_contract import expand_category_checks,validate_category_checks
        from secondary_review import merge_sample
        checks={c:'hit' if c in {d['id'] for d in self.value.get('saturation_defects',[])} else 'clear' for c in ['B','C','D','E1','E2','F']}
        defects=[{'id':'E1','severity':'L1','object':'衣物','description':'衣物局部颜色偏浓。'}]
        explicit={c:'hit' if c=='E1' else 'clear' for c in ['B','C','D','E1','E2','F']}
        self.assertIsNone(validate_category_checks(defects,expand_category_checks(defects,explicit,list(explicit),True),list(explicit)))
        missing=dict(explicit);del missing['F']
        self.assertIsNotNone(validate_category_checks(defects,expand_category_checks(defects,missing,list(explicit),True),list(explicit)))
        baseline={'other_defects':[{'baseline_id':'P001','defect':{'id':'C','severity':'L1','object':'墙面','description':'墙面局部冷色与暖光不协调。'}}]}
        value={'saturation_defects':[],'other_decisions':{'P001':{'action':'retain','inherit':True,'reason':'成立'}},'other_additions':[]}
        self.assertEqual(merge_sample(value,baseline,True),[baseline['other_defects'][0]['defect']])
        baseline['other_defects'][0]['defect']['description']='墙面相对GT偏蓝。'
        with self.assertRaises(ValueError):merge_sample(value,baseline,True)
        store=self.store();calls=[];success=self.factory(calls)
        class Finished:
            pid=0;returncode=0
            def poll(self):return 0
            def wait(self):return 0
        def factory(command,cwd,stdout,stderr,**kwargs):
            if not calls:
                calls.append(command);stdout.write(b'{"status":"SUCCESS","response":"","conversation_id":"empty-success-session"}');stdout.flush();return Finished()
            self.assertIn('empty-success-session',command)
            self.assertIn('已成功读过的看板不要重读',command[command.index('-p')+1])
            return success(command,cwd,stdout,stderr,**kwargs)
        Executor(store,1,factory).run(True)
        self.assertEqual(len(calls),2)
        self.assertEqual(store.rows()[0]['state'],'completed')
        self.assertEqual(store.rows()[0]['qa_failures'],0)
        self.assertEqual(len(list(store.run_dir.joinpath('attempts').iterdir())),1)

    def test_15_limited_medium_run_stops_at_two_batches(self):
        store=self.store(3);calls=[]
        Executor(store,1,self.factory(calls),model='gemini-3.8-flash-medium',maximum_batches=2).run(True)
        self.assertEqual(len(calls),2)
        self.assertTrue(all(call[call.index('--model')+1]=='gemini-3.8-flash-medium' for call in calls))
        self.assertEqual(store.summary()['stats']['completed'],2)
        self.assertEqual(store.summary()['stats']['secondary_ready'],1)
        self.assertIn('--conversation',calls[1])
        with self.assertRaises(ValueError):Executor(store,16,maximum_batches=2)

    def test_16_visual_receipt_gate_rejects_unread_boards(self):
        from visual_receipts import read_visual_receipts
        store=self.store();engine=Executor(store);rows=store.claim('secondary_chroma','W01')
        d,request,mapping,_=engine.materialize(store.worker('W01'),rows)
        self.output(d)
        missing={'seen':[],'missing':[s['path'] for s in request['sheets']]}
        with patch('pipeline_engine.read_visual_receipts',lambda conv,sheets:missing):
            accepted,pending=engine.accept(rows,d,request,mapping,{'started':True,'conversation_id':'offline'},True)
        self.assertEqual(accepted,0);self.assertEqual(pending,1)
        self.assertEqual(store.rows()[0]['state'],'secondary_chroma_ready')
        self.assertEqual(store.rows()[0]['qa_failures'],0)
        trace=d/'receipt_fixture.jsonl';sheet=request['sheets'][0]['path']
        events=[{'tool_calls':[{'name':'view_file','args':{'AbsolutePath':json.dumps(sheet)}}]},
            {'type':'GENERIC','status':'DONE','content':'The following is the entire, complete content of the requested file.'}]
        trace.write_text('\n'.join(json.dumps(x) for x in events),encoding='utf-8')
        self.assertEqual(read_visual_receipts('offline',request['sheets'],trace)['missing'],[])
        events[-1]['content']='Error: JSON hook failed'
        trace.write_text('\n'.join(json.dumps(x) for x in events),encoding='utf-8')
        self.assertEqual(read_visual_receipts('offline',request['sheets'],trace)['seen'],[])

    def test_17_zero_usage_does_not_reset_cumulative_counter(self):
        store=self.store(3);calls=[];base=self.factory(calls)
        def factory(command,cwd,stdout,stderr,**kwargs):
            proc=base(command,cwd,stdout,stderr,**kwargs)
            value=[100,0,150][len(calls)-1]
            stdout.seek(0);stdout.truncate()
            stdout.write(json.dumps({'status':'SUCCESS','conversation_id':'fixture-explicit-conversation',
                'usage':{'input_tokens':value}}).encode());stdout.flush()
            return proc
        Executor(store,1,factory).run(True)
        increments=[r['provenance']['incremental_usage']['input_tokens'] for r in store.rows()]
        self.assertEqual(increments,[100,0,50])

    def test_18_missing_envelope_recovers_owned_log_conversation_before_continue(self):
        store=self.store();calls=[];base=self.factory(calls)
        conversation='11111111-2222-4333-8444-555555555555'
        def factory(command,cwd,stdout,stderr,**kwargs):
            if not calls:
                calls.append(command)
                Path(command[command.index('--log-file')+1]).write_text(
                    'I1016 12:00:00 cli_setting_manager.go:1] permissions command(echo Forwarding user message to conversation 99999999-9999-4999-8999-999999999999)\n'
                    'I1016 12:00:01 conversation_manager.go:783] Forwarding user message to conversation '+conversation+' (items=1, media=0)',encoding='utf-8')
                stdout.write(b'{"status":"ERROR","error":"native protocol failure"}');stdout.flush()
                class Finished:
                    pid=0;returncode=1
                    def poll(self):return 1
                    def wait(self):return 1
                return Finished()
            proc=base(command,cwd,stdout,stderr,**kwargs)
            stdout.seek(0);stdout.truncate()
            stdout.write(json.dumps({'status':'SUCCESS','conversation_id':conversation}).encode());stdout.flush()
            return proc
        engine=Executor(store,1,factory)
        rows=store.claim('secondary_chroma','W01')
        engine.run_one(store.worker('W01'),rows)
        self.assertEqual(len(calls),2)
        self.assertIn('--conversation',calls[1]);self.assertIn(conversation,calls[1])
        self.assertEqual(store.rows()[0]['state'],'completed')
        self.assertEqual(store.rows()[0]['qa_failures'],0)

    def test_19_location_and_network_require_manual_same_packet_continue(self):
        for error,reason in [('User location is not supported','location_unsupported'),
                ('connection reset','network_error')]:
            with self.subTest(reason=reason):
                store=self.store();calls=[]
                class Failed:
                    pid=0;returncode=1
                    def poll(self):return 1
                    def wait(self):return 1
                def fail(command,cwd,stdout,stderr,**kwargs):
                    calls.append(command)
                    Path(command[command.index('--log-file')+1]).write_text('agent executor error: '+error+'\n',encoding='utf-8')
                    stdout.write(json.dumps({'status':'ERROR','error':error,
                        'conversation_id':'preserved-conversation'}).encode());stdout.flush()
                    return Failed()
                with patch.object(pipeline_delivery,'sync') as automatic_sync:
                    Executor(store,1,fail).run(True)
                    automatic_sync.assert_not_called()
                self.assertEqual(len(calls),6)
                self.assertEqual(store.summary()['stop_reason'],'sessions_paused')
                self.assertEqual(store.worker('W01')['last_session_error'],reason)
                self.assertEqual(store.worker('W01')['status'],'awaiting_continue')
                pending=copy.deepcopy(store.worker('W01')['pending_resume'])
                self.assertEqual(store.rows()[0]['qa_failures'],0)
                self.assertEqual(store.claim('secondary_chroma','W02'),[])
                Executor(store,1,fail,continue_blocked=True).run(True)
                self.assertEqual(len(calls),12)
                self.assertEqual(store.worker('W01')['pending_resume']['attempt'],pending['attempt'])
                pending=copy.deepcopy(store.worker('W01')['pending_resume'])
                Executor(store,1,fail).run(True)
                self.assertEqual(len(calls),12)
                self.assertEqual(store.worker('W01')['pending_resume'],pending)
                successful=[]
                Executor(store,1,self.factory(successful),continue_blocked=True).run(True)
                self.assertEqual(len(successful),1)
                self.assertIn('preserved-conversation',successful[0])
                self.assertTrue(successful[0][successful[0].index('-p')+1].startswith('继续'))
                self.assertEqual(store.rows()[0]['state'],'completed')
                self.assertEqual(len(list((store.run_dir/'attempts').iterdir())),1)
                self.assertEqual(store.rows()[0]['last_attempt'],pending['attempt'])
                self.assertNotIn('pending_resume',store.worker('W01'))

    def test_20_manual_import_range_does_not_touch_outside_selection(self):
        store=self.store(3)
        Executor(store,1,self.factory([]),maximum_batches=2).run(True)
        rows,preview=pipeline_delivery.select_rows(store,{'start':2,'end':3})
        self.assertEqual(preview['selected'],2)
        self.assertEqual(preview['eligible'],1)
        self.assertEqual(preview['excluded'],1)
        imported=[]
        def api(base,token,path,method='GET',body=None):
            if path.startswith('/api/projects?'):return {'results':[{'id':91,'title':'上色评价_恢复批次_'+store.run_dir.name}]}
            if path.startswith('/api/tasks?'):return {'tasks':[]}
            if path.endswith('/import'):imported.extend(body);return {'task_count':len(body)}
            raise AssertionError(path)
        before=store.rows()
        with patch.dict(os.environ,{'LABEL_STUDIO_API_KEY':'offline-fixture-only'}),patch.object(pipeline_delivery,'api',api):
            result=pipeline_delivery.sync(store,{'start':2,'end':3})
        self.assertEqual(result['status'],'synced')
        self.assertEqual([t['data']['source_sample_key'] for t in imported],[rows[0]['source_sample_key']])
        self.assertEqual(store.rows(),before)
        with self.assertRaises(ValueError):pipeline_delivery.select_rows(store,{'start':3,'end':2})

    def test_21_location_failure_waits_for_exit_and_keeps_other_lane_running(self):
        store=self.store(2);calls=[];second_started=threading.Event();fault_paused=threading.Event();terminated=[]
        class Running:
            pid=0;returncode=None
            def __init__(self,lane,log):self.lane,self.log=lane,log
            def poll(self):
                if self.returncode is None and self.lane=='W01' and second_started.is_set():
                    self.log.write_text('User location is not supported',encoding='utf-8')
                    self.returncode=1;fault_paused.set()
                if self.lane=='W02' and fault_paused.is_set():self.returncode=0
                return self.returncode
            def wait(self):return self.returncode
        def factory(command,cwd,stdout,stderr,**kwargs):
            log=Path(command[command.index('--log-file')+1])
            lane=log.parent.name.split('_')[1]
            calls.append(command)
            stdout.write(json.dumps({'conversation_id':'preserved-'+lane}).encode());stdout.flush()
            if lane=='W02':
                self.output(log.parent);second_started.set()
            return Running(lane,log)
        def terminate(engine,proc):
            terminated.append(proc.lane);proc.returncode=-15;fault_paused.set()
        with patch.object(Executor,'terminate',terminate):
            engine=Executor(store,2,factory);engine.run(True)
        self.assertEqual(len(calls),7)
        self.assertEqual(terminated,[])
        self.assertFalse(engine.stopped.is_set())
        self.assertEqual(store.summary()['stats']['completed'],1)
        self.assertEqual(sum(bool(w.get('pending_resume')) for w in store.summary()['workers'].values()),1)
        self.assertTrue(all(r['qa_failures']==0 for r in store.rows()))
        # Explicit user stop before a resumed CLI starts must still retain its packet.
        worker=store.worker('W01');pending=copy.deepcopy(worker['pending_resume'])
        rows=store.claim_resume(worker)
        engine=Executor(store,2);engine.reason='location_unsupported';engine.stopped.set()
        with patch.object(engine,'_execute_agy',return_value=({'started':False},'stopped',None)):
            engine.run_one(worker,rows,resume_attempt=pending)
        self.assertEqual(store.worker('W01')['pending_resume']['conversation_id'],pending['conversation_id'])
        self.assertEqual(store.worker('W01')['pending_resume']['keys'],pending['keys'])

    def test_23_manual_continue_while_other_lane_runs(self):
        store=self.store(2);calls=[];resumed=threading.Event();queued=threading.Event()
        test=self
        class Process:
            pid=0
            def __init__(self,lane,failed):self.lane,self.returncode=lane,1 if failed else None
            def poll(self):
                if self.lane=='W02' and resumed.is_set():self.returncode=0
                return self.returncode
            def wait(self):return self.returncode
        def factory(command,cwd,stdout,stderr,**kwargs):
            directory=Path(command[command.index('--log-file')+1]).parent
            lane=directory.name.split('_')[1];calls.append((lane,command))
            failed=lane=='W01' and sum(lane_id=='W01' for lane_id,_ in calls)<=6
            if not failed:test.output(directory)
            stdout.write(json.dumps({'status':'ERROR' if failed else 'SUCCESS',
                'error':'connection reset' if failed else None,'conversation_id':'same-'+lane}).encode());stdout.flush()
            if lane=='W01' and not failed:
                resumed.set();proc=Process(lane,False);proc.returncode=0;return proc
            return Process(lane,failed)
        def continue_once():
            for _ in range(200):
                if store.worker('W01').get('pending_resume'):
                    store.command('continue-blocked');queued.set();return
                queued.wait(.05)
        watcher=threading.Thread(target=continue_once,daemon=True);watcher.start()
        engine=Executor(store,2,factory)
        with patch.object(engine,'terminate',side_effect=AssertionError('Healthy process must not be terminated')):
            engine.run(True)
        watcher.join(1)
        self.assertTrue(queued.is_set());self.assertTrue(resumed.is_set())
        self.assertFalse(engine.stopped.is_set());self.assertEqual(store.summary()['stats']['completed'],2)
        self.assertEqual(len(calls),8)
        continued=[command for lane,command in calls if lane=='W01' and '--conversation' in command]
        self.assertEqual(len(continued),6);self.assertTrue(all('same-W01' in command for command in continued))
        self.assertEqual(store.summary()['phase'],'completed')

    def test_24_user_stop_and_handover_classification(self):
        from activate_lane_policy import classify_workers
        store=self.store();engine=Executor(store);killed=[]
        engine.processes={'W01':object(),'W02':object()}
        with patch.object(engine,'terminate',side_effect=lambda proc:killed.append(proc)):
            engine.stop('user_pause')
        self.assertEqual(len(killed),2);self.assertTrue(engine.stopped.is_set())
        workers={}
        for worker_id,error in [('W01','location_unsupported'),('W02',None),('W03','quota_exhausted')]:
            directory=store.run_dir/worker_id;directory.mkdir()
            write(directory/'native_result.json',{'started':True,'session_error':error,'conversation_id':worker_id})
            workers[worker_id]={'pending_resume':{'attempt':str(directory),'conversation_id':worker_id,'keys':[]}}
        healthy,faulted=classify_workers(workers,{})
        self.assertEqual(healthy,['W02']);self.assertEqual(set(faulted),{'W01','W03'})
        workers['W04']={}
        directory=store.run_dir/'completed_with_fault';directory.mkdir()
        write(directory/'native_result.json',{'started':True,'session_error':'location_unsupported','conversation_id':'W04'})
        _,faulted=classify_workers(workers,{'W04':directory})
        self.assertIn('W04',faulted)  # A complete result cannot clear its conversation's native fault.

    def test_25_retry_interval_and_interruption_pool(self):
        from datetime import datetime,timezone
        store=self.store();engine=Executor(store);worker=store.worker('W01')
        with patch.object(Executor,'RETRY_DELAY_SECONDS',20),patch.object(engine.stopped,'wait',return_value=False) as waiting:
            self.assertTrue(engine.wait_for_retry(worker,2,'network_error'))
            waiting.assert_called_once_with(20)
            remaining=(datetime.fromisoformat(worker['continue_retry']['next_at'])-datetime.now(timezone.utc)).total_seconds()
            self.assertGreater(remaining,18);self.assertLessEqual(remaining,20)
            self.assertEqual(store.worker('W01')['status'],'retry_wait')
        with patch.object(engine.stopped,'wait',return_value=True):
            self.assertFalse(engine.wait_for_retry(worker,3,'network_error'))
        calls=[]
        class Failed:
            pid=0;returncode=1
            def poll(self):return 1
            def wait(self):return 1
        def fail(command,cwd,stdout,stderr,**kwargs):
            calls.append(command);stdout.write(b'{"status":"ERROR","error":"connection reset","conversation_id":"same-network"}');stdout.flush();return Failed()
        Executor(store,1,fail).run(True)
        self.assertEqual(len(calls),6)
        self.assertEqual(store.worker('W01')['pending_resume']['continue_retries'],5)
        self.assertEqual(store.worker('W01')['rounds'],0)
        calls.clear()
        Executor(store,1,fail,auto_resume_pending=True).run(True)
        self.assertEqual(len(calls),5)  # An inherited fault uses five continuations, without a fresh initial call.
        self.assertTrue(all('same-network' in command for command in calls))

    def test_22_manual_continue_preserves_already_accepted_partial(self):
        store=self.store(2)
        rows=store.rows()
        with store.tx() as db:
            for row in rows:
                row['group_id']='same-packet';Store.put_sample(db,row)
        calls=[]
        class Failed:
            pid=0;returncode=1
            def poll(self):return 1
            def wait(self):return 1
        def fail(command,cwd,stdout,stderr,**kwargs):
            calls.append(command)
            directory=Path(command[command.index('--log-file')+1]).parent
            self.output(directory)
            raw=read(directory/'reviews_gemini.json');local=list(raw['reviews'])[1]
            raw['reviews'][local]=None;raw['category_checks'][local]=None
            write(directory/'reviews_gemini.json',raw)
            stdout.write(b'{"status":"ERROR","error":"User location is not supported","conversation_id":"partial-conversation"}')
            stdout.flush();return Failed()
        accept=Executor.accept
        def reserve_check(engine,*args,**kwargs):
            result=accept(engine,*args,**kwargs)
            self.assertEqual(store.claim('secondary_chroma','W02'),[])
            return result
        with patch.object(Executor,'accept',reserve_check):
            Executor(store,1,fail).run(True)
        saved=copy.deepcopy(store.rows()[0])
        self.assertEqual(saved['state'],'completed')
        self.assertEqual(store.worker('W01')['rounds'],1)
        self.assertEqual(len(store.worker('W01')['pending_resume']['keys']),1)
        Executor(store,1,self.factory([]),continue_blocked=True).run(True)
        self.assertEqual(store.rows()[0],saved)
        self.assertTrue(all(r['state']=='completed' for r in store.rows()))
        self.assertEqual(store.worker('W01')['rounds'],1)

    def test_26_background_browser_guard_and_retry_preservation(self):
        from batch_auth import batch_environment,GUARD
        import shutil
        marker=self.root/'offline_browser_block.json'
        env=batch_environment(marker)
        self.assertEqual(Path(shutil.which('rundll32',path=env['PATH'])),GUARD)
        before=os.environ.get('PATH')
        # Exercise the real Windows helper with an inert URL; no browser is launched.
        result=subprocess.run([str(GUARD),'url.dll,FileProtocolHandler',
            'https://accounts.google.com/o/oauth2/auth?client_id=offline-guard-test'],
            env=env,capture_output=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        self.assertEqual(result.returncode,77)
        self.assertEqual(read(marker)['reason'],'auth_browser_blocked')
        self.assertNotIn('client_id',marker.read_text())
        from native_quota_monitor import NativeTerminal
        terminal=NativeTerminal.__new__(NativeTerminal)
        terminal.stop=threading.Event();terminal.auth_marker=marker
        with self.assertRaisesRegex(RuntimeError,'auth_browser_blocked'):
            terminal.wait_for(lambda text:True)
        self.assertEqual(os.environ.get('PATH'),before)
        self.assertEqual(failure_kind('auth_browser_blocked'),'auth_browser_blocked')
        store=self.store();worker=store.worker('W01')
        worker.update(conversation_id='preserved-auth-conversation',model='gemini-3.8-flash-high');store.worker('W01',worker)
        calls=[]
        class Finished:
            pid=0;returncode=77
            def poll(self):return 77
            def wait(self):return 77
        def blocked(command,cwd,stdout,stderr,**kwargs):
            calls.append(command)
            write(Path(kwargs['env']['MCL_AUTH_BROWSER_BLOCK_LOG']),{'reason':'auth_browser_blocked'})
            return Finished()
        # Keep the live project's global executor lock untouched during this fixture.
        (self.root/'auth_guard_global_lock').mkdir()
        with patch('pipeline_engine.OwnerLock',lambda directory:OwnerLock(
                self.root/'auth_guard_global_lock' if Path(directory)==PROJECT/'runtime' else directory)):
            Executor(store,1,blocked).run(True)
        self.assertEqual(len(calls),6)
        self.assertTrue(all('preserved-auth-conversation' in cmd for cmd in calls))
        worker=store.worker('W01')
        self.assertEqual(worker['last_session_error'],'auth_browser_blocked')
        self.assertEqual(worker['pending_resume']['continue_retries'],5)
        self.assertEqual(store.rows()[0]['qa_failures'],0)

    def test_27_complete_stream_warning_dispatches_next_packet(self):
        store=self.store(2);calls=[];normal=self.factory(calls)
        def stream_warning(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            stdout.seek(0);stdout.truncate()
            stdout.write(json.dumps({'status':'ERROR','error':
                'The stream was interrupted. Please continue the task you were working on.',
                'conversation_id':'stream-warning-conversation'}).encode());stdout.flush()
            return proc
        Executor(store,1,stream_warning).run(True)
        self.assertEqual(len(calls),2)  # Two original packets; no continuation of a complete packet.
        self.assertNotEqual(Path(calls[0][calls[0].index('--log-file')+1]).parent,
            Path(calls[1][calls[1].index('--log-file')+1]).parent)
        self.assertIn('stream-warning-conversation',calls[1])
        self.assertTrue(all(r['state']=='completed' for r in store.rows()))
        self.assertNotIn('pending_resume',store.worker('W01'))
        for row in store.rows():
            self.assertEqual(row['provenance']['native_status'],'ERROR')
            self.assertEqual(row['provenance']['completion_warning'],'stream_interrupted_after_complete_result')
            self.assertIsNone(row['provenance']['session_error'])

    def test_28_complete_results_never_retry_empty_task_but_identity_stays_protected(self):
        from pipeline_engine import completed_call_error
        stream={'native_error':'The stream was interrupted. Please continue the task you were working on.'}
        self.assertEqual(completed_call_error(copy.deepcopy(stream),'native_call_failed',False),'native_call_failed')
        self.assertIsNone(completed_call_error({**stream,'observed_transient_error':'network_error'},
            'native_call_failed',True))
        for reason in ['location_unsupported','quota_exhausted','auth_browser_blocked']:
            value=copy.deepcopy(stream)
            self.assertIsNone(completed_call_error(value,reason,True))
            self.assertEqual(value['ignored_session_error'],reason)
            self.assertEqual(completed_call_error(copy.deepcopy(stream),reason,False),reason)
        self.assertEqual(completed_call_error(copy.deepcopy(stream),'conversation_identity_mismatch',True),'conversation_identity_mismatch')
        self.assertIsNone(completed_call_error({'native_error':'unrelated CLI failure'},
            'native_call_failed',True))
        store=self.store();calls=[];normal=self.factory(calls,always_bad=True)
        def unfinished(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            stdout.seek(0);stdout.truncate();stdout.write(json.dumps({'status':'ERROR',
                'error':stream['native_error'],'conversation_id':'unfinished-stream-conversation'}).encode())
            stdout.flush();return proc
        Executor(store,1,unfinished).run(True)
        self.assertEqual(len(calls),6)
        self.assertEqual(store.worker('W01')['pending_resume']['continue_retries'],5)
        self.assertEqual(store.rows()[0]['state'],'secondary_chroma_ready')

    def test_29_telemetry_and_internal_retry_do_not_terminate_cli(self):
        from pipeline_engine import live_failure_kind
        self.assertIsNone(live_failure_kind('Post "https://play.googleapis.com/log": net/http: TLS handshake timeout'))
        self.assertIsNone(live_failure_kind('run.go:80] API error: unexpected EOF, retrying in 4s'))
        self.assertEqual(live_failure_kind('agent executor error: FAILED_PRECONDITION: User location is not supported'),'location_unsupported')
        self.assertEqual(failure_kind('streamGenerateContent: wsasend: forcibly closed by the remote host'),'network_error')
        store=self.store();calls=[];normal=self.factory(calls)
        class Delayed:
            pid=0;returncode=None
            def __init__(self):self.polls=0
            def poll(self):
                self.polls+=1
                if self.polls>3:self.returncode=0
                return self.returncode
            def wait(self):return self.returncode
        def telemetry(command,cwd,stdout,stderr,**kwargs):
            normal(command,cwd,stdout,stderr,**kwargs)
            Path(command[command.index('--log-file')+1]).write_text(
                'Post "https://play.googleapis.com/log": net/http: TLS handshake timeout\n',encoding='utf-8')
            return Delayed()
        with patch.object(Executor,'terminate',side_effect=AssertionError('Telemetry killed the task')):
            Executor(store,1,telemetry).run(True)
        self.assertEqual(len(calls),1)
        self.assertEqual(store.rows()[0]['state'],'completed')

    def test_30_old_zero_item_hold_releases_same_conversation_without_relabel(self):
        store=self.store();calls=[]
        Executor(store,1,self.factory(calls)).run(True)
        before=copy.deepcopy(store.rows());worker=store.worker('W01');conv=worker['conversation_id']
        worker.update(status='awaiting_continue',pending_resume={'keys':[],
            'attempt':before[0]['last_attempt'],'conversation_id':conv,'reason':'location_unsupported'})
        store.worker('W01',worker)
        engine=Executor(store,1,self.factory(calls))
        self.assertTrue(engine.release_completed_resume(worker))
        self.assertEqual(worker['conversation_id'],conv)
        self.assertNotIn('pending_resume',worker)
        self.assertEqual(store.rows(),before)
        self.assertEqual(len(calls),1)

    def test_31_worker_configuration_has_no_mcp_launchers_and_keeps_original_store(self):
        store=self.store();calls=[];normal=self.factory(calls)
        def isolated(command,cwd,stdout,stderr,**kwargs):
            profile=Path(kwargs['env']['USERPROFILE'])
            self.assertEqual(read(Path(cwd)/'.agents/mcp_config.json'),{'mcpServers':{}})
            self.assertEqual(read(profile/'.gemini/config/mcp_config.json'),{'mcpServers':{}})
            self.assertTrue(os.path.samefile(profile/'.gemini/antigravity-cli',Path.home()/'.gemini/antigravity-cli'))
            self.assertTrue(os.path.samefile(profile/'.gemini/config/projects',Path.home()/'.gemini/config/projects'))
            return normal(command,cwd,stdout,stderr,**kwargs)
        Executor(store,1,isolated).run(True)
        self.assertEqual(store.rows()[0]['state'],'completed')

    def test_32_missing_result_header_gets_precise_same_packet_feedback(self):
        store=self.store();calls=[];normal=self.factory(calls)
        def missing_header(command,cwd,stdout,stderr,**kwargs):
            directory=Path(command[command.index('--log-file')+1]).parent
            if calls:
                feedback=read(directory/'continuation_feedback.json')['pending']['file']
                self.assertIn('annotation_contract',feedback)
                self.assertIn(read(directory/'request.json')['annotation_contract'],feedback)
                self.assertIn('schema_version',feedback)
                raw=read(directory/'reviews_gemini.json')
                raw['annotation_contract']=read(directory/'request.json')['annotation_contract']
                write(directory/'reviews_gemini.json',raw)
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            if len(calls)==1:
                raw=read(directory/'reviews_gemini.json')
                raw.pop('annotation_contract')
                write(directory/'reviews_gemini.json',raw)
            return proc
        Executor(store,1,missing_header).run(True)
        self.assertEqual(len(calls),2)
        self.assertEqual(store.rows()[0]['state'],'completed')

    def test_33_complete_format_examples_pass_current_validator(self):
        from prepare import FOUR,SIX
        from secondary_review import POLICY
        initial=read(PROJECT/'prompts/examples/initial_rgb.json')
        secondary=read(PROJECT/'prompts/examples/secondary_chroma.json')
        examples=[initial,secondary]
        for example in examples:
            request={key:example[key] for key in ['annotation_contract','stage','packet_id','prompt_revision']}
            request.update(compact_transport='explicit_checks_v1',checked_categories=SIX if example is secondary else FOUR)
            mapping={key:{'source_sample_key':'format_example_only/'+key} for key in example['reviews']}
            if example is secondary:
                decisions=example['reviews']['EXAMPLE_001']['other_decisions']
                request.update(secondary_merge_policy=POLICY,secondary_baseline={
                    'EXAMPLE_001':{'other_defects':[
                        {'baseline_id':'P001','defect':{'id':'D','severity':'L2',
                            'object':decisions['P001']['object'],'description':decisions['P001']['description']}},
                        {'baseline_id':'P002','defect':copy.deepcopy(initial['reviews']['EXAMPLE_001'][1])},
                        {'baseline_id':'P003','defect':copy.deepcopy(initial['reviews']['EXAMPLE_001'][0])},
                        {'baseline_id':'P004','defect':copy.deepcopy(initial['reviews']['EXAMPLE_001'][1])}],
                        'old_saturation':[]},
                    'EXAMPLE_002':{'other_defects':[],'old_saturation':[]}})
            accepted,pending=validate_file(example,request,mapping)
            self.assertFalse(pending);self.assertEqual(len(accepted),len(mapping))
            if example is secondary:
                bad=copy.deepcopy(example)
                bad['reviews']['EXAMPLE_001']['saturation_defects'][0]['reason']=''
                _,pending=validate_file(bad,request,mapping)
                self.assertIn('defect fields must be',pending['format_example_only/EXAMPLE_001'])

    def test_34_each_packet_and_retry_points_to_real_example_file(self):
        store=self.store(2);calls=[]
        Executor(store,1,self.factory(calls,bad_first=True)).run(True)
        self.assertEqual(len(calls),3)
        for command in calls:
            directory=Path(command[command.index('--log-file')+1]).parent
            request=read(directory/'request.json');example=Path(request['format_example_file'])
            self.assertTrue(example.is_absolute());self.assertTrue(example.is_file())
            self.assertIn(str(example),command[command.index('-p')+1])
            self.assertIn('再读取本轮结果骨架',command[command.index('-p')+1])
            self.assertIn(str(example),request['allowed_read_files'])
            self.assertTrue(all(key.startswith('EXAMPLE_') for key in read(example)['reviews']))
            for key in ['annotation_contract','stage','packet_id','prompt_revision']:
                self.assertEqual(read(example)[key],request[key])

    def test_35_recovery_clears_badge_and_next_fault_gets_five_fresh_retries(self):
        store=self.store(2);calls=[];per_packet={};observed={};first_packet=[]
        normal=self.factory(calls)
        def intermittent(command,cwd,stdout,stderr,**kwargs):
            directory=Path(command[command.index('--log-file')+1]).parent
            if not first_packet:first_packet.append(directory)
            per_packet[directory]=per_packet.get(directory,0)+1
            observed.setdefault(directory,[]).append(copy.deepcopy(store.worker('W01')))
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            if directory!=first_packet[0] or per_packet[directory]<=2:self.output(directory,bad=True)
            return proc
        Executor(store,1,intermittent).run(True)
        first,second=list(per_packet)
        self.assertEqual(list(per_packet.values()),[3,6])
        self.assertEqual(read(first/'native_result.json')['continue_retries'],2)
        self.assertEqual(observed[second][0]['retry_count'],0)
        self.assertNotIn('continue_retry',observed[second][0])
        self.assertEqual(observed[second][1]['continue_retry']['attempt'],1)
        self.assertEqual(observed[second][1]['continue_retry']['limit'],5)
        self.assertEqual(store.worker('W01')['pending_resume']['continue_retries'],5)
        self.assertTrue(all('fixture-explicit-conversation' in command for command in calls[1:]))
        Executor(store,1,self.factory([]),continue_blocked=True).run(True)
        worker=store.worker('W01')
        self.assertEqual(worker['retry_count'],0)
        self.assertNotIn('continue_retry',worker)
        self.assertNotIn('pending_resume',worker)
        self.assertTrue(all(row['state']=='completed' for row in store.rows()))

    def test_36_upgrade_preserves_three_used_retries_and_only_adds_four_and_five(self):
        store=self.store();calls=[];bad=self.factory(calls,always_bad=True)
        with patch('pipeline_engine.SESSION_RETRY_LIMIT',3):
            Executor(store,1,bad).run(True)
        self.assertEqual(len(calls),4)
        original=copy.deepcopy(store.worker('W01')['pending_resume'])
        self.assertEqual(original['continue_retries'],3)
        Executor(store,1,bad,resume_workers=['W01'],resume_retry_offsets={'W01':4}).run(True)
        self.assertEqual(len(calls),6)
        pending=store.worker('W01')['pending_resume']
        self.assertEqual(pending['continue_retries'],5)
        self.assertEqual(pending['conversation_id'],original['conversation_id'])
        self.assertEqual(pending['attempt'],original['attempt'])
        self.assertTrue(all(original['conversation_id'] in command for command in calls[4:]))

    def test_37_running_call_has_no_deadline_and_access_logs_do_not_kill_it(self):
        store=self.store();calls=[];normal=self.factory(calls)
        class Delayed:
            pid=0;returncode=None
            def __init__(self):self.polls=0
            def poll(self):
                self.polls+=1
                if self.polls>3:self.returncode=0
                return self.returncode
            def wait(self):return self.returncode
        def slow(command,cwd,stdout,stderr,**kwargs):
            self.assertEqual(command[command.index('--print-timeout')+1],'0')
            normal(command,cwd,stdout,stderr,**kwargs)
            Path(command[command.index('--log-file')+1]).write_text(
                'agent executor error: FAILED_PRECONDITION: User location is not supported\n',encoding='utf-8')
            return Delayed()
        with patch.object(Executor,'terminate',side_effect=AssertionError('Running call was killed')), \
                patch('pipeline_engine.time.monotonic',side_effect=[0]+[1000000]*100):
            Executor(store,1,slow).run(True)
        self.assertEqual(len(calls),1)
        self.assertEqual(store.rows()[0]['state'],'completed')

    def test_38_historical_envelope_error_is_audited_without_a_current_failure(self):
        from pipeline_engine import native_error_scope
        store=self.store();calls=[];normal=self.factory(calls)
        transcript=store.run_dir/'transcript_fixture.jsonl'
        error='API error: wsasend: forcibly closed by the remote host'
        transcript.write_text(json.dumps({'type':'ERROR_MESSAGE','error':error,
            'created_at':'2026-10-16T00:00:00Z'})+'\n',encoding='utf-8')
        scope=native_error_scope(error,'fixture','2026-10-17T00:00:00Z',transcript)
        self.assertEqual(scope['scope'],'historical')
        self.assertEqual(native_error_scope(error,'fixture','2026-10-15T00:00:00Z',transcript)['scope'],'current_call')
        self.assertEqual(native_error_scope('unknown','fixture','2026-10-17T00:00:00Z',transcript)['scope'],'unverified')
        def stale(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            stdout.seek(0);stdout.truncate();stdout.write(json.dumps({'status':'ERROR','error':error,
                'conversation_id':'fixture-explicit-conversation'}).encode());stdout.flush()
            return proc
        with patch('pipeline_engine.native_error_scope',return_value=scope):
            Executor(store,1,stale).run(True)
        native=store.rows()[0]['provenance']
        self.assertIsNone(native['session_error'])
        self.assertEqual(native['native_error'],error)
        self.assertNotIn('ignored_session_error',native)
        self.assertEqual(len(calls),1)

    def test_39_illegal_legacy_inherit_identifies_the_exact_P_item(self):
        from secondary_review import merge_sample,write_inheritance_guidance
        store=self.store();directory=store.run_dir
        old={'id':'C','name':'legacy','severity':'L2','description':'Visible color patch.'}
        good={'id':'C','severity':'L2','object':'wall','description':'A purple patch is visible on the wall.'}
        baseline={'other_defects':[{'baseline_id':'P001','defect':old},
            {'baseline_id':'P002','defect':good}],'old_saturation':[]}
        request={'secondary_baseline':{'S001':copy.deepcopy(baseline)}}
        write_inheritance_guidance(directory,request)
        items=read(directory/'prior_reviews.json')['reviews']['S001']['other_defects']
        self.assertFalse(items[0]['inherit_allowed']);self.assertTrue(items[1]['inherit_allowed'])
        self.assertEqual(items[0]['defect'],old)
        value={'saturation_defects':[],'other_additions':[],
            'other_decisions':{pid:{'action':'retain','inherit':True,'reason':'Visible on the board.'}
                for pid in ['P001','P002']}}
        with self.assertRaisesRegex(ValueError,'P001: inherit is invalid.*explicitly write object and description'):
            merge_sample(value,baseline,True)
        value['other_decisions']['P001']={'action':'retain','object':'wall',
            'description':good['description'],'reason':'Visible on the board.'}
        self.assertEqual(merge_sample(value,baseline,True),[good,good])

    def test_40_manual_stop_still_terminates_a_running_call(self):
        store=self.store();engine=Executor(store);worker=store.worker('W01')
        directory=store.run_dir
        class Running:
            pid=0;returncode=None
            def poll(self):engine.stopped.set();return self.returncode
            def wait(self):return self.returncode
        proc=Running();engine.process_factory=lambda *args,**kwargs:proc
        def terminate(p):p.returncode=1
        with patch.object(engine,'terminate',side_effect=terminate) as killed:
            engine._execute_agy(worker,directory,['fixture'],directory/'client.log',
                directory/'stdout.json',directory/'stderr.log','fixture','secondary_chroma')
        killed.assert_called_once_with(proc)

    def test_41_five_hour_zero_pauses_once_and_fresh_native_recovery_resumes_original_lane(self):
        from quota_control import observe_quota
        from update_quota_snapshot import record
        store=self.store();worker=store.worker('W01')
        worker.update(status='running',conversation_id='original-quota-conversation',retry_count=2,
            pending_resume={'attempt':'original-packet','conversation_id':'original-quota-conversation','keys':['original-key']})
        store.worker('W01',worker);store.update_meta(owner_pid=os.getpid(),phase='running')
        before=copy.deepcopy(store.rows())
        exhausted=record(store,five_hour=0,weekly=35)
        observe_quota(store,exhausted);observe_quota(store,exhausted)
        self.assertEqual([c['action'] for c in store.pending_commands()],['quota-stop'])
        self.assertEqual(store.meta()['quota_guard']['resume_workers'],['W01'])
        store.update_meta(owner_pid=None,phase='quota_waiting')
        fresh=record(store,five_hour=1,weekly=35)
        launched=[]
        def launcher(command,**kwargs):
            launched.append(command)
            return type('Process',(),{'pid':12345})()
        observe_quota(store,fresh,launcher);observe_quota(store,fresh,launcher)
        self.assertEqual(len(launched),1)
        self.assertIn('--resume-workers',launched[0]);self.assertIn('W01',launched[0])
        self.assertEqual(json.loads(launched[0][launched[0].index('--resume-retry-offsets')+1]),{'W01':2})
        self.assertNotIn('--continue-blocked',launched[0])
        self.assertEqual(store.rows(),before)
        self.assertFalse(any(c['action']=='quota-stop' for c in store.pending_commands()))

    def test_42_weekly_zero_stays_manual_even_when_both_quotas_recover(self):
        from quota_control import observe_quota,allow_requested_start
        from update_quota_snapshot import record
        store=self.store();store.update_meta(owner_pid=os.getpid(),phase='running')
        observe_quota(store,record(store,five_hour=0,weekly=0))
        self.assertTrue(store.meta()['quota_guard']['weekly_manual_hold'])
        store.update_meta(owner_pid=None)
        with patch('quota_control.subprocess.Popen',side_effect=AssertionError('Weekly recovery auto-started')):
            observe_quota(store,record(store,five_hour=100,weekly=100))
        self.assertTrue(store.meta()['quota_guard']['waiting_for_recovery'])
        self.assertTrue(allow_requested_start(store))
        self.assertFalse(store.meta()['quota_guard']['waiting_for_recovery'])

    def test_43_old_positive_failed_query_and_manual_stop_cannot_auto_resume(self):
        from quota_control import observe_quota,pause_for_quota
        from update_quota_snapshot import record
        store=self.store();old=record(store,five_hour=99,weekly=99)
        store.update_meta(owner_pid=os.getpid(),phase='running')
        pause_for_quota(store,{'native_error':'RESOURCE_EXHAUSTED'},'native quota error')
        store.update_meta(owner_pid=None)
        with patch('quota_control.subprocess.Popen',side_effect=AssertionError('Unconfirmed recovery started')):
            observe_quota(store,old)
            before_last_fault=record(store,five_hour=99,weekly=99)
            pause_for_quota(store,{'native_error':'Individual quota reached'},'native quota error')
            observe_quota(store,before_last_fault)
            observe_quota(store,record(store,error='Offline query failed'))
            store.command('stop')
            observe_quota(store,record(store,five_hour=99,weekly=99))
        self.assertTrue(store.meta()['quota_guard']['manual_hold'])
        self.assertTrue(store.meta()['quota_guard']['waiting_for_recovery'])

    def test_44_live_quota_error_stops_every_running_process_without_retries(self):
        from quota_control import explicit_exhaustion
        self.assertFalse(explicit_exhaustion('HTTP 429 Too Many Requests'))
        store=self.store();engine=Executor(store);worker=store.worker('W01')
        store.update_meta(owner_pid=os.getpid(),phase='running')
        directory=store.run_dir
        class Running:
            returncode=None
            def __init__(self,pid):self.pid=pid
            def poll(self):return self.returncode
            def wait(self):return self.returncode
        current=Running(1);other=Running(2);engine.processes['W02']=other
        def factory(command,cwd,stdout,stderr,**kwargs):
            (directory/'client.log').write_text('agent executor error: RESOURCE_EXHAUSTED\n',encoding='utf-8')
            stdout.write(b'{"status":"ERROR","error":"RESOURCE_EXHAUSTED","conversation_id":"original-quota-id"}')
            stdout.flush();return current
        engine.process_factory=factory;killed=[]
        def terminate(proc):proc.returncode=1;killed.append(proc.pid)
        with patch.object(engine,'terminate',side_effect=terminate):
            engine._execute_agy(worker,directory,['fixture'],directory/'client.log',
                directory/'stdout.json',directory/'stderr.log','original-quota-id','secondary_chroma')
        self.assertEqual(set(killed),{1,2})
        self.assertTrue(engine.stopped.is_set());self.assertEqual(engine.reason,'quota_exhausted')

    def test_45_start_at_zero_quota_submits_no_model_call(self):
        from update_quota_snapshot import record
        store=self.store();record(store,five_hour=0,weekly=35)
        with patch('subprocess.Popen',side_effect=AssertionError('Zero quota launched a model')):
            Executor(store,1).run(True)
        self.assertEqual(store.summary()['phase'],'quota_waiting')
        self.assertEqual(store.rows()[0]['state'],'secondary_chroma_ready')
        engine=Executor(store,1,process_factory=lambda *a,**k:self.fail('Quota gate launched a process'))
        native,_,_=engine._execute_agy(store.worker('W01'),store.run_dir,['fixture'],
            store.run_dir/'client.log',store.run_dir/'stdout.json',store.run_dir/'stderr.log',
            'original-conversation','secondary_chroma')
        self.assertFalse(native['started'])

    def test_46_native_monitor_applies_global_quota_control_without_model_probing(self):
        from native_quota_monitor import QuotaMonitor
        store=self.store();store.update_meta(owner_pid=os.getpid(),phase='running')
        query=lambda stop:{'five_hour':0,'weekly':35,'five_reset':'2h','weekly_reset':'150h'}
        QuotaMonitor(store,query=query).check_once()
        self.assertTrue(store.meta()['quota_guard']['waiting_for_recovery'])
        self.assertEqual([c['action'] for c in store.pending_commands()],['quota-stop'])

    def test_47_historical_quota_error_does_not_pause_new_work(self):
        store=self.store();calls=[];normal=self.factory(calls)
        def stale(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            stdout.seek(0);stdout.truncate();stdout.write(json.dumps({'status':'ERROR',
                'error':'Individual quota reached','conversation_id':'fixture-explicit-conversation'}).encode())
            stdout.flush();return proc
        with patch('pipeline_engine.native_error_scope',return_value={'scope':'historical'}):
            Executor(store,1,stale).run(True)
        self.assertEqual(store.summary()['phase'],'completed')
        self.assertFalse(store.meta().get('quota_guard',{}).get('waiting_for_recovery'))
        self.assertEqual(len(calls),1)

    def test_48_unverified_cached_quota_error_does_not_stop_complete_packets(self):
        # Reproduce W07: no quota ERROR_MESSAGE and no current terminal error, but ERROR in stdout.
        store=self.store(2);calls=[];normal=self.factory(calls)
        original=read(PROJECT/'runtime/recovery5000_20261016_01/attempts/20261017T135135_W07_1a4112e7/stdout_manual_20261017T165332_d93aea.json')
        def replay(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            raw=copy.deepcopy(original)
            raw['conversation_id']=command[command.index('--conversation')+1] if '--conversation' in command else 'offline-replay-cid'
            stdout.seek(0);stdout.truncate();stdout.write(json.dumps(raw).encode());stdout.flush()
            return proc
        Executor(store,1,replay).run(True)
        self.assertEqual(len(calls),2)
        self.assertEqual(store.summary()['stats']['completed'],2)
        self.assertFalse(store.meta().get('quota_guard',{}).get('waiting_for_recovery'))
        for row in store.rows():
            self.assertEqual(row['provenance']['native_error_scope']['scope'],'unverified')
            self.assertIsNone(row['provenance']['effective_error'])
            self.assertIsNone(row['provenance']['session_error'])

    def test_49_other_unverified_envelope_errors_are_not_current_faults(self):
        for error in ['User location is not supported','connection reset','UNAUTHENTICATED']:
            with self.subTest(error=error):
                store=self.store();calls=[];normal=self.factory(calls)
                def replay(command,cwd,stdout,stderr,**kwargs):
                    proc=normal(command,cwd,stdout,stderr,**kwargs)
                    stdout.seek(0);stdout.truncate();stdout.write(json.dumps({'status':'ERROR',
                        'error':error,'conversation_id':'fixture-explicit-conversation'}).encode());stdout.flush()
                    return proc
                Executor(store,1,replay).run(True)
                native=store.rows()[0]['provenance']
                self.assertIsNone(native['session_error'])
                self.assertIsNone(native['effective_error'])
                self.assertEqual(len(calls),1)

    def test_50_current_terminal_quota_wins_even_when_the_same_text_was_historical(self):
        store=self.store(2);calls=[]
        with patch('pipeline_engine.native_error_scope',return_value={'scope':'historical'}):
            Executor(store,1,self.factory(calls,quota=True)).run(True)
        self.assertEqual(len(calls),1)
        self.assertEqual(store.summary()['phase'],'quota_waiting')
        self.assertEqual(store.rows()[0]['provenance']['native_error_scope']['scope'],'current_call')
        self.assertEqual(store.summary()['stats']['completed'],1)

    def test_51_identity_mismatch_overrides_network_error_and_cannot_accept_complete_results(self):
        store=self.store();worker=store.worker('W01')
        worker.update(conversation_id='correct-cid',model='gemini-3.8-flash-high',
            last_usage={'input_tokens':10},usage_conversation_id='correct-cid');store.worker('W01',worker)
        calls=[];normal=self.factory(calls)
        def wrong_identity(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            Path(command[command.index('--log-file')+1]).write_text('agent executor error: connection reset\n',encoding='utf-8')
            stdout.seek(0);stdout.truncate();stdout.write(json.dumps({'status':'ERROR','error':'connection reset',
                'conversation_id':'wrong-cid','usage':{'input_tokens':999}}).encode());stdout.flush()
            return proc
        Executor(store,1,wrong_identity).run(True)
        self.assertEqual(store.summary()['stats']['completed'],0)
        self.assertEqual(store.worker('W01')['pending_resume']['reason'],'conversation_identity_mismatch')
        self.assertEqual(store.worker('W01')['last_usage'],{'input_tokens':10})
        self.assertEqual(store.rows()[0]['qa_failures'],0)
        self.assertEqual(len(calls),6)
        self.assertTrue(all('correct-cid' in command for command in calls))

    def test_52_missing_identity_cannot_accept_a_complete_file(self):
        store=self.store();calls=[];normal=self.factory(calls)
        def missing(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            stdout.seek(0);stdout.truncate();stdout.write(b'{"status":"SUCCESS"}');stdout.flush()
            return proc
        Executor(store,1,missing).run(True)
        self.assertEqual(store.summary()['stats']['completed'],0)
        self.assertEqual(store.worker('W01')['pending_resume']['reason'],'missing_conversation_id')
        self.assertEqual(len(calls),1)

    def test_53_successful_retry_does_not_keep_the_previous_calls_identity_warning(self):
        store=self.store();worker=store.worker('W01')
        worker.update(conversation_id='correct-cid',model='gemini-3.8-flash-high');store.worker('W01',worker)
        calls=[];normal=self.factory(calls)
        def transient(command,cwd,stdout,stderr,**kwargs):
            proc=normal(command,cwd,stdout,stderr,**kwargs)
            if len(calls)==1:
                stdout.seek(0);stdout.truncate();stdout.write(b'{"status":"SUCCESS","conversation_id":"wrong-cid"}');stdout.flush()
            return proc
        Executor(store,1,transient).run(True)
        self.assertEqual(len(calls),2)
        native=store.rows()[0]['provenance']
        self.assertIsNone(native['session_error'])
        self.assertNotIn('reported_conversation_id',native)
        self.assertEqual(native['conversation_id'],'correct-cid')

    def test_54_resume_launch_cannot_overwrite_a_new_weekly_pause(self):
        from quota_control import observe_quota,pause_for_quota
        from update_quota_snapshot import record
        store=self.store();store.update_meta(owner_pid=os.getpid(),phase='running')
        observe_quota(store,record(store,five_hour=0,weekly=35))
        store.update_meta(owner_pid=None)
        fresh=record(store,five_hour=100,weekly=35)
        def launcher(command,**kwargs):
            pause_for_quota(store,{'weekly_remaining_percent':0,'five_hour_remaining_percent':100},
                'new native quota observation',force=True)
            return type('Process',(),{'pid':12345})()
        observe_quota(store,fresh,launcher)
        guard=store.meta()['quota_guard']
        self.assertTrue(guard['waiting_for_recovery']);self.assertTrue(guard['weekly_manual_hold'])
        self.assertNotIn('resumed_executor_pid',guard)

    def test_55_new_quota_episode_does_not_reuse_the_old_windows_or_recovery_evidence(self):
        from quota_control import pause_for_quota
        store=self.store();store.update_meta(owner_pid=os.getpid(),phase='running',quota_guard={
            'enabled':True,'waiting_for_recovery':False,'zero_windows':['five_hour'],
            'trigger_snapshot':{'old':True},'resuming_at':'old','resumed_executor_pid':999,'recovery_observed_at':'old'})
        pause_for_quota(store,{'native_error':'Individual quota reached'},'native terminal quota error')
        guard=store.meta()['quota_guard']
        self.assertEqual(guard['zero_windows'],[]);self.assertIsNone(guard['trigger_snapshot'])
        self.assertNotIn('resuming_at',guard);self.assertNotIn('resumed_executor_pid',guard)
        self.assertEqual(failure_kind('HTTP 429 Too Many Requests'),'rate_limited')

    def test_56_context_uses_latest_request_including_cache_after_compaction(self):
        from pipeline_engine import latest_context_usage
        source=self.root/'context_fixture.jsonl'
        steps=[{'step_index':i,'source':'MODEL','type':'PLANNER_RESPONSE','status':'DONE',
            'created_at':at,'input_tokens':fresh,'cache_read_tokens':cached}
            for i,at,fresh,cached in [(1,'2026-10-17T17:00:00Z',900000,0),
                (2,'2026-10-17T17:47:20Z',3394,200166),(3,'2026-10-17T17:56:30Z',17134,17284)]]
        source.write_text('\n'.join(json.dumps(s) for s in steps)+'\n{broken\n',encoding='utf-8')
        context=latest_context_usage('original-cid','2026-10-17T17:24:40+00:00',source)
        self.assertEqual(context['tokens'],34418)
        self.assertEqual(context['conversation_id'],'original-cid')
        self.assertEqual(context['step_index'],3)
        self.assertIsNone(latest_context_usage('cid','2026-10-18T00:00:00+00:00',source))

    def test_57_completed_context_rotates_before_next_packet_only_at_limit(self):
        from pipeline_engine import latest_context_usage,CONTEXT_TOKEN_LIMIT
        source=self.root/'context_rotation_fixture.jsonl'
        store=self.store(3);calls=[];default=self.factory(calls)
        sizes=[CONTEXT_TOKEN_LIMIT-1,CONTEXT_TOKEN_LIMIT,30000]
        def factory(command,cwd,stdout,stderr,**kwargs):
            proc=default(command,cwd,stdout,stderr,**kwargs)
            conv=command[command.index('--conversation')+1] if '--conversation' in command else 'context-session-'+str(len(calls))
            # Cumulative CLI input must never serve as current context size.
            stdout.seek(0);stdout.truncate();stdout.write(json.dumps({'status':'SUCCESS','conversation_id':conv,
                'usage':{'input_tokens':999999}}).encode());stdout.flush()
            source.write_text(json.dumps({'step_index':len(calls),'source':'MODEL','type':'PLANNER_RESPONSE',
                'status':'DONE','created_at':now(),'input_tokens':1000,
                'cache_read_tokens':sizes[len(calls)-1]-1000}),encoding='utf-8')
            return proc
        with patch('pipeline_engine.latest_context_usage',partial(latest_context_usage,transcript=source)):
            Executor(store,1,factory).run(True)
        self.assertNotIn('--conversation',calls[0]);self.assertIn('context-session-1',calls[1])
        self.assertNotIn('--conversation',calls[2])
        self.assertEqual(store.summary()['stats']['completed'],3)
        worker=store.worker('W01');self.assertIn('context-session-1',worker['history'])
        self.assertEqual(worker['last_context_rotation']['tokens'],CONTEXT_TOKEN_LIMIT)

    def test_58_large_context_never_replaces_pending_or_unfinished_session(self):
        from pipeline_engine import CONTEXT_TOKEN_LIMIT
        store=self.store();engine=Executor(store,1)
        worker=store.worker('W01');worker.update(conversation_id='pending-cid',
            context_rotation_eligible=True,context_usage={'conversation_id':'pending-cid','tokens':CONTEXT_TOKEN_LIMIT+1},
            pending_resume={'conversation_id':'pending-cid','keys':['unfinished'],'attempt':'original'})
        original=copy.deepcopy(worker)
        self.assertFalse(engine.rotate_large_completed_context(worker));self.assertEqual(worker,original)
        worker.pop('pending_resume');worker['context_rotation_eligible']=False
        self.assertFalse(engine.rotate_large_completed_context(worker))
        worker['context_rotation_eligible']=True;worker['context_usage']['conversation_id']='other-cid'
        self.assertFalse(engine.rotate_large_completed_context(worker))
        worker['context_usage']={}
        self.assertFalse(engine.rotate_large_completed_context(worker))

    def test_59_failed_high_context_keeps_original_conversation_for_all_five_retries(self):
        from pipeline_engine import CONTEXT_TOKEN_LIMIT
        store=self.store();calls=[]
        def usage(conv,*args):return {'conversation_id':conv,'tokens':CONTEXT_TOKEN_LIMIT+1}
        with patch('pipeline_engine.latest_context_usage',usage):
            Executor(store,1,self.factory(calls,always_bad=True)).run(True)
        worker=store.worker('W01')
        self.assertEqual(len(calls),6);self.assertTrue(all('--conversation' in c for c in calls[1:]))
        self.assertEqual(worker['pending_resume']['conversation_id'],'fixture-explicit-conversation')
        self.assertEqual(worker['retry_count'],5);self.assertFalse(worker['context_rotation_eligible'])
        self.assertNotIn('last_context_rotation',worker)

    def test_60_export_audit_accepts_valid_inherited_decisions_without_rewriting_labels(self):
        baseline={'defects':[{'id':'C','severity':'L1','object':'衣物','description':'衣物呈现不自然的紫红色块。'}]}
        row=self.store().rows()[0]
        row['record']['baseline']=copy.deepcopy(baseline)
        row.update(state='completed',defects=copy.deepcopy(baseline['defects']),provenance={},
            baseline_review={'saturation_defects':[],'other_additions':[],
                'other_decisions':{'P001':{'action':'retain','inherit':True,'reason':'该色块依然可见。'}}})
        original=copy.deepcopy(row)
        task=pipeline_delivery.make_task(row)
        audit=task['data']['review_audit_html']
        self.assertIn('衣物呈现不自然的紫红色块。',audit);self.assertIn('保留',audit)
        self.assertEqual(row,original)
        self.assertEqual(task['data']['pipeline_review']['defects'],original['defects'])
        row['baseline_review']['other_decisions']['P001']={'action':'retain','object':'衣物',
            'description':'衣物边缘呈现突兀的紫红色斑块。','reason':'规范描述。'}
        audit=pipeline_delivery.make_task(row)['data']['review_audit_html']
        self.assertIn('衣物边缘呈现突兀的紫红色斑块。',audit)
        row['baseline_review']['other_decisions']['P001']={'action':'remove','reason':'未发现该异常。'}
        self.assertIn('删除',pipeline_delivery.make_task(row)['data']['review_audit_html'])

    def test_61_drain_finishes_live_task_blocks_claims_and_manual_resume_works(self):
        store=self.store(2);calls=[];started=threading.Event();finish=threading.Event()
        normal=self.factory(calls)
        class Running:
            pid=0;returncode=None
            def poll(self):
                if finish.is_set():self.returncode=0
                return self.returncode
            def wait(self):return self.returncode
        def launch(*args,**kwargs):
            normal(*args,**kwargs);started.set();return Running()
        engine=Executor(store,1,launch)
        with patch.object(engine,'terminate',side_effect=AssertionError('Drain killed a live call')):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(engine.run,True)
                try:
                    self.assertTrue(started.wait(10))
                    peer=Store(store.run_dir);peer.command('drain')
                    self.assertEqual(peer.meta()['phase'],'draining')
                    self.assertEqual(peer.claim('secondary_chroma','W02'),[])
                    self.assertFalse(future.done());self.assertEqual(len(calls),1)
                finally:finish.set()
                future.result(timeout=30)
        state=store.summary()
        self.assertEqual(state['phase'],'paused');self.assertEqual(state['stop_reason'],'user_drain')
        self.assertEqual(state['stats']['completed'],1);self.assertEqual(state['stats']['secondary_ready'],1)
        self.assertFalse(store.worker('W01').get('pending_resume'))
        self.assertTrue(all(r['qa_failures']==0 for r in store.rows()))
        before={r['source_sample_key']:copy.deepcopy(r) for r in store.rows() if r['state']=='completed'}
        Executor(store,1,self.factory(calls)).run(True)
        self.assertEqual(len(calls),2);self.assertIn('--conversation',calls[1])
        self.assertEqual(store.summary()['stats']['completed'],2)
        for row in store.rows():
            if row['source_sample_key'] in before:self.assertEqual(row,before[row['source_sample_key']])

    def test_62_drain_allows_current_packet_retry_and_preserves_exhausted_packet(self):
        for always_bad,expected_calls in [(False,2),(True,6)]:
            with self.subTest(always_bad=always_bad):
                store=self.store(2);calls=[];normal=self.factory(calls,bad_first=True,always_bad=always_bad)
                def launch(*args,**kwargs):
                    proc=normal(*args,**kwargs)
                    if len(calls)==1:store.command('drain')
                    return proc
                engine=Executor(store,1,launch)
                with patch.object(engine,'terminate',side_effect=AssertionError('Drain killed a retry')):
                    engine.run(True)
                self.assertEqual(len(calls),expected_calls)
                self.assertEqual(store.meta()['stop_reason'],'user_drain')
                self.assertTrue(all('--conversation' in call for call in calls[1:]))
                self.assertEqual(store.summary()['stats']['secondary_ready'],2 if always_bad else 1)
                pending=store.worker('W01').get('pending_resume')
                if always_bad:
                    self.assertEqual(pending['continue_retries'],5)
                    self.assertEqual(len(pending['keys']),1)
                    self.assertEqual(Store(store.run_dir).claim_resume(store.worker('W01')),[])
                else:self.assertIsNone(pending)

    def test_63_drain_then_safety_stop_still_terminates_current_call(self):
        store=self.store();calls=[];started=threading.Event()
        class Running:
            pid=0;returncode=None
            def poll(self):return self.returncode
            def wait(self):return self.returncode
        proc=Running()
        def launch(*args,**kwargs):calls.append(args);started.set();return proc
        engine=Executor(store,1,launch);killed=[]
        def terminate(p):killed.append(p);p.returncode=1
        with patch.object(engine,'terminate',side_effect=terminate):
            with ThreadPoolExecutor(max_workers=1) as pool:
                future=pool.submit(engine.run,True)
                try:
                    self.assertTrue(started.wait(10));store.command('drain');engine.stop('user_pause')
                finally:proc.returncode=1
                future.result(timeout=30)
        self.assertTrue(killed);self.assertEqual(store.meta()['stop_reason'],'user_pause')
        self.assertEqual(len(calls),1);self.assertEqual(store.rows()[0]['qa_failures'],0)

    def test_64_dashboard_drain_checks_executor_capability_and_rejects_new_work(self):
        store=self.store();preflight(store);before=store.rows()
        store.update_meta(owner_pid=os.getpid(),phase='running',heartbeat_at=now())
        server=ThreadingHTTPServer(('127.0.0.1',0),partial(DashboardHandler,store=store))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        base=f'http://127.0.0.1:{server.server_port}'
        def post(action):
            return urllib.request.urlopen(urllib.request.Request(base+'/api/action/'+action,data=b'{}',method='POST'))
        try:
            with self.assertRaises(urllib.error.HTTPError) as ctx:post('drain')
            self.assertEqual(ctx.exception.code,409);self.assertFalse(store.meta().get('dispatch_hold'))
            store.update_meta(dispatch_control={'version':1,'owner_pid':os.getpid()})
            with post('drain') as response:first=json.load(response)
            with post('drain') as response:second=json.load(response)
            self.assertEqual(first['command_id'],second['command_id']);self.assertFalse(second['created'])
            for action in ['start','continue-blocked']:
                with self.assertRaises(urllib.error.HTTPError) as ctx:post(action)
                self.assertEqual(ctx.exception.code,409)
            self.assertEqual(store.rows(),before)
        finally:server.shutdown();server.server_close();thread.join()

    def test_65_quota_stop_overrides_drain_but_recovery_cannot_auto_resume_it(self):
        from quota_control import observe_quota
        from update_quota_snapshot import record
        store=self.store(2);calls=[];normal=self.factory(calls,quota=True)
        def launch(*args,**kwargs):
            proc=normal(*args,**kwargs);store.command('drain');return proc
        Executor(store,1,launch).run(True)
        self.assertEqual(store.meta()['stop_reason'],'quota_exhausted')
        self.assertEqual(store.meta()['phase'],'quota_waiting');self.assertEqual(len(calls),1)
        with patch('quota_control.subprocess.Popen',side_effect=AssertionError('Drain auto-resumed')):
            observe_quota(store,record(store,five_hour=100,weekly=100))
        self.assertTrue(store.meta()['dispatch_hold']['active'])

    def test_66_pending_drain_before_workers_start_dispatches_nothing(self):
        store=self.store();before=store.rows();calls=[];store.command('drain')
        Executor(store,1,self.factory(calls)).run(True)
        self.assertEqual(calls,[]);self.assertEqual(store.rows(),before)
        self.assertEqual(store.meta()['phase'],'paused');self.assertEqual(store.pending_commands(),[])

    def test_10_initial_then_secondary_changes_session_and_preserves_baseline(self):
        store=self.store();row=store.rows()[0]
        row['record']['baseline']=None;row.update(stage='initial_rgb',state='initial_rgb_ready')
        with store.tx() as db:Store.put_sample(db,row)
        calls=[]
        default=self.factory(calls)
        def factory(command,cwd,stdout,stderr,**kwargs):
            cwd=Path(command[command.index("--log-file")+1]).parent
            request=read(Path(cwd)/'request.json')
            if request['stage']=='initial_rgb':
                calls.append(command);raw=read(Path(cwd)/'reviews_gemini.json')
                raw['reviews']={'S001':[]};raw['category_checks']={'S001':{c:{'status':'clear','evidence':'Offline fixture observation'} for c in ['B','C','D','F']}}
                write(Path(cwd)/'reviews_gemini.json',raw)
                stdout.write(b'{"conversation_id":"initial-fixture-session","status":"SUCCESS"}');stdout.flush()
                class Finished:
                    pid=0;returncode=0
                    def poll(self):return 0
                    def wait(self):return 0
                return Finished()
            raw=read(Path(cwd)/'reviews_gemini.json')
            self.assertEqual(request['secondary_baseline']['S001']['other_defects'],[])
            # Secondary review of empty initial baseline remains a separate completed stage.
            calls.append(command)
            raw['reviews']={'S001':{'saturation_defects':[],'other_decisions':{},'other_additions':[]}}
            raw['category_checks']={'S001':{c:{'status':'clear','evidence':'Offline fixture observation'} for c in ['B','C','D','E1','E2','F']}}
            write(Path(cwd)/'reviews_gemini.json',raw)
            stdout.write(b'{"conversation_id":"secondary-fixture-session","status":"SUCCESS"}');stdout.flush()
            class Finished:
                pid=0;returncode=0
                def poll(self):return 0
                def wait(self):return 0
            return Finished()
        Executor(store,1,factory).run(True)
        self.assertEqual(len(calls),2)
        self.assertNotIn('--conversation',calls[1])
        self.assertEqual(store.rows()[0]['state'],'completed')
        self.assertEqual(store.rows()[0]['record']['baseline']['source']['kind'],'new_initial_NR_review')


if __name__=='__main__':
    unittest.main(verbosity=2)
