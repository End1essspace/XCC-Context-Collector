from __future__ import annotations

import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QStyle,
    QStyleOptionComboBox,
)

import xcc.gui as gui_module
from xcc import __version__
from xcc.gui import SelectedFilesReviewDialog, XccMainWindow
from xcc.settings import AppSettings, SettingsLoadResult


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def window(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> XccMainWindow:
    monkeypatch.setattr(
        gui_module,
        "load_settings_result",
        lambda: SettingsLoadResult(
            AppSettings(
                start_maximized=False,
                close_to_tray=False,
                show_tray_notifications=False,
            )
        ),
    )
    monkeypatch.setattr(gui_module, "save_settings", lambda settings: None)
    monkeypatch.setattr(gui_module, "is_autostart_enabled", lambda: False)
    monkeypatch.setattr(XccMainWindow, "_setup_tray", lambda self: None)

    result = XccMainWindow()
    result.resize(1280, 760)
    result.show()
    qapp.processEvents()

    yield result

    result._is_quitting = True
    result.close()
    qapp.processEvents()


def _select_mode(
    qapp: QApplication,
    window: XccMainWindow,
    mode: str,
) -> None:
    button = {
        "files": window.mode_files,
        "folder": window.mode_folder,
        "git": window.mode_git,
        "tree": window.mode_tree,
    }[mode]
    button.click()
    qapp.processEvents()


def test_mode_actions_and_paste_visibility_follow_product_contract(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    expected = {
        "files": ("Select Files", True),
        "folder": ("Select Folder", False),
        "git": ("Select Repository", False),
        "tree": ("Select Folder", False),
    }

    for mode, (action_label, paste_visible) in expected.items():
        _select_mode(qapp, window, mode)

        assert window.select_source_button.text() == action_label
        assert window.paste_paths_button.isVisible() is paste_visible
        assert bool(window.source_helper_label.text().strip())


def test_selected_files_source_summary_clear_and_review_opening(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    _select_mode(qapp, window, "files")

    project_root = tmp_path / "project"
    first = project_root / "src" / "first.py"
    second = project_root / "docs" / "guide.md"
    first.parent.mkdir(parents=True)
    second.parent.mkdir(parents=True)
    first.write_text("FIRST = True\n", encoding="utf-8")
    second.write_text("# Guide\n", encoding="utf-8")

    window.selected_paths = [first, second]
    window.project_root = project_root
    window._refresh_source_controls()

    assert window.source_input.text() == "project · 2 files selected"
    assert window.source_box.property("reviewable") is True
    assert window.clear_source_button.isEnabled()

    opened: list[bool] = []

    def reject_review(self: SelectedFilesReviewDialog) -> int:
        opened.append(True)
        return int(QDialog.DialogCode.Rejected)

    monkeypatch.setattr(SelectedFilesReviewDialog, "exec", reject_review)
    window.source_input.clicked.emit()
    qapp.processEvents()
    assert opened == [True]

    window.project_root = None
    window._refresh_source_controls()
    assert window.source_input.text() == "2 files selected · Mixed locations"

    window.clear_source_button.click()
    qapp.processEvents()
    assert window.selected_paths == []
    assert window.project_root is None
    assert window.source_input.text() == ""
    assert window.source_box.property("reviewable") is False
    assert not window.clear_source_button.isEnabled()


def test_collection_active_state_disables_setup_without_disabling_cancel(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    _select_mode(qapp, window, "files")

    window._set_collection_active(True)
    qapp.processEvents()

    for control in (
        window.select_source_button,
        window.paste_paths_button,
        window.clear_source_button,
        window.source_input,
        window.compact_checkbox,
        window.max_chars_input,
        window.mode_files,
        window.mode_folder,
        window.mode_git,
        window.mode_tree,
    ):
        assert not control.isEnabled()

    assert window.collect_button.isEnabled()
    assert window.collect_button.text() == "Cancel"

    window._set_collection_active(False)
    qapp.processEvents()
    assert window.collect_button.isEnabled()
    assert window.collect_button.text() == "Collect && Copy"
    assert window.mode_files.isEnabled()


def test_shell_roles_versions_hotkey_and_accessible_names(
    window: XccMainWindow,
) -> None:
    assert window.header_status.text() == "Ready"
    assert window.status_label.text().startswith("Ready ·")
    assert window.header_status.text() != window.status_label.text()

    assert window.window_version_capsule.text() == f"v{__version__}"
    assert window.window_version_capsule.accessibleName() == "Application version"
    assert window.window_minimize_button.accessibleName() == "Minimize window"
    assert window.window_maximize_button.accessibleName() == "Maximize window"
    assert window.window_close_button.accessibleName() == "Close window"
    assert all(
        button.focusPolicy() == Qt.FocusPolicy.NoFocus
        for button in (
            window.window_minimize_button,
            window.window_maximize_button,
            window.window_close_button,
        )
    )
    assert window.sidebar_brand_header.accessibleName() == "XCC Context Collector"
    assert window.sidebar_brand_label.text() == "XCC Context Collector"
    assert window.sidebar_brand_label.accessibleName() == "XCC Context Collector"
    assert not hasattr(window, "sidebar_brand_title")
    assert not hasattr(window, "sidebar_brand_subtitle")
    assert not hasattr(window, "sidebar_brand_separator")
    assert not hasattr(window, "window_brand_icon")
    assert not hasattr(window, "window_brand_title")
    assert not hasattr(window, "status_version_label")
    assert window.status_label.accessibleName() == "Current event status"
    assert window.status_label.alignment() & Qt.AlignmentFlag.AlignLeft
    assert not hasattr(window, "sidebar_footer")
    assert window.status_bar.accessibleName() == "Application footer"
    assert window.sidebar_status_group.parent() is window.status_bar

    assert window.hotkey_capsule.text() == "Hotkey: Ctrl+Alt+X"
    assert window.hotkey_capsule.accessibleName() == "Restore hotkey"
    assert window.collect_button.accessibleName() == "Collect and copy context"
    assert window.last_run_state_label.accessibleName() == "Last run state"

    assert all(button.accessibleName() for button in window.nav.buttons)
    assert all(
        metric.accessibleName().endswith(" metric")
        for metric in window.metric_capsules
    )


def test_close_to_tray_rearms_guarded_close_controller(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    class VisibleTray:
        @staticmethod
        def isVisible() -> bool:
            return True

        @staticmethod
        def showMessage(*args, **kwargs) -> None:
            return None

    window.tray_icon = VisibleTray()
    window.app_settings.close_to_tray = True
    window.app_settings.show_tray_notifications = False
    window._fitts_close._close_requested = True
    window.window_close_button.set_force_hover(True)

    window._fitts_close._perform_close()
    qapp.processEvents()

    assert not window.isVisible()
    assert window._fitts_close.close_requested is False
    assert window.window_close_button.force_hover is False
    assert not window._fitts_close.timer.isActive()

    window.app_settings.close_to_tray = False
    window.show()
    qapp.processEvents()

def test_hotkey_restores_minimized_normal_window(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    window._restore_to_normal_geometry()
    qapp.processEvents()

    window._minimize_window()
    qapp.processEvents()
    assert window.isMinimized()
    assert window._restore_maximized_on_show is False

    window._restore_from_hotkey()
    qapp.processEvents()

    assert window.isVisible()
    assert not window.isMinimized()
    assert not window._is_effectively_maximized()


def test_tray_restores_minimized_custom_maximized_window(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    window._maximize_to_available_geometry()
    qapp.processEvents()
    assert window._is_effectively_maximized()

    window._minimize_window()
    qapp.processEvents()
    assert window.isMinimized()
    assert window._restore_maximized_on_show is True

    window._show_from_tray()
    qapp.processEvents()

    assert window.isVisible()
    assert not window.isMinimized()
    assert window._is_effectively_maximized()


def test_tray_trigger_restores_instead_of_hiding_minimized_window(
    qapp: QApplication,
    window: XccMainWindow,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    restored: list[bool] = []
    hidden: list[bool] = []

    window._restore_to_normal_geometry()
    window._minimize_window()
    qapp.processEvents()
    assert window.isMinimized()

    monkeypatch.setattr(
        window,
        "_show_from_tray",
        lambda: restored.append(True),
    )
    monkeypatch.setattr(
        window,
        "_hide_to_tray",
        lambda: hidden.append(True),
    )

    window._on_tray_activated(
        gui_module.QSystemTrayIcon.ActivationReason.Trigger
    )

    assert restored == [True]
    assert hidden == []


def test_hidden_startup_restore_preserves_configured_maximized_mode(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    window._restore_to_normal_geometry()
    window._restore_maximized_on_show = True
    window.hide()
    qapp.processEvents()

    window._show_from_tray()
    qapp.processEvents()

    assert window.isVisible()
    assert not window.isMinimized()
    assert window._is_effectively_maximized()


def test_interface_scale_setting_is_persistent_and_restart_gated(
    qapp: QApplication,
    window: XccMainWindow,
) -> None:
    combo = window.interface_scale_combo

    assert combo.currentData() == "auto"
    assert [
        combo.itemData(index)
        for index in range(combo.count())
    ] == ["auto", "90", "100", "110", "120", "125", "150"]
    assert combo.itemText(0) == "Auto (recommended)"
    assert (
        combo.sizeAdjustPolicy()
        == QComboBox.SizeAdjustPolicy.AdjustToContents
    )
    assert combo.minimumContentsLength() == len("Auto (recommended)")

    # Check the actual styled edit field rather than a hard-coded control
    # width. This protects the longest label when padding, arrow chrome, font,
    # or the optional XCC interface scale changes.
    option = QStyleOptionComboBox()
    combo.initStyleOption(option)
    edit_rect = combo.style().subControlRect(
        QStyle.ComplexControl.CC_ComboBox,
        option,
        QStyle.SubControl.SC_ComboBoxEditField,
        combo,
    )
    longest_text_width = combo.fontMetrics().horizontalAdvance(
        "Auto (recommended)"
    )
    assert edit_rect.width() >= longest_text_width

    target_index = combo.findData("125")
    assert target_index >= 0
    combo.setCurrentIndex(target_index)
    qapp.processEvents()

    assert window.app_settings.interface_scale == "125"
    assert "Restart XCC to apply" in window.status_label.text()

def test_footer_series_wordmark_is_subtle_and_noninteractive(
    window: XccMainWindow,
) -> None:
    brand = window.footer_series_brand

    assert brand.objectName() == "FooterSeriesBrand"
    assert brand.size() == gui_module.FOOTER_SERIES_WORDMARK_SIZE
    assert brand.testAttribute(
        Qt.WidgetAttribute.WA_TransparentForMouseEvents
    )
    assert brand.focusPolicy() == Qt.FocusPolicy.NoFocus
    assert not brand.pixmap().isNull()

    assert brand.graphicsEffect() is None
    assert brand.image_opacity == pytest.approx(
        gui_module.FOOTER_SERIES_WORDMARK_OPACITY
    )

    status_index = window.status_bar_layout.indexOf(
        window.sidebar_status_group
    )
    brand_index = window.status_bar_layout.indexOf(brand)
    assert status_index >= 0
    assert brand_index > status_index
