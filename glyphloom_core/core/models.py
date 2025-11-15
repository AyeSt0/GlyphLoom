"""使用 pydantic 定义项目配置与运行结果。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field


def _default_source_path() -> Path:
    """Stage 0 默认使用仓库里的示例 Excel。"""

    return Path("examples") / "template_basic.xlsx"


class SourceConfig(BaseModel):
    """源数据配置，描述 adapter、输入路径与编码。"""

    model_config = ConfigDict(str_strip_whitespace=True)

    adapter: str = "table"
    path: Path = Field(default_factory=_default_source_path)
    encoding: str = "utf-8"


class ProjectConfig(BaseModel):
    """项目级配置，记录 schema 版本、输出目录等。"""

    model_config = ConfigDict(validate_assignment=True, arbitrary_types_allowed=True)

    name: str = "GlyphLoom Demo Project"
    source: SourceConfig = Field(default_factory=SourceConfig)
    output_dir: Path = Field(default=Path("output"))
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

    @property
    def success(self) -> bool:
        """是否所有阶段均成功。"""

        return all(step.succeeded for step in self.steps)
