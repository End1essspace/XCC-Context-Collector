from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import MAX_OUTPUT_CHARS

VALID_MODES = {"files", "folder", "git", "tree"}

DEFAULT_MODE = "folder"
DEFAULT_COMPACT_MODE = True
DEFAULT_LAST_SOURCE = ""

DEFAULT_START_WITH_WINDOWS = False
DEFAULT_START_MINIMIZED_TO_TRAY = False
DEFAULT_CLOSE_TO_TRAY = True
DEFAULT_START_MAXIMIZED = True
DEFAULT_SHOW_TRAY_NOTIFICATIONS = True


@dataclass(slots=True)
class SettingsLoadResult:
    settings: AppSettings
    recovered_from_error: bool = False
    message: str = ""

@dataclass(slots=True)
class AppSettings:
    default_mode: str = DEFAULT_MODE
    max_chars: int = MAX_OUTPUT_CHARS
    compact_mode: bool = DEFAULT_COMPACT_MODE
    last_source: str = DEFAULT_LAST_SOURCE

    start_with_windows: bool = DEFAULT_START_WITH_WINDOWS
    start_minimized_to_tray: bool = DEFAULT_START_MINIMIZED_TO_TRAY
    close_to_tray: bool = DEFAULT_CLOSE_TO_TRAY
    start_maximized: bool = DEFAULT_START_MAXIMIZED
    show_tray_notifications: bool = DEFAULT_SHOW_TRAY_NOTIFICATIONS


def default_settings_path() -> Path:
    return Path.home() / ".xcc" / "config.json"

def load_settings_result(path: str | Path | None = None) -> SettingsLoadResult:
    settings_path = Path(path) if path is not None else default_settings_path()

    if not settings_path.exists():
        return SettingsLoadResult(AppSettings())

    try:
        raw_data = json.loads(settings_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return SettingsLoadResult(
            AppSettings(),
            recovered_from_error=True,
            message=f"Could not read config file: {exc}",
        )
    except json.JSONDecodeError:
        return SettingsLoadResult(
            AppSettings(),
            recovered_from_error=True,
            message="Config file is invalid JSON. Defaults were loaded.",
        )

    if not isinstance(raw_data, dict):
        return SettingsLoadResult(
            AppSettings(),
            recovered_from_error=True,
            message="Config file format is invalid. Defaults were loaded.",
        )

    return SettingsLoadResult(validate_settings(raw_data))

def load_settings(path: str | Path | None = None) -> AppSettings:
    return load_settings_result(path).settings


def save_settings(settings: AppSettings, path: str | Path | None = None) -> None:
    settings_path = Path(path) if path is not None else default_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    settings_path.write_text(
        json.dumps(asdict(settings), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def validate_settings(raw_data: dict[str, Any]) -> AppSettings:
    default_mode = raw_data.get("default_mode", DEFAULT_MODE)
    if default_mode not in VALID_MODES:
        default_mode = DEFAULT_MODE

    max_chars = raw_data.get("max_chars", MAX_OUTPUT_CHARS)
    if not isinstance(max_chars, int) or max_chars <= 0:
        max_chars = MAX_OUTPUT_CHARS

    compact_mode = _read_bool(
        raw_data,
        "compact_mode",
        DEFAULT_COMPACT_MODE,
    )

    last_source = raw_data.get("last_source", DEFAULT_LAST_SOURCE)
    if not isinstance(last_source, str):
        last_source = DEFAULT_LAST_SOURCE

    start_with_windows = _read_bool(
        raw_data,
        "start_with_windows",
        DEFAULT_START_WITH_WINDOWS,
    )
    start_minimized_to_tray = _read_bool(
        raw_data,
        "start_minimized_to_tray",
        DEFAULT_START_MINIMIZED_TO_TRAY,
    )
    close_to_tray = _read_bool(
        raw_data,
        "close_to_tray",
        DEFAULT_CLOSE_TO_TRAY,
    )
    start_maximized = _read_bool(
        raw_data,
        "start_maximized",
        DEFAULT_START_MAXIMIZED,
    )
    show_tray_notifications = _read_bool(
        raw_data,
        "show_tray_notifications",
        DEFAULT_SHOW_TRAY_NOTIFICATIONS,
    )

    return AppSettings(
        default_mode=default_mode,
        max_chars=max_chars,
        compact_mode=compact_mode,
        last_source=last_source,
        start_with_windows=start_with_windows,
        start_minimized_to_tray=start_minimized_to_tray,
        close_to_tray=close_to_tray,
        start_maximized=start_maximized,
        show_tray_notifications=show_tray_notifications,
    )


def _read_bool(raw_data: dict[str, Any], key: str, default: bool) -> bool:
    value = raw_data.get(key, default)

    if not isinstance(value, bool):
        return default

    return value