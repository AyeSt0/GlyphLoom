"""占位符提取实现，解析器版本，支持多种括号与空格。"""

from __future__ import annotations

import re
from typing import Iterable, Set

from .base import Placeholder, PlaceholderSet

# 额外可配置的占位符模式（非括号类），支持动态注册。
_EXTRA_PATTERN_STRS: list[str] = [
    r"%\([^)]+\)s",  # %(name)s
    r"%s",  # %s
    r"\$\{[A-Za-z0-9_]+\}",  # ${ENV}
]
_EXTRA_PATTERNS: list[re.Pattern[str]] = [re.compile(p) for p in _EXTRA_PATTERN_STRS]

# 默认支持的括号对，按长度降序匹配，避免 "{{" 与 "{" 冲突。
_ENCLOSED_PAIRS = [
    ("{{", "}}"),
    ("[[", "]]"),
    ("((", "))"),
    ("{", "}"),
    ("[", "]"),
    ("(", ")"),
    ("<", ">"),
]


def register_placeholder_patterns(patterns: Iterable[str]) -> None:
    """批量注册自定义占位符模式，便于从配置加载。"""

    extended = [p for p in patterns if p]
    if not extended:
        return
    _EXTRA_PATTERN_STRS.extend(extended)
    _rebuild_extra_patterns()


def register_placeholder_pattern(pattern: str) -> None:
    """单个注册自定义占位符模式，无需修改源码即可支持新格式。"""

    if not pattern:
        return
    _EXTRA_PATTERN_STRS.append(pattern)
    _rebuild_extra_patterns()


def _rebuild_extra_patterns() -> None:
    """重建额外模式的正则，保证新增模式即时生效。"""

    global _EXTRA_PATTERNS
    _EXTRA_PATTERNS = [re.compile(p) for p in _EXTRA_PATTERN_STRS]


class PlaceholderParser:
    """解析器：处理括号类占位符，以及动态注册的模式。"""

    def parse(self, text: str) -> PlaceholderSet:
        if not text:
            return set()
        results: Set[Placeholder] = set()
        self._parse_enclosed(text, results)
        self._parse_extra_patterns(text, results)
        return results

    def _parse_enclosed(self, text: str, results: Set[Placeholder]) -> None:
        """
        处理各种括号占位符，支持空格与嵌套。

        规则：
        - 按开括号长度降序匹配，避免 "{{" 被 "{" 抢先。
        - 遇到 ${ENV} 或 %(...)s 时，由额外模式处理，不重复捕获。
        - 嵌套时只返回最外层占位符，内层由计数驱动，但不单独记录。
        """

        i = 0
        n = len(text)
        pairs = sorted(_ENCLOSED_PAIRS, key=lambda p: len(p[0]), reverse=True)
        while i < n:
            matched = False
            for open_tok, close_tok in pairs:
                if text.startswith(open_tok, i):
                    # 跳过 ${...} 给额外模式处理
                    if open_tok.startswith("{") and i > 0 and text[i - 1] == "$":
                        i += 1
                        matched = True
                        break
                    # 跳过 %(...) 给额外模式处理
                    if open_tok == "(" and i > 0 and text[i - 1] == "%":
                        i += 1
                        matched = True
                        break
                    depth = 1
                    j = i + len(open_tok)
                    while j < n and depth > 0:
                        if text.startswith(open_tok, j):
                            depth += 1
                            j += len(open_tok)
                            continue
                        if text.startswith(close_tok, j):
                            depth -= 1
                            j += len(close_tok)
                            if depth == 0:
                                results.add(text[i:j])
                                matched = True
                                break
                            continue
                        j += 1
                    if matched:
                        i = j
                        break
            if not matched:
                i += 1

    def _parse_extra_patterns(self, text: str, results: Set[Placeholder]) -> None:
        """处理动态注册的额外模式（包括默认 %s / %(name)s / ${ENV}）。"""

        for pattern in _EXTRA_PATTERNS:
            matches = pattern.findall(text)
            if not matches:
                continue
            if isinstance(matches, list):
                results.update(matches)
            else:
                results.add(matches)


def extract_placeholders(
    text: str, whitelist: set[str] | None = None
) -> PlaceholderSet:
    """
    提取文本中的占位符集合。

    :param text: 原始字符串
    :param whitelist: 白名单，占位符在列表中则忽略（用于允许特定占位符存在差异）
    :return: 占位符集合，已去重
    """

    parser = PlaceholderParser()
    found = parser.parse(text)
    if not whitelist:
        return found
    return {ph for ph in found if ph not in whitelist}
