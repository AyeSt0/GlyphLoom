"""加载 YAML 配置并构造 ProjectConfig。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, MutableMapping

import yaml

from .models import ProjectConfig, SourceConfig


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
    source_data: dict[str, Any] = {}
    if "adapter" in source_section:
        source_data["adapter"] = source_section["adapter"]
    resolved_source = _resolve_path(source_section.get("path"), base_dir=path.parent)
    if resolved_source is not None:
        source_data["path"] = resolved_source
    if "encoding" in source_section:
        source_data["encoding"] = source_section["encoding"]

    project_data: dict[str, Any] = {}
    if "name" in project_section:
        project_data["name"] = project_section["name"]
    resolved_output = _resolve_path(
        project_section.get("output_dir"), base_dir=path.parent
    )
    if resolved_output is not None:
        project_data["output_dir"] = resolved_output
    metadata = _ensure_mapping(project_section.get("metadata"))
    if metadata:
        project_data["metadata"] = metadata
    if "schema_version" in project_section:
        project_data["schema_version"] = str(project_section["schema_version"])

    if source_data:
        project_data["source"] = SourceConfig(**source_data)

    return ProjectConfig(**project_data)


def _resolve_path(value: Any, base_dir: Path) -> Path | None:
    if value in (None, ""):
        return None
    resolved = Path(value)
    if not resolved.is_absolute():
        resolved = (base_dir / resolved).resolve()
    return resolved
