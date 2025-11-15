"""Command line entry point for GlyphLoom core."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .core.config_loader import load_project_config
from .core.pipeline import run_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GlyphLoom pipelines.")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="Path to YAML configuration file. When omitted, a demo config is used.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only load the configuration without running the pipeline.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s %(name)s: %(message)s"
    )

    config = load_project_config(args.config)
    logging.info(
        "Loaded project '%s' (output -> %s)",
        config.name,
        config.output_dir,
    )
    if args.dry_run:
        return 0

    result = run_project(config)
    logging.info("Pipeline finished: %s", "success" if result.success else "failed")
    logging.info("Artifacts: %s", ", ".join(map(str, result.created_files)) or "none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
