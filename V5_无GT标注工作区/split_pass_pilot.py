"""Run the three-round V5 pilot on the frozen 40-image human comparison set."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import random
import shutil
from threading import Event

from v5_pipeline.io_utils import publish_image
from v5_pipeline.stage_runner import (
    ALLOWED,
    CATEGORIES,
    DRAFT_MODEL,
    FIELDS,
    FINAL,
    FIRST,
    MODEL,
    QUOTA_INTERRUPTED,
    READS,
    ROOT,
    SECOND,
    SESSION_START_LOCK,
    OwnerLock,
    batch_auth,
    digest,
    empty_session_start,
    load,
    native_log,
    output_at,
    public_inputs,
    render,
    run_batch,
    run_stage,
    save,
    snapshot,
    stage_paths,
    validate,
    wait_for_session,
)

HUMAN = Path("V5_无GT标注工作区/local/human_annotations_merged_20261124/人工标注合并.json")
SEED = 2026112440
BATCH_SIZE = 5


def prepare(args):
    manifest_path = args.run / "manifest.json"
    if manifest_path.exists():
        previous = load(manifest_path)
        if (previous["packets"] != str(args.packets) or previous["model"] != args.model
                or previous.get("batch_size", BATCH_SIZE) != args.batch_size):
            raise ValueError("续跑须使用原任务目录、模型和每包图数")
        return previous

    human = args.source_root / HUMAN
    rows = load(human)["images"]
    if len(rows) != 40 or len({row["sample_key"] for row in rows}) != 40:
        raise ValueError("人工对照集应为 40 个唯一身份")
    counts = Counter(row["current_annotation"]["status"] for row in rows)
    if counts["adjudicated_whole_image"] != 17 or sum(counts.values()) != 40:
        raise ValueError("人工对照集应含 17 张已裁决图和 23 张待核对稿")
    random.Random(SEED).shuffle(rows)
    args.packets.mkdir(parents=True, exist_ok=True)
    cache = args.packets / "_cache"
    cache.mkdir(exist_ok=True)
    templates = load(ROOT / "split_pass_prompts/stages.json")
    common = (ROOT / "split_pass_prompts/common.md").read_text(encoding="utf-8").strip()
    batches = {}
    for offset in range(0, len(rows), args.batch_size):
        name = f"batch{offset // args.batch_size + 1:02d}"
        folder = args.packets / name
        images = folder / "images"
        images.mkdir(parents=True, exist_ok=True)
        references = {}
        for index, row in enumerate(rows[offset:offset + args.batch_size], offset + 1):
            sid = f"S{index:03d}"
            anonymous = images / f"{sid}.png"
            pixels = publish_image(args.source_root / row["image"], cache)
            if not anonymous.exists():
                shutil.copyfile(pixels, anonymous)
            if digest(anonymous) != digest(pixels):
                raise ValueError(f"匿名图已有不同内容：{anonymous}")
            reference = row["current_annotation"]
            references[sid] = {
                "sample_key": row["sample_key"], "reference_status": reference["status"],
                "reference": reference["labels"], "png_sha256": digest(anonymous),
            }
        for stage, template in templates.items():
            render(folder, stage, references, template, common)
        (args.run / name).mkdir(exist_ok=True)
        batches[name] = references
    plan = {
        "packets": str(args.packets), "model": args.model, "seed": SEED,
        "batch_size": args.batch_size, "human_source_sha256": digest(human),
        "batches": batches, "source_counts": counts,
    }
    save(manifest_path, plan)
    return plan


def comparison(args, plan):
    metrics = Counter()
    result = {}
    for name, cases in plan["batches"].items():
        private = args.run / name
        if not all((private / f"{stage}.proof.json").exists()
                   and "step" in load(private / f"{stage}.proof.json") for stage in ALLOWED):
            continue
        first, second, final = (load(snapshot(private, stage)) for stage in (FIRST, SECOND, FINAL))
        for sid, case in cases.items():
            reference = {label.split("-", 1)[0] for label in case["reference"]}
            initial = {d["id"] for d in first[sid] + second[sid]}
            revised = {d["id"] for d in final[sid]}
            group = "adjudicated" if case["reference_status"] == "adjudicated_whole_image" else "draft"
            for cohort in (group, "combined"):
                metrics[cohort, "images"] += 1
                metrics[cohort, "reference_categories"] += len(reference)
                for stage, labels in (("initial", initial), ("final", revised)):
                    metrics[cohort, f"{stage}_hits"] += len(labels & reference)
                    metrics[cohort, f"{stage}_predicted"] += len(labels)
                for kind, count in {
                    "correct_additions": len((revised - initial) & reference),
                    "incorrect_additions": len((revised - initial) - reference),
                    "correct_deletions": len((initial - revised) - reference),
                    "incorrect_deletions": len((initial - revised) & reference),
                }.items():
                    metrics[cohort, kind] += count
            result[case["sample_key"]] = {
                "reference_status": case["reference_status"], "reference": case["reference"],
                "initial": first[sid] + second[sid], "final": final[sid],
            }
    grouped = {
        group: {label: count for (cohort, label), count in metrics.items() if cohort == group}
        for group in ("adjudicated", "draft", "combined")
    }
    save(args.run / "comparison.json", {"model": args.model, "completed": len(result), "expected": 40,
                                        "metrics": grouped, "images": result})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-root", "run", "packets"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--agy", type=Path, default=Path(shutil.which("agy") or "agy"))
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--draft-model", default=DRAFT_MODEL)
    parser.add_argument("--workers", type=int, default=8, choices=range(1, 17), metavar="1..16")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, choices=(5, 10, 15, 20))
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    for name in ("source_root", "run", "packets", "agy"):
        setattr(args, name, getattr(args, name).resolve())
    args.stage_models = {FIRST: args.draft_model, SECOND: args.draft_model, FINAL: args.model}
    if args.run.is_relative_to(args.packets) or args.packets.is_relative_to(args.run):
        parser.error("主控结果和匿名执行目录必须分别存放")
    args.run.mkdir(parents=True, exist_ok=True)
    with OwnerLock(args.run):
        plan = prepare(args)
        print(f"prepared {sum(map(len, plan['batches'].values()))} anonymous images in {len(plan['batches'])} batches", flush=True)
        if args.prepare_only:
            return
        if not batch_auth.GUARD.is_file():
            batch_auth.GUARD = args.source_root / "annotation_delivery/train_val_v1_20261015/scripts/no_browser/rundll32.exe"
        quota_stop = Event()
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(run_batch, args, name, cases, quota_stop) for name, cases in plan["batches"].items()]
            for future in as_completed(futures):
                future.result()
        comparison(args, plan)


if __name__ == "__main__":
    main()
