"""GlyphLoom core 的命令行入口，提供最小 translate 子命令。"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from glyphloom_core.core.config_loader import load_project_config
from glyphloom_core.core.pipeline import run_project


def build_parser() -> argparse.ArgumentParser:
    """构建 CLI 参数解析器，默认子命令为 translate。"""

    parser = argparse.ArgumentParser(description="Run GlyphLoom pipelines.")
    parser.add_argument(
        "command",
        nargs="?",
        default="translate",
        choices=["translate"],
        help="执行的子命令，当前仅支持 translate。",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="YAML 配置文件路径，缺省时使用默认示例配置。",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只加载配置，不执行流水线。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """入口函数：加载配置并执行 pipeline。"""

    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    config = load_project_config(args.config)
    logging.info(
        "项目：%s | 输出目录：%s | 源文件：%s",
        config.name,
        config.output_dir,
        config.source.path,
    )
    if args.dry_run:
        logging.info("Dry-run 模式，仅加载配置后退出。")
        return 0

    if args.command == "translate":
        result = run_project(config)
        logging.info(
            "流水线完成：%s",
            "success" if result.success else "failed",
        )
        logging.info(
            "输出文件：%s",
            ", ".join(map(str, result.created_files)) or "无",
        )
        return 0

    parser.error(f"未知命令：{args.command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
