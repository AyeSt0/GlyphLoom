"""Stage 0 placeholder pipeline implementation."""

from __future__ import annotations

import logging
from pathlib import Path
from time import perf_counter
from typing import List

from .models import PipelineResult, PipelineStep, ProjectConfig

logger = logging.getLogger("glyphloom.core.pipeline")


def run_project(config: ProjectConfig) -> PipelineResult:
    """Execute a minimal pipeline for Stage 0."""

    steps: List[PipelineStep] = []
    _log_stage(
        "extract", f"Collecting source using adapter '{config.source.adapter}'", steps
    )
    _log_stage("translate", "Simulating LLM translation batch", steps)
    _log_stage("qa", "Running placeholder QA checks", steps)
    created_files = _log_stage(
        "export",
        f"Writing summary into output directory {config.output_dir}",
        steps,
        writer=lambda: _write_summary(config, steps),
    )

    return PipelineResult(
        project_name=config.name,
        steps=steps,
        output_dir=config.output_dir,
        created_files=created_files,
    )


def _log_stage(
    name: str,
    message: str,
    steps: List[PipelineStep],
    writer: callable | None = None,
) -> List[Path]:
    logger.info("[%s] %s", name, message)
    start = perf_counter()
    created: List[Path] = []
    if writer:
        created = writer() or []
    elapsed = perf_counter() - start
    steps.append(
        PipelineStep(
            name=name,
            description=f"{message} (elapsed {elapsed:.2f}s)",
            succeeded=True,
        )
    )
    return created


def _write_summary(config: ProjectConfig, steps: List[PipelineStep]) -> List[Path]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = config.output_dir / "summary.txt"
    lines = [
        f"GlyphLoom Stage 0 summary for project: {config.name}",
        f"Source adapter: {config.source.adapter}",
        f"Source path: {config.source.path}",
        "",
        "Steps:",
    ]
    lines.extend(f"- {step.name}: {step.description}" for step in steps)
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return [summary_path]
