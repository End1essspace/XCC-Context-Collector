from __future__ import annotations

from pathlib import Path

from .tree import build_project_tree
from .models import CollectionResult, CollectionStats, FileContent
from .optimizer import compact_text
from .budget import apply_char_budget
from .config import MAX_OUTPUT_CHARS
from .file_size import sort_files_by_size
from . import __version__

def format_collection(
    files: list[FileContent],
    errors: list[str] | None = None,
    *,
    project_root: str | Path | None = None,
    compact: bool = True,
    max_output_chars: int | None = MAX_OUTPUT_CHARS,
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
        f"XCC Version: {__version__}",
        "Mode: Compact" if compact else "Mode: Full",
        f"Max Output Characters: {max_output_chars if max_output_chars is not None else 'Unlimited'}",
        "",
        f"Files: {stats.files}",
        f"Lines: {stats.lines}",
        f"Characters: {stats.chars}",
        "",
    ]

    tree = build_project_tree([file.path for file in files], project_root)

    if tree:
        parts.extend(
            [
                tree,
                "",
                "# Files",
                "",
            ]
        )
        
    files = sort_files_by_size(files)

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
    
    if compact:
        text = compact_text(text)
    
    text = apply_char_budget(text, max_output_chars)
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