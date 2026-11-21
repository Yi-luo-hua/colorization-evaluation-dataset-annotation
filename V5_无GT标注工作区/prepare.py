"""Prepare the two V5 turns with anonymous PNGs."""
import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from uuid import uuid4

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
MODELS = {REPO / dataset / "model" / model
          for dataset in ("9_14_10000GT_V1", "10_5_val_V1", "10_5_test_V1")
          for model in ("lcad", "unicolor")}


def write_text(path, content):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, mode="w", encoding="utf8") as stream:
        temporary = Path(stream.name)
        stream.write(content)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def publish_image(source, cache):
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    target = cache / (digest + ".png")
    if not target.exists():
        with tempfile.NamedTemporaryFile(dir=cache, delete=False) as tmp:
            temp_path = Path(tmp.name)
        try:
            with Image.open(source) as original:
                pixels = ImageOps.exif_transpose(original).convert("RGB")
                profile = pixels.info.get("icc_profile")
                pixels.info.clear()
                pixels.save(temp_path, format="PNG", icc_profile=profile)
            try:
                os.link(temp_path, target)
            except FileExistsError:
                pass
        finally:
            temp_path.unlink(missing_ok=True)
    return target


def prepare_examples(directory):
    document = directory / "示例.md"
    if document.exists():
        return document
    directory.mkdir(parents=True, exist_ok=True)
    cache = directory.parent / "_reference_images"
    cache.mkdir(exist_ok=True)
    guide = (ROOT / "模型读本.md").read_text(encoding="utf-8-sig")
    definitions = (ROOT / "规则.md").read_text(encoding="utf-8-sig").split("## 已裁决的边界")[0]
    cards = guide.split("## 典型生成图", 1)[1].split("\n### ")[1:]
    sections = [definitions, "## 典型样例\n\n逐张打开 R 图，把可见现象与说明对上。每张只演示标出的判断。"]
    for i, card in enumerate(cards, 1):
        heading, caption, link = card.strip().split("\n\n")
        source = ROOT / re.search(r"\((examples/[^)]+)\)", link)[1]
        label = heading.split(" · ")[0]
        url = "../_reference_images/" + publish_image(source, cache).name
        sections.append(f"R{i:03}　{label}　{caption}\n\n![R{i:03}]({url})")
    write_text(document, "\n\n".join(sections) + "\n")
    return document


def prepare_task(directory, images):
    """Publish the S turn after the runner verifies the example checkpoint."""
    document = directory / "label" / "任务.md"
    if document.exists():
        return document
    paths = [path.resolve(strict=True) for path in images]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError("需要至少一张生成图，同一任务内不可重复")
    example_ids = {p.stem.split("-")[-1] for p in (ROOT / "examples").glob("*.png")}
    for path in paths:
        if path.parent not in MODELS or not re.fullmatch(r"\d{12}\.(jpg|png)", path.name):
            raise ValueError(f"请选择生成结果目录中的原始生成图：{path}")
        if path.stem in example_ids:
            raise ValueError("待标图与读本样例同一原图，请另选")

    cache = directory / "_images"
    results = directory / "_results"
    private = ROOT / "local" / "task_index"
    for folder in (cache, results, document.parent, private):
        folder.mkdir(parents=True, exist_ok=True)
    packet = [(ROOT / "标注步骤.md").read_text(encoding="utf-8-sig"), "## 本轮待标图"]
    mapping = {}
    for i, path in enumerate(paths, 1):
        alias = f"S{i:03}"
        mapping[alias] = path.relative_to(REPO).as_posix()
        packet.append(f"![{alias}](../_images/{publish_image(path, cache).name})")
    task = uuid4().hex
    packet.append(f"结果写入 ../_results/{task}.json")
    write_text(private / f"{task}.json", json.dumps(mapping, indent=2))
    write_text(document, "\n\n".join(packet) + "\n")
    return document


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="独立 agy 任务目录")
    parser.add_argument("images", type=Path, nargs="*", help="第二轮的生成图")
    parser.add_argument("--conversation", help="已确认阅读示例的原生会话 ID")
    args = parser.parse_args()
    directory = args.destination.resolve()
    if bool(args.images) != bool(args.conversation):
        parser.error("备第二轮任务必须同时提供生成图和 --conversation")
    if args.images:
        from turns import EXAMPLES, verify_turn
        verify_turn(args.conversation, directory / "示例.md", EXAMPLES)
        print(prepare_task(directory, args.images))
    else:
        print(prepare_examples(directory))

