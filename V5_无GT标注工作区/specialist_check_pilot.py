"""Run a small paired pilot on locally stored V5 adjudications.

Use observe to create a fresh run, resolve to send candidate and relationship
packets, and report to recalculate metrics from the accepted outputs.
The native transport uses agy media receipts. The API transport uses the
project's existing vision connection and records HTTP response receipts.
"""
import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import sys
from threading import Event
from time import perf_counter
from uuid import uuid4

from prepare import publish_image, write_text
from turns import FORMAT_EXAMPLES, FORMAT_LINK, LABEL, verify_turn

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
DELIVERY = REPO / "annotation_delivery/train_val_v1_20261015"
HUMAN = ROOT / "local/human_annotations_merged_20261124/人工标注合并.json"
EXPORT = DELIVERY / "exports/training_train_val_20261021"
ROLES = {"A": ("A",), "D": ("D",), "B": ("B",), "F": ("F",), "C": ("C",), "E": ("E1", "E2")}
CATEGORIES = ("A", "B", "C", "D", "E1", "E2", "F")
SEED = 20261125

sys.path.append(str(DELIVERY / "scripts"))
from batch_auth import batch_environment, prepare_worker_profile
from quota_control import explicit_exhaustion

SPECIALTY = {
    "A": "找应有色彩区分却只剩近灰明暗的区域，排除固有中性色及光照。按确认区域占整幅面积分级。",
    "D": "查不同材质、不同区域是否共偏。找画面支持的合理光源和仍呈正常色的反证，准确区分 L1 与 L2/L3。",
    "B": "沿主次物体及边缘找来源、受染处及可见联系。允许不相连的跨越式溢出。只要证据完整，轻微可见也标。",
    "F": "扫连续表面是否有无结构、材质、纹理或光照依据的斑块、碎片、色带及突变。与 B、C 可按独立证据共存。",
    "C": "观察实际颜色与同一物体或场景的语义冲突。核对异常是不是仅有彩度变化、合理涂装、环境光或全局色偏。",
    "E": "在可辨且合理的色相上核对彩度异常，E1/E2 分别检查。先提交区域候选；整图 D 和同区 A 交后续关系核查。",
    "direct": "独立完整标注七类。按 D、A、B、C/E、F 扫图。同处 A 排除 C/E，显著 D 时两类 E 均记 clear。",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def source_rows():
    rows = {}
    for path in sorted(EXPORT.glob("*.json")):
        model, split = path.stem.split("_")
        for item in load(path):
            rows[f"{split}/{model}/{Path(item['image']).stem}"] = item["solution"]["defects"]
    return rows


def set_up(run, limit):
    old = source_rows()
    chosen = [
        row for row in load(HUMAN)["images"]
        if row["current_annotation"]["status"] == "adjudicated_whole_image"
    ]
    rng = random.Random(SEED)
    rng.shuffle(chosen)
    chosen = chosen[:limit]
    audit = set(rng.sample(range(len(chosen)), min(8, (len(chosen) + 1) // 2)))
    cases = {}
    for index, row in enumerate(chosen):
        key = row["sample_key"]
        labels = {item["id"] for item in old[key]}
        routed = [role for role, categories in ROLES.items() if labels.intersection(categories)]
        # With no CV in this pilot, old C/E are practical signals for an A check.
        if labels & {"C", "E1", "E2"} and "A" not in routed:
            routed.append("A")
        if labels & {"E1", "E2"} and "D" not in routed:
            routed.append("D")
        cases[f"S{index + 1:03d}"] = {
            "key": key, "image": row["image"], "human": row["feishu_v5_r48"]["grades"],
            "human_text": row["feishu_v5_r48"]["annotation"], "old": old[key],
            "base_routes": routed, "audit": index in audit,
        }
    save(run / "cases.json", cases)
    return cases


def prepare_packet(public, name, ids, cases, role, context=None):
    folder = public / name
    folder.mkdir(parents=True, exist_ok=False)
    document = folder / "任务.md"
    result = folder / "结果.json"
    categories = ROLES.get(role, CATEGORIES)
    example = [{
        "id": "EXAMPLE", "checks": {label: "clear" for label in categories},
        "defects": [],
    }]
    save(folder / FORMAT_EXAMPLES, example)
    rules = (ROOT / "规则.md").read_text(encoding="utf-8-sig").split("## 已裁决的边界")[0]
    if role in ROLES:
        rules = "\n".join(
            line for line in rules.splitlines()
            if not line.startswith("|") or line.startswith(("|类别", "|---", *(f"|{c} " for c in categories), *(("|E1/E2 ",) if role == "E" else ())))
        )
    instruction = SPECIALTY.get(role, "")
    if context is not None:
        save(folder / FORMAT_EXAMPLES, {"example": example, "candidate_cases": context})
        instruction = (
            "你负责关系核查、旧候选确认或洗空补漏。先逐图独立观察，再读本包链接的格式示例 JSON，"
            "它包含专职观察和匿名旧候选。按每图 reason 指定的分支工作。"
            "关系分支仅裁决显著 D 对 E、同一缺色对象对 C/E，以及同对象的 C/E；"
            "每类证据分别成立时保留合法的 B/C/F 并存。对同一关系集合输出完整判决，"
            "保留其他区域有证据的缺陷，确认 D-L2/L3 时 E1/E2 清空。"
            "wash 洗空分支扫整图七类。confirm_ 分支复核对应旧条目，也可补同类新部位。只接受具体图像证据。"
            "结果的 checks 只包含该图 target 指定类别。"
        )
    read_order = "先完整读取" if context is None else "读图后完整读取"
    lines = [
        rules, "## 任务", instruction,
        f"{read_order} {FORMAT_LINK}。用 read_file 逐张打开下列生成图。"
        "只查任务指定类别，务必扫前景、主体、背景。已确认的 L1 也标。"
        "确认命中写 hit，余项写 clear。每条缺陷包含 category、severity、object、description，"
        "描述写可见的对象、部位、颜色和证据。逐图完成判断后把整个 JSON 数组一次写到 "
        f"{result}。只访问所列文件，只用 read_file 和 write_file。",
    ]
    if context is None:
        lines.append("没有历史候选。checks 的类别：" + "、".join(categories))
    for sid in ids:
        cache_image = publish_image(REPO / cases[sid]["image"], folder)
        image = folder / f"{sid}.png"
        os.link(cache_image, image)
        lines.append(f"![{sid}](./{image.name})")
    write_text(document, "\n\n".join(lines) + "\n")
    return document, result


def validate(rows, expected):
    if (not isinstance(rows, list) or len(rows) != len(expected)
            or not all(isinstance(row, dict) for row in rows)
            or {row.get("id") for row in rows} != set(expected)):
        raise ValueError("结果样本编号与任务不符")
    for row in rows:
        sid = row["id"]
        checks = row["checks"]
        if set(checks) != set(expected[sid]) or set(checks.values()) - {"hit", "clear"}:
            raise ValueError(f"{sid}: 检查类别或状态无效")
        defects = row["defects"]
        for defect in defects:
            if defect["severity"] not in {"L1", "L2", "L3"} or not all(
                defect[field].strip() for field in ("description", "object")
            ):
                raise ValueError(f"{sid}: 缺陷字段无效")
        if {defect["category"] for defect in defects} != {k for k, v in checks.items() if v == "hit"}:
            raise ValueError(f"{sid}: 命中状态与缺陷不一致")


def lane(agy, model, run, stop, job):
    name, document, result, expected = job
    started = perf_counter()
    out_log = run / f"{name}.jsonl"
    err_log = run / f"{name}.err"
    env = batch_environment(run / f"{name}.auth.json", prepare_worker_profile(run / f"profile-{name}"))
    prompt = (
        f"{LABEL} 完整阅读 {document}，然后按其范围读图、按指定格式把 JSON 直接写入目标文件。"
        "只读取任务指定的文件，不使用终端。"
    )
    proof = {"accepted": 0, "expected": len(expected)}
    last_cid = None
    for attempt in range(2):
        if stop.is_set():
            break
        out_path = out_log if not attempt else out_log.with_suffix(".retry.jsonl")
        err_path = err_log if not attempt else err_log.with_suffix(".retry.err")
        command = [str(agy), "--model", model, "--mode", "accept-edits", "--output-format", "stream-json"]
        if last_cid:
            command += ["--conversation", last_cid]
        with out_path.open("wb") as out, err_path.open("wb") as err:
            process = subprocess.Popen(
                command + ["--print", prompt], cwd=document.parent.parent, stdout=out, stderr=err,
                env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            while process.poll() is None:
                if stop.wait(2):
                    process.terminate()
                    process.wait()
                    break
        errors = err_path.read_text(encoding="utf-8-sig", errors="replace")
        if explicit_exhaustion(errors):
            stop.set()
        try:
            with out_path.open(encoding="utf-8-sig") as stdout:
                cid = json.loads(stdout.readline())["conversation_id"]
            if last_cid and cid != last_cid:
                raise ValueError("续接会话身份不一致")
            last_cid = cid
            rows = load(result)
            validate(rows, expected)
            proof.update(verify_turn(cid, document, LABEL, result=result), accepted=len(rows))
            save(run / f"{name}.results.json", rows)
            break
        except (ValueError, KeyError, OSError, TypeError) as error:
            proof["problem"] = str(error)
            if not last_cid or stop.wait(20):
                break
            prompt = (
                f"{LABEL} 继续原任务 {document}。请按原任务重新写出完整 JSON。"
                f"验收问题：{error}"
            )
    proof.update(elapsed_seconds=round(perf_counter() - started, 1), conversation_id=last_cid)
    save(run / f"{name}.proof.json", proof)
    print(name, f"{proof['accepted']}/{proof['expected']}", proof["elapsed_seconds"], proof.get("problem", ""), flush=True)




def stream_api(payload, key):
    import httpx

    chunks = []
    envelope = {}
    with httpx.stream(
        "POST", "https://api.tryanotherone.com/v1/chat/completions", content=payload,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        timeout=httpx.Timeout(75, connect=15),
    ) as response:
        metadata = {"http_status": response.status_code, "provider_request_id": response.headers.get("x-request-id")}
        if response.is_error or "text/event-stream" not in response.headers.get("content-type", ""):
            raw = response.read().decode("utf8", errors="replace").replace(key, "[REDACTED]")
            return metadata, raw
        for line in response.iter_lines():
            if not line.startswith("data:"):
                continue
            value = line[5:].strip()
            if value == "[DONE]":
                break
            item = json.loads(value)
            if item.get("error"):
                return metadata, value.replace(key, "[REDACTED]")
            for field in ("id", "model", "usage"):
                if item.get(field):
                    envelope[field] = item[field]
            for choice in item.get("choices", []):
                delta = choice.get("delta", {}).get("content")
                if isinstance(delta, str):
                    chunks.append(delta)
    envelope["choices"] = [{"message": {"content": "".join(chunks)}}]
    return metadata, json.dumps(envelope, ensure_ascii=False)



def api_lane(model, run, stop, key, job):
    import base64
    import re
    import httpx

    name, document, _, expected = job
    if stop.is_set():
        return
    started = perf_counter()
    context = load(document.parent / FORMAT_EXAMPLES)
    task = document.read_text(encoding="utf-8-sig")
    rules = task.split("## 任务")[0]
    images = re.findall(r"!\[(S\d+)\]\(\./([^)]+)\)", task)
    role = name.rsplit("-", 1)[0]
    instruction = SPECIALTY.get(role, (
        "复核候选和依赖。relation 仅评定 target 指定的 D/A/C/E 类，核对显著 D 关闭整图 E 和"
        "同一确认缺色区域排除 C/E。wash 独立扫图补漏。confirm_ 核对旧候选定义和等级。"
        "保留其他位置和有独立证据的缺陷。"
    ))
    content = [{"type": "text", "text": (
        rules + "\n" + instruction + "\n只依据下列生成图。按图编号返回 JSON 对象 {\"rows\": [...]}。"
        "每条含 id、checks、defects。checks 只设该编号指定类别，值 hit 或 clear。"
        "每个缺陷含 category、severity（L1、L2 或 L3）、object、description，"
        "说明颜色、实际部位和可见依据。明确的 L1 也写。各图检查类别："
        + json.dumps(expected, ensure_ascii=False)
    )}]
    for sid, filename in images:
        image = (document.parent / filename).read_bytes()
        content.extend((
            {"type": "text", "text": sid},
            {"type": "image_url", "image_url": {
                "url": "data:image/png;base64," + base64.b64encode(image).decode("ascii"), "detail": "high",
            }},
        ))
    if isinstance(context, dict):
        content.append({"type": "text", "text": "先独立观察，再对照候选：" + json.dumps(context["candidate_cases"], ensure_ascii=False)})
    request = {
        "model": model, "messages": [{"role": "user", "content": content}],
        "max_tokens": 5000, "stream": True, "response_format": {"type": "json_object"},
    }
    payload = json.dumps(request, ensure_ascii=False).encode("utf8")
    proof = {"accepted": 0, "expected": len(expected), "request_sha256": hashlib.sha256(payload).hexdigest()}
    try:
        metadata, raw = stream_api(payload, key)
        proof.update(metadata)
        write_text(run / f"{name}.api-response.json", raw)
        if metadata["http_status"] in {401, 403, 402} or explicit_exhaustion(raw):
            stop.set()
        if metadata["http_status"] >= 400:
            raise ValueError(f"HTTP {metadata['http_status']}: {raw[:300]}")
        envelope = json.loads(raw)
        result = envelope["choices"][0]["message"]["content"]
        proof.update(provider_response_id=envelope.get("id"), reported_model=envelope.get("model"), usage=envelope.get("usage"))
        rows = json.loads(re.sub(r"^\x60{3}(?:json)?\s*|\s*\x60{3}$", "", result.strip()))["rows"]
        validate(rows, expected)
        save(run / f"{name}.results.json", rows)
        proof["accepted"] = len(rows)
    except (ValueError, KeyError, TypeError, httpx.HTTPError) as error:
        proof["problem"] = str(error).replace(key, "[REDACTED]")
    proof["elapsed_seconds"] = round(perf_counter() - started, 1)
    save(run / f"{name}.proof.json", proof)
    print(name, f"{proof['accepted']}/{proof['expected']}", proof["elapsed_seconds"], proof.get("problem", ""), flush=True)



def invoke(args, jobs):
    stop = Event()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        if args.transport == "api":
            sys.path.append(str(REPO / "experiments/reliability_refine_pilot_20261025"))
            from provider_credentials import token
            key = token()
            futures = [pool.submit(api_lane, args.model, args.run, stop, key, job) for job in jobs]
        else:
            futures = [pool.submit(lane, args.agy, args.model, args.run, stop, job) for job in jobs]
        for future in as_completed(futures):
            future.result()
    if stop.is_set():
        raise SystemExit("模型通道报额度或认证阻塞，停止余下任务")


def stage_one(args, cases):
    jobs = []
    for role in ("direct", *ROLES):
        ids = [sid for sid, case in cases.items() if role == "direct" or role in case["base_routes"] or case["audit"]]
        for offset in range(0, len(ids), 6):
            chunk = ids[offset:offset + 6]
            name = f"{role}-{offset // 6 + 1:02d}"
            document, result = prepare_packet(args.public, name, chunk, cases, role)
            expected = {sid: ROLES.get(role, CATEGORIES) for sid in chunk}
            jobs.append((name, document, result, expected))
    save(args.run / "stage_one_jobs.json", {job[0]: job[3] for job in jobs})
    print("Blind specialist / direct jobs:", len(jobs), flush=True)
    invoke(args, jobs)



def category_set(defects):
    return {defect.get("category", defect.get("id")) for defect in defects}


def role_results(run, jobs):
    rows = {}
    for name, expected in jobs.items():
        path = run / f"{name}.results.json"
        if path.exists():
            output = load(path)
            validate(output, expected)
            rows[name] = {row["id"]: row for row in output}
    return rows


def collect_drafts(cases, observations):
    drafts = {sid: {"checks": {}, "defects": []} for sid in cases}
    direct = {}
    for name, rows in observations.items():
        if name.startswith("direct-"):
            direct.update(rows)
            continue
        for sid, row in rows.items():
            drafts[sid]["checks"].update(row["checks"])
            drafts[sid]["defects"].extend(row["defects"])
    return drafts, direct


def plan_followup(cases, drafts):
    plans = {}
    for sid, case in cases.items():
        draft = drafts[sid]
        if not draft["checks"]:
            continue
        before = category_set(case["old"])
        found = category_set(draft["defects"])
        possible = before | found
        targets = {}
        if before and not found:
            targets["wash"] = set(CATEGORIES)
        else:
            if (("D" in possible and possible & {"E1", "E2"}) or
                ("A" in possible and possible & {"C", "E1", "E2"}) or
                ("C" in possible and possible & {"E1", "E2"})):
                targets["relation"] = {"A", "C", "D", "E1", "E2"} & draft["checks"].keys()
            covered = targets.get("relation", set())
            for role, categories in ROLES.items():
                disputed = set(categories) & (before - found) - covered
                if disputed:
                    targets[f"confirm_{role}"] = disputed
        for group, target in targets.items():
            if target:
                plans.setdefault(group, {})[sid] = {
                    "target": sorted(target), "reason": group,
                    "independent_observations": [
                        defect for defect in draft["defects"] if defect["category"] in target
                    ],
                    "old_candidates": [defect for defect in case["old"] if defect["id"] in target],
                }
    return plans


def stage_two(args, cases, drafts):
    jobs = []
    for group, records in plan_followup(cases, drafts).items():
        ids = list(records)
        for offset in range(0, len(ids), 5):
            chunk = ids[offset:offset + 5]
            context = {sid: records[sid] for sid in chunk}
            name = f"{group}-{offset // 5 + 1:02d}"
            document, result = prepare_packet(args.public, name, chunk, cases, group, context)
            expected = {sid: records[sid]["target"] for sid in chunk}
            jobs.append((name, document, result, expected))
    save(args.run / "stage_two_jobs.json", {job[0]: job[3] for job in jobs})
    print("Candidate / relationship jobs:", len(jobs), flush=True)
    invoke(args, jobs)


def combine(cases, drafts, followup):
    final = {}
    for sid in cases:
        row = drafts[sid]
        checks = dict(row["checks"])
        defects = list(row["defects"])
        for rows in followup.values():
            if sid not in rows:
                continue
            update = rows[sid]
            checks.update(update["checks"])
            defects = [d for d in defects if d["category"] not in update["checks"]] + update["defects"]
        excluded = []
        if any(d["category"] == "D" and d["severity"] in {"L2", "L3"} for d in defects):
            excluded = [d for d in defects if d["category"] in {"E1", "E2"}]
            defects = [d for d in defects if d["category"] not in {"E1", "E2"}]
            checks.update(E1="skipped_due_to_D", E2="skipped_due_to_D")
        final[sid] = {
            "status": {label: checks.get(label, "not_dispatched") for label in CATEGORIES},
            "defects": defects, "suppressed_E": excluded,
        }
    return final


def grades(defects):
    values = {}
    for defect in defects:
        label = defect.get("category", defect.get("id"))
        severity = defect["severity"]
        level = int(severity.removeprefix("L")) if severity else 0
        values[label] = max(values.get(label, 0), level)
    return values


def measurement(cases, output, matched):
    total = Counter()
    categories = {label: Counter() for label in CATEGORIES}
    detail = {}
    for sid in matched:
        human = cases[sid]["human"]
        old = category_set(cases[sid]["old"])
        prediction = grades(output[sid]["defects"])
        new = set(prediction)
        true = set(human)
        edits = {
            "remove_fp": sorted((old - new) - true),
            "remove_tp": sorted((old - new) & true),
            "add_tp": sorted((new - old) & true),
            "add_fp": sorted((new - old) - true),
        }
        for edit, labels in edits.items():
            total[edit] += len(labels)
            for label in labels:
                categories[label][edit] += 1
        total.update({
            "tp": len(true & new), "fp": len(new - true), "fn": len(true - new),
            "exact_grade": sum(human[label] == prediction[label] for label in true & new),
            "empty": not new, "miss_entire_image": bool(true and not new),
        })
        for label in CATEGORIES:
            categories[label].update({
                "tp": label in true & new, "fp": label in new - true, "fn": label in true - new,
                "exact_grade": label in true & new and human[label] == prediction[label],
            })
        detail[sid] = {"key": cases[sid]["key"], "actual": human, "prediction": prediction, **edits}
    return {"total": dict(total), "by_category": categories, "per_image": detail}


def write_report(args, cases, stage1, stage2, drafts, direct):
    final = combine(cases, drafts, stage2)
    expected1 = load(args.run / "stage_one_jobs.json")
    expected2 = load(args.run / "stage_two_jobs.json")
    missing = {
        sid for jobs, answers in ((expected1, stage1), (expected2, stage2))
        for name, expected in jobs.items() if name not in answers for sid in expected
    }
    matched = [sid for sid in cases if sid in direct and sid not in missing]
    for jobs, answers in ((expected1, stage1), (expected2, stage2)):
        for name in jobs.keys() - answers.keys():
            if name.startswith("direct-"):
                continue
            for sid, labels in jobs[name].items():
                for label in labels:
                    final[sid]["status"][label] = "pending_review"
    old = {sid: {"defects": case["old"]} for sid, case in cases.items()}
    audit_hits = []
    for sid in matched:
        case = cases[sid]
        for label in sorted(set(case["human"]) - category_set(case["old"])):
            role = "E" if label in ("E1", "E2") else label
            if role not in case["base_routes"] and case["audit"]:
                audit_hits.append({
                    "id": sid, "category": label,
                    "proposed_blind": label in category_set(drafts[sid]["defects"]),
                    "present_final": label in category_set(final[sid]["defects"]),
                })
    e_gate = [
        {"id": sid, "true_E": sorted({"E1", "E2"} & cases[sid]["human"].keys()),
         "final_D": grades(final[sid]["defects"]).get("D"), "suppressed_candidates": final[sid]["suppressed_E"]}
        for sid in matched if final[sid]["status"]["E1"] == "skipped_due_to_D"
    ]
    metrics = {
        title: measurement(cases, output, matched)
        for title, output in (("旧底稿", old), ("专职首遍", drafts), ("专职复核最终", final), ("同模型直接盲标", direct))
    }
    save(args.run / "final.json", final)
    save(args.run / "comparison.json", {
        "matched": matched, "missing_packets": sorted((expected1.keys() - stage1.keys()) | (expected2.keys() - stage2.keys())),
        "audit_only_true_defects": audit_hits, "D_gate": e_gate, "metrics": metrics,
    })
    specialist = sum(len(rows) for name, rows in stage1.items() if not name.startswith("direct-"))
    special_packets = sum(not name.startswith("direct-") for name in stage1)
    followup_count = sum(len(rows) for rows in stage2.values())
    headings = [
        "# V5 专职 Check 首轮试验", "",
        f"模型 {args.model}。{len(cases)} 张飞书修订 48 已裁决图。随机抽 {sum(case['audit'] for case in cases.values())} 张扩至全部专职，其他图按历史候选派发。"
        "A 同时受旧 C/E 触发，D 同时受旧 E 触发。本轮无 CV、无 GT、无裁决示例输入。",
        f"同图完整配对 {len(matched)}/{len(cases)}。专职首遍 {special_packets} 包、{specialist} 次受理图像，"
        f"候选和关系复核 {len(stage2)} 包、{followup_count} 次受理图像，直接盲标 {len(direct)} 次受理图像。",
        "",
        "|方法|命中|多报|漏报|同类同级|人工阳性但整图空|删对|误删|补对|新增错标|",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    columns = ("tp", "fp", "fn", "exact_grade", "miss_entire_image", "remove_fp", "remove_tp", "add_tp", "add_fp")
    for title, group in metrics.items():
        headings.append("|" + title + "|" + "|".join(str(group["total"].get(key, 0)) for key in columns) + "|")
    headings += [
        "",
        "同图同类与等级按最高等级统计。对象、部位及成因保留在逐图原文，不由类别指标代理。",
        "派发未回收记 pending_review，未派发记 not_dispatched，按规则跳过 E 另有记录。",
        "",
        "|类别|人工阳性|旧命中/多报|专职最终命中/多报|删对|误删|补对|新增错标|",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in CATEGORIES:
        ref = metrics["旧底稿"]["by_category"][label]
        score = metrics["专职复核最终"]["by_category"][label]
        headings.append(
            f"|{label}|{ref['tp'] + ref['fn']}|{ref['tp']}/{ref['fp']}|{score['tp']}/{score['fp']}|"
            + "|".join(str(score.get(key, 0)) for key in columns[5:]) + "|"
        )
    headings += [
        "",
        f"随机补派覆盖 {len(audit_hits)} 个旧路由会跳过的人工阳性，专职首遍命中 "
        f"{sum(row['proposed_blind'] for row in audit_hits)} 个，终版命中 {sum(row['present_final'] for row in audit_hits)} 个。",
        f"显著 D 关闭 E 共 {len(e_gate)} 张，涉及人工 E 阳性 "
        f"{sum(len(row['true_E']) for row in e_gate)} 个图×类别。",
        "",
        "[逐图对照和指标](comparison.json) · [专职最终结果和派发状态](final.json) · [样本与人工裁决](cases.json)",
    ]
    write_text(args.run / "REPORT.md", "\n".join(headings) + "\n")
    print("\n".join(headings[:11]), flush=True)



def retry_api_packets(args, planned, accepted):
    """Retry unresolved API packets once and retain the first attempt's receipts."""
    jobs = []
    archive = args.run / "first_api_attempts"
    for name in sorted(planned.keys() - accepted.keys()):
        proof_path = args.run / f"{name}.proof.json"
        if proof_path.exists():
            proof = load(proof_path)
            if proof.get("http_status") in {401, 403, 402}:
                raise SystemExit("API 通道仍待恢复：" + name)
        previous = [path for path in (
            proof_path, args.run / f"{name}.api-response.json",
        ) if path.exists()]
        archive.mkdir(exist_ok=True)
        if any((archive / path.name).exists() for path in previous):
            continue
        for path in previous:
            path.replace(archive / path.name)
        folder = args.public / name
        jobs.append((name, folder / "任务.md", folder / "结果.json", planned[name]))
    if jobs:
        invoke(args, jobs)



def finish_stage(args, cases):
    stage_one_jobs = load(args.run / "stage_one_jobs.json")
    first = role_results(args.run, stage_one_jobs)
    if args.stage == "resolve" and args.transport == "api":
        retry_api_packets(args, stage_one_jobs, first)
        first = role_results(args.run, stage_one_jobs)
    if args.stage == "resolve" and (missing := stage_one_jobs.keys() - first.keys()):
        raise SystemExit("首遍缺少已验收任务：" + ", ".join(sorted(missing)))
    drafts, direct = collect_drafts(cases, first)
    if args.stage == "resolve" and not (args.run / "stage_two_jobs.json").exists():
        stage_two(args, cases, drafts)
    stage_two_jobs = load(args.run / "stage_two_jobs.json")
    second = role_results(args.run, stage_two_jobs)
    if args.stage == "resolve" and args.transport == "api":
        retry_api_packets(args, stage_two_jobs, second)
        second = role_results(args.run, stage_two_jobs)
    write_report(args, cases, first, second, drafts, direct)
    if missing := stage_two_jobs.keys() - second.keys():
        raise SystemExit("收口缺少已验收任务：" + ", ".join(sorted(missing)))



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("observe", "resolve", "report"))
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--agy", type=Path, default=Path("E:/programming/agy/bin/agy.exe"))
    parser.add_argument("--transport", choices=("native", "api"), default="native")
    parser.add_argument("--model")
    parser.add_argument("--limit", type=int, choices=range(1, 18), default=17)
    parser.add_argument("--workers", type=int, choices=range(1, 17), default=12)
    args = parser.parse_args()
    args.run = args.run.resolve()
    args.model = args.model or ("gpt-6-luna" if args.transport == "api" else "gemini-4-hydrogen-high")
    if args.stage == "observe":
        args.run.mkdir(parents=True, exist_ok=False)
        args.public = Path(os.environ["LOCALAPPDATA"]) / "MCLReview" / ("V5-check-" + uuid4().hex[:12])
        args.public.mkdir(parents=True)
        cases = set_up(args.run, args.limit)
        save(args.run / "setup.json", {
            "public": str(args.public), "model": args.model, "seed": SEED, "transport": args.transport,
            "source_sha256": {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in EXPORT.glob("*.json")},
        })
        stage_one(args, cases)
    else:
        setup = load(args.run / "setup.json")
        args.public, args.model = Path(setup["public"]), setup["model"]
        args.transport = setup.get("transport", "native")
        finish_stage(args, load(args.run / "cases.json"))


if __name__ == "__main__":
    main()

