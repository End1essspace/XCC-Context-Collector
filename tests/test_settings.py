from __future__ import annotations

from pathlib import Path

from src.xcc.config import MAX_OUTPUT_CHARS
from src.xcc.settings import AppSettings, load_settings, save_settings, validate_settings


def test_load_settings_returns_defaults_when_file_missing(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"

    settings = load_settings(path)

    assert settings == AppSettings()


def test_save_and_load_settings_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "config.json"

    original = AppSettings(
        default_mode="git",
        max_chars=50000,
        compact_mode=False,
        last_source="D:/projects/xcc",
    )

    save_settings(original, path)
    loaded = load_settings(path)

    assert loaded == original


def test_load_settings_falls_back_on_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{ invalid json", encoding="utf-8")

    settings = load_settings(path)

    assert settings == AppSettings()


def test_validate_settings_accepts_valid_values() -> None:
    settings = validate_settings(
        {
            "default_mode": "files",
            "max_chars": 999,
            "compact_mode": False,
            "last_source": "D:/tmp",
        }
    )

    assert settings.default_mode == "files"
    assert settings.max_chars == 999
    assert settings.compact_mode is False
    assert settings.last_source == "D:/tmp"


def test_validate_settings_falls_back_on_invalid_mode() -> None:
    settings = validate_settings({"default_mode": "bad"})

    assert settings.default_mode == "folder"


def test_validate_settings_falls_back_on_invalid_max_chars() -> None:
    settings = validate_settings({"max_chars": -10})

    assert settings.max_chars == MAX_OUTPUT_CHARS


def test_validate_settings_falls_back_on_invalid_compact_mode() -> None:
    settings = validate_settings({"compact_mode": "yes"})

    assert settings.compact_mode is True


def test_validate_settings_falls_back_on_invalid_last_source() -> None:
    settings = validate_settings({"last_source": 123})

    assert settings.last_source == ""