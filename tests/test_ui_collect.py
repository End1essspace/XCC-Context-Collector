from __future__ import annotations

import pytest

from xcc.ui_collect import (
    COLLECT_PAGE_SUBTITLE,
    COLLECT_PAGE_TITLE,
    COMPACT_MODE_HELPER,
    collect_mode_presentation,
    selected_files_source_summary,
)


def test_collect_page_copy_matches_frozen_contract() -> None:
    assert COLLECT_PAGE_TITLE == "Collect Context"
    assert COLLECT_PAGE_SUBTITLE == (
        "Configure what to collect and generate an AI-ready context snapshot."
    )
    assert COMPACT_MODE_HELPER == (
        "Reduce XCC-generated structural whitespace. "
        "Source file contents remain unchanged."
    )


def test_mode_presentations_use_explicit_source_actions() -> None:
    files = collect_mode_presentation("files")
    folder = collect_mode_presentation("folder")
    git = collect_mode_presentation("git")
    tree = collect_mode_presentation("tree")

    assert files.action_label == "Select Files"
    assert files.paste_paths_visible is True
    assert files.source_helper == (
        "Choose files manually or paste paths returned by an AI assistant."
    )

    assert folder.action_label == "Select Folder"
    assert folder.paste_paths_visible is False
    assert folder.source_helper == (
        "Collect supported files while respecting project ignore rules."
    )

    assert git.action_label == "Select Repository"
    assert git.paste_paths_visible is False
    assert "staged and unstaged Git diffs" in git.source_helper

    assert tree.action_label == "Select Folder"
    assert tree.paste_paths_visible is False
    assert tree.source_helper == (
        "Collect project structure without file contents."
    )

    assert "Select Source" not in {
        files.action_label,
        folder.action_label,
        git.action_label,
        tree.action_label,
    }


def test_selected_files_source_summary_is_stable_and_grammatical() -> None:
    assert selected_files_source_summary(
        1,
        project_name="XCC",
    ) == "XCC · 1 file selected"
    assert selected_files_source_summary(
        14,
        project_name="XCC",
    ) == "XCC · 14 files selected"
    assert selected_files_source_summary(
        14,
        mixed_locations=True,
    ) == "14 files selected · Mixed locations"


def test_collect_mode_policy_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="Unsupported collection mode"):
        collect_mode_presentation("unknown")

    with pytest.raises(ValueError, match="count must not be negative"):
        selected_files_source_summary(-1)
