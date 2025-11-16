"""OpenAI 兼容 HTTP translator 的占位实现（当前为假翻译）。"""

from __future__ import annotations

import os

from glyphloom_core.core.models import TranslatorConfig
from .base import BaseTranslator


class OpenAIHttpTranslator(BaseTranslator):
    """使用 OpenAI 兼容接口的 translator。

    当前阶段：不实际访问网络，仅返回带前缀的伪翻译结果。
    未来可以在 translate_batch 中替换为 httpx/requests 调用，并加入重试/错误处理。
    """

    def __init__(self, config: TranslatorConfig) -> None:
        super().__init__(config)
        # TODO：后续接入 glyphloom_core.core.secrets.get() 统一管理密钥读取
        # 假实现允许 key 为空，真实实现可在此校验并报错
        self.api_key = os.getenv(config.api_key_env, "")

    def translate_batch(self, texts: list[str]) -> list[str]:
        """伪翻译：为每条文本添加 [provider:model] 前缀，长度与输入一致。"""

        prefix = f"[{self.config.provider}:{self.config.model}]"
        return [f"{prefix} {text}" for text in texts]
