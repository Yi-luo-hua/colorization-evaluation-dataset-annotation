"""CLI entrypoint for full V5 three-stage queue preparation and execution."""

from v5_pipeline.queue_runner import *  # noqa: F401,F403
from v5_pipeline.queue_runner import main

if __name__ == "__main__":
    main()
