from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from xcc.clipboard import copy_files_to_clipboard


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(autouse=True)
def clear_qt_clipboard(
    qapp: QApplication,
    tmp_path: Path,
):
    """Release clipboard file URLs before pytest removes temporary files."""

    clipboard = qapp.clipboard()
    clipboard.clear()
    qapp.processEvents()

    try:
        yield
    finally:
        clipboard.clear()
        qapp.processEvents()


def test_copy_files_to_clipboard_publishes_local_file_urls_in_order(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.bin"
    second = tmp_path / "second.png"
    first.write_bytes(b"1")
    second.write_bytes(b"22")

    copied = copy_files_to_clipboard([first, second])
    mime = qapp.clipboard().mimeData()

    assert copied == (first.resolve(), second.resolve())
    assert mime.hasUrls()
    assert [Path(url.toLocalFile()).resolve() for url in mime.urls()] == list(copied)


def test_copy_files_to_clipboard_rejects_empty_and_stale_selection(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="empty"):
        copy_files_to_clipboard([])

    missing = tmp_path / "missing.bin"
    with pytest.raises(FileNotFoundError, match="no longer exists"):
        copy_files_to_clipboard([missing])


def test_copy_files_to_clipboard_rejects_directory(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    folder = tmp_path / "folder"
    folder.mkdir()
    with pytest.raises(ValueError, match="regular file"):
        copy_files_to_clipboard([folder])