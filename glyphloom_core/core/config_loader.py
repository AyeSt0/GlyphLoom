"""加载 YAML 配置并构造 ProjectConfig。"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, MutableMapping

import yaml

from .models import (
    ProjectConfig,
    SourceConfig,
    TableAdapterConfig,
    TranslatorConfig,
)


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
    source_data = _parse_source(source_section, base_dir=path.parent)

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

    table_section = _ensure_mapping(project_section.get("table_adapter"))
    table_data = _parse_table_adapter(table_section)
    if table_data:
        project_data["table_adapter"] = TableAdapterConfig(**table_data)

    translator_section = _ensure_mapping(project_section.get("translator"))
    translator_data = _parse_translator(translator_section)
    if translator_data:
        project_data["translator"] = TranslatorConfig(**translator_data)

    return ProjectConfig(**project_data)


def _resolve_path(value: Any, base_dir: Path) -> Path | None:
    if value in (None, ""):
        return None
    resolved = Path(value)
    if not resolved.is_absolute():
        resolved = (base_dir / resolved).resolve()
    return resolved


def _parse_source(section: MutableMapping[str, Any], base_dir: Path) -> dict[str, Any]:
    """解析 source 段落，负责处理路径等默认值。"""

    data: dict[str, Any] = {}
    if "adapter" in section:
        data["adapter"] = section["adapter"]
    resolved = _resolve_path(section.get("path"), base_dir=base_dir)
    if resolved is not None:
        data["path"] = resolved
    if "encoding" in section:
        data["encoding"] = section["encoding"]
    return data


def _parse_table_adapter(section: MutableMapping[str, Any]) -> dict[str, Any]:
    """解析 table_adapter 段落，仅保留用户覆盖字段。"""

    data: dict[str, Any] = {}
    for key in (
        "sheet_name",
        "source_column",
        "translation_column",
        "status_column",
        "qa_flags_column",
    ):
        if key in section:
            data[key] = section[key]
    return data


def _parse_translator(section: MutableMapping[str, Any]) -> dict[str, Any]:
    """解析 translator 段落，注意将数值转为字符串/浮点。"""

    data: dict[str, Any] = {}
    mapping = {
        "provider": "provider",
        "base_url": "base_url",
        "model": "model",
        "api_key_env": "api_key_env",
        "temperature": "temperature",
        "max_tokens": "max_tokens",
    }
    for key, target in mapping.items():
        if key in section:
            data[target] = section[key]
    return data
