"""TableAdapter 的具体实现。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..core.models import SourceConfig, TableAdapterConfig
from .base import BaseAdapter


class TableAdapter(BaseAdapter):
    """Excel/CSV 适配器，负责“读表 + 补列 + 写表”。

    仅处理结构相关的逻辑，不涉及任何翻译或 QA 细节。"""

    def __init__(self, source: SourceConfig, table_cfg: TableAdapterConfig) -> None:
        super().__init__()
        self._source = source
        self._table_cfg = table_cfg

    def load(self) -> pd.DataFrame:
        """根据文件后缀选择读表方式。"""

        path = self._source.path
        if path.suffix.lower() in {".xlsx", ".xls"}:
            # Excel 可指定 sheet_name，默认使用第一个 sheet
            self._data = pd.read_excel(path, sheet_name=self._table_cfg.sheet_name or 0)
        elif path.suffix.lower() == ".csv":
            # 读取 CSV 时尊重 SourceConfig.encoding
            self._data = pd.read_csv(path, encoding=self._source.encoding)
        else:
            raise ValueError(f"暂不支持的表格格式：{path.suffix}")
        return self._data

    def ensure_columns(self) -> None:
        """确保翻译相关列存在，并验证源列不可缺失。"""

        df = self._require_data()
        source_column = self._table_cfg.source_column
        if source_column not in df.columns:
            raise ValueError(
                f"源文本列 {source_column} 不存在，请检查文件：{self._source.path}"
            )

        for key, column_name in self._table_cfg.column_mapping.items():
            if key == "source":
                continue
            if column_name not in df.columns:
                # translation/status/qa_flags 如果缺失则创建空列，便于后续流水线填充
                df[column_name] = ""

    def save(self, output_path: Path) -> Path:
        """写出 DataFrame，返回最终路径。"""

        df = self._require_data()
        if output_path.suffix.lower() in {".xlsx", ".xls"}:
            df.to_excel(output_path, index=False)
        elif output_path.suffix.lower() == ".csv":
            df.to_csv(output_path, index=False, encoding=self._source.encoding)
        else:
            raise ValueError(f"暂不支持写出的表格格式：{output_path.suffix}")
        return output_path
