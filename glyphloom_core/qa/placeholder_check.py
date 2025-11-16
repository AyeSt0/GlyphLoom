"""占位符一致性检查规则。"""

from __future__ import annotations

from typing import List, Set

from glyphloom_core.qa.base import Issue
from glyphloom_core.qa.placeholders import extract_placeholders


def check_placeholder_consistency(
    source_text: str,
    target_text: str,
    row: int = 0,
    whitelist: Set[str] | None = None,
) -> List[Issue]:
    """
    对比源文本与译文的占位符集合，生成缺失/多余的 Issue。

    :param source_text: 源文本
    :param target_text: 译文文本
    :param row: 行号或记录序号，方便回写 Issue
    :param whitelist: 白名单，占位符在此集合内则忽略检查
    """

    src_placeholders = extract_placeholders(source_text, whitelist=whitelist or set())
    tgt_placeholders = extract_placeholders(target_text, whitelist=whitelist or set())

    issues: List[Issue] = []

    missing = src_placeholders - tgt_placeholders
    for ph in sorted(missing):
        issues.append(Issue(row=row, placeholder=ph, message=f"译文缺少占位符：{ph}"))

    extra = tgt_placeholders - src_placeholders
    for ph in sorted(extra):
        issues.append(Issue(row=row, placeholder=ph, message=f"译文多出占位符：{ph}"))

    return issues
