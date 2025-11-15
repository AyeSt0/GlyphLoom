"""Dataclasses that describe GlyphLoom project configuration and results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SourceConfig:
    """Definition of a single source extractor input."""

    adapter: str = "table"
    path: Path = Path("examples") / "template_basic.xlsx"
    encoding: str = "utf-8"


@dataclass
class ProjectConfig:
    """High level configuration for running a project pipeline."""

    name: str = "GlyphLoom Demo Project"
    source: SourceConfig = field(default_factory=SourceConfig)
    output_dir: Path = Path("output")
    metadata: Dict[str, Any] = field(default_factory=dict)
    schema_version: int = 1


@dataclass
class PipelineStep:
    """Represents the result of an individual pipeline phase."""

    name: str
    description: str
    succeeded: bool = True


@dataclass
class PipelineResult:
    """Summary returned by :func:`glyphloom_core.core.pipeline.run_project`."""

    project_name: str
    steps: List[PipelineStep]
    output_dir: Path
    created_files: List[Path] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Whether every pipeline step succeeded."""
        return all(step.succeeded for step in self.steps)
