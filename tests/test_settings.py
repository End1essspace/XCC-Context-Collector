from __future__ import annotations

from pathlib import Path

from src.xcc.config import MAX_OUTPUT_CHARS
from src.xcc.settings import AppSettings, load_settings, save_settings, validate_settings, load_settings_result

def test_load_settings_result_reports_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{ invalid json", encoding="utf-8")

    result = load_settings_result(path)

    assert result.settings == AppSettings()
    assert result.recovered_from_error is True
    assert "invalid JSON" in result.message


def test_load_settings_result_reports_invalid_format(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text('["not", "a", "dict"]', encoding="utf-8")

    result = load_settings_result(path)

    assert result.settings == AppSettings()
    assert result.recovered_from_error is True
    assert "format is invalid" in result.message
    
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
        start_with_windows=True,
        start_minimized_to_tray=True,
        close_to_tray=False,
        start_maximized=False,
        show_tray_notifications=False,
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


def test_validate_settings_accepts_project_tree_mode() -> None:
    settings = validate_settings({"default_mode": "tree"})

    assert settings.default_mode == "tree"


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

def test_validate_settings_falls_back_on_invalid_behavior_flags() -> None:
    settings = validate_settings(
        {
            "start_with_windows": "yes",
            "start_minimized_to_tray": 1,
            "close_to_tray": "no",
            "start_maximized": None,
            "show_tray_notifications": "true",
        }
    )

    assert settings.start_with_windows is False
    assert settings.start_minimized_to_tray is False
    assert settings.close_to_tray is True
    assert settings.start_maximized is True
    assert settings.show_tray_notifications is True