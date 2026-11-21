"""Run two turns in one native session for each V5 annotation packet."""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, wait
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import zipfile

from prepare import prepare_examples, prepare_task, write_text
from single1000 import COMPLETION_ARCHIVE, MODEL, PUBLIC, ROOT, RUN, REPO, sample
from turns import EXAMPLES, LABEL, prompt_for, result_path, verify_turn
from validate import validate

sys.path.append(str(REPO / "annotation_delivery/train_val_v1_20261015/scripts"))
from batch_auth import batch_environment
from pipeline_store import OwnerLock, Store, now, pid_alive
from quota_control import explicit_exhaustion, pause_for_quota

store = Store(RUN)
stop = threading.Event()
drain = threading.Event()
finished = threading.Event()
continue_requested = threading.Event()
ROLE = "secondary_chroma"


def keys(paths):
    return ["/".join(("train" if p.startswith("9_14") else "val", Path(p).parent.name, Path(p).stem)) for p in paths]


def seed(paths):
    if store.rows():
        return
    with store.tx() as db:
        for index, key in enumerate(keys(paths)):
            store.put_sample(db, dict(source_sample_key=key, state=ROLE + "_ready", stage=ROLE,
                                      group_id=f"{index // 10 + 1:03}", ready_at="0"))


def first_event(log):
    if log.exists():
        with log.open(encoding="utf-8-sig", errors="replace") as stream:
            try:
                return json.loads(stream.readline()).get("conversation_id")
            except ValueError:
                pass


def accept(document, cid, rows, worker, failures, reads):
    result = result_path(document)
    mapping = json.loads((ROOT / "local/task_index" / (result.stem + ".json")).read_text(encoding="utf8"))
    report = {keys([mapping[r["id"]]])[0]: r for r in json.loads(result.read_text(encoding="utf-8-sig"))}
    if set(report) != {r["source_sample_key"] for r in rows}:
        raise ValueError("S 编号与队列源身份不一致")
    batch = document.parent.parent.name
    write_text(RUN / f"{batch}.label.receipts.json", json.dumps(reads, ensure_ascii=False))
    with store.tx() as db:
        for row in rows:
            review = report[row["source_sample_key"]]
            row.update(state="completed", checks=review["checks"], defects=review["defects"],
                       notes=review.get("notes", {}), qa_failures=failures,
                       provenance=dict(worker_id=worker, conversation_id=cid, result_path=str(result.resolve()),
                                       finished_at=now()))
            store.put_sample(db, row)
        store.put_meta(db, "state_updated_at", now())


def command_loop():
    while not finished.wait(1):
        store.update_meta(heartbeat_at=now())
        for command in store.pending_commands():
            action = command["action"]
            if action in ("stop", "quota-stop"):
                stop.set()
            elif action == "drain":
                drain.set()
            elif action == "continue-blocked":
                continue_requested.set()
            store.ack(command["id"])


def run_phase(agy, directory, document, phase, worker, status, on_success):
    """Finish or resume the current turn without changing the native session ID."""
    name = worker["worker_id"]
    pending = worker["pending_resume"]
    marker = EXAMPLES if phase == "examples" else LABEL
    phase_name = "阅读示例" if phase == "examples" else "标注待标图"
    cid = worker.get("conversation_id")
    for retry in range(worker.get("retry_count", 0), 6):
        if stop.is_set() or drain.is_set():
            status(status="awaiting_continue")
            return False
        process = None
        if worker.get("call_log"):
            log = RUN / worker["call_log"]
            pid = worker.get("pid")
        else:
            log = RUN / f"b{pending['batch']:03}.{phase}.{time.time_ns()}.jsonl"
            args = [agy, "--model", MODEL, "--mode", "accept-edits", "--output-format", "stream-json"]
            if cid:
                args.extend(("--conversation", cid))
            prompt = prompt_for(marker, document, worker.get("last_error", ""))
            with log.open("wb") as out, log.with_suffix(".err").open("wb") as errors:
                process = subprocess.Popen(args + ["--print", prompt], cwd=directory, stdout=out, stderr=errors,
                                           env=batch_environment(RUN / f"auth-{name}.json"),
                                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            pid = process.pid
        status(pid=pid, call_log=log.name, status="running", current_task=f"{directory.name} · {phase_name}",
               retry_count=retry)
        while True:
            if not cid and (cid := first_event(log)):
                status(conversation_id=cid)
            alive = process.poll() is None if process else pid_alive(pid)
            if not alive:
                break
            if stop.wait(1):
                if process:
                    process.terminate()
                    process.wait()
                elif pid_alive(pid):
                    os.kill(pid, 15)
                status(status="awaiting_continue", pid=None)
                return False

        actual = first_event(log)
        if not cid and actual:
            cid = actual
            status(conversation_id=cid)
        try:
            if not actual or actual != cid:
                raise ValueError("会话身份异常")
            on_success(cid, retry)
            return True
        except (ValueError, OSError, TypeError, KeyError) as exc:
            feedback = str(exc)
            store.event("validation_failure", worker_id=name, batch=pending["batch"], phase=phase,
                        attempt=retry + 1, detail=feedback)
            errors = log.with_suffix(".err")
            if errors.exists() and explicit_exhaustion(errors.read_text(encoding="utf8", errors="replace")):
                pause_for_quota(store, {"source": "current agy stderr", "batch": pending["batch"]},
                                "current agy stderr", force=True)
                stop.set()
                store.update_meta(phase="quota_paused")
            if stop.is_set() or drain.is_set():
                status(status="awaiting_continue", pid=None, last_error=feedback)
                return False
            status(call_log=None, pid=None, last_error=feedback,
                   status="awaiting_continue" if retry == 5 or not cid else "retry_wait")
            if retry == 5 or not cid:
                return False
            status(retry_count=retry + 1)
            if stop.wait(20):
                return False
    return False


def lane(number, paths, agy):
    name = f"W{number:02}"
    worker = store.worker(name)

    def status(**fields):
        worker.update(fields)
        store.worker(name, worker)

    def release():
        status(status="idle", pid=None, call_log=None, current_task=None, pending_resume=None,
               retry_count=0, conversation_id=None, last_error="")

    if (worker.get("status") == "awaiting_continue" and worker.get("retry_count") == 5
            and not worker.get("call_log")):
        status(retry_count=0)

    while not stop.is_set() and not drain.is_set():
        reserved = worker.get("pending_resume")
        if reserved:
            rows = [r for r in store.rows() if r["source_sample_key"] in reserved["keys"]]
            if not rows or all(r["state"] == "completed" for r in rows):
                release()
                continue
        else:
            rows = [r for r in store.rows() if r.get("worker_id") == name and r["state"] == ROLE + "_running"]
            rows = rows or store.claim(ROLE, name)
            if not rows:
                return
            reserved = dict(keys=[r["source_sample_key"] for r in rows], batch=int(rows[0]["group_id"]),
                            phase="examples")
            status(pending_resume=reserved, role="V5 两轮", started_at=now(), retry_count=0,
                   conversation_id=None, pid=None, call_log=None, last_error="")

        n = reserved["batch"]
        directory = PUBLIC / f"batch{n:03}"
        if reserved["phase"] == "examples":
            examples = prepare_examples(directory)

            def confirm(cid, failures):
                proof = verify_turn(cid, examples, EXAMPLES)
                write_text(RUN / f"{directory.name}.examples.receipts.json", json.dumps(proof, ensure_ascii=False))
                reserved.update(phase="label", example_step=proof["step"], example_retries=failures)
                status(pending_resume=reserved, call_log=None, pid=None, retry_count=0, last_error="")

            if not run_phase(agy, directory, examples, "examples", worker, status, confirm):
                return
        if stop.is_set() or drain.is_set():
            status(status="awaiting_continue", pid=None)
            return

        checkpoint = json.loads((RUN / f"{directory.name}.examples.receipts.json").read_text(encoding="utf8"))
        if (not worker.get("conversation_id") or checkpoint["conversation_id"] != worker["conversation_id"]
                or checkpoint["step"] != reserved["example_step"]):
            status(status="awaiting_continue", last_error="示例验收凭证与原会话不一致")
            return
        document = prepare_task(directory, [REPO / p for p in paths[(n - 1) * 10:n * 10]])

        def submit(cid, failures):
            validate(document)
            reads = verify_turn(cid, document, LABEL, after_step=reserved["example_step"], result=result_path(document))
            accept(document, cid, rows, name, reserved["example_retries"] + failures, reads)

        if not run_phase(agy, directory, document, "label", worker, status, submit):
            return
        release()


def pack():
    rows = store.rows()
    if len(rows) != 1000 or any(r["state"] != "completed" for r in rows):
        return
    report = {"completed": len(rows), "categories": dict(Counter(d["category"] for r in rows for d in r["defects"])),
              "empty_defects": sum(not r["defects"] for r in rows),
              "retried_images": sum(bool(r.get("qa_failures")) for r in rows)}
    for file, data in [("reviews.json", rows), ("summary.json", report)]:
        write_text(RUN / file, json.dumps(data, ensure_ascii=False, indent=2))
    final = RUN / COMPLETION_ARCHIVE
    partial = final.with_suffix(".partial")
    with zipfile.ZipFile(partial, "w", zipfile.ZIP_DEFLATED) as archive:
        for file in ["reviews.json", "summary.json", "samples.json"]:
            archive.write(RUN / file, file)
        for path in RUN.glob("*.receipts.json"):
            archive.write(path, "receipts/" + path.name)
        for file in ["规则.md", "标注步骤.md"]:
            archive.write(ROOT / file, file)
    partial.replace(final)
    store.update_meta(phase="completed")


def main(agy):
    with OwnerLock(RUN):
        if (RUN / COMPLETION_ARCHIVE).exists():
            return
        paths = sample()
        seed(paths)
        store.update_meta(owner_pid=os.getpid(), heartbeat_at=now(), phase="running",
                          state_updated_at=now(), preflight={"ready": True}, dispatch_hold={"active": False},
                          session_fault_policy="continue_five_then_pool_v4",
                          dispatch_control={"version": 1, "owner_pid": os.getpid()})
        watcher = threading.Thread(target=command_loop, daemon=True)
        watcher.start()
        try:
            with ThreadPoolExecutor(max_workers=16) as pool:
                lanes = {i: pool.submit(lane, i, paths, agy) for i in range(1, 17)}
                while lanes:
                    wait(lanes.values(), timeout=1)
                    for i, task in list(lanes.items()):
                        if task.done():
                            task.result()
                            del lanes[i]
                    if continue_requested.is_set() and not stop.is_set() and not drain.is_set():
                        continue_requested.clear()
                        for i in range(1, 17):
                            if i not in lanes and store.worker(f"W{i:02}")["status"] == "awaiting_continue":
                                lanes[i] = pool.submit(lane, i, paths, agy)
            pack()
        finally:
            finished.set()
            watcher.join()
            store.update_meta(owner_pid=None, heartbeat_at=now())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agy", required=True)
    main(parser.parse_args().agy)

