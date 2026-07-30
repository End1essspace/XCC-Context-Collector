from __future__ import annotations

from xcc.ui_shell import RuntimeState, default_footer_message


def test_runtime_state_vocabulary_is_fixed() -> None:
    assert [state.label for state in RuntimeState] == [
        "Ready",
        "Working",
        "Cancelling",
        "Copied",
        "Warnings",
        "Failed",
        "Cancelled",
    ]

    assert RuntimeState.READY.semantic_state == "success"
    assert RuntimeState.WARNINGS.semantic_state == "warning"
    assert RuntimeState.FAILED.semantic_state == "error"


def test_default_footer_guidance_avoids_duplicate_ready_only_message() -> None:
    assert default_footer_message(mode="files") == (
        "Ready · Choose files or paste paths to begin"
    )
    assert default_footer_message(
        mode="files",
        selected_count=1,
    ) == "1 file selected"
    assert default_footer_message(
        mode="files",
        selected_count=14,
    ) == "14 files selected"
    assert default_footer_message(
        mode="folder",
        has_source=False,
    ) == "Ready · Select a source to begin"
    assert default_footer_message(
        mode="git",
        has_source=True,
    ) == "Ready · Source selected"
