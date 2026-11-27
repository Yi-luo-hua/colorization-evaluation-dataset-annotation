"""Compare 10 and 20 images per V5 session with the same images and concurrency."""

import argparse
from collections import Counter
from datetime import datetime
import json
from pathlib import Path
import subprocess
import sys
import time

from split_pass_pilot import MODEL, ROOT, OwnerLock, load, native_log, save

SIZES = (10, 20)
TOKEN_FIELDS = ("input_tokens", "cache_read_tokens", "output_tokens", "thinking_tokens")


def now():
    return datetime.now().astimezone().isoformat()


def observe_quota(args, directory):
    script = ROOT.parent / "annotation_delivery/train_val_v1_20261015/scripts/native_quota_monitor.py"
    runtime = args.source_root / "annotation_delivery/train_val_v1_20261015"
    cmd = [sys.executable, "-B", "-X", "utf8", str(script), "--agy", str(args.agy),
           "--cwd", str(args.source_root), "--guard-dir", str(directory),
           "--dependencies", str(runtime / "runtime/quota_dependencies"),
           "--browser-guard", str(runtime / "scripts/no_browser/rundll32.exe")]
    try:
        result = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=True)
        return {"observed_at": now(), **json.loads(result.stdout)}
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip().splitlines()[-1:] if error.stderr else []
        return {"observed_at": now(), "error": detail[0] if detail else str(error)}
    except (OSError, ValueError) as error:
        return {"observed_at": now(), "error": str(error)}



def measure(run):
    attempts = sorted(run.glob("batch*/*.jsonl"))
    sessions = {cid for log in attempts if (cid := native_log(log)[0])}
    counts, totals, fields = Counter(), Counter(), Counter()
    model_ids = set()
    telemetry_missing = 0
    ctx_max = 0
    for cid in sessions:
        trace = Path.home() / ".gemini/antigravity-cli/brain" / cid / ".system_generated/logs/transcript_full.jsonl"
        if not trace.is_file():
            telemetry_missing += 1
            continue
        with trace.open(encoding="utf-8-sig", errors="replace") as log:
            for line in log:
                try:
                    step = json.loads(line)
                except ValueError:
                    continue
                if step.get("type") != "PLANNER_RESPONSE" or type(step.get("input_tokens")) is not int:
                    continue
                counts["native_requests"] += 1
                if step.get("model"):
                    model_ids.add(step["model"])
                for field in TOKEN_FIELDS:
                    if type(step.get(field)) is int:
                        totals[field] += step[field]
                        fields[field] += 1
                ctx_max = max(ctx_max, step["input_tokens"] + (step.get("cache_read_tokens") or 0))
    stages = Counter(log.name.split(".", 1)[0] for log in attempts)
    comparison_path = run / "comparison.json"
    result = load(comparison_path) if comparison_path.is_file() else {}
    reads = sum(len(load(p).get("seen", [])) for p in run.glob("batch*/*.proof.json")
                if not p.name.startswith("03b_"))
    return {
        "completed": result.get("completed", 0), "metrics": result.get("metrics", {}),
        "cli_calls": len(attempts), "cli_calls_by_message": dict(stages), "native_sessions": len(sessions),
        "model_ids": sorted(model_ids), "verified_reads": reads, "native_requests": counts["native_requests"],
        "token_totals": dict(totals), "token_field_request_counts": dict(fields), "sessions_missing_trace": telemetry_missing,
        "max_request_input_with_cache": ctx_max,
    }


def runner_command(args, size, run, packets):
    return [sys.executable, "-B", "-X", "utf8", str(ROOT / "split_pass_pilot.py"),
            "--source-root", str(args.source_root), "--run", str(run), "--packets", str(packets),
            "--agy", str(args.agy), "--batch-size", str(size), "--workers", str(args.workers), "--model", args.model]


def execute(args, size, run, packets, before):
    save(args.run / "status.json", {"state": "running", "images_per_session": size, "started_at": now()})
    begin = time.perf_counter()
    with (run / "executor.stdout.log").open("ab") as output, (run / "executor.stderr.log").open("ab") as errors:
        result = subprocess.run(runner_command(args, size, run, packets), stdout=output, stderr=errors, check=False)
    seconds = round(time.perf_counter() - begin, 2)
    measured = measure(run)
    save(args.run / "status.json", {"state": "querying_quota", "images_per_session": size, "completed": measured["completed"]})
    after = observe_quota(args, args.run / "quota_checks")
    drops = {}
    for window in ("five_hour", "weekly"):
        if window in before and window in after and before[window] >= after[window]:
            drops[window] = round(before[window] - after[window], 3)
    return {"images_per_session": size, "elapsed_seconds": seconds, "returncode": result.returncode,
            "quota_before": before, "quota_after": after, "quota_drop_percentage_points": drops, **measured}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source-root", "run", "packets", "agy"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--model", default=MODEL)
    parser.add_argument("--workers", default=2, type=int, choices=(1, 2))
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    for name in ("source_root", "run", "packets", "agy"):
        setattr(args, name, getattr(args, name).resolve())
    args.run.mkdir(parents=True, exist_ok=True)
    args.packets.mkdir(parents=True, exist_ok=True)

    with OwnerLock(args.run):
        destinations = {}
        preshuffle = []
        for size in SIZES:
            run, packets = args.run / f"batch_size_{size}", args.packets / f"size{size}"
            subprocess.run(runner_command(args, size, run, packets) + ["--prepare-only"], check=True)
            manifest = load(run / "manifest.json")
            preshuffle.append({sid: (row["sample_key"], row["png_sha256"])
                               for rows in manifest["batches"].values() for sid, row in rows.items()})
            destinations[size] = run, packets
        if preshuffle[0] != preshuffle[1] or len(preshuffle[0]) != 40:
            raise ValueError("两组应使用相同的 40 张图和编号")
        if args.prepare_only:
            return

        report_path = args.run / "benchmark.json"
        report = load(report_path) if report_path.exists() else {
            "model": args.model, "workers_per_group": args.workers, "images_per_group": 40, "groups": {},
        }
        for size, (run, packets) in destinations.items():
            if report["groups"].get(str(size), {}).get("completed") == 40:
                continue
            save(args.run / "status.json", {"state": "querying_quota", "images_per_session": size})
            before = observe_quota(args, args.run / "quota_checks")
            if before.get("five_hour") == 0 or before.get("weekly") == 0:
                save(args.run / "status.json", {"state": "quota_paused", "images_per_session": size, "quota": before})
                return
            result = execute(args, size, run, packets, before)
            report["groups"][str(size)] = result
            save(report_path, report)
            print(f"batch size {size}: {result['completed']}/40 in {result['elapsed_seconds']} seconds", flush=True)
            if (run / "quota_pause.json").exists():
                save(args.run / "status.json", {"state": "quota_paused", "images_per_session": size,
                                                "completed": result["completed"], "quota": result["quota_after"]})
                return
        state = "completed" if all(report["groups"].get(str(size), {}).get("completed") == 40 for size in SIZES) else "partial"
        save(args.run / "status.json", {"state": state, "finished_at": now()})


if __name__ == "__main__":
    main()

