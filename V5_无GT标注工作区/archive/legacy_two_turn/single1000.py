import json
import os
import random
import sqlite3
from pathlib import Path

from prepare import ROOT, REPO

RUN_NAME = "two_turn1000"
RUN = ROOT / "local" / RUN_NAME
PUBLIC = Path(os.environ["LOCALAPPDATA"]) / "MCLReview" / RUN_NAME
COMPLETION_ARCHIVE = "V5_两轮1000.zip"
PORTABLE_ARCHIVE = "V5_两轮1000_图像与标注.zip"
MODEL = "gemini-3.8-flash-high"


def sample():
    RUN.mkdir(parents=True, exist_ok=True)
    manifest = RUN / "samples.json"
    if manifest.exists():
        return json.loads(manifest.read_text(encoding="utf8"))
    excluded = {p.stem.split("-")[-1] for p in (ROOT / "examples").glob("*.png")}
    sealed = REPO / "experiments/human_standard_600_20261102/local/image_ids_600_20261111.json"
    excluded.update(Path(x["source_sample_key"]).name for x in json.loads(sealed.read_text(encoding="utf8"))["images"])
    db = REPO / "annotation_delivery/train_val_v1_20261015/runtime/recovery5000_20261016_01/state.sqlite3"
    with sqlite3.connect(db.as_uri()+"?mode=ro", uri=True) as con:
        rows = con.execute("select json_extract(body,'$.record.model_path') from samples where state in ('completed','fixed_a') order by key").fetchall()
    rng = random.Random(20261121)
    groups = {}
    for path, in rows:
        p = Path(path)
        if p.stem not in excluded:
            groups.setdefault((p.parts[0], p.parts[-2]), []).append(path)
    selected = []
    for group in sorted(groups):
        pool = [p for p in groups[group] if Path(p).stem not in excluded]
        picked = rng.sample(pool, 250)
        selected.extend(picked)
        excluded.update(Path(p).stem for p in picked)
    assert len(selected) == 1000
    rng.shuffle(selected)
    manifest.write_text(json.dumps(selected, ensure_ascii=False, indent=2), encoding="utf8")
    return selected
