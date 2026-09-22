from __future__ import annotations

import json
import os
from collections.abc import MutableMapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import (
    DEFAULT_ATTACHMENT_HANDOFF_HOTKEY,
    DEFAULT_COLLECT_HOTKEY,
    DEFAULT_HOTKEY,
    MAX_OUTPUT_CHARS,
)
from .hotkeys import HotkeyValidationError, normalize_hotkey

VALID_MODES = {"files", "folder", "git", "tree"}

DEFAULT_MODE = "files"
DEFAULT_COMPACT_MODE = False
DEFAULT_LAST_SOURCE = ""

DEFAULT_START_WITH_WINDOWS = True
DEFAULT_START_MINIMIZED_TO_TRAY = True
DEFAULT_CLOSE_TO_TRAY = True
DEFAULT_START_MAXIMIZED = True
DEFAULT_SHOW_TRAY_NOTIFICATIONS = False
DEFAULT_CONFIRM_SAFETY_WARNINGS = False
DEFAULT_RESTORE_HOTKEY_ENABLED = True
DEFAULT_RESTORE_HOTKEY = DEFAULT_HOTKEY
DEFAULT_COLLECT_HOTKEY_ENABLED = False
DEFAULT_ATTACHMENT_HANDOFF_HOTKEY_ENABLED = False

DEFAULT_INTERFACE_SCALE = "110"
VALID_INTERFACE_SCALES = (
    "auto",
    "90",
    "100",
    "110",
    "120",
    "125",
    "150",
)
INTERFACE_SCALE_FACTORS = {
    "90": "0.90",
    "100": "1.00",
    "110": "1.10",
    "120": "1.20",
    "125": "1.25",
    "150": "1.50",
}


@dataclass(slots=True)
class SettingsLoadResult:
    settings: AppSettings
    recovered_from_error: bool = False
    message: str = ""
    first_run: bool = False

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
    confirm_safety_warnings: bool = DEFAULT_CONFIRM_SAFETY_WARNINGS
    restore_hotkey_enabled: bool = DEFAULT_RESTORE_HOTKEY_ENABLED
    restore_hotkey: str = DEFAULT_RESTORE_HOTKEY
    collect_hotkey_enabled: bool = DEFAULT_COLLECT_HOTKEY_ENABLED
    collect_hotkey: str = DEFAULT_COLLECT_HOTKEY
    attachment_handoff_hotkey_enabled: bool = DEFAULT_ATTACHMENT_HANDOFF_HOTKEY_ENABLED
    attachment_handoff_hotkey: str = DEFAULT_ATTACHMENT_HANDOFF_HOTKEY
    interface_scale: str = DEFAULT_INTERFACE_SCALE


def default_settings_path() -> Path:
    return Path.home() / ".xcc" / "config.json"

def load_settings_result(path: str | Path | None = None) -> SettingsLoadResult:
    settings_path = Path(path) if path is not None else default_settings_path()

    if not settings_path.exists():
        return SettingsLoadResult(AppSettings(), first_run=True)

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
    confirm_safety_warnings = _read_bool(
        raw_data,
        "confirm_safety_warnings",
        DEFAULT_CONFIRM_SAFETY_WARNINGS,
    )

    restore_hotkey_enabled = _read_bool(
        raw_data,
        "restore_hotkey_enabled",
        DEFAULT_RESTORE_HOTKEY_ENABLED,
    )
    restore_hotkey = _read_hotkey(
        raw_data,
        "restore_hotkey",
        DEFAULT_RESTORE_HOTKEY,
    )
    collect_hotkey_enabled = _read_bool(
        raw_data,
        "collect_hotkey_enabled",
        DEFAULT_COLLECT_HOTKEY_ENABLED,
    )
    collect_hotkey = _read_hotkey(
        raw_data,
        "collect_hotkey",
        DEFAULT_COLLECT_HOTKEY,
    )
    attachment_handoff_hotkey_enabled = _read_bool(
        raw_data,
        "attachment_handoff_hotkey_enabled",
        DEFAULT_ATTACHMENT_HANDOFF_HOTKEY_ENABLED,
    )
    attachment_handoff_hotkey = _read_hotkey(
        raw_data,
        "attachment_handoff_hotkey",
        DEFAULT_ATTACHMENT_HANDOFF_HOTKEY,
    )

    # Restore is the primary recovery shortcut. Optional bindings are disabled
    # on persisted conflicts instead of making startup hotkey registration fail.
    occupied: set[str] = set()
    if restore_hotkey_enabled:
        occupied.add(restore_hotkey)
    if collect_hotkey_enabled:
        if collect_hotkey in occupied:
            collect_hotkey_enabled = False
        else:
            occupied.add(collect_hotkey)
    if attachment_handoff_hotkey_enabled:
        if attachment_handoff_hotkey in occupied:
            attachment_handoff_hotkey_enabled = False
        else:
            occupied.add(attachment_handoff_hotkey)

    interface_scale = raw_data.get(
        "interface_scale",
        DEFAULT_INTERFACE_SCALE,
    )
    if interface_scale not in VALID_INTERFACE_SCALES:
        interface_scale = DEFAULT_INTERFACE_SCALE

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
        confirm_safety_warnings=confirm_safety_warnings,
        restore_hotkey_enabled=restore_hotkey_enabled,
        restore_hotkey=restore_hotkey,
        collect_hotkey_enabled=collect_hotkey_enabled,
        collect_hotkey=collect_hotkey,
        attachment_handoff_hotkey_enabled=attachment_handoff_hotkey_enabled,
        attachment_handoff_hotkey=attachment_handoff_hotkey,
        interface_scale=interface_scale,
    )



def qt_scale_factor_for_interface_scale(interface_scale: str) -> str | None:
    """Translate one persisted XCC scale choice to Qt's global multiplier."""

    return INTERFACE_SCALE_FACTORS.get(interface_scale)


def apply_interface_scale_environment(
    interface_scale: str,
    environment: MutableMapping[str, str] | None = None,
) -> str | None:
    """Apply a persisted XCC scale override before QApplication is created.

    Auto deliberately leaves the process environment unchanged so Qt can
    follow the platform-native display scaling without an XCC override.
    """

    target = os.environ if environment is None else environment
    factor = qt_scale_factor_for_interface_scale(interface_scale)
    if factor is not None:
        target["QT_SCALE_FACTOR"] = factor
    return factor

def _read_bool(raw_data: dict[str, Any], key: str, default: bool) -> bool:
    value = raw_data.get(key, default)

    if not isinstance(value, bool):
        return default

    return value


def _read_hotkey(raw_data: dict[str, Any], key: str, default: str) -> str:
    value = raw_data.get(key, default)
    if not isinstance(value, str):
        return default
    try:
        return normalize_hotkey(value)
    except HotkeyValidationError:
        return default
