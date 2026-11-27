"""Shared IO, hashing, image anonymization, and legacy script path helpers."""

from datetime import datetime
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
import tempfile

from PIL import Image, ImageOps

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = WORKSPACE_ROOT.parent
LEGACY_DELIVERY_ROOT = REPO_ROOT / "annotation_delivery/train_val_v1_20261015"
LEGACY_SCRIPTS_ROOT = LEGACY_DELIVERY_ROOT / "scripts"


def ensure_legacy_scripts(*, include_delivery_root=False):
    """Register legacy helper directories once without mutating unrelated modules."""
    paths = [LEGACY_SCRIPTS_ROOT]
    if include_delivery_root:
        paths.append(LEGACY_DELIVERY_ROOT)
    for directory in paths:
        text = str(directory)
        if text not in sys.path:
            sys.path.insert(0, text)


def stamp():
    return datetime.now().astimezone().isoformat()


def write_text(path, content):
    path = Path(path)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False, mode="w", encoding="utf8") as stream:
        temporary = Path(stream.name)
        stream.write(content)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def save_json(path, value):
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha256_file(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def publish_image(source, cache):
    """Export an EXIF-stripped RGB PNG into cache keyed by source SHA-256."""
    source, cache = Path(source), Path(cache)
    digest = sha256_file(source)
    target = cache / f"{digest}.png"
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
