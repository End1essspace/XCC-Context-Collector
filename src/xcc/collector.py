from __future__ import annotations

from pathlib import Path
from collections.abc import Callable, Iterable

from .cancellation import CollectionCancelled
from .models import FileContent
from .config import (
    ALLOWED_EXTENSIONS,
    ENCODINGS,
    MAX_FILE_SIZE_BYTES,
    is_allowed_context_file,
)


def collect_files(
    paths: Iterable[str | Path],
    *,
    allowed_extensions: set[str] | None = None,
    encodings: tuple[str, ...] = ENCODINGS,
    max_file_size_bytes: int = MAX_FILE_SIZE_BYTES,
    progress_callback: Callable[[int, int], None] | None = None,
    cancel_check: Callable[[], bool] | None = None,
) -> tuple[list[FileContent], list[str]]:
    allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS

    path_list = list(paths)
    files: list[FileContent] = []
    errors: list[str] = []
    total = len(path_list)

    for index, raw_path in enumerate(path_list, start=1):
        if cancel_check is not None and cancel_check():
            raise CollectionCancelled("Collection cancelled.")
        path = Path(raw_path)

        if not path.exists():
            errors.append(f"File not found: {path}")
            if progress_callback is not None:
                progress_callback(index, total)
            continue

        if not path.is_file():
            errors.append(f"Not a file: {path}")
            if progress_callback is not None:
                progress_callback(index, total)
            continue

        if not is_allowed_context_file(path, allowed_extensions=allowed_extensions):
            errors.append(f"Skipped unsupported file type: {path}")
            if progress_callback is not None:
                progress_callback(index, total)
            continue

        try:
            file_size = path.stat().st_size
        except OSError as exc:
            errors.append(f"Cannot read file size: {path} ({exc})")
            if progress_callback is not None:
                progress_callback(index, total)
            continue

        if file_size > max_file_size_bytes:
            files.append(
                FileContent(
                    path=path,
                    content=(
                        "# XCC Large File Summary\n\n"
                        f"Original file size: {file_size} bytes\n"
                        f"Limit: {max_file_size_bytes} bytes\n"
                        "Full content was not included to reduce AI context size.\n"
                    ),
                    line_count=0,
                    char_count=0,
                    is_summary=True,
                )
            )
            errors.append(
                f"Summarized large file: {path} "
                f"({file_size} bytes > {max_file_size_bytes} bytes)"
            )
            if progress_callback is not None:
                progress_callback(index, total)
            continue

        content = _read_text_with_fallback(path, encodings)

        if content is None:
            errors.append(f"Cannot decode file: {path}")
            if progress_callback is not None:
                progress_callback(index, total)
            continue

        files.append(
            FileContent(
                path=path,
                content=content,
                line_count=count_lines(content),
                char_count=len(content),
            )
        )

        if progress_callback is not None:
            progress_callback(index, total)

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