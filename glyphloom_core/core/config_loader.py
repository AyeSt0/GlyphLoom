"""Utilities for loading project configuration files."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping, MutableMapping

import yaml

from .models import ProjectConfig, SourceConfig

DEFAULT_PROJECT = ProjectConfig()


def _ensure_mapping(data: Any) -> MutableMapping[str, Any]:
    if isinstance(data, Mapping):
        return dict(data)
    return {}


def load_project_config(config_path: str | Path | None = None) -> ProjectConfig:
    """Load a :class:`ProjectConfig`.

    Args:
        config_path: Optional yaml file. When ``None`` a default configuration is used.
    """

    if config_path is None:
        return ProjectConfig()

    path = Path(config_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    project_section = _ensure_mapping(data.get("project"))

    source_section = _ensure_mapping(project_section.get("source"))
    source_config = replace(
        SourceConfig(),
        adapter=source_section.get("adapter", DEFAULT_PROJECT.source.adapter),
        path=_resolve_path(source_section.get("path"), base_dir=path.parent)
        or DEFAULT_PROJECT.source.path,
        encoding=source_section.get("encoding", DEFAULT_PROJECT.source.encoding),
    )

    output_dir = _resolve_path(project_section.get("output_dir"), base_dir=path.parent)
    metadata = _ensure_mapping(project_section.get("metadata"))

    return ProjectConfig(
        name=project_section.get("name", DEFAULT_PROJECT.name),
        source=source_config,
        output_dir=output_dir or DEFAULT_PROJECT.output_dir,
        metadata=metadata,
        schema_version=int(
            project_section.get("schema_version", DEFAULT_PROJECT.schema_version)
        ),
    )


def _resolve_path(value: Any, base_dir: Path) -> Path | None:
    if value in (None, ""):
        return None
    resolved = Path(value)
    if not resolved.is_absolute():
        resolved = (base_dir / resolved).resolve()
    return resolved
