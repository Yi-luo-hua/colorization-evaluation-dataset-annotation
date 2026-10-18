"""A slow/failed batch must not prevent independent batches from running."""
import itertools
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
import run_sheet_workers as queue
from workflow import read_json,write_json,ANNOTATION_CONTRACT


class RollingChecks(unittest.TestCase):
    def exercise(self,fail=False):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);a=root/'a';b=root/'b';a.mkdir();b.mkdir()
            config={'annotation_contract':ANNOTATION_CONTRACT,'visual_harness':{'parallel_scheduler':{'workers':2,'sheets_per_job':1}}}
            manifests={a:{'configuration':config,'sheets':[{'path':'one.png'},{'path':'two.png'}],'records':[{'sample_key':'A1'},{'sample_key':'A2'}]},
                       b:{'configuration':config,'sheets':[{'path':'one.png'}],'records':[{'sample_key':'B1'}]}}
            exported_b=threading.Event();finished=[];pids=itertools.count(100)
            def prepare(baseline,child,harness,selected_sheets):
                child.mkdir();calls=child/'agy_calls'/'first';calls.mkdir(parents=True)
                m={'records':[{'sample_key':child.name}]};manifests[child]=m
                write_json(calls/'result.json',{'state':'candidate_exported','elapsed_seconds':0.1,'usage':{'total_tokens':1}})
                return m
            class Process:
                def __init__(self,command,**kwargs):
                    self.child=Path(command[command.index('--batch')+1]);self.pid=next(pids)
                    self.slow=self.child.parent.parent==a and self.child.name=='job_001'
                    self.returncode=1 if fail and self.slow else 0
                def communicate(self):
                    if self.slow and not fail and not exported_b.wait(5):raise AssertionError('Batch B was blocked by batch A')
                    return b'',b'fixture failure' if self.returncode else b''
            def finish(out,manifest,results,failures,*rest):
                finished.append(out.name)
                if out==b:exported_b.set()
                return {'state':'workers_incomplete' if failures else 'candidate_exported','elapsed_seconds':0.1}
            argv=['run_sheet_workers','--batch',str(a),str(b),'--queue-run-id','global','--workers','2','--sheets-per-job','1']
            with patch.object(sys,'argv',argv),patch.object(queue,'OUTPUT',root),\
                 patch.object(queue,'verify_sources',side_effect=lambda p:manifests[p]),\
                 patch.object(queue,'prepare_trial',side_effect=prepare),patch.object(queue.subprocess,'Popen',Process),\
                 patch.object(queue,'finish_batch',side_effect=finish),patch.object(queue,'combine_queue',return_value='fixture candidate'):
                if fail:
                    with self.assertRaises(SystemExit):queue.main()
                else:queue.main()
            return finished,read_json(root/'global/queue_result.json')

    def test_next_batch_exports_while_previous_batch_is_still_running(self):
        finished,result=self.exercise()
        self.assertEqual(finished,['b','a']);self.assertEqual(result['failures'],[])
        self.assertEqual(result['batches']['b']['state'],'candidate_exported')

    def test_failed_batch_does_not_cancel_other_batches(self):
        finished,result=self.exercise(fail=True)
        self.assertEqual(set(finished),{'a','b'});self.assertEqual(len(result['failures']),1)
        self.assertEqual(result['batches']['a']['state'],'workers_incomplete')
        self.assertEqual(result['batches']['b']['state'],'candidate_exported')


if __name__=='__main__':unittest.main(verbosity=2)
