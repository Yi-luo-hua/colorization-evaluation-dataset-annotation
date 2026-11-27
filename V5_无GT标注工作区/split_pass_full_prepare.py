"""Prepare and resume V5 split-pass annotation from generated images in all splits."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from threading import Event
import hashlib
import json
import random
import shutil
import sqlite3

from PIL import Image
from prepare import publish_image
from split_pass_pilot import ALLOWED, FINAL, MODEL, ROOT, OwnerLock, batch_auth, digest, load, render, run_batch, save, snapshot

DATASETS = {"train": "9_14_10000GT_V1", "val": "10_5_val_V1", "test": "10_5_test_V1"}
MODELS = ("lcad", "unicolor")
EXTENSIONS = {".jpg", ".jpeg", ".png"}
PROMPTS = ("common.md", "stages.json")
BATCH_SIZE, WORKERS, SEED = 10, 16, 20261127


def stamp():
    return datetime.now().astimezone().isoformat()


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
        if digest(source) != row["sha256"]:
            raise ValueError(f"生成图在建库之后已变化：{row['sample_key']}")
        png = publish_image(source, images)
        anonymous = images / f"{row['sid']}.png"
        if not anonymous.exists():
            png.replace(anonymous)
        elif png.exists():
            if digest(png) != digest(anonymous):
                raise ValueError(f"现有匿名图与冻结的源图不一致：{anonymous}")
            png.unlink()
        cases[row["sid"]] = {"sample_key": row["sample_key"], "png_sha256": digest(anonymous)}
    frozen = private / "samples.json"
    if frozen.exists():
        if load(frozen) != cases:
            raise ValueError(f"批次的样本文件已变化：{batch}")
    else:
        save(frozen, cases)
    common = (args.run / "prompts/common.md").read_text(encoding="utf-8").strip()
    for stage, role in load(args.run / "prompts/stages.json").items():
        document = public / stage / "任务.md"
        if not document.exists():
            render(public, stage, cases, role, common)
    return cases


def summary(run):
    with connect(run) as db:
        groups = {row["status"]: {"batches": row["batches"], "images": row["images"]}
                  for row in db.execute("SELECT status, COUNT(*) AS batches, SUM(size) AS images FROM batches GROUP BY status")}
    return groups


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
            shutil.copyfile(ROOT / "split_pass_prompts" / name, prompts / name)
        cfg = {
            "created_at": stamp(), "state": "prepared_offline", "source_root": str(args.source_root),
            "packet_root": str(args.packets), "model": args.model, "batch_size": BATCH_SIZE,
            "default_workers": WORKERS, "seed": SEED, "sources": dict(by_scope), "images": len(samples),
            "input_bytes": sum(row["bytes"] for row in samples), "stage_order": list(ALLOWED),
            "prompt_hashes": {name: digest(prompts / name) for name in PROMPTS},
            "cli_calls": 0, "queued": summary(args.run),
        }
        save(args.run / "preparation.json", cfg)
        with connect(args.run) as db:
            first = [r["batch_id"] for r in db.execute("SELECT batch_id FROM batches ORDER BY seq LIMIT ?", (args.starter,))]
        with ThreadPoolExecutor(max_workers=8) as pool:
            starter = list(pool.map(lambda name: materialize(args, name), first))
        cfg["prepared_starter_batches"] = len(starter)
        cfg["prepared_starter_images"] = sum(map(len, starter))
        save(args.run / "preparation.json", cfg)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))


def status_for(run, batch, value):
    with connect(run) as db:
        db.execute("UPDATE batches SET status=?, updated_at=? WHERE batch_id=?", (value, stamp(), batch))


def collect(run):
    out = run / "final_reviews.jsonl"
    temporary = out.with_suffix(".tmp")
    with connect(run) as db:
        complete = [r["batch_id"] for r in db.execute("SELECT batch_id FROM batches WHERE status='completed' ORDER BY seq")]
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as stream:
            for batch in complete:
                private = run / "batches" / batch
                cases = load(private / "samples.json")
                final_path = snapshot(private, FINAL)
                proof = load(private / f"{FINAL}.proof.json")
                if digest(final_path) != proof["result_sha256"]:
                    raise ValueError(f"终标哈希不一致：{batch}")
                final = load(final_path)
                if final.keys() != cases.keys():
                    raise ValueError(f"终标与任务身份不一致：{batch}")
                for sid, defects in final.items():
                    stream.write(json.dumps({"sample_key": cases[sid]["sample_key"], "defects": defects},
                                            ensure_ascii=False, separators=(",", ":")) + "\n")
        temporary.replace(out)
    finally:
        temporary.unlink(missing_ok=True)


def execute(args):
    cfg = load(args.run / "preparation.json")
    if (cfg["source_root"], cfg["packet_root"], cfg["model"]) != (str(args.source_root), str(args.packets), args.model):
        raise ValueError("续跑须使用准备时的源目录、匿名包目录和模型")
    if any(digest(args.run / "prompts" / f) != expected for f, expected in cfg["prompt_hashes"].items()):
        raise ValueError("冻结提示词已变化")
    if not args.agy or not args.agy.is_file():
        raise ValueError("运行时必须提供本机 agy 可执行文件")
    if not batch_auth.GUARD.is_file():
        batch_auth.GUARD = args.source_root / "annotation_delivery/train_val_v1_20261015/scripts/no_browser/rundll32.exe"

    with OwnerLock(args.run):
        with connect(args.run) as db:
            selection = list(db.execute("SELECT batch_id FROM batches WHERE status!='completed' ORDER BY seq LIMIT ?",
                                        (args.limit if args.limit is not None else -1,)))
        quota_stop = Event()

        def lane(batch):
            if quota_stop.is_set():
                return
            cases = materialize(args, batch)
            status_for(args.run, batch, "running")
            worker = argparse.Namespace(run=args.run / "batches", packets=args.packets, agy=args.agy, model=args.model)
            try:
                run_batch(worker, batch, cases, quota_stop)
                finished = args.run / "batches" / batch / "status.json"
                completed = finished.is_file() and load(finished)["state"] == "completed"
                status_for(args.run, batch, "completed" if completed else "paused")
            except Exception:
                status_for(args.run, batch, "paused")
                raise

        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(lane, row["batch_id"]) for row in selection]
            for future in as_completed(futures):
                future.result()
        collect(args.run)
        print(json.dumps(summary(args.run), ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "status", "run"))
    for name in ("source-root", "run", "packets"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--model", default=MODEL)
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


if __name__ == "__main__":
    main()

