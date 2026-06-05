from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import ALLOWED_EXTENSIONS, ALLOWED_FILENAMES, EXCLUDED_DIRS


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

        if not _is_allowed_context_file(path, allowed_extensions):
            continue

        files.append(path)

    return sorted(files, key=_file_priority_key)


def _is_allowed_context_file(
    path: Path,
    allowed_extensions: set[str],
    allowed_filenames: set[str] = ALLOWED_FILENAMES,
) -> bool:
    return (
        path.suffix.lower() in allowed_extensions
        or path.name in allowed_filenames
    )

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


def _file_priority_key(path: Path) -> tuple[int, str]:
    name = path.name.lower()
    suffix = path.suffix.lower()
    path_text = path.as_posix().lower()

    if name in {"readme.md", "pyproject.toml", "requirements.txt"}:
        priority = 0
    elif name in {"main.py", "run.py", "__init__.py"}:
        priority = 1
    elif "/src/" in path_text or "\\src\\" in path_text:
        priority = 2
    elif "/tests/" in path_text or "\\tests\\" in path_text:
        priority = 4
    elif suffix in {".md", ".txt"}:
        priority = 5
    else:
        priority = 3

    return priority, path_text