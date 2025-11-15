#!/usr/bin/env python3
"""
Stage every change,管理内部 alpha 版本号，并生成按文件拆解的中英双语自动提交信息。
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = REPO_ROOT / "VERSION"
MAX_HIGHLIGHTS = 3
QUALITY_SKIP_ENV = "GL_SKIP_QUALITY"


def _python_for_quality() -> str:
    return os.environ.get("PYTHON_FOR_QUALITY", sys.executable)


QUALITY_COMMANDS = [
    [_python_for_quality(), "-m", "ruff", "check", "."],
    [_python_for_quality(), "-m", "black", "--check", "."],
    [_python_for_quality(), "-m", "pytest", "-q"],
]

CATEGORY_INFO = {
    "docs": {"en": "Documentation updates", "zh": "文档更新"},
    "test": {"en": "Test coverage updates", "zh": "测试更新"},
    "build": {"en": "Build or tooling updates", "zh": "构建与工具调整"},
    "chore": {"en": "Repository maintenance", "zh": "仓库维护"},
    "feat": {"en": "Feature updates", "zh": "功能更新"},
}

CATEGORY_RULES = (
    (
        "docs",
        lambda p: p.suffix.lower() in {".md", ".rst", ".txt"}
        or "docs" in p.parts
        or p.name.lower() == "readme.md",
    ),
    (
        "test",
        lambda p: any(part.startswith("test") for part in p.parts)
        or p.name.lower().startswith("test_")
        or p.name.lower().endswith("_test.py"),
    ),
    (
        "build",
        lambda p: p.suffix.lower()
        in {".json", ".yml", ".yaml", ".toml", ".ini", ".ps1", ".sh", ".bat"}
        or "config" in p.parts
        or "scripts" in p.parts,
    ),
    (
        "chore",
        lambda p: p.name.lower() in {"license", "version"} or p.parent == Path("."),
    ),
)

CATEGORY_PRIORITY = {
    name: index for index, name in enumerate(["docs", "feat", "build", "test", "chore"])
}

STATUS_INFO = {
    "A": {"en": "Added", "zh": "新增"},
    "M": {"en": "Modified", "zh": "修改"},
    "D": {"en": "Deleted", "zh": "删除"},
    "R": {"en": "Renamed", "zh": "重命名"},
    "C": {"en": "Copied", "zh": "复制"},
}

HUNK_PATTERN = re.compile(r"@@ .*@@(.*)")


@dataclass
class FileChange:
    path: str
    category: str
    status: str
    additions: Optional[int]
    deletions: Optional[int]
    contexts: List[str] = field(default_factory=list)


def run_git(*args: str, strip_output: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip() if strip_output else result.stdout


def has_pending_changes() -> bool:
    status = run_git("status", "--porcelain")
    return bool(status.strip())


def read_version() -> str:
    if not VERSION_FILE.exists():
        return "alpha.0"
    return VERSION_FILE.read_text(encoding="utf-8").strip() or "alpha.0"


def bump_version(current: str) -> str:
    match = re.fullmatch(r"alpha\.(\d+)", current.strip())
    counter = int(match.group(1)) if match else 0
    return f"alpha.{counter + 1}"


def write_version(new_version: str) -> None:
    VERSION_FILE.write_text(f"{new_version}\n", encoding="utf-8")


def categorize(path_str: str) -> str:
    path = Path(path_str)
    for name, matcher in CATEGORY_RULES:
        if matcher(path):
            return name
    return "feat"


def normalize_diff_path(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("a/") or raw.startswith("b/"):
        return raw[2:]
    return raw


def parse_numstat() -> Dict[str, Tuple[Optional[int], Optional[int]]]:
    stats: Dict[str, Tuple[Optional[int], Optional[int]]] = {}
    output = run_git("diff", "--cached", "--numstat", strip_output=False)
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add_str, del_str, *path_parts = parts
        path = path_parts[-1]
        additions = None if add_str == "-" else int(add_str)
        deletions = None if del_str == "-" else int(del_str)
        stats[path] = (additions, deletions)
    return stats


def parse_name_status() -> Dict[str, str]:
    raw = run_git("diff", "--cached", "--name-status", "-z", strip_output=False)
    if not raw:
        return {}
    entries = [entry for entry in raw.split("\0") if entry]
    statuses: Dict[str, str] = {}
    idx = 0
    while idx < len(entries):
        status_token = entries[idx]
        idx += 1
        code = status_token[0]
        if code in {"R", "C"}:
            if idx + 1 >= len(entries):
                break
            _old_path = entries[idx]
            new_path = entries[idx + 1]
            idx += 2
            statuses[new_path] = code
        else:
            if idx >= len(entries):
                break
            path = entries[idx]
            idx += 1
            statuses[path] = code
    return statuses


def parse_hunk_contexts() -> Dict[str, List[str]]:
    diff_output = run_git("diff", "--cached", "--unified=0", strip_output=False)
    contexts: Dict[str, List[str]] = defaultdict(list)
    if not diff_output.strip():
        return contexts

    current_new: Optional[str] = None
    current_old: Optional[str] = None

    for line in diff_output.splitlines():
        if line.startswith("diff --git"):
            current_new = None
            current_old = None
            continue
        if line.startswith("--- "):
            old_path = line[4:]
            if old_path != "/dev/null":
                current_old = normalize_diff_path(old_path)
            continue
        if line.startswith("+++ "):
            new_path = line[4:]
            if new_path == "/dev/null":
                current_new = None
            else:
                current_new = normalize_diff_path(new_path)
            continue
        if not line.startswith("@@"):
            continue

        match = HUNK_PATTERN.match(line)
        context = match.group(1).strip() if match else ""
        if not context:
            context = line.replace("@@", "").strip()

        target_path = current_new or current_old
        if target_path:
            contexts[target_path].append(context)

    return contexts


def collect_file_changes(files: Iterable[str]) -> List[FileChange]:
    stats = parse_numstat()
    statuses = parse_name_status()
    contexts = parse_hunk_contexts()

    changes: List[FileChange] = []
    for file_path in files:
        additions, deletions = stats.get(file_path, (None, None))
        status_code = statuses.get(file_path, "M")
        change = FileChange(
            path=file_path,
            category=categorize(file_path),
            status=status_code,
            additions=additions,
            deletions=deletions,
            contexts=contexts.get(file_path, []),
        )
        changes.append(change)
    return changes


def condensed_contexts(contexts: Iterable[str]) -> List[str]:
    highlights: List[str] = []
    seen = set()
    for context in contexts:
        cleaned = context.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        highlights.append(cleaned)
        if len(highlights) >= MAX_HIGHLIGHTS:
            break
    return highlights


def format_line_counts(
    additions: Optional[int], deletions: Optional[int], lang: str
) -> str:
    if additions is None or deletions is None:
        return "binary changes" if lang == "en" else "二进制改动"
    if lang == "en":
        return f"+{additions}/-{deletions} lines"
    return f"增加 {additions} 行 / 删除 {deletions} 行"


def describe_change(change: FileChange, lang: str) -> str:
    status_info = STATUS_INFO.get(change.status[0], STATUS_INFO["M"])
    category_info = CATEGORY_INFO.get(change.category, CATEGORY_INFO["feat"])
    counts = format_line_counts(change.additions, change.deletions, lang)
    highlights = condensed_contexts(change.contexts)
    if lang == "en":
        base = f"{change.path} | {category_info['en']} | {status_info['en']} ({counts})"
        if highlights:
            base += f". Highlights: {', '.join(highlights)}"
        else:
            base += ". General adjustments."
        return base

    base = f"{change.path} | {category_info['zh']} | {status_info['zh']}（{counts}）"
    if highlights:
        base += f"。亮点：{', '.join(highlights)}"
    else:
        base += "。主要为常规调整。"
    return base


def select_dominant_category(changes: Iterable[FileChange]) -> str:
    weights: Dict[str, int] = defaultdict(int)
    for change in changes:
        delta = (change.additions or 0) + (change.deletions or 0)
        weights[change.category] += max(delta, 1)
    if not weights:
        return "feat"
    return max(weights, key=lambda cat: (weights[cat], -CATEGORY_PRIORITY.get(cat, 99)))


def build_commit_message(
    changes: List[FileChange], version_label: str
) -> Tuple[str, str]:
    if not changes:
        raise ValueError("No files were provided for commit generation.")

    dominant = select_dominant_category(changes)
    dominant_info = CATEGORY_INFO.get(dominant, CATEGORY_INFO["feat"])
    english_lines = [f"- {describe_change(change, 'en')}" for change in changes]
    chinese_lines = [f"- {describe_change(change, 'zh')}" for change in changes]

    title = (
        f"{dominant}: {dominant_info['en']} · {dominant_info['zh']} ({version_label})"
    )
    english_body = (
        "\n".join(english_lines) if english_lines else "- Minor housekeeping changes"
    )
    chinese_body = "\n".join(chinese_lines) if chinese_lines else "- 细微的维护调整"

    body = (
        f"English Summary:\n{english_body}\n\n"
        f"中文摘要：\n{chinese_body}\n\n"
        f"Auto version tag: {version_label}"
    )
    return title, body


def stage_everything() -> None:
    subprocess.run(["git", "add", "-A"], cwd=REPO_ROOT, check=True)


def staged_files() -> List[str]:
    output = run_git("diff", "--cached", "--name-only")
    return [line for line in output.splitlines() if line.strip()]


def should_skip_quality_checks() -> bool:
    value = os.environ.get(QUALITY_SKIP_ENV, "")
    return value.lower() in {"1", "true", "yes"}


def run_quality_checks() -> None:
    if should_skip_quality_checks():
        print(f"跳过质量检查，因为 {QUALITY_SKIP_ENV}=1")
        return

    for command in QUALITY_COMMANDS:
        pretty = " ".join(command)
        print(f"Running quality check: {pretty}")
        result = subprocess.run(command, cwd=REPO_ROOT)
        if result.returncode != 0:
            print(f"质量检查失败：{pretty}", file=sys.stderr)
            sys.exit(result.returncode)


def main() -> None:
    if not has_pending_changes():
        print("No detected changes. Skipping commit.")
        return

    run_quality_checks()

    current_version = read_version()
    new_version = bump_version(current_version)
    write_version(new_version)

    stage_everything()
    files = staged_files()
    if not files:
        print("Nothing ended up staged. Aborting automatic commit.")
        return

    changes = collect_file_changes(files)
    title, body = build_commit_message(changes, new_version)
    commit = subprocess.run(
        ["git", "commit", "-m", title, "-m", body],
        cwd=REPO_ROOT,
        text=True,
    )
    if commit.returncode == 0:
        print(f"Auto-commit created: {title}")
    else:
        print("Commit failed", file=sys.stderr)
        sys.exit(commit.returncode)


if __name__ == "__main__":
    main()
