"""Root CLI wrapper for Autonomous Quality Pipeline."""
import os
import subprocess
import sys
from pathlib import Path

DELIVERY_PIPELINE = Path(__file__).resolve().parent / 'annotation_delivery/train_val_v1_20261015/pipeline.py'

if __name__ == '__main__':
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    command = [sys.executable, '-X', 'utf8', str(DELIVERY_PIPELINE)] + sys.argv[1:]
    sys.exit(subprocess.call(command, env=env))
