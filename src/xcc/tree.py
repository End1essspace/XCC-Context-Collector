from __future__ import annotations

from pathlib import Path


def build_project_tree(paths: list[Path], root: str | Path | None = None) -> str:
    if not paths:
        return ""

    display_paths = [_make_display_path(path, root) for path in paths]
    display_paths = sorted(display_paths, key=str.lower)

    lines = ["# Project Tree", ""]

    for path in display_paths:
        lines.append(path)

    return "\n".join(lines)


def _make_display_path(path: Path, root: str | Path | None = None) -> str:
    if root is None:
        return path.name

    root_path = Path(root)

    try:
        return path.resolve().relative_to(root_path.resolve()).as_posix()
    except ValueError:
        return path.name