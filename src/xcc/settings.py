from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import MAX_OUTPUT_CHARS

VALID_MODES = {"files", "folder", "git"}
DEFAULT_MODE = "folder"
DEFAULT_COMPACT_MODE = True
DEFAULT_LAST_SOURCE = ""


@dataclass(slots=True)
class AppSettings:
    default_mode: str = DEFAULT_MODE
    max_chars: int = MAX_OUTPUT_CHARS
    compact_mode: bool = DEFAULT_COMPACT_MODE
    last_source: str = DEFAULT_LAST_SOURCE


def default_settings_path() -> Path:
    return Path.home() / ".xcc" / "config.json"


def load_settings(path: str | Path | None = None) -> AppSettings:
    settings_path = Path(path) if path is not None else default_settings_path()

    if not settings_path.exists():
        return AppSettings()

    try:
        raw_data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppSettings()

    if not isinstance(raw_data, dict):
        return AppSettings()

    return validate_settings(raw_data)


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

    compact_mode = raw_data.get("compact_mode", DEFAULT_COMPACT_MODE)
    if not isinstance(compact_mode, bool):
        compact_mode = DEFAULT_COMPACT_MODE

    last_source = raw_data.get("last_source", DEFAULT_LAST_SOURCE)
    if not isinstance(last_source, str):
        last_source = DEFAULT_LAST_SOURCE

    return AppSettings(
        default_mode=default_mode,
        max_chars=max_chars,
        compact_mode=compact_mode,
        last_source=last_source,
    )