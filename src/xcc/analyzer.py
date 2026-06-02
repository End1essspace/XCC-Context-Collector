from __future__ import annotations

from .models import FileContent


def estimate_tokens(files: list[FileContent]) -> int:
    chars = sum(file.char_count for file in files)

    return chars // 4