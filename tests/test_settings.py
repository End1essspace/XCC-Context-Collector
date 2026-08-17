from __future__ import annotations

from pathlib import Path

from xcc.config import MAX_OUTPUT_CHARS
from xcc.settings import (
    AppSettings,
    apply_interface_scale_environment,
    load_settings_result,
    qt_scale_factor_for_interface_scale,
    save_settings,
    validate_settings,
)

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
    
def test_load_settings_result_returns_defaults_when_file_missing(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"

    settings = load_settings_result(path).settings

    assert settings == AppSettings()


def test_save_and_load_settings_result_roundtrip(tmp_path: Path) -> None:
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
        confirm_safety_warnings=False,
        interface_scale="125",
    )

    save_settings(original, path)
    loaded = load_settings_result(path).settings

    assert loaded == original


def test_load_settings_result_falls_back_on_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{ invalid json", encoding="utf-8")

    settings = load_settings_result(path).settings

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
            "confirm_safety_warnings": "off",
        }
    )

    assert settings.start_with_windows is False
    assert settings.start_minimized_to_tray is False
    assert settings.close_to_tray is True
    assert settings.start_maximized is True
    assert settings.show_tray_notifications is True
    assert settings.confirm_safety_warnings is True


def test_validate_settings_accepts_disabled_safety_confirmation() -> None:
    settings = validate_settings({"confirm_safety_warnings": False})

    assert settings.confirm_safety_warnings is False


def test_safety_confirmation_defaults_to_enabled_for_older_configs() -> None:
    settings = validate_settings({"default_mode": "folder"})

    assert settings.confirm_safety_warnings is True


def test_validate_settings_accepts_interface_scale() -> None:
    settings = validate_settings({"interface_scale": "120"})

    assert settings.interface_scale == "120"


def test_validate_settings_falls_back_on_invalid_interface_scale() -> None:
    settings = validate_settings({"interface_scale": "175"})

    assert settings.interface_scale == "auto"


def test_interface_scale_maps_to_qt_global_factor() -> None:
    assert qt_scale_factor_for_interface_scale("auto") is None
    assert qt_scale_factor_for_interface_scale("90") == "0.90"
    assert qt_scale_factor_for_interface_scale("100") == "1.00"
    assert qt_scale_factor_for_interface_scale("110") == "1.10"
    assert qt_scale_factor_for_interface_scale("120") == "1.20"
    assert qt_scale_factor_for_interface_scale("125") == "1.25"
    assert qt_scale_factor_for_interface_scale("150") == "1.50"


def test_auto_interface_scale_leaves_qt_environment_untouched() -> None:
    environment = {"QT_SCALE_FACTOR": "1.75"}

    factor = apply_interface_scale_environment("auto", environment)

    assert factor is None
    assert environment["QT_SCALE_FACTOR"] == "1.75"


def test_explicit_interface_scale_sets_qt_environment() -> None:
    environment: dict[str, str] = {}

    factor = apply_interface_scale_environment("125", environment)

    assert factor == "1.25"
    assert environment["QT_SCALE_FACTOR"] == "1.25"
