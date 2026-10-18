"""Retired unsafe runner: route explicitly authorized resume to the unified executor."""
from pathlib import Path
import subprocess
import sys

if __name__=='__main__':
    entry = Path(__file__).resolve().parents[1]/'pipeline.py'
    sys.exit(subprocess.call([sys.executable,'-X','utf8',str(entry),'resume',*sys.argv[1:]]))
