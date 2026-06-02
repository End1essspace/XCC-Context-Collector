from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import ALLOWED_EXTENSIONS, EXCLUDED_DIRS


def scan_project_files(
    root: str | Path,
    *,
    allowed_extensions: set[str] | None = None,
    excluded_dirs: set[str] | None = None,
) -> list[Path]:
    root_path = Path(root)

    if not root_path.exists():
        raise FileNotFoundError(f"Project folder not found: {root_path}")

    if not root_path.is_dir():
        raise NotADirectoryError(f"Not a folder: {root_path}")

    allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS
    excluded_dirs = excluded_dirs or EXCLUDED_DIRS

    files: list[Path] = []

    for path in root_path.rglob("*"):
        if not path.is_file():
            continue

        if _is_inside_excluded_dir(path, root_path, excluded_dirs):
            continue

        if path.suffix.lower() not in allowed_extensions:
            continue

        files.append(path)

    return sorted(files, key=lambda item: item.as_posix().lower())


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