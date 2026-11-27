"""Adapt the full V5 queue to the existing annotation dashboard contract."""

from collections import Counter
from contextlib import closing
from datetime import datetime
from functools import partial
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import sqlite3
from urllib.parse import parse_qs, urlparse

from dashboard_server import DashboardHandler, pid_alive

FIRST = "01_initial"
SECOND = "02_color_and_distribution"
BLIND = "03a_independent_review"
FINAL = "03b_finalize_review"
ROLES = {FIRST: "initial_rgb", SECOND: "secondary_chroma", BLIND: "tertiary_empty", FINAL: "tertiary_empty"}


def load(path):
    return json.loads(path.read_bytes())



class FullQueue:
    def __init__(self, run):
        self.run_dir = run
        self.cfg = load(run / "preparation.json")
        self.uri = (run / "queue.sqlite3").as_uri() + "?mode=ro"

    def db(self):
        return closing(sqlite3.connect(self.uri, uri=True, timeout=5))

    def info(self, batch):
        path = self.run_dir / "batches" / batch / "status.json"
        return load(path) if path.is_file() else {}

    def summary(self):
        with self.db() as db:
            db.execute("BEGIN")
            totals = dict(db.execute("SELECT status,SUM(size) FROM batches GROUP BY status"))
            in_flight = list(db.execute(
                "SELECT batch_id,size,status FROM batches WHERE status IN ('running','paused')"))
            have_lanes = db.execute("SELECT 1 FROM sqlite_master WHERE name='worker_lanes'").fetchone()
            lanes = list(db.execute("""SELECT slot,b.batch_id,b.status,assigned_at
                FROM worker_lanes JOIN batches AS b USING(batch_id)""")) if have_lanes else []
            pending = {}
            for _, batch, state, _ in lanes:
                if state == "paused":
                    pending[batch] = [sid for sid, in db.execute(
                        "SELECT sid FROM samples WHERE batch_id=? ORDER BY sid", (batch,))]
        total = sum(totals.values())
        completed = totals.get("completed", 0)
        worker_limit = self.cfg["default_workers"]
        observed = datetime.now().astimezone().isoformat()
        progress = Counter({stage: completed for stage in ROLES})
        workers = {f"W{i:02d}": {"worker_id": f"W{i:02d}", "active": False, "status": "idle",
                                 "role": ROLES[FIRST], "productive_rounds": 0}
                   for i in range(1, worker_limit + 1)}
        batch_rounds = Counter()
        for batch, size, state in in_flight:
            directory = self.run_dir / "batches" / batch
            for stage in ROLES:
                receipt = directory / f"{stage}.proof.json"
                if receipt.is_file() and "step" in load(receipt):
                    progress[stage] += size
                    batch_rounds[batch] += 1

        for slot, batch, state, assigned_at in lanes:
            worker = workers.get(f"W{slot:02d}")
            if worker is None or state == "completed":
                continue
            path = self.run_dir / "batches" / batch / "status.json"
            info = self.info(batch)
            live = False
            status = "session_blocked"
            if state == "running":
                status = "preparing"
                if info and path.stat().st_mtime >= datetime.fromisoformat(assigned_at).timestamp():
                    status = info["state"]
                    live = bool(info.get("pid") and pid_alive(info["pid"]))
            worker.update(active=live, status=status, batch_id=batch, productive_rounds=batch_rounds[batch],
                          role=ROLES.get(info.get("stage"), ROLES[FIRST]),
                          last_session_error=info.get("problem"), conversation_id=info.get("conversation_id"),
                          started_at=info.get("started_at"))
            if status == "retry_wait":
                worker["continue_retry"] = {"attempt": info["retry_attempt"], "limit": 5, "next_at": info["next_at"]}
            if state == "paused":
                worker["pending_resume"] = {"keys": pending[batch], "reason": info.get("problem") or "批次已保留"}

        running = sum(w["active"] for w in workers.values())
        assigned = totals.get("running", 0)
        phase = ("running" if assigned else "completed" if total == completed
                 else "needs_attention" if totals.get("paused") else "prepared")
        stage_progress = {
            "total": total * 3, "completed": progress[FIRST] + progress[SECOND] + progress[FINAL],
            "initial": {"total": total, "completed": progress[FIRST]},
            "secondary": {"total": total, "completed": progress[SECOND]},
            "tertiary": {"total": total, "completed": progress[FINAL]},
        }
        data = {
            "stats": {"total": total, "completed": completed, "program_validated": completed,
                      "fixed_a": 0, "needs_manual": totals.get("paused", 0), "initial_ready": totals.get("queued", 0),
                      "secondary_ready": 0, "tertiary_ready": 0, "running": totals.get("running", 0)},
            "stage_progress": stage_progress, "workers": workers,
            "phase": phase, "active_calls": running, "engine_alive": bool(assigned), "heartbeat_healthy": bool(assigned),
            "worker_limit": worker_limit, "observed_at": observed,
            "preflight": {"ready": False, "data_prepared": True}, "delivery": {"detail": "全量结果尚未导入"},
        }
        quota_path = self.run_dir / "quota_snapshot.json"
        if quota_path.is_file():
            quota = load(quota_path)
            data["quota_snapshot"] = {
                "five_hour_remaining_percent": quota["five_hour"], "weekly_remaining_percent": quota["weekly"],
                "five_hour_refresh_in": quota["five_reset"], "weekly_refresh_in": quota["weekly_reset"],
                "checked_at": quota["observed_at"], "source": "native agy /usage",
            }
            data["quota_monitor"] = {"status": "ok", "interval_minutes": 10, "enabled": bool(running)}
        wait = self.run_dir / "quota_wait.json"
        if wait.is_file():
            guard = load(wait)
            if guard["state"] in {"five_hour", "weekly_manual"}:
                data["quota_guard"] = {"waiting_for_recovery": True, "triggered_at": guard["at"],
                                       "weekly_manual_hold": guard["state"] == "weekly_manual"}
        return data

    def page(self, page, size, state, query):
        size = max(1, min(size, 100))
        page = max(1, page)
        with self.db() as db:
            db.execute("BEGIN")
            roles = {batch: ROLES.get(self.info(batch).get("stage"), ROLES[FIRST])
                     for batch, in db.execute("SELECT batch_id FROM batches WHERE status='running'")}
            def sample_state(batch, current):
                if current == "running":
                    return roles[batch] + "_running"
                return {"queued": "initial_rgb_ready", "paused": "needs_manual", "completed": "completed"}[current]
            db.create_function("full_state", 2, sample_state, deterministic=True)
            condition = """
                FROM samples AS s JOIN batches AS b USING (batch_id)
                WHERE instr(lower(s.sample_key), lower(?))>0
                AND (?='all' OR full_state(s.batch_id,b.status)=?)
            """
            params = (query, state, state)
            total, = db.execute("SELECT COUNT(*) " + condition, params).fetchone()
            page = min(page, max(1, (total + size - 1) // size))
            results = db.execute(
                "SELECT s.sample_key,s.sid,s.batch_id,full_state(s.batch_id,b.status) " + condition
                + " ORDER BY s.sample_key LIMIT ? OFFSET ?", (*params, size, (page - 1) * size)).fetchall()
        final_by_batch = {}
        items = []
        for key, sid, batch, current in results:
            defects = None
            if current == "completed":
                if batch not in final_by_batch:
                    final_by_batch[batch] = load(self.run_dir / "batches" / batch / f"{FINAL}.accepted.json")
                defects = final_by_batch[batch][sid]
            items.append({"source_sample_key": key, "state": current, "defects": defects,
                          "last_feedback": self.info(batch).get("problem") if current == "needs_manual" else None})
        return {"total": total, "page": page, "size": size, "items": items}

    def import_preview(self, query):
        filters = {name: query.get(name, ["all"])[0] for name in ("split", "model")}
        with self.db() as db:
            total, = db.execute("""
                SELECT COUNT(*) FROM samples
                WHERE (?='all' OR split=?) AND (?='all' OR model=?)
            """, (filters["split"], filters["split"], filters["model"], filters["model"])).fetchone()
        start = max(1, int(query.get("start", ["1"])[0]))
        end = min(total, int(query.get("end", [str(total)])[0] or total))
        selected = max(0, end - start + 1)
        return {"filtered_total": total, "selected": selected, "eligible": 0, "excluded": selected}


class FullBoard(DashboardHandler):
    def do_GET(self):
        route = urlparse(self.path)
        if route.path == "/":
            source = Path(self.store.cfg["source_root"])
            template = source / "annotation_delivery/train_val_v1_20261015/web/index.html"
            html = template.read_text(encoding="utf-8")
            html = html.replace("三阶段标注", "V5 全量三轮 · 每包 10 张")
            # Keep the existing workbench and DOM. Its legacy dispatch actions do
            # not operate on the separate full-image queue.
            html = html.replace('<div class="control-actions">', '<div class="control-actions" style="display:none">')
            html = html.replace("等待本次页面的操作与新增完成事件。", "全量上色图队列，等待新增完成事件。")
            html = html.replace("const stateLabel=retrying ?", """const laneLabel = {
              preparing: '备包中', waiting_to_start: '等待创建会话', starting_session: '创建会话中'
            }[w.status];
    const stateLabel=laneLabel || (retrying ?""").replace("isolated ? '已隔离' : '空闲';",
                                                           "isolated ? '已隔离' : '空闲');")
            html = html.replace("会话 ID：${escapeText(w.conversation_id || '尚未创建')}",
                                "批次：${escapeText(w.batch_id || '未派发')}&#10;会话 ID：${escapeText(w.conversation_id || '尚未创建')}")
            html = html.replace("w.role === 'initial_rgb' ? '初标' : '二次'",
                                "w.role === 'initial_rgb' ? '初标' : w.role === 'tertiary_empty' ? '检查' : '二次'")
            payload = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        elif route.path == "/api/import-preview":
            try:
                self.reply(200, self.store.import_preview(parse_qs(route.query)))
            except ValueError as error:
                self.reply(400, {"error": str(error)})
        else:
            super().do_GET()

    def do_POST(self):
        self.reply(405, {"error": "此窗口只读取全量上色图队列与验收进度"})


def serve_full(run, port):
    snapshot = FullQueue(run.resolve())
    snapshot.summary()
    handler = partial(FullBoard, store=snapshot, snapshot=snapshot)
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"Existing annotation dashboard http://127.0.0.1:{port}/ | {run}", flush=True)
        server.serve_forever()

