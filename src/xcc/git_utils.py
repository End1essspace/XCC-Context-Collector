from __future__ import annotations

from pathlib import Path


def is_git_repository(path: str | Path) -> bool:
    path = Path(path)

    return (path / ".git").exists()