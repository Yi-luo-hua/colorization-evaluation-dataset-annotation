"""Unified Pipeline CLI & Dashboard Runner for Colorization Review (V4 Standard).
Provides a single, intuitive entrypoint for auditing, sheet rendering, stream building,
exporting, validation, and multi-model/multi-split dataset status inspection.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
BASE_REVIEWER_DIR = WORKSPACE_ROOT / "LS_lcad_reviewer"
TASKS_POOL_DIR = BASE_REVIEWER_DIR / "tasks_pool"
EXPORTS_DIR = BASE_REVIEWER_DIR / "exports"
CORE_PIPELINE_DIR = BASE_REVIEWER_DIR / "core_pipeline"


if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def print_status():
    print("=" * 70)
    print(" [V4标准体系] 图像上色质量评估 · 数据集与工具矩阵全景")
    print("=" * 70)

    # 1. Tasks pool overview
    print("\n[1] 任务池矩阵 (tasks_pool/):")
    splits = ["train", "val", "test"]
    models = ["lcad", "unicolor"]

    for sp in splits:
        sp_dir = TASKS_POOL_DIR / sp
        if not sp_dir.exists():
            print(f"  - {sp.upper()}: 未创建")
            continue
        print(f"  - 分区 {sp.upper()}:")
        for m in models:
            matches = list(sp_dir.glob(f"*{m}*.json"))
            if matches:
                task_file = matches[0]
                try:
                    with open(task_file, "r", encoding="utf-8") as f:
                        count = len(json.load(f))
                    print(f"    * {m.upper():<10}: {count} 项任务 ({task_file.name})")
                except Exception as e:
                    print(f"    * {m.upper():<10}: 读取失败 ({e})")
            else:
                print(f"    * {m.upper():<10}: 尚未生成任务文件")

    # 2. Exports overview
    print("\n[2] 成品交付成果 (exports/):")
    if EXPORTS_DIR.exists():
        deliverables = list(EXPORTS_DIR.glob("reviewed_*.json"))
        clean_file = EXPORTS_DIR / "reviewed_1_10000_clean.json"
        all_file = EXPORTS_DIR / "reviewed_1_10000_all.json"

        print(f"  - 总交付文件数: {len(deliverables)} 个")
        if clean_file.exists():
            print(f"  - LCAD 全量纯净交付版: {clean_file.name} ({clean_file.stat().st_size / (1024**2):.1f} MB)")
        if all_file.exists():
            print(f"  - LCAD 全量过程留痕版: {all_file.name} ({all_file.stat().st_size / (1024**2):.1f} MB)")
    else:
        print("  - exports/ 目录不存在")

    # 3. Core tools
    print("\n[3] 通用工具链 (core_pipeline/):")
    tools = [
        ("cv_anomaly_detector.py", "CV 物理特征全量遥测计算 (0自动放行，100%送大图直审)"),
        ("generate_inspection_sheets.py", "并排三联高清看板全量生成 (6组/张，100%大图视觉覆盖)"),
        ("build_stream_batch.py", "批次流式抽检包构建器 (按物体饱和度定物)"),
        ("export_final_batch.py", "官方权威成品导出器 (自动基准契约强校验)"),
        ("validate_export_schema.py", "基准契约格式与逻辑断言工具"),
        ("merge_master_reviews.py", "主人人工抽检 SQLite 增量融合补丁工具")
    ]
    for script_name, desc in tools:
        sp_path = CORE_PIPELINE_DIR / script_name
        status = "✅ 就绪" if sp_path.exists() else "❌ 缺失"
        print(f"  - {script_name:<30}: {status} - {desc}")

    print("\n" + "=" * 70)


def forward_command(script_name: str, extra_args):
    target_script = CORE_PIPELINE_DIR / script_name
    if not target_script.exists():
        print(f"Error: Script not found: {target_script}")
        sys.exit(1)
    cmd = [sys.executable, str(target_script)] + extra_args
    res = subprocess.run(cmd)
    sys.exit(res.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Unified Pipeline CLI & Status Monitor (V4 Standard)",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: status
    subparsers.add_parser("status", help="Show full dataset, task pool and pipeline status")

    # Subcommand: detect
    p_detect = subparsers.add_parser("detect", help="Run CV physical anomaly detector")
    p_detect.add_argument("--model", default="lcad", choices=["lcad", "unicolor"])
    p_detect.add_argument("--split", default="train", choices=["train", "val", "test"])
    p_detect.add_argument("--start", type=int, default=1)
    p_detect.add_argument("--end", type=int, default=1000)

    # Subcommand: render
    p_render = subparsers.add_parser("render", help="Generate 3-column inspection sheets")
    p_render.add_argument("--audit-file", required=True)
    p_render.add_argument("--out-dir", required=True)
    p_render.add_argument("--model", default="lcad", choices=["lcad", "unicolor"])
    p_render.add_argument("--split", default="train", choices=["train", "val", "test"])

    # Subcommand: build
    p_build = subparsers.add_parser("build", help="Build stream batch package")
    p_build.add_argument("--start", type=int, default=1)
    p_build.add_argument("--end", type=int, default=500)
    p_build.add_argument("--model", default="lcad", choices=["lcad", "unicolor"])
    p_build.add_argument("--split", default="train", choices=["train", "val", "test"])

    # Subcommand: export
    p_export = subparsers.add_parser("export", help="Export reviewed deliverable JSON")
    p_export.add_argument("stream_file")
    p_export.add_argument("--ignore-db", action="store_true")

    # Subcommand: validate
    p_val = subparsers.add_parser("validate", help="Validate deliverable JSON against schema")
    p_val.add_argument("deliverable_file")

    # Subcommand: merge
    p_merge = subparsers.add_parser("merge", help="Merge master sqlite reviews into deliverable")
    p_merge.add_argument("target_file", nargs="?", default=None)

    args, unknown = parser.parse_known_args()

    if args.command == "status" or args.command is None:
        print_status()
    elif args.command == "detect":
        forward_command("cv_anomaly_detector.py", sys.argv[2:])
    elif args.command == "render":
        forward_command("generate_inspection_sheets.py", sys.argv[2:])
    elif args.command == "build":
        forward_command("build_stream_batch.py", sys.argv[2:])
    elif args.command == "export":
        forward_command("export_final_batch.py", sys.argv[2:])
    elif args.command == "validate":
        forward_command("validate_export_schema.py", sys.argv[2:])
    elif args.command == "merge":
        forward_command("merge_master_reviews.py", sys.argv[2:])


if __name__ == "__main__":
    main()
