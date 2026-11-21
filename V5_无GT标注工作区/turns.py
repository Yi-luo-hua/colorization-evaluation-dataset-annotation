"""Verify the ordering and native media receipts of the two V5 turns."""
from collections import deque
import json
import os
from pathlib import Path
import re

EXAMPLES = "[V5 示例轮]"
LABEL = "[V5 标注轮]"
CONFIRMED = "V5_EXAMPLES_READ"
READ_TOOLS = {"read_file", "view_file", "view_image"}
WRITE_TOOLS = {"write_file", "write_to_file"}


def result_path(document):
    body = document.read_text(encoding="utf8")
    return document.parent / re.search(r"结果写入 (\.\./_results/[a-f0-9]{32}\.json)", body)[1]


def path_aliases(path):
    return {os.path.normcase(os.path.abspath(path)), os.path.normcase(str(path.resolve()))}


def tool_path(args):
    path = args.get("Path") or args.get("AbsolutePath") or args.get("ImagePath")
    return Path(path) if path else None


def prompt_for(phase, document, feedback):
    if phase == EXAMPLES:
        instruction = (
            "只读定义和示例。用 read_file 打开每张列出的 R 图，核对对象、现象与示例说明。"
            f"所有 R 图看完后只回复 {CONFIRMED}。遇到无法打开的图，报告其 R 编号。"
        )
    else:
        instruction = (
            "沿用本会话已经阅读的 V5 定义与示例，只打开任务列出的 S 图，逐张评定。"
            "使用 read_file 查看图像，使用 write_file 把完整 JSON 写入任务指定的结果路径。"
        )
    return f"{phase} 读取 {document}。\n{instruction}\n只访问本轮列出的文件，不使用终端或其他工具。\n{feedback}".strip()


def verify_turn(cid, document, phase, *, after_step=-1, result=None, transcript=None):
    """Count successful image attachments in the intended turn and retries only."""
    source = transcript or (
        Path.home() / ".gemini/antigravity-cli/brain" / cid / ".system_generated/logs/transcript_full.jsonl"
    )
    prefix = "R" if phase == EXAMPLES else "S"
    targets = {label: document.parent / path for label, path in
               re.findall(rf"!\[({prefix}\d+)\]\(([^)]+)\)", document.read_text(encoding="utf8"))}
    if not targets:
        raise ValueError(f"{document.name} 缺少 {prefix} 图索引")
    paths = {alias: label for label, path in targets.items() for alias in path_aliases(path)}
    output_paths = path_aliases(result) if result else set()
    expected = json.loads(result.read_text(encoding="utf-8-sig")) if result else None
    waiting = deque()
    seen = set()
    started = False
    accepted = None
    last_reply = None
    with source.open(encoding="utf-8-sig") as log:
        for line in log:
            try:
                step = json.loads(line)
            except ValueError:
                continue
            index = step["step_index"]
            if index <= after_step:
                continue
            kind = step.get("type")
            content = step.get("content") or ""
            calls = step.get("tool_calls")
            if kind == "USER_INPUT":
                user_text = content.split("</USER_REQUEST>", 1)[0]
                started = phase in user_text and str(document) in user_text
                waiting.clear()
                last_reply = None
            elif started and calls:
                waiting.clear()
                for call in calls:
                    args = call.get("args", {})
                    name = call.get("name")
                    path = tool_path(args)
                    key = os.path.normcase(os.path.abspath(path)) if path else ""
                    label = paths.get(key) if name in READ_TOOLS else None
                    matches = False
                    if key in output_paths and name in WRITE_TOOLS and seen == targets.keys():
                        try:
                            matches = json.loads(args.get("Content") or args.get("CodeContent")) == expected
                        except (TypeError, ValueError):
                            pass
                    waiting.append((label, matches))
            elif started and kind == "GENERIC" and waiting:
                label, matches = waiting.popleft()
                if step.get("status") == "DONE" and "Error:" not in content:
                    if label and "Showing binary file of type image/" in content and any(
                        m.get("mime_type", "").startswith("image/") for m in step.get("media", [])
                    ):
                        seen.add(label)
                    if matches:
                        accepted = index
            elif started and kind == "PLANNER_RESPONSE" and step.get("status") == "DONE" and content:
                last_reply = content.strip()
                if phase == EXAMPLES:
                    accepted = index if last_reply == CONFIRMED and seen == targets.keys() else None

    missing = sorted(targets.keys() - seen)
    if missing:
        raise ValueError("缺少本轮成功读图凭证 " + "、".join(missing))
    if phase == EXAMPLES and (accepted is None or last_reply != CONFIRMED):
        raise ValueError("示例图已齐，请明确回复 " + CONFIRMED)
    if accepted is None:
        raise ValueError("请在读齐 S 图后用 write_file 重新写入完整结果")
    return {
        "conversation_id": cid, "seen": [str(targets[label].resolve()) for label in sorted(seen)],
        "missing": [], "transcript": str(source), "step": accepted,
    }

