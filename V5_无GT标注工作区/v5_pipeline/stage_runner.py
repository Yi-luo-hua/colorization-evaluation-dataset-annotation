"""Three-stage V5 annotation runner, task rendering, and output validation."""

from contextlib import nullcontext
from datetime import datetime, timedelta
import json
from pathlib import Path
import subprocess
from threading import Lock
import time

from turns import FORMAT_EXAMPLES, FORMAT_LINK, LABEL, verify_turn
from .io_utils import (
    WORKSPACE_ROOT,
    ensure_legacy_scripts,
    load_json,
    save_json,
    sha256_file,
    write_text,
)

ensure_legacy_scripts()
import batch_auth
from pipeline_store import OwnerLock
from quota_control import explicit_exhaustion

MODEL = "gemini-4-hydrogen-high"
DRAFT_MODEL = "gemini-4-hydrogen-medium"
FIRST, SECOND, FINAL = "01_initial", "02_color_and_distribution", "03b_finalize_review"
CATEGORIES = set("ABCD") | {"E1", "E2", "F"}
ALLOWED = {FIRST: set("ABD"), SECOND: {"C", "E1", "E2", "F"}, FINAL: CATEGORIES}
READS = {FIRST: (), SECOND: (FIRST,), FINAL: (FIRST, SECOND)}
FIELDS = {"id", "severity", "object", "description"}
QUOTA_INTERRUPTED = "因额度暂停中断，待恢复继续"
SESSION_START_LOCK = Lock()

# Backwards-compatible aliases
ROOT = WORKSPACE_ROOT
load = load_json
save = save_json
digest = sha256_file


def output_at(folder, stage):
    return folder / stage / "结果.json"


def stage_paths(folder, stage):
    stage_dir = folder / stage
    return stage_dir / "任务.md", stage_dir / FORMAT_EXAMPLES, output_at(folder, stage)


def public_inputs(folder, stage):
    return [folder / stage / f"前轮_{previous}.json" for previous in READS[stage]]


def snapshot(private, stage):
    return private / f"{stage}.accepted.json"


def render(folder, stage, labels, template, common):
    task, example, result = stage_paths(folder, stage)
    task.parent.mkdir(exist_ok=True)
    save_json(example, template["example"])
    if not result.exists():
        save_json(result, dict.fromkeys(labels))
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
        rows = load_json(result)
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
        proof = load_json(proof_file)
        if "step" in proof:
            if not snapshot(private, stage).exists():
                save_json(snapshot(private, stage), load_json(output_at(folder, stage)))
            if sha256_file(snapshot(private, stage)) != proof["result_sha256"]:
                raise ValueError(f"{stage} 已验收结果发生变化")
            return proof
    else:
        proof = {}

    document, _, result = stage_paths(folder, stage)
    upstream = public_inputs(folder, stage)
    for previous, public_file in zip(READS[stage], upstream):
        save_json(public_file, load_json(snapshot(private, previous)))
    previous_proof = load_json(private / f"{FIRST}.proof.json") if stage == SECOND else {}
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
            save_json(status_path, dict(attempt_status, state="waiting_to_start"))
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
                save_json(status_path, attempt_status)
                if gated and (created := wait_for_session(child, stdout, quota_stop)):
                    attempt_status.update(state="running", conversation_id=created)
                    save_json(status_path, attempt_status)
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
            save_json(args.run / "quota_pause.json", {"batch": private.name, "stage": stage, "log": stdout.name})
            quota_stop.set()
        try:
            if not actual_cid or (cid and cid != actual_cid):
                raise ValueError("缺少原生会话身份或续接身份不一致")
            cid = actual_cid
            rows = load_json(result)
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
            save_json(snapshot(private, stage), rows)
            proof.update(result_sha256=sha256_file(snapshot(private, stage)), log=stdout.name)
            save_json(proof_file, proof)
            return proof
        except (ValueError, KeyError, OSError, TypeError) as exc:
            feedback = QUOTA_INTERRUPTED if terminated_by_quota else str(exc)
            fresh_retry = False if terminated_by_quota else empty_session_start(cid, actual_cid, fault, result)
            if fresh_retry:
                feedback = "agy 创建会话时返回空 ID"
                if native.is_file() and b"its database was initialized by another opener" in native.read_bytes():
                    feedback = "agy 会话数据库初始化冲突，返回空 ID"
            save_json(proof_file, {"conversation_id": cid, "problem": feedback, "log": stdout.name})
            if quota_stop.is_set() or (not cid and not fresh_retry) or attempt == 5:
                break
            next_at = (datetime.now().astimezone() + timedelta(seconds=20)).isoformat()
            save_json(status_path, {"stage": stage, "state": "retry_wait", "problem": feedback,
                                    "conversation_id": cid, "retry_attempt": attempt + 1, "next_at": next_at})
            if quota_stop.wait(20):
                break
    save_json(status_path, {"stage": stage, "state": "quota_wait" if quota_stop.is_set() else "needs_review",
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
    save_json(private / "status.json", {"stage": FINAL, "state": "completed"})
