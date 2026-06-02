from __future__ import annotations

from pathlib import Path

from .models import CollectionResult, CollectionStats, FileContent


def format_collection(
    files: list[FileContent],
    errors: list[str] | None = None,
    *,
    project_root: str | Path | None = None,
) -> CollectionResult:
    errors = errors or []

    stats = CollectionStats(
        files=len(files),
        lines=sum(file.line_count for file in files),
        chars=sum(file.char_count for file in files),
    )

    parts: list[str] = [
        "# XCC Context",
        "",
        f"Files: {stats.files}",
        f"Lines: {stats.lines}",
        f"Characters: {stats.chars}",
        "",
    ]

    for file in files:
        parts.append(format_file(file, project_root=project_root))

    if errors:
        parts.extend(
            [
                "",
                "# XCC Errors",
                "",
                *[f"- {error}" for error in errors],
            ]
        )

    text = "\n".join(parts).rstrip() + "\n"

    return CollectionResult(
        text=text,
        stats=stats,
        errors=errors,
    )


def format_file(
    file: FileContent,
    *,
    project_root: str | Path | None = None,
) -> str:
    display_path = make_display_path(file.path, project_root)

    return (
        f"===== file: {display_path} =====\n\n"
        f"{file.content.rstrip()}\n"
    )


def make_display_path(path: Path, project_root: str | Path | None = None) -> str:
    if project_root is None:
        return path.name

    root = Path(project_root)

    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name