from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class FileContent:
    path: Path
    content: str
    line_count: int
    char_count: int


@dataclass(slots=True)
class CollectionStats:
    files: int
    lines: int
    chars: int


@dataclass(slots=True)
class CollectionResult:
    text: str
    stats: CollectionStats
    errors: list[str]
    was_truncated: bool = False