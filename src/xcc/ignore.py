from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True, slots=True)
class IgnoreRule:
    pattern: str
    negated: bool
    directory_only: bool
    anchored: bool
    has_slash: bool
    regex: re.Pattern[str]


@dataclass(slots=True)
class ProjectIgnoreMatcher:
    rules: list[IgnoreRule]

    def is_ignored(self, relative_path: str | Path, *, is_dir: bool = False) -> bool:
        normalized = _normalize_relative_path(relative_path)
        if not normalized:
            return False

        ignored = False
        for rule in self.rules:
            if rule.directory_only and not is_dir:
                parts = normalized.split("/")
                parent_paths = [
                    "/".join(parts[:index])
                    for index in range(1, len(parts))
                ]
                matched = any(rule.regex.search(parent) for parent in parent_paths)
            else:
                matched = bool(rule.regex.search(normalized))

            if matched:
                ignored = not rule.negated

        return ignored

    @classmethod
    def from_project_root(
        cls,
        project_root: str | Path,
        *,
        respect_xccignore: bool = True,
        respect_gitignore: bool = True,
    ) -> "ProjectIgnoreMatcher":
        root = Path(project_root)
        rules: list[IgnoreRule] = []

        if respect_gitignore:
            rules.extend(load_ignore_rules(root / ".gitignore"))

        if respect_xccignore:
            # XCC-specific rules are loaded last, so they can override matching
            # .gitignore rules with negation. Built-in excluded directories are
            # enforced separately and cannot be re-enabled by project rules.
            rules.extend(load_ignore_rules(root / ".xccignore"))

        return cls(rules)


def load_ignore_rules(path: str | Path) -> list[IgnoreRule]:
    ignore_path = Path(path)
    if not ignore_path.exists() or not ignore_path.is_file():
        return []

    try:
        text = ignore_path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError):
        return []

    rules: list[IgnoreRule] = []
    for raw_line in text.splitlines():
        rule = parse_ignore_rule(raw_line)
        if rule is not None:
            rules.append(rule)

    return rules


def parse_ignore_rule(raw_line: str) -> IgnoreRule | None:
    line = raw_line.strip()
    if not line:
        return None

    if line.startswith(r"\#"):
        line = line[1:]
    elif line.startswith("#"):
        return None

    negated = False
    if line.startswith(r"\!"):
        line = line[1:]
    elif line.startswith("!"):
        negated = True
        line = line[1:].strip()

    if not line:
        return None

    line = line.replace("\\", "/")
    anchored = line.startswith("/")
    if anchored:
        line = line[1:]

    directory_only = line.endswith("/")
    if directory_only:
        line = line.rstrip("/")

    if not line:
        return None

    has_slash = "/" in line
    regex = re.compile(
        _build_rule_regex(
            line,
            anchored=anchored,
            directory_only=directory_only,
            has_slash=has_slash,
        ),
        re.IGNORECASE,
    )

    return IgnoreRule(
        pattern=line,
        negated=negated,
        directory_only=directory_only,
        anchored=anchored,
        has_slash=has_slash,
        regex=regex,
    )


def _build_rule_regex(
    pattern: str,
    *,
    anchored: bool,
    directory_only: bool,
    has_slash: bool,
) -> str:
    translated = _translate_glob(pattern)

    if anchored or has_slash:
        prefix = "^"
    else:
        prefix = r"(?:^|/)"

    if directory_only:
        suffix = r"(?:/.*)?$"
    elif anchored or has_slash:
        suffix = "$"
    else:
        # Basename-style patterns match a file or directory segment anywhere.
        suffix = r"(?:$|/)"

    return prefix + translated + suffix


def _translate_glob(pattern: str) -> str:
    result: list[str] = []
    index = 0

    while index < len(pattern):
        char = pattern[index]

        if char == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                index += 2
                if index < len(pattern) and pattern[index] == "/":
                    result.append(r"(?:.*/)?")
                    index += 1
                else:
                    result.append(r".*")
                continue

            result.append(r"[^/]*")
            index += 1
            continue

        if char == "?":
            result.append(r"[^/]")
            index += 1
            continue

        if char == "[":
            closing = pattern.find("]", index + 1)
            if closing != -1:
                content = pattern[index + 1 : closing]
                if content.startswith("!"):
                    content = "^" + content[1:]
                elif content.startswith("^"):
                    content = "\\" + content
                result.append("[" + content + "]")
                index = closing + 1
                continue

        result.append(re.escape(char))
        index += 1

    return "".join(result)


def _normalize_relative_path(path: str | Path) -> str:
    value = str(path).replace("\\", "/").strip("/")
    if not value or value == ".":
        return ""

    return PurePosixPath(value).as_posix()
