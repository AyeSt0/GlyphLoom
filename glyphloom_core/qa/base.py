"""QA 基础类型与接口声明。"""

from __future__ import annotations

from typing import Set

# 占位符类型别名，后续规则与引擎可复用
Placeholder = str
PlaceholderSet = Set[Placeholder]


# 占位符解析器接口，便于替换具体实现（正则、分词、语法树等）
class PlaceholderParserProtocol:
    """占位符解析协议，后续可用分词/语法树等实现。"""

    def parse(self, text: str) -> PlaceholderSet:
        """解析文本并返回占位符集合。"""

        raise NotImplementedError


def extract_placeholders(
    text: str, whitelist: set[str] | None = None
) -> PlaceholderSet:
    """
    占位符提取接口声明（实现见 qa.placeholders）。

    设计原因：
    - base 仅声明接口与类型，便于后续替换实现或做类型提示；
    - 可以在不同规则/引擎中注入不同的提取实现（如正则或解析树）。
    TODO：若未来支持更复杂占位符（带参数/嵌套），可在此处引入新接口或协议。
    """

    raise NotImplementedError
