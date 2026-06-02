from __future__ import annotations

import subprocess
from pathlib import Path
from .config import ALLOWED_EXTENSIONS, EXCLUDED_DIRS
from .scanner import _is_inside_excluded_dir

def is_git_repository(path: str | Path) -> bool:
    path = Path(path)

    return (path / ".git").exists()


def get_changed_files(
    path: str | Path,
    *,
    allowed_extensions: set[str] | None = None,
    excluded_dirs: set[str] | None = None,
) -> list[Path]:
    repo_path = Path(path)
    
    allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS
    excluded_dirs = excluded_dirs or EXCLUDED_DIRS
    
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return []

    files: list[Path] = []

    for line in result.stdout.splitlines():
        if not line.strip():
            continue

        relative_path = line[3:].strip()

        if not relative_path:
            continue

        full_path = repo_path / relative_path

        if not full_path.exists() or not full_path.is_file():
            continue

        if _is_inside_excluded_dir(full_path, repo_path, excluded_dirs):
            continue

        if full_path.suffix.lower() not in allowed_extensions:
            continue

        files.append(full_path)

    return files

def get_git_diff(path: str | Path) -> str:
    repo_path = Path(path)

    result = subprocess.run(
        ["git", "diff", "--", "."],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()