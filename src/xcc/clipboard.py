from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pyperclip

from .attachment_importer import revalidate_attachment_files


def copy_to_clipboard(text: str) -> None:
    if not text:
        raise ValueError("Cannot copy empty text to clipboard")

    pyperclip.copy(text)


def copy_files_to_clipboard(paths: Sequence[str | Path]) -> tuple[Path, ...]:
    """Place existing local files on the Qt/Windows clipboard as file objects.

    Qt publishes local-file URLs and maps them to the native Windows clipboard
    formats supported by the platform plugin (including Explorer-style file
    transfer where available). Source bytes are never loaded into XCC memory.
    Windows validation confirms this backend publishes the complete FileDrop
    selection to Explorer; target applications may still impose their own paste
    limitations.
    """

    if not paths:
        raise ValueError("Cannot copy an empty attachment selection")

    # Keep the legacy text-clipboard helper importable without initializing or
    # importing Qt. File-object transfer is a GUI-only operation and resolves
    # its Qt dependency only when invoked.
    from PySide6.QtCore import QMimeData, QThread, QUrl
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        raise RuntimeError("A QApplication instance is required for file clipboard transfer")
    if QThread.currentThread() is not app.thread():
        raise RuntimeError("File clipboard transfer must run on the GUI thread")

    validated = revalidate_attachment_files(paths)
    resolved_paths = tuple(item.path for item in validated)

    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile(str(path)) for path in resolved_paths])
    app.clipboard().setMimeData(mime_data)
    return resolved_paths
