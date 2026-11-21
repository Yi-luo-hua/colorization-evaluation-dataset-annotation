"""Compatibility entry for the V5 workspace."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parents[2] / "V5_无GT标注工作区" / "prepare.py"),
                   run_name="__main__")
