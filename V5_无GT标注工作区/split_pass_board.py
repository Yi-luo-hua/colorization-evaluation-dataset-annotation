"""Read-only view of the V5 full annotation queue, using the project dashboard styles."""

import argparse
from collections import Counter
from contextlib import closing
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import sqlite3

from split_pass_pilot import ALLOWED, load
from pipeline_store import pid_alive

HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent / "annotation_delivery/train_val_v1_20261015/web/index.html"


def status(run):
    cfg = load(run / "preparation.json")
    uri = (run / "queue.sqlite3").as_uri() + "?mode=ro"
    with closing(sqlite3.connect(uri, uri=True, timeout=5)) as db:
        counts = {state: {"packs": packs, "images": images}
                  for state, packs, images in db.execute("SELECT status,COUNT(*),SUM(size) FROM batches GROUP BY status")}
        scopes = list(db.execute("""
            SELECT s.split,s.model,COUNT(*),SUM(b.status='completed')
            FROM samples AS s JOIN batches AS b USING (batch_id) GROUP BY s.split,s.model
            ORDER BY CASE s.split WHEN 'train' THEN 1 WHEN 'val' THEN 2 ELSE 3 END,s.model
        """))
        open_batches = list(db.execute("SELECT batch_id,size,status FROM batches WHERE status IN ('running','paused') ORDER BY seq"))

    complete = counts.get("completed", {}).get("images", 0)
    stages = Counter({stage: complete for stage in ALLOWED})
    active = []
    for batch, size, state in open_batches:
        directory = run / "batches" / batch
        for stage in ALLOWED:
            proof_path = directory / f"{stage}.proof.json"
            if proof_path.is_file() and "step" in load(proof_path):
                stages[stage] += size
        status_path = directory / "status.json"
        info = load(status_path) if status_path.is_file() else {}
        active.append({"batch": batch, "images": size, "stage": info.get("stage"),
                       "state": info.get("state", state) if state == "running" else "paused",
                       "live": bool(info.get("pid") and pid_alive(info["pid"])),
                       "attempt": info.get("attempt"), "problem": info.get("problem")})
    return {"run": run.name, "model": cfg["model"], "total": cfg["images"], "batch_size": cfg["batch_size"],
            "worker_limit": cfg["default_workers"], "starter_images": cfg["prepared_starter_images"],
            "counts": counts, "scopes": scopes, "stages": dict(stages), "active": active[:24]}


class Board(BaseHTTPRequestHandler):
    def __init__(self, *args, run, page, **kwargs):
        self.run = run
        self.page = page
        super().__init__(*args, **kwargs)

    def send(self, code, body, content_type):
        self.send_response(code)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            self.send(200, self.page, "text/html")
        elif self.path == "/api/status":
            payload = json.dumps(status(self.run), ensure_ascii=False).encode("utf-8")
            self.send(200, payload, "application/json")
        else:
            self.send_error(404)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8948)
    args = parser.parse_args()
    run = args.run.resolve()
    status(run)
    styles = LEGACY.read_text(encoding="utf-8").split("<style>", 1)[1].split("</style>", 1)[0]
    page = (HERE / "split_pass_board.html").read_text(encoding="utf-8").replace("/* PROJECT_DASHBOARD_STYLES */", styles)
    handler = partial(Board, run=run, page=page.encode("utf-8"))
    with ThreadingHTTPServer(("127.0.0.1", args.port), handler) as http:
        print(f"V5 full queue dashboard at http://127.0.0.1:{args.port}/", flush=True)
        http.serve_forever()


if __name__ == "__main__":
    main()

