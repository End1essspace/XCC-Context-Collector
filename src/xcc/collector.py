from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .models import FileContent


ALLOWED_EXTENSIONS = {".py"}
DEFAULT_ENCODINGS = ("utf-8", "utf-8-sig", "cp1251")
DEFAULT_MAX_FILE_SIZE_BYTES = 512 * 1024


def collect_files(
    paths: Iterable[str | Path],
    *,
    allowed_extensions: set[str] | None = None,
    encodings: tuple[str, ...] = DEFAULT_ENCODINGS,
    max_file_size_bytes: int = DEFAULT_MAX_FILE_SIZE_BYTES,
) -> tuple[list[FileContent], list[str]]:
    allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS

    files: list[FileContent] = []
    errors: list[str] = []

    for raw_path in paths:
        path = Path(raw_path)

        if not path.exists():
            errors.append(f"File not found: {path}")
            continue

        if not path.is_file():
            errors.append(f"Not a file: {path}")
            continue

        if path.suffix.lower() not in allowed_extensions:
            errors.append(f"Skipped unsupported file type: {path}")
            continue

        try:
            file_size = path.stat().st_size
        except OSError as exc:
            errors.append(f"Cannot read file size: {path} ({exc})")
            continue

        if file_size > max_file_size_bytes:
            errors.append(
                f"Skipped large file: {path} "
                f"({file_size} bytes > {max_file_size_bytes} bytes)"
            )
            continue

        content = _read_text_with_fallback(path, encodings)

        if content is None:
            errors.append(f"Cannot decode file: {path}")
            continue

        files.append(
            FileContent(
                path=path,
                content=content,
                line_count=count_lines(content),
                char_count=len(content),
            )
        )

    return files, errors


def _read_text_with_fallback(path: Path, encodings: tuple[str, ...]) -> str | None:
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None

    return None


def count_lines(text: str) -> int:
    if not text:
        return 0

    return text.count("\n") + 1