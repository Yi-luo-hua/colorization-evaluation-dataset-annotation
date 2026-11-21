"""Compatibility entry for the V5 workspace."""
import runpy
import sys
from pathlib import Path

if __name__ == "__main__":
    workspace = Path(__file__).resolve().parents[2] / "V5_无GT标注工作区"
    sys.path.insert(0, str(workspace))
    runpy.run_path(str(workspace / "prepare.py"), run_name="__main__")
