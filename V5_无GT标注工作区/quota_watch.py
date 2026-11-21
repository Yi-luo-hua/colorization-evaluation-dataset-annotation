"""Poll native agy /usage and apply the legacy global pause to the V5 executor."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
import threading
from unittest.mock import patch

WORKSPACE=Path(__file__).resolve().parent
LEGACY=WORKSPACE.parent/"annotation_delivery/train_val_v1_20261015/scripts"
sys.path.insert(0,str(LEGACY))
from native_quota_monitor import DEPENDENCIES, query_native, monitor_lock
from pipeline_store import Store, pid_alive
from quota_control import pause_for_quota, zero_windows
from update_quota_snapshot import record


def watch(binary):
    sys.path.insert(0,str(DEPENDENCIES))
    from winpty import PtyProcess
    spawn=PtyProcess.spawn
    stopped=threading.Event()
    store=Store(WORKSPACE/"local/single1000")
    with monitor_lock(store.run_dir):
        while not (store.run_dir/"V5_单轮1000.zip").exists():
            try:
                with patch.object(PtyProcess,"spawn",side_effect=lambda args,**kw:spawn([binary,*args[1:]],**kw)):
                    observation=record(store,**query_native(stopped))
                snap=observation["snapshot"]
                meta=store.meta()
                guard=meta.get("quota_guard") or {}
                if zero_windows(snap):
                    pause_for_quota(store,snap,"native agy /usage")
                elif (guard.get("waiting_for_recovery") and not guard.get("weekly_manual_hold")
                      and not guard.get("manual_hold") and not pid_alive(meta.get("owner_pid"))
                      and snap["checked_at"]>guard["last_exhaustion_at"]):
                    guard.update(waiting_for_recovery=False,recovery_observed_at=snap["checked_at"])
                    store.update_meta(quota_guard=guard)
                    with (store.run_dir/"resume.log").open("ab") as log:
                        subprocess.Popen([sys.executable,"-X","utf8","run1000.py","--agy",binary],
                                         cwd=WORKSPACE,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
            except Exception as exc:
                record(store,error=str(exc))
            stopped.wait(600)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--agy",required=True)
    watch(parser.parse_args().agy)
