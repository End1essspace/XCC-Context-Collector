from __future__ import annotations

import re
from pathlib import PurePosixPath, PureWindowsPath

from .config import ALLOWED_FILENAMES

_FENCED_BLOCK_RE = re.compile(r"```[^\n]*\n(?P<body>.*?)```", re.DOTALL)
_LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*+•]\s+|\d+[.)]\s+)")
_WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")
_GLOB_CHARS = frozenset("*?[]{}")
_WRAPPERS = (("`", "`"), ('"', '"'), ("'", "'"))


def parse_path_list(text: str) -> list[str]:
    """Extract an ordered, de-duplicated list of path-like lines.

    Fenced Markdown blocks are preferred when they contain paths. This allows a
    complete AI answer to be pasted without treating surrounding prose as file
    paths. When no useful fenced block exists, the complete text is inspected
    line by line.
    """
    if not text or not text.strip():
        return []

    fenced_candidates: list[str] = []
    for match in _FENCED_BLOCK_RE.finditer(text):
        fenced_candidates.extend(_parse_lines(match.group("body")))

    candidates = fenced_candidates or _parse_lines(text)

    result: list[str] = []
    seen: set[str] = set()

    for candidate in candidates:
        key = _path_comparison_key(candidate)
        if key in seen:
            continue

        seen.add(key)
        result.append(candidate)

    return result


def contains_relative_paths(paths: list[str]) -> bool:
    return any(not is_absolute_path_text(path) for path in paths)


def is_absolute_path_text(value: str) -> bool:
    normalized = value.strip()
    if not normalized:
        return False

    if _WINDOWS_ABSOLUTE_RE.match(normalized) or normalized.startswith("\\\\"):
        return True

    return PurePosixPath(normalized).is_absolute() or PureWindowsPath(
        normalized
    ).is_absolute()


def _parse_lines(text: str) -> list[str]:
    result: list[str] = []

    for raw_line in text.splitlines():
        candidate = _clean_line(raw_line)
        if candidate is None or not _looks_like_path(candidate):
            continue

        result.append(candidate)

    return result


def _clean_line(raw_line: str) -> str | None:
    line = raw_line.strip()
    if not line or line.startswith("```"):
        return None

    line = _LIST_PREFIX_RE.sub("", line, count=1).strip()

    changed = True
    while changed and len(line) >= 2:
        changed = False
        for opening, closing in _WRAPPERS:
            if line.startswith(opening) and line.endswith(closing):
                line = line[len(opening) : -len(closing)].strip()
                changed = True
                break

    line = line.rstrip(",;").strip()
    return line or None


def _looks_like_path(value: str) -> bool:
    if not value or value in {".", ".."}:
        return False

    if "://" in value or any(char in value for char in "<>|"):
        return False

    if any(char in value for char in _GLOB_CHARS):
        return False

    if value.startswith("#"):
        return False

    if is_absolute_path_text(value):
        return True

    normalized = value.replace("\\", "/")

    if normalized.endswith("/") and normalized.strip("/"):
        return True

    name = normalized.rsplit("/", 1)[-1]

    if not name or name in {".", ".."}:
        return False

    if "/" in normalized:
        return True

    if name.casefold() in {item.casefold() for item in ALLOWED_FILENAMES}:
        return True

    # A standalone filename such as AI_PROJECT_CONTEXT.md is valid. A normal
    # prose sentence almost never ends in a supported-looking file suffix.
    suffix = PurePosixPath(name).suffix
    return bool(suffix and " " not in suffix)


def _path_comparison_key(value: str) -> str:
    # XCC is a Windows application. Case-fold and normalize separators so the
    # same path is not imported twice when an AI answer mixes slash styles.
    return value.replace("\\", "/").casefold()
