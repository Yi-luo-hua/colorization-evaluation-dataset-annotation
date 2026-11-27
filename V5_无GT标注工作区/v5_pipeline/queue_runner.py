"""SQLite queue preparation, worker-lane scheduling, and quota recovery for full V5 runs."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
from queue import Empty, SimpleQueue
import random
import re
import shutil
import sqlite3
import subprocess
import sys
from threading import Event, Thread
import time

from PIL import Image

from .io_utils import (
    WORKSPACE_ROOT,
    load_json,
    publish_image,
    save_json,
    sha256_file,
    stamp,
)
from .stage_runner import (
    ALLOWED,
    BLIND,
    DRAFT_MODEL,
    FINAL,
    FIRST,
    MODEL,
    SECOND,
    OwnerLock,
    batch_auth,
    render,
    run_batch,
    snapshot,
)

DATASETS = {"train": "9_14_10000GT_V1", "val": "10_5_val_V1", "test": "10_5_test_V1"}
MODELS = ("lcad", "unicolor")
EXTENSIONS = {".jpg", ".jpeg", ".png"}
PROMPTS = ("common.md", "stages.json")
BATCH_SIZE, WORKERS, SEED = 5, 8, 20261127
QUOTA_POLL_SECONDS = 120


def inventory(source):
    images = []
    for split, dataset in DATASETS.items():
        for model in MODELS:
            root = source / dataset / "model" / model
            files = [p for p in sorted(root.iterdir()) if p.is_file() and p.suffix.lower() in EXTENSIONS]
            if not files or len({p.stem for p in files}) != len(files):
                raise ValueError(f"{split}/{model} 图像目录为空或存在重复编号")
            images.extend((split, model, path) for path in files)

    def inspect(entry):
        split, model, path = entry
        raw = path.read_bytes()
        with Image.open(path) as image:
            width, height = image.size
            image.verify()
        return {"sample_key": f"{split}/{model}/{path.stem}", "split": split, "model": model,
                "image": path.relative_to(source).as_posix(), "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw), "width": width, "height": height}

    with ThreadPoolExecutor(max_workers=8) as pool:
        return list(pool.map(inspect, images))


def connect(run):
    con = sqlite3.connect(run / "queue.sqlite3", timeout=30)
    con.row_factory = sqlite3.Row
    return con


def seed_queue(run, samples):
    with connect(run) as db:
        db.execute("PRAGMA journal_mode=WAL")
        db.executescript("""
            CREATE TABLE samples (
                sid TEXT PRIMARY KEY, sample_key TEXT NOT NULL UNIQUE, batch_id TEXT NOT NULL,
                split TEXT NOT NULL, model TEXT NOT NULL, image TEXT NOT NULL,
                sha256 TEXT NOT NULL, bytes INTEGER NOT NULL, width INTEGER NOT NULL, height INTEGER NOT NULL
            );
            CREATE TABLE batches (
                batch_id TEXT PRIMARY KEY, seq INTEGER NOT NULL UNIQUE, size INTEGER NOT NULL,
                status TEXT NOT NULL, updated_at TEXT
            );
            CREATE INDEX samples_batch ON samples(batch_id);
        """)
        for offset in range(0, len(samples), BATCH_SIZE):
            seq = offset // BATCH_SIZE + 1
            key = f"b{seq:04d}"
            items = samples[offset:offset + BATCH_SIZE]
            db.execute("INSERT INTO batches VALUES (?,?,?,?,?)", (key, seq, len(items), "queued", None))
            db.executemany("INSERT INTO samples VALUES (?,?,?,?,?,?,?,?,?,?)", [
                (f"S{index:05d}", row["sample_key"], key, row["split"], row["model"], row["image"],
                 row["sha256"], row["bytes"], row["width"], row["height"])
                for index, row in enumerate(items, offset + 1)
            ])


def materialize(args, batch):
    private = args.run / "batches" / batch
    public = args.packets / batch
    images = public / "images"
    images.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    with connect(args.run) as db:
        rows = list(db.execute("SELECT * FROM samples WHERE batch_id=? ORDER BY sid", (batch,)))
    if not rows:
        raise ValueError(f"批次不存在：{batch}")
    cases = {}
    for row in rows:
        source = args.source_root / row["image"]
        if sha256_file(source) != row["sha256"]:
            raise ValueError(f"生成图在建库之后已变化：{row['sample_key']}")
        png = publish_image(source, images)
        anonymous = images / f"{row['sid']}.png"
        if not anonymous.exists():
            png.replace(anonymous)
        elif png.exists():
            if sha256_file(png) != sha256_file(anonymous):
                raise ValueError(f"现有匿名图与冻结的源图不一致：{anonymous}")
            png.unlink()
        cases[row["sid"]] = {"sample_key": row["sample_key"], "png_sha256": sha256_file(anonymous)}
    frozen = private / "samples.json"
    if frozen.exists():
        if load_json(frozen) != cases:
            raise ValueError(f"批次的样本文件已变化：{batch}")
    else:
        save_json(frozen, cases)
    common = (args.run / "prompts/common.md").read_text(encoding="utf-8").strip()
    for stage, role in load_json(args.run / "prompts/stages.json").items():
        document = public / stage / "任务.md"
        if not document.exists():
            render(public, stage, cases, role, common)
    return cases


def summary(run):
    with connect(run) as db:
        return {row["status"]: {"batches": row["batches"], "images": row["images"]}
                for row in db.execute("SELECT status, COUNT(*) AS batches, SUM(size) AS images FROM batches GROUP BY status")}


def prepare(args):
    args.run.mkdir(parents=True, exist_ok=True)
    with OwnerLock(args.run):
        if (args.run / "queue.sqlite3").exists():
            raise ValueError("该目录已有全量队列")
        print("正在盘点并校验六个生成图目录", flush=True)
        samples = inventory(args.source_root)
        by_scope = Counter(f"{row['split']}/{row['model']}" for row in samples)
        random.Random(SEED).shuffle(samples)
        seed_queue(args.run, samples)
        prompts = args.run / "prompts"
        prompts.mkdir(exist_ok=True)
        for name in PROMPTS:
            shutil.copyfile(WORKSPACE_ROOT / "split_pass_prompts" / name, prompts / name)
        cfg = {
            "created_at": stamp(), "state": "prepared_offline", "source_root": str(args.source_root),
            "packet_root": str(args.packets), "model": args.model, "draft_model": args.draft_model,
            "batch_size": BATCH_SIZE, "default_workers": WORKERS, "seed": SEED,
            "sources": dict(by_scope), "images": len(samples),
            "input_bytes": sum(row["bytes"] for row in samples), "stage_order": list(ALLOWED),
            "prompt_hashes": {name: sha256_file(prompts / name) for name in PROMPTS},
            "cli_calls": 0, "queued": summary(args.run),
        }
        save_json(args.run / "preparation.json", cfg)
        with connect(args.run) as db:
            first = [r["batch_id"] for r in db.execute("SELECT batch_id FROM batches ORDER BY seq LIMIT ?", (args.starter,))]
        with ThreadPoolExecutor(max_workers=8) as pool:
            starter = list(pool.map(lambda name: materialize(args, name), first))
        cfg["prepared_starter_batches"] = len(starter)
        cfg["prepared_starter_images"] = sum(map(len, starter))
        save_json(args.run / "preparation.json", cfg)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))


def status_for(run, batch, value):
    with connect(run) as db:
        db.execute("UPDATE batches SET status=?, updated_at=? WHERE batch_id=?", (value, stamp(), batch))


def run_lanes(args, planned, quota_stop):
    planned_set = set(planned)
    with connect(args.run) as db:
        retained = {slot: batch for slot, batch in db.execute(
            "SELECT slot,batch_id FROM worker_lanes WHERE slot<=?", (args.workers,))
                    if batch in planned_set}
    reserved = set(retained.values())
    pending = SimpleQueue()
    for batch in planned:
        if batch not in reserved:
            pending.put(batch)
    worker = argparse.Namespace(run=args.run / "batches", packets=args.packets, agy=args.agy,
                                model=args.model,
                                stage_models={FINAL: args.model},
                                serialize_session_start=True,
                                isolate_cli_store=True)

    def lane(slot, batch):
        while not quota_stop.is_set() and not (args.run / "drain.request").is_file():
            if batch is None:
                try:
                    batch = pending.get_nowait()
                except Empty:
                    return
            now = stamp()
            with connect(args.run) as db:
                db.execute("DELETE FROM worker_lanes WHERE batch_id=? AND slot!=?", (batch, slot))
                db.execute("""INSERT INTO worker_lanes(slot,batch_id,assigned_at) VALUES (?,?,?)
                              ON CONFLICT(slot) DO UPDATE SET batch_id=excluded.batch_id,
                              assigned_at=excluded.assigned_at""", (slot, batch, now))
                db.execute("UPDATE batches SET status='running', updated_at=? WHERE batch_id=?", (now, batch))
            try:
                cases = materialize(args, batch)
                run_batch(worker, batch, cases, quota_stop)
                latest = args.run / "batches" / batch / "status.json"
                complete = latest.is_file() and load_json(latest)["state"] == "completed"
                status_for(args.run, batch, "completed" if complete else "paused")
            except Exception:
                status_for(args.run, batch, "paused")
                raise
            batch = None

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(lane, slot, retained.get(slot)) for slot in range(1, args.workers + 1)]
        for future in as_completed(futures):
            future.result()


def collect(run):
    out = run / "final_reviews.jsonl"
    temporary = out.with_suffix(".tmp")
    with connect(run) as db:
        complete = [r["batch_id"] for r in db.execute("SELECT batch_id FROM batches WHERE status='completed' ORDER BY seq")]
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            for batch in complete:
                private = run / "batches" / batch
                cases = load_json(private / "samples.json")
                final_path = snapshot(private, FINAL)
                proof = load_json(private / f"{FINAL}.proof.json")
                if sha256_file(final_path) != proof["result_sha256"]:
                    raise ValueError(f"终标哈希不一致：{batch}")
                final = load_json(final_path)
                if final.keys() != cases.keys():
                    raise ValueError(f"终标与任务身份不一致：{batch}")
                for sid, defects in final.items():
                    stream.write(json.dumps({"sample_key": cases[sid]["sample_key"], "defects": defects},
                                            ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary.replace(out)
    finally:
        temporary.unlink(missing_ok=True)


def quota_read(args):
    legacy = args.source_root / "annotation_delivery/train_val_v1_20261015"
    helper = WORKSPACE_ROOT.parent / "annotation_delivery/train_val_v1_20261015/scripts/native_quota_monitor.py"
    command = [sys.executable, "-B", "-X", "utf8", str(helper), "--agy", str(args.agy),
               "--cwd", str(args.source_root), "--guard-dir", str(args.run / "quota_checks"),
               "--dependencies", str(legacy / "runtime/quota_dependencies"),
               "--browser-guard", str(batch_auth.GUARD)]
    try:
        response = subprocess.run(command, capture_output=True, encoding="utf8", check=True)
        result = json.loads(response.stdout)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        result = {"error": str(error)}
    result["observed_at"] = stamp()
    dest = "quota_read_error.json" if "error" in result else "quota_snapshot.json"
    save_json(args.run / dest, result)
    return result


def watch_quota(args, stop, done, signal):
    next_check = time.monotonic() + QUOTA_POLL_SECONDS
    while not done.wait(1):
        if (args.run / "stop.request").is_file():
            signal["manual"] = True
            stop.set()
            return
        if time.monotonic() >= next_check:
            values = quota_read(args)
            if done.is_set():
                return
            if 0 in (values.get("five_hour"), values.get("weekly")):
                signal["quota"] = values
                stop.set()
                return
            next_check = time.monotonic() + QUOTA_POLL_SECONDS


def seconds_until_reset(value):
    units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
    return sum(int(amount) * units[unit] for amount, unit in re.findall(r"(\d+)\s*([dhms])", value))


def wait_for_quota(args, values, not_before=None):
    path = args.run / "quota_wait.json"
    if values.get("weekly") == 0:
        save_json(path, {"state": "weekly_manual", "quota": values, "at": stamp()})
        return False
    last_snapshot = args.run / "quota_snapshot.json"
    previous = load_json(last_snapshot) if last_snapshot.is_file() else {}
    if not_before is None:
        reported = values if "five_reset" in values else previous
        observed = datetime.fromisoformat(reported.get("observed_at", stamp()))
        not_before = observed + timedelta(seconds=seconds_until_reset(reported.get("five_reset", "")))

    save_json(path, {"state": "five_hour", "quota": values, "at": stamp(),
                     "resume_not_before": not_before.isoformat()})
    first = True
    stop_request = args.run / "stop.request"
    while not stop_request.is_file():
        remaining = (not_before - datetime.now().astimezone()).total_seconds()
        delay = min(600, max(1, int(remaining) + 1)) if remaining > 0 else (0 if first else 600)
        first = False
        for _ in range(delay):
            if stop_request.is_file():
                return False
            time.sleep(1)
        values = quota_read(args)
        if stop_request.is_file():
            return False
        if values.get("weekly") == 0:
            save_json(path, {"state": "weekly_manual", "quota": values, "at": stamp()})
            return False
        fresh = datetime.fromisoformat(values["observed_at"]) >= not_before
        if fresh and values.get("five_hour", 0) > 0 and values.get("weekly", 0) > 0:
            save_json(path, {"state": "resumed", "quota": values, "at": stamp()})
            return True
    return False


def execute(args):
    cfg = load_json(args.run / "preparation.json")
    if (cfg["source_root"], cfg["packet_root"], cfg["model"]) != (str(args.source_root), str(args.packets), args.model):
        raise ValueError("续跑须使用准备时的源目录、匿名包目录和模型")
    if any(sha256_file(args.run / "prompts" / f) != expected for f, expected in cfg["prompt_hashes"].items()):
        raise ValueError("冻结提示词已变化")
    if not args.agy or not args.agy.is_file():
        raise ValueError("运行时必须提供本机 agy 可执行文件")
    if not batch_auth.GUARD.is_file():
        batch_auth.GUARD = args.source_root / "annotation_delivery/train_val_v1_20261015/scripts/no_browser/rundll32.exe"

    with OwnerLock(args.run):
        (args.run / "executor.pid").write_text(f"{os.getpid()}\n", encoding="utf-8")
        with connect(args.run) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS worker_lanes (
                slot INTEGER PRIMARY KEY, batch_id TEXT NOT NULL UNIQUE, assigned_at TEXT NOT NULL
            )""")
        quota_path = args.run / "quota_wait.json"
        wait = load_json(quota_path) if quota_path.is_file() else {}
        if wait.get("state") == "five_hour":
            deadline = datetime.fromisoformat(wait["resume_not_before"]) if "resume_not_before" in wait else None
            if not wait_for_quota(args, wait["quota"], deadline):
                return
        elif wait.get("state") == "weekly_manual":
            values = quota_read(args)
            if values.get("weekly", 0) <= 0 or values.get("five_hour", 0) <= 0:
                return
            save_json(quota_path, {"state": "resumed", "quota": values, "at": stamp()})
        with connect(args.run) as db:
            selection = list(db.execute("SELECT batch_id FROM batches WHERE status!='completed' ORDER BY seq LIMIT ?",
                                        (args.limit if args.limit is not None else -1,)))
        planned = [row["batch_id"] for row in selection]
        pause_file = args.run / "batches/quota_pause.json"
        while planned and not (args.run / "stop.request").is_file():
            quota_stop, finished = Event(), Event()
            signal = {}
            watcher = Thread(target=watch_quota, args=(args, quota_stop, finished, signal), daemon=True)
            watcher.start()

            try:
                run_lanes(args, planned, quota_stop)
            finally:
                finished.set()

            collect(args.run)
            print(json.dumps(summary(args.run), ensure_ascii=False), flush=True)
            if signal.get("manual") or not quota_stop.is_set():
                break
            if pause_file.is_file():
                archive = pause_file.with_name(f"quota_pause.{time.time_ns()}.json")
                pause_file.replace(archive)
            values = signal.get("quota") or quota_read(args)
            if not wait_for_quota(args, values):
                break
            with connect(args.run) as db:
                complete = {row["batch_id"] for row in db.execute("SELECT batch_id FROM batches WHERE status='completed'")}
            planned = [batch for batch in planned if batch not in complete]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "status", "run"))
    for name in ("source-root", "run", "packets"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--draft-model", default=DRAFT_MODEL)
    parser.add_argument("--agy", type=Path)
    parser.add_argument("--workers", type=int, choices=range(1, 17), default=WORKERS, metavar="1..16")
    parser.add_argument("--starter", type=int, choices=range(17), default=WORKERS, metavar="0..16")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    for name in ("source_root", "run", "packets", "agy"):
        if value := getattr(args, name):
            setattr(args, name, value.resolve())
    if args.run.is_relative_to(args.packets) or args.packets.is_relative_to(args.run):
        parser.error("主控目录与模型执行目录必须分开放置")
    if args.limit is not None and args.limit <= 0:
        parser.error("--limit 应为正的任务包数量")
    if args.action == "prepare":
        prepare(args)
    elif args.action == "status":
        print(json.dumps(summary(args.run), ensure_ascii=False, indent=2))
    else:
        execute(args)
