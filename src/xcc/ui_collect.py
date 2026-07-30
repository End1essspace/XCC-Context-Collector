from __future__ import annotations

from dataclasses import dataclass


COLLECT_PAGE_TITLE = "Collect Context"
COLLECT_PAGE_SUBTITLE = (
    "Configure what to collect and generate an AI-ready context snapshot."
)
COMPACT_MODE_HELPER = (
    "Reduce XCC-generated structural whitespace. "
    "Source file contents remain unchanged."
)


@dataclass(frozen=True, slots=True)
class CollectModePresentation:
    """User-facing copy and actions for one collection mode."""

    action_label: str
    source_placeholder: str
    source_helper: str
    dialog_title: str
    paste_paths_visible: bool = False


_MODE_PRESENTATIONS: dict[str, CollectModePresentation] = {
    "files": CollectModePresentation(
        action_label="Select Files",
        source_placeholder="No files selected — choose files or paste paths",
        source_helper=(
            "Choose files manually or paste paths returned by an AI assistant."
        ),
        dialog_title="Select context files",
        paste_paths_visible=True,
    ),
    "folder": CollectModePresentation(
        action_label="Select Folder",
        source_placeholder="No folder selected",
        source_helper=(
            "Collect supported files while respecting project ignore rules."
        ),
        dialog_title="Select project folder",
    ),
    "git": CollectModePresentation(
        action_label="Select Repository",
        source_placeholder="No repository selected",
        source_helper=(
            "Collect supported changed files with staged and unstaged Git diffs."
        ),
        dialog_title="Select Git repository",
    ),
    "tree": CollectModePresentation(
        action_label="Select Folder",
        source_placeholder="No folder selected",
        source_helper="Collect project structure without file contents.",
        dialog_title="Select project folder",
    ),
}


def collect_mode_presentation(mode: str) -> CollectModePresentation:
    try:
        return _MODE_PRESENTATIONS[mode]
    except KeyError as exc:
        raise ValueError(f"Unsupported collection mode: {mode}") from exc


def selected_files_source_summary(
    count: int,
    *,
    project_name: str | None = None,
    mixed_locations: bool = False,
) -> str:
    if count < 0:
        raise ValueError("count must not be negative")

    noun = "file" if count == 1 else "files"
    selection = f"{count} {noun} selected"

    if mixed_locations or not project_name:
        return f"{selection} · Mixed locations"

    return f"{project_name} · {selection}"
