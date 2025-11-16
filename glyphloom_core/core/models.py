"""使用 pydantic 定义项目配置与运行结果。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field
from glyphloom_core.qa.base import QAResult


def _default_source_path() -> Path:
    """Stage 0 默认使用仓库里的示例 Excel。"""

    return Path("examples") / "template_basic.xlsx"


class SourceConfig(BaseModel):
    """源数据配置，描述 adapter、输入路径与编码。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    adapter: str = "table"
    path: Path = Field(default_factory=_default_source_path)
    encoding: str = "utf-8"


class TableAdapterConfig(BaseModel):
    """TableAdapter 相关的配置，例如 sheet 与列名。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    sheet_name: str | None = None
    source_column: str = "source_text"
    translation_column: str = "translation"
    status_column: str = "status"
    qa_flags_column: str = "qa_flags"

    @computed_field  # type: ignore[misc]
    @property
    def column_mapping(self) -> Dict[str, str]:
        """方便 pipeline/adapter 做列名映射。"""

        return {
            "source": self.source_column,
            "translation": self.translation_column,
            "status": self.status_column,
            "qa_flags": self.qa_flags_column,
        }


class TranslatorConfig(BaseModel):
    """Translator 相关配置（Stage 1 仅支持最基础字段）。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    provider: str = "openai"
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    api_key_env: str = "OPENAI_API_KEY"
    temperature: float = 0.3
    max_tokens: int = 1024


class ProjectConfig(BaseModel):
    """项目级配置，记录 schema 版本、输出目录等。"""

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="forbid",
    )

    name: str = "GlyphLoom Demo Project"
    source: SourceConfig = Field(default_factory=SourceConfig)
    table_adapter: TableAdapterConfig = Field(default_factory=TableAdapterConfig)
    translator: TranslatorConfig = Field(default_factory=TranslatorConfig)
    output_dir: Path = Field(default_factory=lambda: Path("output"))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    schema_version: str = "0.0"


@dataclass
class PipelineStep:
    """流水线阶段执行结果（保持 dataclass，方便日志使用）。"""

    name: str
    description: str
    succeeded: bool = True


@dataclass
class PipelineResult:
    """流水线最终摘要，主要用于日志展示与测试断言。"""

    project_name: str
    steps: List[PipelineStep]
    output_dir: Path
    created_files: List[Path] = field(default_factory=list)
    qa_result: Optional[QAResult] = None

    @property
    def success(self) -> bool:
        """是否所有阶段均成功。"""

        return all(step.succeeded for step in self.steps)
