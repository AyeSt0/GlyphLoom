"""QA 基础类型与接口声明。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol, Set

# 占位符类型别名，后续规则与引擎可复用
Placeholder = str
PlaceholderSet = Set[Placeholder]


class PlaceholderParserProtocol(Protocol):
    """占位符解析协议，便于替换具体实现（正则、分词、语法树等）。"""

    def parse(self, text: str) -> PlaceholderSet:
        """解析文本并返回占位符集合。"""


@dataclass
class Issue:
    """QA 问题描述：记录行号、占位符与消息。"""

    row: int
    placeholder: str
    message: str


@dataclass
class QAResult:
    """QA 结果汇总，存储所有 Issue。"""

    issues: List[Issue] = field(default_factory=list)


def extract_placeholders(
    text: str, whitelist: set[str] | None = None
) -> PlaceholderSet:
    """
    占位符提取接口声明（实现见 qa.placeholders）。

    保持接口稳定，便于外部替换不同的解析实现。
    """

    raise NotImplementedError


def run(lines: List[str]) -> List[Issue]:
    """
    QA 运行框架接口，当前作为占位实现。

    说明：
    - 后续规则（如占位符一致性）将在此基础上扩展；
    - 当前返回空列表，保证空输入或无规则时不报错。
    """

    return []
