from __future__ import annotations

from pathlib import Path

from src.xcc.config import (
    is_allowed_context_file,
    qt_context_file_filter,
    tkinter_context_filetypes,
)


def test_allows_file_by_extension() -> None:
    assert is_allowed_context_file(Path("app.tsx")) is True
    assert is_allowed_context_file(Path("main.py")) is True


def test_allows_file_by_name() -> None:
    assert is_allowed_context_file(Path("Dockerfile")) is True
    assert is_allowed_context_file(Path(".env.example")) is True


def test_rejects_sensitive_env_file() -> None:
    assert is_allowed_context_file(Path(".env")) is False


def test_qt_filter_contains_new_extensions() -> None:
    file_filter = qt_context_file_filter()

    assert "*.tsx" in file_filter
    assert "*.rs" in file_filter
    assert "Dockerfile" in file_filter
    assert ".env.example" in file_filter


def test_tkinter_filter_contains_new_extensions() -> None:
    filetypes = tkinter_context_filetypes()
    patterns = filetypes[0][1]

    assert "*.tsx" in patterns
    assert "*.rs" in patterns
    assert "Dockerfile" in patterns
    assert ".env.example" in patterns