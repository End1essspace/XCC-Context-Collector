
from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QDialog, QHeaderView, QLineEdit

import xcc.gui as gui_module
from xcc.attachment_importer import AttachmentFile
from xcc.gui import (
    ATTACHMENT_SIZE_COLUMN_WIDTH,
    AttachmentSelectionDelegate,
    XccMainWindow,
)
from xcc.settings import AppSettings, SettingsLoadResult


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def window(qapp: QApplication, monkeypatch: pytest.MonkeyPatch) -> XccMainWindow:
    monkeypatch.setattr(
        gui_module,
        "load_settings_result",
        lambda: SettingsLoadResult(
            AppSettings(
                start_maximized=False,
                close_to_tray=False,
                show_tray_notifications=False,
            ),
            first_run=False,
        ),
    )
    monkeypatch.setattr(gui_module, "save_settings", lambda settings: None)
    monkeypatch.setattr(gui_module, "is_autostart_enabled", lambda: False)
    monkeypatch.setattr(XccMainWindow, "_setup_tray", lambda self: None)

    result = XccMainWindow()
    result.resize(1480, 840)
    result.show()
    qapp.processEvents()
    yield result
    result._is_quitting = True
    result.close()
    qapp.processEvents()


def test_attachments_page_is_a_distinct_sidebar_workflow(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    assert [button.text() for button in window.nav.buttons] == [
        "Collect",
        "Attachments",
        "History",
        "Settings",
        "About",
    ]

    window.nav.setCurrentRow(1)
    qapp.processEvents()

    assert window.pages.currentWidget() is window.attachments_page
    assert window.attachments_page_header.title_label.text() == "Attachments"
    assert window.attachments_local_capsule.text() == "Local files only"
    assert window.attachments_copy_files_button.text() == "Copy Files"
    assert window.attachments_sequential_button.text() == "Send One-by-One"
    assert window.attachments_zip_button.text() == "Create ZIP && Copy"




def test_attachment_table_polish_uses_one_row_indicator_and_roomier_size_column(
    window: XccMainWindow,
) -> None:
    header = window.attachments_file_list.header()

    assert header.sectionResizeMode(0) == QHeaderView.ResizeMode.Stretch
    assert header.sectionResizeMode(1) == QHeaderView.ResizeMode.Fixed
    assert header.sectionSize(1) == ATTACHMENT_SIZE_COLUMN_WIDTH
    assert ATTACHMENT_SIZE_COLUMN_WIDTH == 104
    assert window.attachments_file_list.headerItem().textAlignment(1) == int(
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
    )
    assert isinstance(
        window.attachments_file_list.itemDelegate(),
        AttachmentSelectionDelegate,
    )

def test_attachment_selection_renders_order_relative_paths_and_sizes(
    qapp: QApplication,
    window: XccMainWindow,
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    first = root / "Assets" / "Game.unity"
    second = root / "Assets" / "image.png"
    first.parent.mkdir(parents=True)
    first.write_bytes(b"123")
    second.write_bytes(b"12345")

    window.attachment_project_root = root
    window.attachment_files = [
        AttachmentFile(first.resolve(), 3),
        AttachmentFile(second.resolve(), 5),
    ]
    window._refresh_attachments_page()
    qapp.processEvents()

    assert window.attachments_selection_meta.text() == "2 files · 8 B"
    assert window.attachments_file_list.topLevelItemCount() == 2
    assert window.attachments_file_list.topLevelItem(0).text(0) == "Assets/Game.unity"
    assert window.attachments_file_list.topLevelItem(1).text(0) == "Assets/image.png"
    expected_size_alignment = int(
        Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
    )
    assert (
        window.attachments_file_list.topLevelItem(0).textAlignment(1)
        == expected_size_alignment
    )
    assert (
        window.attachments_file_list.topLevelItem(1).textAlignment(1)
        == expected_size_alignment
    )
    assert window.attachments_transfer_values["Structure"].text() == "Preserved"
    assert window.attachments_copy_files_button.isEnabled()
    assert window.attachments_zip_button.isEnabled()


def test_attachment_remove_and_clear_preserve_order_and_root(
    qapp: QApplication,
    window: XccMainWindow,
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    files = []
    for index in range(3):
        path = root / f"f{index}.bin"
        path.write_bytes(bytes([index]))
        files.append(AttachmentFile(path.resolve(), 1))

    window.attachment_project_root = root
    window.attachment_files = list(files)
    window._refresh_attachments_page()

    window.attachments_file_list.topLevelItem(1).setSelected(True)
    window._remove_selected_attachments()
    assert [item.path for item in window.attachment_files] == [
        files[0].path,
        files[2].path,
    ]

    window._clear_attachments()
    assert window.attachment_files == []
    assert window.attachment_project_root == root
    assert window.attachments_root_value.text() == str(root)


def test_ctrl_v_dispatch_is_page_local_and_does_not_steal_editable_paste(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attachment_calls: list[bool] = []
    collect_calls: list[bool] = []
    monkeypatch.setattr(
        window,
        "_paste_attachment_paths_from_clipboard",
        lambda: attachment_calls.append(True),
    )
    monkeypatch.setattr(
        window,
        "_paste_paths_from_clipboard",
        lambda: collect_calls.append(True),
    )

    window.pages.setCurrentWidget(window.attachments_page)
    window.attachments_add_files_button.setFocus()
    qapp.processEvents()
    window._on_paste_paths_shortcut()
    assert attachment_calls == [True]
    assert collect_calls == []

    editable = QLineEdit(window.attachments_page)
    editable.show()
    editable.setFocus()
    qapp.processEvents()
    window._on_paste_paths_shortcut()
    assert attachment_calls == [True]


def test_copy_files_uses_file_clipboard_contract(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    file = tmp_path / "asset.blend"
    file.write_bytes(b"blend")
    window.attachment_files = [AttachmentFile(file.resolve(), 5)]
    window._refresh_attachments_page()

    calls: list[tuple[Path, ...]] = []

    def fake_copy(paths):
        resolved = tuple(Path(path) for path in paths)
        calls.append(resolved)
        return resolved

    monkeypatch.setattr(gui_module, "copy_files_to_clipboard", fake_copy)
    window._copy_attachment_files()

    assert calls == [(file.resolve(),)]
    assert "1 file copied" in window._attachment_last_action
    assert window.attachments_header_status.text() == "Copied"



def test_attachment_handoff_automatically_pastes_files_in_order(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    files: list[AttachmentFile] = []
    for index in range(3):
        path = root / f"asset-{index}.png"
        path.write_bytes(bytes([index + 1]))
        files.append(AttachmentFile(path.resolve(), 1))

    window.attachment_project_root = root
    window.attachment_files = list(files)
    window._refresh_attachments_page()

    events: list[tuple[str, object]] = []

    def fake_copy(paths):
        resolved = tuple(Path(path) for path in paths)
        events.append(("copy", resolved))
        return resolved

    monkeypatch.setattr(gui_module, "copy_files_to_clipboard", fake_copy)
    monkeypatch.setattr(
        gui_module,
        "send_ctrl_v_to_foreground",
        lambda hwnd: events.append(("paste", hwnd)),
    )
    monkeypatch.setattr(gui_module, "is_foreground_window", lambda hwnd: True)
    monkeypatch.setattr(
        gui_module,
        "window_belongs_to_current_process",
        lambda hwnd: False,
    )
    monkeypatch.setattr(
        window,
        "_schedule_attachment_sequential",
        lambda delay_ms, callback: callback(),
    )

    window._start_attachment_sequential(target_hwnd=4242)
    qapp.processEvents()

    assert events == [
        ("copy", (files[0].path,)),
        ("paste", 4242),
        ("copy", (files[1].path,)),
        ("paste", 4242),
        ("copy", (files[2].path,)),
        ("paste", 4242),
    ]
    assert window._attachment_sequential_active is False
    assert window.attachments_sequential_button.text() == "Send One-by-One"
    assert "Attachment Handoff completed" in window._attachment_last_action
    record = window.history_entries[0]
    assert getattr(record, "transfer_type", None) == "Attachment Handoff"
    assert getattr(record, "outcome", None) == "SUCCESS"


def test_attachment_handoff_stops_before_pasting_into_changed_focus(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.bin"
    second = tmp_path / "second.bin"
    first.write_bytes(b"1")
    second.write_bytes(b"2")
    window.attachment_files = [
        AttachmentFile(first.resolve(), 1),
        AttachmentFile(second.resolve(), 1),
    ]
    window._refresh_attachments_page()

    copied: list[Path] = []
    pasted: list[int] = []
    foreground_checks = iter((True, True, False))

    def fake_copy(paths):
        path = Path(tuple(paths)[0])
        copied.append(path)
        return (path,)

    monkeypatch.setattr(gui_module, "copy_files_to_clipboard", fake_copy)
    monkeypatch.setattr(
        gui_module,
        "send_ctrl_v_to_foreground",
        lambda hwnd: pasted.append(hwnd),
    )
    monkeypatch.setattr(
        gui_module,
        "is_foreground_window",
        lambda hwnd: next(foreground_checks),
    )
    monkeypatch.setattr(
        gui_module,
        "window_belongs_to_current_process",
        lambda hwnd: False,
    )
    monkeypatch.setattr(
        window,
        "_schedule_attachment_sequential",
        lambda delay_ms, callback: callback(),
    )

    window._start_attachment_sequential(target_hwnd=99)
    qapp.processEvents()

    assert copied == [first.resolve()]
    assert pasted == [99]
    assert window._attachment_sequential_active is False
    assert "lost focus" in window._attachment_issue_summary
    record = window.history_entries[0]
    assert getattr(record, "transfer_type", None) == "Attachment Handoff"
    assert getattr(record, "outcome", None) == "CANCELLED"


def test_attachment_handoff_stops_on_later_file_revalidation_failure(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.bin"
    second = tmp_path / "second.bin"
    first.write_bytes(b"1")
    second.write_bytes(b"2")
    window.attachment_files = [
        AttachmentFile(first.resolve(), 1),
        AttachmentFile(second.resolve(), 1),
    ]
    window._refresh_attachments_page()

    copy_calls = 0
    pasted: list[int] = []

    def fake_copy(paths):
        nonlocal copy_calls
        copy_calls += 1
        if copy_calls == 2:
            raise FileNotFoundError("second file disappeared")
        return tuple(Path(path) for path in paths)

    monkeypatch.setattr(gui_module, "copy_files_to_clipboard", fake_copy)
    monkeypatch.setattr(
        gui_module,
        "send_ctrl_v_to_foreground",
        lambda hwnd: pasted.append(hwnd),
    )
    monkeypatch.setattr(gui_module, "is_foreground_window", lambda hwnd: True)
    monkeypatch.setattr(
        gui_module,
        "window_belongs_to_current_process",
        lambda hwnd: False,
    )
    monkeypatch.setattr(
        window,
        "_schedule_attachment_sequential",
        lambda delay_ms, callback: callback(),
    )

    window._start_attachment_sequential(target_hwnd=77)
    qapp.processEvents()

    assert copy_calls == 2
    assert pasted == [77]
    assert window._attachment_sequential_active is False
    assert "failed at 1/2" in window._attachment_issue_summary
    record = window.history_entries[0]
    assert getattr(record, "transfer_type", None) == "Attachment Handoff"
    assert getattr(record, "outcome", None) == "FAILED"


def test_attachment_handoff_button_arms_three_second_target_countdown(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    path = tmp_path / "one.png"
    path.write_bytes(b"1")
    window.attachment_files = [AttachmentFile(path.resolve(), 1)]
    window._refresh_attachments_page()

    scheduled: list[tuple[int, object]] = []
    monkeypatch.setattr(
        window,
        "_schedule_attachment_sequential",
        lambda delay_ms, callback: scheduled.append((delay_ms, callback)),
    )

    window._start_attachment_sequential()
    qapp.processEvents()

    assert window._attachment_sequential_active is True
    assert window._attachment_sequential_phase == "countdown"
    assert window._attachment_sequential_countdown == 3
    assert window.attachments_sequential_button.text() == "Starting in 3s"
    assert scheduled and scheduled[0][0] == 1000
    window._cancel_attachment_sequential()


def test_zip_completion_copies_completed_bundle_and_exposes_location(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    from xcc.attachment_bundle import AttachmentBundleResult

    source = tmp_path / "asset.bin"
    source.write_bytes(b"asset")
    bundle = tmp_path / "XCC-Attachments-20260922-120000.zip"
    bundle.write_bytes(b"zip")
    window.attachment_files = [AttachmentFile(source.resolve(), 5)]
    window._attachment_bundle_active = True
    window._attachment_bundle_started_at = 0.0

    calls: list[tuple[Path, ...]] = []

    def fake_copy(paths):
        result = tuple(Path(path) for path in paths)
        calls.append(result)
        return result

    monkeypatch.setattr(gui_module, "copy_files_to_clipboard", fake_copy)
    window._on_attachment_bundle_completed(
        AttachmentBundleResult(bundle.resolve(), 1, 5, 3)
    )

    assert calls == [(bundle.resolve(),)]
    assert window._attachment_bundle_last_path == bundle.resolve()
    assert "ZIP created and copied" in window._attachment_last_action
    assert window.history_entries
    record = window.history_entries[0]
    assert getattr(record, "bundle_name", None) == bundle.name
    assert str(source.resolve()) not in repr(record)
