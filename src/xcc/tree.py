from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import EXCLUDED_DIRS


def build_project_tree(paths: list[Path], root: str | Path | None = None) -> str:
    if not paths:
        return ""

    display_paths = [_make_display_path(path, root) for path in paths]
    display_paths = sorted(display_paths, key=str.lower)

    lines = ["# Project Tree", ""]

    for path in display_paths:
        lines.append(path)

    return "\n".join(lines)


def build_directory_tree(
    root: str | Path,
    *,
    excluded_dirs: Iterable[str] | None = None,
) -> tuple[str, int, int]:
    root_path = Path(root)

    if not root_path.exists():
        raise FileNotFoundError(f"Project folder not found: {root_path}")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a folder: {root_path}")

    excluded = set(excluded_dirs or EXCLUDED_DIRS)

    entries: list[str] = []
    file_count = 0
    directory_count = 0

    for path in root_path.rglob("*"):
        if _is_inside_excluded_dir(path, root_path, excluded):
            continue

        try:
            relative_path = path.relative_to(root_path).as_posix()
        except ValueError:
            continue

        if path.is_dir():
            entries.append(f"{relative_path}/")
            directory_count += 1
            continue

        if path.is_file():
            entries.append(relative_path)
            file_count += 1

    lines = ["# Project Tree", ""]

    for entry in sorted(entries, key=str.lower):
        lines.append(entry)

    return "\n".join(lines), file_count, directory_count


def _make_display_path(path: Path, root: str | Path | None = None) -> str:
    if root is None:
        return path.name

    root_path = Path(root)

    try:
        return path.resolve().relative_to(root_path.resolve()).as_posix()
    except ValueError:
        return path.name


def _is_inside_excluded_dir(
    path: Path,
    root: Path,
    excluded_dirs: Iterable[str],
) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        return False

    excluded = set(excluded_dirs)

    return any(part in excluded for part in relative_parts)