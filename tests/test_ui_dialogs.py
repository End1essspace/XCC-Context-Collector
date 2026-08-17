from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from xcc.gui import PastePathsDialog, SelectedFilesReviewDialog


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_paste_paths_dialog_exposes_success_validation_state(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    source = project_root / "src" / "module.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 1\n", encoding="utf-8")

    dialog = PastePathsDialog(
        "src/module.py",
        existing_paths=[],
        initial_root=project_root,
    )
    qapp.processEvents()

    assert dialog.objectName() == "PastePathsDialog"
    assert dialog._dialog_size_spec is not None
    assert dialog.minimumWidth() == dialog._dialog_size_spec.minimum_width
    assert dialog.minimumHeight() == dialog._dialog_size_spec.minimum_height
    assert dialog.width() <= dialog._dialog_size_spec.usable_width
    assert dialog.height() <= dialog._dialog_size_spec.usable_height
    assert (
        dialog.body_scroll.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert (
        dialog.body_scroll.verticalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    )
    assert (
        dialog.paths_input.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert dialog.summary_label.property("state") == "success"
    assert dialog.summary_label.text().startswith("Ready ·")
    assert dialog.add_button.isEnabled()
    assert dialog.add_button.text() == "Add 1 File"
    assert dialog.paths_input.accessibleName() == "Pasted file paths"

    dialog.close()


def test_paste_paths_dialog_marks_missing_root_as_warning(
    qapp: QApplication,
) -> None:
    dialog = PastePathsDialog(
        "src/module.py",
        existing_paths=[],
    )
    qapp.processEvents()

    assert dialog.summary_label.property("state") == "warning"
    assert "Project root required" in dialog.summary_label.text()
    assert not dialog.add_button.isEnabled()

    dialog.close()


def test_selected_files_review_preserves_transactional_actions(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    first = project_root / "src" / "first.py"
    second = project_root / "docs" / "guide.md"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_text("FIRST = True\n", encoding="utf-8")
    second.write_text("# Guide\n", encoding="utf-8")

    dialog = SelectedFilesReviewDialog(
        [first, second],
        project_root=project_root,
    )
    qapp.processEvents()

    assert dialog.objectName() == "SelectedFilesReviewDialog"
    assert dialog._dialog_size_spec is not None
    assert dialog.minimumWidth() == dialog._dialog_size_spec.minimum_width
    assert dialog.minimumHeight() == dialog._dialog_size_spec.minimum_height
    assert dialog.width() <= dialog._dialog_size_spec.usable_width
    assert dialog.height() <= dialog._dialog_size_spec.usable_height
    assert (
        dialog.body_scroll.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert (
        dialog.body_scroll.verticalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    )
    assert (
        dialog.files_list.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert dialog.count_label.text() == "2 files"
    assert dialog.root_value.property("scope") == "project"
    assert dialog.files_list.count() == 2
    assert not dialog.apply_button.isEnabled()
    assert not dialog.remove_button.isEnabled()

    dialog.files_list.item(0).setSelected(True)
    qapp.processEvents()
    assert dialog.remove_button.isEnabled()

    dialog._remove_selected()
    assert dialog.count_label.text() == "1 file"
    assert dialog.apply_button.isEnabled()
    assert len(dialog.selected_paths) == 1

    dialog.close()


def test_selected_files_review_marks_separate_repositories_as_mixed(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    first_repo = tmp_path / "first"
    second_repo = tmp_path / "second"
    (first_repo / ".git").mkdir(parents=True)
    (second_repo / ".git").mkdir(parents=True)
    first = first_repo / "src" / "first.py"
    second = second_repo / "src" / "second.py"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_text("FIRST = True\n", encoding="utf-8")
    second.write_text("SECOND = True\n", encoding="utf-8")

    dialog = SelectedFilesReviewDialog(
        [first, second],
        project_root=None,
    )
    qapp.processEvents()

    assert dialog.root_value.text() == "Mixed locations"
    assert dialog.root_value.property("scope") == "mixed"
    assert dialog.root_value.toolTip() == "Mixed locations"

    dialog.close()


def test_paste_paths_dialog_preserves_long_root_tooltip_and_accessible_summary(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    project_root = tmp_path
    for index in range(8):
        project_root = project_root / f"very-long-project-segment-{index}"
    source = project_root / "src" / "module.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 1\n", encoding="utf-8")

    dialog = PastePathsDialog(
        "src/module.py",
        existing_paths=[],
        initial_root=project_root,
    )
    qapp.processEvents()

    assert dialog.root_input.toolTip() == str(project_root)
    assert dialog.summary_label.accessibleDescription() == dialog.summary_label.text()
    assert dialog.summary_label.toolTip() == dialog.summary_label.text()
    assert dialog.add_button.isEnabled()

    dialog.close()


def test_selected_files_review_handles_large_selection_and_empty_state(
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    paths: list[Path] = []

    for index in range(101):
        path = project_root / "src" / f"module_{index:03d}.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"VALUE = {index}\n", encoding="utf-8")
        paths.append(path)

    dialog = SelectedFilesReviewDialog(
        paths,
        project_root=project_root,
    )
    qapp.processEvents()

    assert dialog.count_label.text() == "101 files"
    assert dialog.files_list.count() == 101
    assert (
        dialog.files_list.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert dialog.root_value.toolTip() == str(project_root)

    dialog._clear_all()
    qapp.processEvents()

    assert dialog.count_label.text() == "0 files"
    assert dialog.root_value.text() == "No files selected"
    assert dialog.root_value.property("scope") == "empty"
    assert not dialog.clear_button.isEnabled()
    assert dialog.apply_button.isEnabled()

    dialog.close()
