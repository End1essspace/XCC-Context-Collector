
from __future__ import annotations

from enum import Enum


class RuntimeState(Enum):
    """Small, fixed vocabulary for the persistent header runtime capsule."""

    READY = ("Ready", "success")
    WORKING = ("Working", "neutral")
    CANCELLING = ("Cancelling", "warning")
    COPIED = ("Copied", "success")
    WARNINGS = ("Warnings", "warning")
    FAILED = ("Failed", "error")
    CANCELLED = ("Cancelled", "neutral")

    def __init__(self, label: str, semantic_state: str) -> None:
        self.label = label
        self.semantic_state = semantic_state


def format_hotkey_for_display(hotkey: str) -> str:
    """Return a stable product-facing label.

    The registration value remains unchanged and can stay normalized for the
    native hotkey parser.
    """

    aliases = {
        "ctrl": "Ctrl",
        "control": "Ctrl",
        "alt": "Alt",
        "shift": "Shift",
        "win": "Win",
        "windows": "Win",
        "meta": "Win",
    }
    parts = [part.strip() for part in hotkey.split("+") if part.strip()]
    rendered: list[str] = []

    for part in parts:
        normalized = part.casefold()
        if normalized in aliases:
            rendered.append(aliases[normalized])
        elif len(part) == 1:
            rendered.append(part.upper())
        elif normalized.startswith("f") and normalized[1:].isdigit():
            rendered.append(normalized.upper())
        else:
            rendered.append(part)

    return "+".join(rendered)


def default_footer_message(
    *,
    mode: str,
    selected_count: int = 0,
    has_source: bool = False,
) -> str:
    """Return useful idle guidance without duplicating the header's ``Ready``."""

    if mode == "files":
        if selected_count > 0:
            noun = "file" if selected_count == 1 else "files"
            return f"{selected_count} {noun} selected"

        return "Ready · Choose files or paste paths to begin"

    if has_source:
        return "Ready · Source selected"

    return "Ready · Select a source to begin"
