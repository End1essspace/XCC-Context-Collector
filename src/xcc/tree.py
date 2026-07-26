from __future__ import annotations

from pathlib import Path
from collections.abc import Callable, Iterable

from .cancellation import CollectionCancelled
from .config import EXCLUDED_DIRS
from .ignore import ProjectIgnoreMatcher


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
    respect_xccignore: bool = True,
    respect_gitignore: bool = True,
    progress_callback: Callable[[int, int], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> tuple[str, int, int]:
    root_path = Path(root)

    if not root_path.exists():
        raise FileNotFoundError(f"Project folder not found: {root_path}")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a folder: {root_path}")

    excluded = set(excluded_dirs or EXCLUDED_DIRS)
    ignore_matcher = ProjectIgnoreMatcher.from_project_root(
        root_path,
        respect_xccignore=respect_xccignore,
        respect_gitignore=respect_gitignore,
    )

    entries: list[str] = []
    file_count = 0
    directory_count = 0

    processed_entries = 0

    for path in root_path.rglob("*"):
        if cancel_check is not None and cancel_check():
            raise CollectionCancelled("Collection cancelled.")

        if _is_inside_excluded_dir(path, root_path, excluded):
            continue

        try:
            relative = path.relative_to(root_path)
            relative_path = relative.as_posix()
        except ValueError:
            continue

        is_dir = path.is_dir()
        if ignore_matcher.is_ignored(relative, is_dir=is_dir):
            continue

        if is_dir:
            entries.append(f"{relative_path}/")
            directory_count += 1
            processed_entries += 1
            if progress_callback is not None:
                progress_callback(processed_entries, 0)
            continue

        if path.is_file():
            entries.append(relative_path)
            file_count += 1
            processed_entries += 1
            if progress_callback is not None:
                progress_callback(processed_entries, 0)

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