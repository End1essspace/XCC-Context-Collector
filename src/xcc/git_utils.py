from __future__ import annotations

import subprocess
from pathlib import Path


def is_git_repository(path: str | Path) -> bool:
    path = Path(path)

    return (path / ".git").exists()


def get_changed_files(path: str | Path) -> list[Path]:
    repo_path = Path(path)

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

        files.append(repo_path / relative_path)

    return files