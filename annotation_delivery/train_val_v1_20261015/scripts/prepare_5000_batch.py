"""Compatibility entry: offline recovery of the frozen 5000-sample batch, never overwrite old packets."""
from pathlib import Path
import subprocess
import sys

if __name__=='__main__':
    entry=Path(__file__).resolve().parents[1]/'pipeline.py'
    sys.exit(subprocess.call([sys.executable,'-X','utf8',str(entry),'prepare','--verify-images',*sys.argv[1:]]))
