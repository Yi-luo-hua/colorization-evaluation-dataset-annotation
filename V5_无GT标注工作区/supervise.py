"""Reuse the original dashboard UI, sample list and live worker statistics."""
from functools import partial
from http.server import ThreadingHTTPServer
import sys
import os
import shutil
import subprocess
from single1000 import REPO,RUN
legacy=REPO/"annotation_delivery/train_val_v1_20261015"
sys.path.insert(0,str(legacy))
sys.path.insert(0,str(legacy/"scripts"))
# The legacy dashboard imports its own prepare module for legacy commands.
sys.modules.pop("prepare",None)
from dashboard_server import DashboardHandler, DashboardState, Store


class Snapshot(DashboardState):
    def summary(self):
        data=super().summary()
        stats=data["stats"]
        stages=data["stage_progress"].copy()
        stages.update(total=stats["total"],completed=stats["completed"],
                      percent=round(100*stats["completed"]/max(1,stats["total"]),2),
                      initial={"total":0,"completed":0})
        data["stage_progress"]=stages
        return data


class Board(DashboardHandler):
    def do_GET(self):
        if self.path!="/":return super().do_GET()
        html=(legacy/"web/index.html").read_text(encoding="utf8").replace("三阶段标注","V5 无 GT 单轮").replace(">二次标注<",">V5 单轮<")
        self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        if self.path=="/api/action/import":return self.reply(409,{"error":"本轮使用 ZIP 交付"})
        super().do_POST()


if __name__=="__main__":
    store=Store(RUN)
    snapshot=Snapshot(store)
    snapshot.refresh_metrics()
    snapshot.start()
    def launch(_command,**kwargs):
        binary=os.environ.get("MCL_AGY") or shutil.which("agy") or str(Path(sys.executable).parent/"agy/bin/agy.exe")
        kwargs["cwd"]=str(Path(__file__).resolve().parent)
        return subprocess.Popen([sys.executable,"-X","utf8","run1000.py","--agy",binary],**kwargs)
    from pathlib import Path
    ThreadingHTTPServer(("127.0.0.1",8947),partial(Board,store=store,snapshot=snapshot,launcher=launch)).serve_forever()
