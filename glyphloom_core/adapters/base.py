"""表格适配器抽象基类。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pandas as pd


class BaseAdapter(ABC):
    """所有表格类适配器的抽象基类。

    约定：适配器内部维护一个 ``pandas.DataFrame``，并通过 load/ensure/save
    的顺序完成“读取 → 补列 → 写出”的数据闭环。
    """

    def __init__(self) -> None:
        self._data: Optional[pd.DataFrame] = None

    @abstractmethod
    def load(self) -> pd.DataFrame:
        """读取原始数据并返回 DataFrame。"""

    @abstractmethod
    def ensure_columns(self) -> None:
        """确保翻译相关列存在。"""

    @abstractmethod
    def save(self, output_path: Path) -> Path:
        """将内部数据写出到指定路径。"""

    def _require_data(self) -> pd.DataFrame:
        """确保 load 已被调用。"""

        if self._data is None:
            raise RuntimeError("尚未加载数据，请先调用 load()")
        return self._data

    @property
    def data(self) -> pd.DataFrame:
        """只读访问内部 DataFrame，供 pipeline 等上层读取。"""

        return self._require_data()
