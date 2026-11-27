"""Run the three-round V5 pilot on the frozen 40-image human comparison set."""

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import nullcontext
from datetime import datetime, timedelta
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
from threading import Event, Lock
import time

from prepare import publish_image, write_text
from turns import FORMAT_EXAMPLES, FORMAT_LINK, LABEL, verify_turn

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "annotation_delivery/train_val_v1_20261015/scripts"))
import batch_auth
from pipeline_store import OwnerLock
from quota_control import explicit_exhaustion

MODEL = "gemini-4-hydrogen-high"
DRAFT_MODEL = "gemini-4-hydrogen-medium"
HUMAN = Path("V5_无GT标注工作区/local/human_annotations_merged_20261124/人工标注合并.json")
FIRST, SECOND, FINAL = "01_initial", "02_color_and_distribution", "03b_finalize_review"
CATEGORIES = set("ABCD") | {"E1", "E2", "F"}
ALLOWED = {FIRST: set("ABD"), SECOND: {"C", "E1", "E2", "F"}, FINAL: CATEGORIES}
READS = {FIRST: (), SECOND: (FIRST,), FINAL: (FIRST, SECOND)}
FIELDS = {"id", "severity", "object", "description"}
SEED = 2026112440
BATCH_SIZE = 5
SESSION_START_LOCK = Lock()
QUOTA_INTERRUPTED = "因额度暂停中断，待恢复继续"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def output_at(folder, stage):
    return folder / stage / "结果.json"


def stage_paths(folder, stage):
    stage_dir = folder / stage
    return stage_dir / "任务.md", stage_dir / FORMAT_EXAMPLES, output_at(folder, stage)


def public_inputs(folder, stage):
    return [folder / stage / f"前轮_{previous}.json" for previous in READS[stage]]


def render(folder, stage, labels, template, common):
    task, example, result = stage_paths(folder, stage)
    task.parent.mkdir(exist_ok=True)
    save(example, template["example"])
    if not result.exists():
        save(result, dict.fromkeys(labels))
    dependencies = [
        f"- {previous} 的普通标注结果：{path}"
        for previous, path in zip(READS[stage], public_inputs(folder, stage))
    ]
    listing = []
    for sid in labels:
        relative = f"../images/{sid}.png"
        listing.append(f"- ![{sid}]({relative})  文件位置：{(task.parent / relative).resolve()}")
    write_text(task, "\n".join([
        f"# {template['title']}", "",
        f"- 结果 JSON 格式示例：{FORMAT_LINK}，完整路径：{example}",
        f"- 结果骨架与唯一写入位置：{result}",
        *dependencies, "", "## 待标图文件", "", *listing, "",
        "## 本轮要求", "", template["instruction"], "",
        "只读取本任务列出的文件，图像用 read_file 打开。完成后用 write_file 一次写入完整结果 JSON。",
        "第一轮和第三轮各打开本包每张图一次；第二轮承接第一轮同一会话已打开的图。", "",
        common, "", "## 本轮结果 JSON 格式示例", "",
        chr(96) * 3 + "json", json.dumps(template["example"], ensure_ascii=False, indent=2), chr(96) * 3, "",
    ]))


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


def validate(rows, sample_ids, stage):
    if not isinstance(rows, dict) or rows.keys() != sample_ids.keys():
        raise ValueError("结果编号与本包任务不符")
    for sid, defects in rows.items():
        if not isinstance(defects, list):
            raise ValueError(f"{sid} 仍为待处理或缺陷列表无效")
        for defect in defects:
            if not isinstance(defect, dict) or defect.keys() != FIELDS:
                raise ValueError(f"{sid} 缺陷须包含且只包含四个指定字段")
            if any(not isinstance(value, str) or not value.strip() for value in defect.values()):
                raise ValueError(f"{sid} 有空的或不合法的缺陷字段")
            if defect["id"] not in ALLOWED[stage] or defect["severity"] not in {"L1", "L2", "L3"}:
                raise ValueError(f"{sid} 类别不属本轮或严重程度无效")


def snapshot(private, stage):
    return private / f"{stage}.accepted.json"


def native_log(out):
    cid = None
    errors = []
    for line in out.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        cid = cid or event.get("conversation_id")
        if event.get("is_error") is True or event.get("type") == "error":
            errors.append(line)
        if event.get("event") == "result":
            result = event.get("result") or {}
            status = result.get("status")
            if status and status != "SUCCESS":
                errors.extend((str(status), str(result.get("error") or "")))
    return cid, errors


def empty_session_start(expected_cid, actual_cid, fault, result):
    if expected_cid or actual_cid or "backend returned an empty conversation id" not in fault.lower():
        return False
    try:
        rows = load(result)
    except (OSError, ValueError):
        return False
    return isinstance(rows, dict) and bool(rows) and all(value is None for value in rows.values())


def wait_for_session(child, stdout, stop):
    with stdout.open("rb") as stream:
        while True:
            offset = stream.tell()
            line = stream.readline()
            if line.endswith(b"\n"):
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if event.get("event") == "init" and event.get("conversation_id"):
                    return event["conversation_id"]
                continue
            if child.poll() is not None or stop.wait(0.2):
                return None
            stream.seek(offset)


def run_stage(args, private, folder, stage, cases, env, quota_stop):
    proof_file = private / f"{stage}.proof.json"
    if proof_file.exists():
        proof = load(proof_file)
        if "step" in proof:
            if not snapshot(private, stage).exists():
                save(snapshot(private, stage), load(output_at(folder, stage)))
            if digest(snapshot(private, stage)) != proof["result_sha256"]:
                raise ValueError(f"{stage} 已验收结果发生变化")
            return proof
    else:
        proof = {}

    document, _, result = stage_paths(folder, stage)
    upstream = public_inputs(folder, stage)
    for previous, public_file in zip(READS[stage], upstream):
        save(public_file, load(snapshot(private, previous)))
    previous_proof = load(private / f"{FIRST}.proof.json") if stage == SECOND else {}
    cid = proof.get("conversation_id") or previous_proof.get("conversation_id")
    feedback = proof.get("problem", "")
    stage_model = getattr(args, "stage_models", {}).get(stage, args.model)
    serialize_start = getattr(args, "serialize_session_start", False)
    for attempt in range(6):
        if quota_stop.is_set():
            return None
        tag = f"{stage}.{time.time_ns()}"
        stdout, stderr = private / f"{tag}.jsonl", private / f"{tag}.err"
        native = private / f"{tag}.native.log"
        command = [str(args.agy), "--model", stage_model, "--mode", "accept-edits",
                   "--output-format", "stream-json", "--print-timeout", "0"]
        if serialize_start:
            command += ["--log-file", str(native)]
        if cid:
            command += ["--conversation", cid]
        read_hint = "沿用第一轮已打开的图" if stage == SECOND else "逐图用 read_file 查看"
        prompt = (
            f"{LABEL} 完整读取 {document}，其中有完整七类定义、适用关系、文件路径和 JSON 示例。"
            f"只访问任务列出的文件，{read_hint}，完成后用 write_file 写入结果 JSON。"
        )
        if feedback and cid:
            if feedback == QUOTA_INTERRUPTED:
                prompt += "\n继续原任务，完成后用 write_file 写入结果 JSON。"
            else:
                prompt += f"\n继续原任务，核对问题并补齐文件。上次未验收原因：{feedback}"
        gated = serialize_start and not cid
        status_path = private / "status.json"
        attempt_status = {"stage": stage, "attempt": attempt + 1, "log": stdout.name, "model": stage_model}
        if gated:
            save(status_path, dict(attempt_status, state="waiting_to_start"))
        terminated_by_quota = False
        with stdout.open("wb") as out, stderr.open("wb") as err:
            with SESSION_START_LOCK if gated else nullcontext():
                if quota_stop.is_set():
                    return None
                child = subprocess.Popen(command + ["--print", prompt], cwd=folder, env=env, stdout=out,
                                         stderr=err, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                attempt_status.update(pid=child.pid, state="starting_session" if gated else "running",
                                      conversation_id=cid,
                                      started_at=datetime.now().astimezone().isoformat())
                save(status_path, attempt_status)
                if gated and (created := wait_for_session(child, stdout, quota_stop)):
                    attempt_status.update(state="running", conversation_id=created)
                    save(status_path, attempt_status)
            while child.poll() is None:
                if quota_stop.wait(1):
                    if child.poll() is None:
                        terminated_by_quota = True
                        child.terminate()
                        child.wait()
                    break

        actual_cid, native_errors = native_log(stdout)
        fault = stderr.read_text(encoding="utf-8-sig", errors="replace") + "\n" + "\n".join(native_errors)
        if explicit_exhaustion(fault):
            save(args.run / "quota_pause.json", {"batch": private.name, "stage": stage, "log": stdout.name})
            quota_stop.set()
        try:
            if not actual_cid or (cid and cid != actual_cid):
                raise ValueError("缺少原生会话身份或续接身份不一致")
            cid = actual_cid
            rows = load(result)
            validate(rows, cases, stage)
            local_transcript = (
                private / "worker_profile/.gemini/antigravity-cli/brain" / cid
                / ".system_generated/logs/transcript_full.jsonl"
            )
            proof = verify_turn(cid, document, LABEL, result=result,
                                transcript=local_transcript if local_transcript.is_file() else None,
                                after_step=previous_proof.get("step", -1),
                                required_reads=[document, *upstream],
                                previous_images=map(Path, previous_proof.get("seen", [])))
            save(snapshot(private, stage), rows)
            proof.update(result_sha256=digest(snapshot(private, stage)), log=stdout.name)
            save(proof_file, proof)
            return proof
        except (ValueError, KeyError, OSError, TypeError) as exc:
            feedback = QUOTA_INTERRUPTED if terminated_by_quota else str(exc)
            fresh_retry = False if terminated_by_quota else empty_session_start(cid, actual_cid, fault, result)
            if fresh_retry:
                feedback = "agy 创建会话时返回空 ID"
                if native.is_file() and b"its database was initialized by another opener" in native.read_bytes():
                    feedback = "agy 会话数据库初始化冲突，返回空 ID"
            save(proof_file, {"conversation_id": cid, "problem": feedback, "log": stdout.name})
            if quota_stop.is_set() or (not cid and not fresh_retry) or attempt == 5:
                break
            next_at = (datetime.now().astimezone() + timedelta(seconds=20)).isoformat()
            save(status_path, {"stage": stage, "state": "retry_wait", "problem": feedback,
                               "conversation_id": cid, "retry_attempt": attempt + 1, "next_at": next_at})
            if quota_stop.wait(20):
                break
    save(status_path, {"stage": stage, "state": "quota_wait" if quota_stop.is_set() else "needs_review",
                       "problem": feedback, "conversation_id": cid})
    return None


def run_batch(args, name, cases, quota_stop):
    private, folder = args.run / name, args.packets / name
    if quota_stop.is_set():
        return
    profile = batch_auth.prepare_worker_profile(
        private / "worker_profile",
        isolate_cli_store=getattr(args, "isolate_cli_store", False),
    )
    env = batch_auth.batch_environment(private / "auth_browser.json", profile)
    for stage in ALLOWED:
        proof = run_stage(args, private, folder, stage, cases, env, quota_stop)
        if proof is None:
            print(f"{name} {stage} paused", flush=True)
            return
        print(f"{name} {stage} accepted {len(cases)}/{len(cases)}", flush=True)
    save(private / "status.json", {"stage": FINAL, "state": "completed"})


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
    parser.add_argument("--workers", type=int, default=8, choices=range(1, 17), metavar="1..16")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, choices=(5, 10, 20))
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    for name in ("source_root", "run", "packets", "agy"):
        setattr(args, name, getattr(args, name).resolve())
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

