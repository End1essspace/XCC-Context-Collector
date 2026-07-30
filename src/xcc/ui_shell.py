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
