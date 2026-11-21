"""Prepare one Markdown per task; share anonymous generated-image assets across tasks."""
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
            os.replace(temp_path, target)
        finally:
            temp_path.unlink(missing_ok=True)
    return "../_images/" + target.name


def prepare(destination, images):
    paths = [path.resolve(strict=True) for path in images]
    if not paths or len(set(paths)) != len(paths):
        raise ValueError("需要至少一张生成图，同一任务内不可重复")
    for path in paths:
        if path.parent not in MODELS or not re.fullmatch(r"\d{12}\.(jpg|png)", path.name):
            raise ValueError(f"请选择生成结果目录中的原始生成图：{path}")
    destination = destination.resolve()
    if destination.exists() or destination.name in {"_images", "_results"}:
        raise ValueError("请使用新的任务目录")
    cache = destination.parent / "_images"
    results = destination.parent / "_results"
    for folder in (cache, results):
        folder.mkdir(parents=True, exist_ok=True)
    guide = (ROOT / "模型读本.md").read_text(encoding="utf-8-sig")
    definitions = (ROOT / "规则.md").read_text(encoding="utf-8-sig").split("## 已裁决的边界")[0]
    cards = guide.split("## 典型生成图", 1)[1].split("\n### ")[1:]
    packet = [definitions, (ROOT / "标注步骤.md").read_text(encoding="utf-8-sig"), "## 典型样例"]
    example_ids = set()
    for i, card in enumerate(cards, 1):
        heading, caption, link = card.strip().split("\n\n")
        source = ROOT / re.search(r"\((examples/[^)]+)\)", link)[1]
        example_ids.add(source.stem.split("-")[-1])
        label = heading.split(" · ")[0]
        packet.append(f"R{i:03}　{label}　{caption}\n\n![R{i:03}]({publish_image(source, cache)})")
    if any(path.stem in example_ids for path in paths):
        raise ValueError("待标图与读本样例同一原图，请另选")
    packet.append("## 本轮待标图")
    mapping = {}
    for i, path in enumerate(paths, 1):
        alias = f"S{i:03}"
        mapping[alias] = path.relative_to(REPO).as_posix()
        packet.append(f"![{alias}]({publish_image(path, cache)})")
    task = uuid4().hex
    packet.append(f"结果写入 ../_results/{task}.json")
    private = ROOT / "local" / "task_index"
    private.mkdir(parents=True, exist_ok=True)
    destination.mkdir()
    (private / f"{task}.json").write_text(json.dumps(mapping, indent=2), encoding="utf8")
    (destination / "任务.md").write_text("\n\n".join(packet) + "\n", encoding="utf8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="独立 agy 工作区下的新任务目录")
    parser.add_argument("images", nargs="+", type=Path)
    args = parser.parse_args()
    prepare(args.destination, args.images)
