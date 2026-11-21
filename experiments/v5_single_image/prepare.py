"""Build a two-stage, image-only annotation packet from generated image files."""
import argparse
import json
import re
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
CATEGORIES = ("A", "B", "C", "D", "E1", "E2", "F")


def prepare(destination, images):
    guide = (ROOT / "模型读本.md").read_text(encoding="utf8")
    references = re.findall(r"!\[[^\]]*\]\((examples/[^)]+)\)", guide)
    for reference in references:
        with Image.open(ROOT / reference) as image:
            image.verify()
    for path in images:
        with Image.open(path) as image:
            image.verify()
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copytree(ROOT / "examples", destination / "examples")
    (destination / "01_先读.md").write_text(guide, encoding="utf8")
    targets = destination / "targets"
    targets.mkdir()
    rows = []
    for index, path in enumerate(images, 1):
        name = f"S{index:03}"
        target = targets / (name + path.suffix.lower())
        shutil.copyfile(path, target)
        rows.append({"id": name, "image": target.relative_to(destination).as_posix(),
                     "checks": dict.fromkeys(CATEGORIES), "defects": []})
    (destination / "结果.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf8")
    (destination / "02_标注.md").write_text(
        "在同一会话完成第一步：先读 01_先读.md，并实际打开全部示例图片。无法读图时报告文件名并暂停。\n"
        "第二步：逐张打开结果.json 指定的 targets 图片，仅据该图标注，按原编号填写结果.json。\n"
        "checks 的每一项填写 hit、clear、uncertain 或 not_applicable。"
        "不确定及不适用时用同级 notes 字典按类别写理由。"
        "每个 hit 在 defects 中填写 category、severity（L1/L2/L3）、object、description。"
        "显著偏色时 E1/E2 填 not_applicable。A 命中仍继续检查其余类。"
        "全部适用类均 clear 才算无缺陷。", encoding="utf8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    parser.add_argument("images", nargs="+", type=Path)
    args = parser.parse_args()
    prepare(args.destination, args.images)
