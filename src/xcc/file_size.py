from __future__ import annotations

from .models import FileContent


def sort_files_by_size(files: list[FileContent]) -> list[FileContent]:
    return sorted(
        files,
        key=lambda file: file.char_count,
    )