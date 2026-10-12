"""Compatibility entrypoint; canonical implementation is in core_pipeline/."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "core_pipeline" / "merge_master_reviews.py"), run_name="__main__")
