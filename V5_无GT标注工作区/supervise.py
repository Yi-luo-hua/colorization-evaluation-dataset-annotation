"""Launch the V5 annotation dashboard (--full-run for the current three-stage queue)."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-run", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8947)
    args = parser.parse_args()
    from v5_pipeline.dashboard import serve_full
    serve_full(args.full_run, args.port)


if __name__ == "__main__":
    main()
