"""Translator 抽象基类。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from glyphloom_core.core.models import TranslatorConfig


class BaseTranslator(ABC):
    """翻译器抽象基类，统一文本批量翻译接口。"""

    def __init__(self, config: TranslatorConfig) -> None:
        self.config = config

    @abstractmethod
    def translate_batch(self, texts: list[str]) -> list[str]:
        """批量翻译，返回与输入等长的文本列表。"""
        raise NotImplementedError
