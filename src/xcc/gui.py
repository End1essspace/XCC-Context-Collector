from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from PySide6.QtCore import QObject, QLockFile, Qt, QTimer
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtGui import QAction, QIcon, QPixmap, QIntValidator
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from . import __version__
from .config import DEFAULT_HOTKEY, MAX_OUTPUT_CHARS, qt_context_file_filter
from pathlib import Path
from .clipboard import copy_to_clipboard
from .collector import collect_files
from .formatter import format_collection, format_project_tree
from .git_utils import get_changed_files, get_git_diff, is_git_repository
from .scanner import scan_project_files
from .settings import AppSettings, load_settings_result, save_settings
from .autostart import is_autostart_enabled, set_autostart_enabled
from .native_hotkey import NativeHotkeyError, NativeHotkeyManager

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ICON_PATH = PROJECT_ROOT / "assets" / "xcc_app.ico"
TRAY_ICON_PATH = PROJECT_ROOT / "assets" / "xcc_tray.ico"
INSTANCE_SERVER_NAME = "xcc-context-collector-single-instance"
INSTANCE_LOCK_PATH = Path(tempfile.gettempdir()) / "xcc-context-collector.lock"

def _notify_existing_instance() -> bool:
    socket = QLocalSocket()
    socket.connectToServer(INSTANCE_SERVER_NAME)

    if not socket.waitForConnected(500):
        return False

    socket.write(b"restore")
    socket.flush()
    socket.waitForBytesWritten(500)
    socket.disconnectFromServer()

    return True

class SingleInstanceServer(QObject):
    def __init__(self, window: "XccMainWindow") -> None:
        super().__init__(window)

        self.window = window
        self.server = QLocalServer(self)

        QLocalServer.removeServer(INSTANCE_SERVER_NAME)

        if not self.server.listen(INSTANCE_SERVER_NAME):
            print(f"XCC single-instance server failed: {self.server.errorString()}")
            return

        self.server.newConnection.connect(self._handle_new_connection)

    def _handle_new_connection(self) -> None:
        while self.server.hasPendingConnections():
            client = self.server.nextPendingConnection()
            client.disconnectFromServer()
            client.deleteLater()

        self.window._show_from_tray()


class XccMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("XCC Context Collector")
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.setMinimumSize(920, 620)

        self.selected_paths: list[Path] = []
        self.project_root: Path | None = None
        self.history_entries: list[dict[str, object]] = []
        settings_result = load_settings_result()
        self.app_settings: AppSettings = settings_result.settings
        self._settings_recovery_message = settings_result.message
        self._is_loading_settings = True
        self._is_quitting = False
        self._has_shown_tray_hint = False
        self._hotkey_manager: NativeHotkeyManager | None = None
        self._hotkey_available = False
        self._hotkey_status_message = "Not registered"

        self._setup_ui()
        self._apply_loaded_settings()
        if settings_result.recovered_from_error:
            self._set_event_status(self._settings_recovery_message)
        self._is_loading_settings = False
        self._apply_theme()
        self._setup_tray()

    def _setup_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        self.nav = self._build_nav()
        self.pages = QStackedWidget()

        self.collect_page = self._build_collect_page()
        self.history_page = self._build_history_page()
        self.settings_page = self._build_settings_page()
        self.about_page = self._build_about_page()

        self.pages.addWidget(self.collect_page)
        self.pages.addWidget(self.history_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.about_page)

        body_layout.addWidget(self.nav)
        body_layout.addWidget(self.pages, 1)

        root_layout.addWidget(body, 1)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusBar")
        self.status_label.setFixedHeight(38)
        root_layout.addWidget(self.status_label)

        self.setCentralWidget(root)

        self.nav.currentRowChanged.connect(self._change_page)
        self.nav.setCurrentRow(0)

        self.select_source_button.clicked.connect(self._select_source)
        self.clear_source_button.clicked.connect(self._clear_source)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        self.collect_button.clicked.connect(self._collect_and_copy)
        self.compact_checkbox.stateChanged.connect(self._on_settings_changed)
        self.max_chars_input.editingFinished.connect(self._on_settings_changed)
        self.start_with_windows_checkbox.stateChanged.connect(self._on_autostart_changed)
        self.start_minimized_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.start_maximized_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.close_to_tray_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.tray_notifications_checkbox.stateChanged.connect(self._on_behavior_settings_changed)

    def _setup_global_hotkey(self) -> None:
        self._cleanup_global_hotkey()

        manager = NativeHotkeyManager(self._restore_from_hotkey)

        try:
            manager.register(DEFAULT_HOTKEY)
        except NativeHotkeyError as exc:
            self._hotkey_manager = None
            self._hotkey_available = False
            self._hotkey_status_message = f"Unavailable: {exc}"
            self._set_event_status(f"Hotkey unavailable: {exc}")
            self._refresh_settings_page()

            if (
                hasattr(self, "tray_icon")
                and self.tray_icon.isVisible()
                and self.app_settings.show_tray_notifications
            ):
                self.tray_icon.showMessage(
                    "XCC hotkey unavailable",
                    str(exc),
                    QSystemTrayIcon.MessageIcon.Warning,
                    3500,
                )
            return

        self._hotkey_manager = manager
        self._hotkey_available = True
        self._hotkey_status_message = DEFAULT_HOTKEY
        self._set_event_status("Ready")
        self._refresh_settings_page()

    def _restore_from_hotkey(self) -> None:
        if self.app_settings.start_maximized:
            self.showMaximized()
        else:
            self.showNormal()

        self.raise_()
        self.activateWindow()
        self._set_transient_event_status("Window restored by hotkey.")
    
    def _on_autostart_changed(self) -> None:
        if self._is_loading_settings:
            return

        try:
            set_autostart_enabled(self.start_with_windows_checkbox.isChecked())
        except Exception as exc:
            self.start_with_windows_checkbox.blockSignals(True)
            self.start_with_windows_checkbox.setChecked(self.app_settings.start_with_windows)
            self.start_with_windows_checkbox.blockSignals(False)

            self._set_event_status("Autostart setup failed.")
            QMessageBox.warning(self, "XCC", str(exc))
            return

        self._save_current_settings()
        self._set_event_status("Settings saved.")


    def _on_behavior_settings_changed(self) -> None:
        if self._is_loading_settings:
            return

        self._save_current_settings()
        self._set_event_status("Settings saved.")

    def _on_settings_changed(self) -> None:
        if self._is_loading_settings:
            return

        self._save_current_settings()
        self._refresh_settings_page()

    def _on_mode_changed(self) -> None:
        if self._is_loading_settings:
            return

        self._clear_source()
    
    def _apply_loaded_settings(self) -> None:
        mode_to_button = {
            "files": self.mode_files,
            "folder": self.mode_folder,
            "git": self.mode_git,
            "tree": self.mode_tree,
        }

        mode_button = mode_to_button.get(self.app_settings.default_mode, self.mode_folder)
        mode_button.setChecked(True)

        self.compact_checkbox.setChecked(self.app_settings.compact_mode)
        self.max_chars_input.setText(str(self.app_settings.max_chars))

        last_source = self.app_settings.last_source.strip()
        if last_source and self.app_settings.default_mode in {"folder", "git", "tree"}:
            self.source_input.setText(last_source)
            self.project_root = Path(last_source)
            self._set_status("Loaded saved settings.")

        try:
            real_autostart_state = is_autostart_enabled()
        except Exception:
            real_autostart_state = self.app_settings.start_with_windows

        self.app_settings.start_with_windows = real_autostart_state

        if hasattr(self, "start_with_windows_checkbox"):
            self.start_with_windows_checkbox.setChecked(real_autostart_state)

    def _save_current_settings(self) -> None:
        settings = AppSettings(
            default_mode=self._current_mode(),
            max_chars=self._safe_current_max_chars(),
            compact_mode=self.compact_checkbox.isChecked(),
            last_source=self._current_persisted_source(),
            start_with_windows=self.start_with_windows_checkbox.isChecked(),
            start_minimized_to_tray=self.start_minimized_checkbox.isChecked(),
            close_to_tray=self.close_to_tray_checkbox.isChecked(),
            start_maximized=self.start_maximized_checkbox.isChecked(),
            show_tray_notifications=self.tray_notifications_checkbox.isChecked(),
        )

        save_settings(settings)
        self.app_settings = settings

    def _safe_current_max_chars(self) -> int:
        raw_value = self.max_chars_input.text().strip()

        try:
            value = int(raw_value)
        except ValueError:
            return MAX_OUTPUT_CHARS

        if value <= 0:
            return MAX_OUTPUT_CHARS

        return value

    def _current_persisted_source(self) -> str:
        mode = self._current_mode()

        if mode in {"folder", "git", "tree"} and self.project_root is not None:
            return str(self.project_root)

        return ""

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        layout = self._page_layout(page)

        layout.addWidget(self._section_title("History"))

        history_card = self._card()
        history_card.setMinimumHeight(260)

        history_layout = self._card_layout(history_card)
        history_layout.addWidget(self._card_title("Runtime History"))

        self.history_scroll_area = QScrollArea()
        self.history_scroll_area.setObjectName("HistoryScrollArea")
        self.history_scroll_area.setWidgetResizable(True)
        self.history_scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.history_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.history_list_container = QWidget()
        self.history_list_container.setObjectName("TransparentWidget")

        self.history_list_layout = QVBoxLayout(self.history_list_container)
        self.history_list_layout.setContentsMargins(0, 0, 0, 0)
        self.history_list_layout.setSpacing(12)

        self.history_empty_label = QLabel(
            "No runs yet.\nCollect context to see runtime history here."
        )
        self.history_empty_label.setObjectName("HistoryEmpty")
        self.history_empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.history_empty_label.setMinimumHeight(140)

        self.history_list_layout.addWidget(self.history_empty_label)
        self.history_list_layout.addStretch(1)

        self.history_scroll_area.setWidget(self.history_list_container)

        history_layout.addWidget(self.history_scroll_area, 1)

        layout.addWidget(history_card, 1)
        layout.addStretch(0)

        return page

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(56)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setObjectName("HeaderAppIcon")
        icon_label.setFixedSize(28, 28)

        if APP_ICON_PATH.exists():
            pixmap = QPixmap(str(APP_ICON_PATH))
            icon_label.setPixmap(
                pixmap.scaled(
                    28,
                    28,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        title = QLabel("XCC Context Collector")
        title.setObjectName("HeaderTitle")

        self.header_status = QLabel("Ready")
        self.header_status.setObjectName("StatusCapsule")
        self.header_status.setFixedHeight(34)

        hotkey = QLabel(f"Hotkey: {DEFAULT_HOTKEY}")
        hotkey.setObjectName("HotkeyCapsule")
        hotkey.setFixedHeight(34)

        layout.addWidget(icon_label)
        layout.addWidget(title, 1)
        layout.addWidget(self.header_status)
        layout.addWidget(hotkey)

        return header

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        icon_path = TRAY_ICON_PATH if TRAY_ICON_PATH.exists() else APP_ICON_PATH
        tray_icon = QIcon(str(icon_path)) if icon_path.exists() else self.windowIcon()

        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip("XCC Context Collector")

        tray_menu = QMenu(self)
        tray_menu.setObjectName("TrayMenu")
        tray_menu.setStyleSheet(
            """
            QMenu {
                background: #151515;
                border: 1px solid #5A4820;
                padding: 6px;
                color: #F2F2F2;
                font-family: Segoe UI;
                font-size: 12px;
            }

            QMenu::item {
                background: transparent;
                padding: 8px 28px 8px 22px;
                border-radius: 6px;
            }

            QMenu::item:selected {
                background: #D6A93A;
                color: #111111;
            }

            QMenu::separator {
                height: 1px;
                background: #2F2A1C;
                margin: 5px 4px;
            }
            """
        )

        show_action = QAction("Show XCC", self)
        show_action.triggered.connect(self._show_from_tray)

        hide_action = QAction("Hide XCC", self)
        hide_action.triggered.connect(self._hide_to_tray)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_from_tray)

        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _set_transient_event_status(self, message: str, timeout_ms: int = 1800) -> None:
        self.status_label.setText(message)
        QTimer.singleShot(timeout_ms, lambda: self.status_label.setText("Ready"))

    def _set_event_status(self, message: str) -> None:
        self.status_label.setText(message)

    def _show_main_window(self) -> None:
        if self.app_settings.start_maximized:
            self.showMaximized()
        else:
            self.show()

    def _show_from_tray(self) -> None:
        if self.app_settings.start_maximized:
            self.showMaximized()
        else:
            self.showNormal()

        self.raise_()
        self.activateWindow()
        self._set_transient_event_status("Window restored.")

    def _hide_to_tray(self) -> None:
        if not (hasattr(self, "tray_icon") and self.tray_icon.isVisible()):
            self._set_event_status("Tray is not available.")
            return

        self.hide()
        self._set_transient_event_status("Hidden to tray.")

    def _quit_from_tray(self) -> None:
        self._is_quitting = True

        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()

        self._cleanup_global_hotkey()
        QApplication.quit()

    def _cleanup_global_hotkey(self) -> None:
        if self._hotkey_manager is None:
            return

        self._hotkey_manager.unregister()
        self._hotkey_manager = None
        self._hotkey_available = False
        self._hotkey_status_message = "Not registered"

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self._hide_to_tray()
            event.accept()
            return

        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:
        if self._is_quitting:
            self._cleanup_global_hotkey()
            event.accept()
            return

        if (
            self.app_settings.close_to_tray
            and hasattr(self, "tray_icon")
            and self.tray_icon.isVisible()
        ):
            self.hide()
            self._set_transient_event_status("Hidden to tray.")

            if self.app_settings.show_tray_notifications and not self._has_shown_tray_hint:
                self.tray_icon.showMessage(
                    "XCC is still running",
                    "Use the tray icon to restore or quit XCC.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2500,
                )
                self._has_shown_tray_hint = True

            event.ignore()
            return

        self._cleanup_global_hotkey()
        event.accept()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_from_tray()
            return

        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self._hide_to_tray()
            else:
                self._show_from_tray()

    def _build_nav(self) -> QListWidget:
        nav = QListWidget()
        nav.setObjectName("Sidebar")
        nav.setFixedWidth(190)
        nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for title in ["Collect", "History", "Settings", "About"]:
            item = QListWidgetItem(title)
            item.setSizeHint(item.sizeHint())
            nav.addItem(item)

        return nav

    def _build_collect_page(self) -> QWidget:
        page = QWidget()
        layout = self._page_layout(page)

        layout.addWidget(self._section_title("Collect Context"))

        setup_card = self._card()
        setup_card.setMinimumHeight(230)

        setup_layout = self._card_layout(setup_card)
        setup_layout.addWidget(self._card_title("Setup"))

        setup_grid = QGridLayout()
        setup_grid.setContentsMargins(0, 6, 0, 0)
        setup_grid.setHorizontalSpacing(14)
        setup_grid.setVerticalSpacing(14)

        mode_label = QLabel("Mode")
        mode_label.setObjectName("FieldLabel")
        mode_label.setFixedWidth(90)

        self.mode_group = QButtonGroup(self)
        self.mode_files = QRadioButton("Selected Files")
        self.mode_folder = QRadioButton("Full Folder")
        self.mode_git = QRadioButton("Git Changed Files")
        self.mode_tree = QRadioButton("Project Tree")

        self.mode_folder.setChecked(True)

        mode_buttons = QWidget()
        mode_buttons.setObjectName("TransparentWidget")
        mode_buttons_layout = QHBoxLayout(mode_buttons)
        mode_buttons_layout.setContentsMargins(0, 0, 0, 0)
        mode_buttons_layout.setSpacing(22)

        for index, button in enumerate(
            [self.mode_files, self.mode_folder, self.mode_git, self.mode_tree]
        ):
            self.mode_group.addButton(button, index)
            mode_buttons_layout.addWidget(button)

        mode_buttons_layout.addStretch(1)

        source_label = QLabel("Source")
        source_label.setObjectName("FieldLabel")
        source_label.setFixedWidth(90)

        self.source_input = QLineEdit()
        self.source_input.setPlaceholderText("No source selected")
        self.source_input.setReadOnly(True)
        self.source_input.setFixedHeight(38)
        self.source_input.setFrame(False)
        self.source_input.setObjectName("SourceInputEmbedded")

        self.clear_source_button = QPushButton("×")
        self.clear_source_button.setObjectName("ClearSourceButton")
        self.clear_source_button.setFixedSize(24, 24)
        self.clear_source_button.setToolTip("Clear selected source")
        self.clear_source_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.select_source_button = QPushButton("Select Source")
        self.select_source_button.setMinimumWidth(160)
        self.select_source_button.setFixedHeight(40)

        options_label = QLabel("Options")
        options_label.setObjectName("FieldLabel")
        options_label.setFixedWidth(90)

        self.compact_checkbox = QCheckBox("Compact mode")
        self.compact_checkbox.setChecked(True)
        self.compact_checkbox.setFixedHeight(40)

        max_chars_label = QLabel("Max chars")
        max_chars_label.setObjectName("FieldLabelSmall")
        max_chars_label.setFixedHeight(40)

        self.max_chars_input = QLineEdit(str(MAX_OUTPUT_CHARS))
        self.max_chars_input.setValidator(QIntValidator(1, 10_000_000, self))
        self.max_chars_input.setMaximumWidth(160)
        self.max_chars_input.setFixedHeight(40)

        setup_grid.addWidget(mode_label, 0, 0)
        setup_grid.addWidget(mode_buttons, 0, 1, 1, 2)

        source_box = QFrame()
        source_box.setObjectName("SourceInputBox")
        source_box.setFixedHeight(40)

        source_box_layout = QHBoxLayout(source_box)
        source_box_layout.setContentsMargins(10, 0, 8, 0)
        source_box_layout.setSpacing(6)

        source_box_layout.addWidget(self.source_input, 1)
        source_box_layout.addWidget(
            self.clear_source_button,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )

        setup_grid.addWidget(source_label, 1, 0)
        setup_grid.addWidget(source_box, 1, 1)
        setup_grid.addWidget(self.select_source_button, 1, 2)

        setup_grid.addWidget(options_label, 2, 0)

        options_box = QWidget()
        options_box.setObjectName("TransparentWidget")
        options_box_layout = QHBoxLayout(options_box)
        options_box_layout.setContentsMargins(0, 0, 0, 0)
        options_box_layout.setSpacing(16)

        options_box_layout.addWidget(self.compact_checkbox)
        options_box_layout.addSpacing(24)
        options_box_layout.addWidget(max_chars_label)
        options_box_layout.addWidget(self.max_chars_input)
        options_box_layout.addStretch(1)

        setup_grid.addWidget(options_box, 2, 1, 1, 2)

        setup_grid.setColumnStretch(0, 0)
        setup_grid.setColumnStretch(1, 1)
        setup_grid.setColumnStretch(2, 0)

        setup_layout.addLayout(setup_grid)

        layout.addWidget(setup_card)

        stats_card = self._card()
        stats_card.setMinimumHeight(210)

        stats_layout = self._card_layout(stats_card)

        stats_layout.addWidget(self._card_title("Last Run"))

        self.files_metric = self._metric_capsule("Files", "-")
        self.lines_metric = self._metric_capsule("Lines", "-")
        self.source_chars_metric = self._metric_capsule("Source Chars", "-")

        self.output_chars_metric = self._metric_capsule("Output Chars", "-")
        self.tokens_metric = self._metric_capsule("Output Tokens", "-")

        self.truncated_metric = self._metric_capsule("Truncated", "-")
        self.errors_metric = self._metric_capsule("Errors", "-")

        columns_row = QHBoxLayout()
        columns_row.setSpacing(20)
        columns_row.setContentsMargins(0, 0, 0, 0)

        volume_column = QVBoxLayout()
        volume_column.setContentsMargins(0, 0, 0, 0)
        volume_column.setSpacing(8)
        volume_title = QLabel("Volume")
        volume_title.setObjectName("MetricGroupTitle")
        volume_column.addWidget(volume_title)
        volume_column.addWidget(self.files_metric)
        volume_column.addWidget(self.lines_metric)
        volume_column.addWidget(self.source_chars_metric)

        output_column = QVBoxLayout()
        output_column.setContentsMargins(0, 0, 0, 0)
        output_column.setSpacing(8)
        output_title = QLabel("Output")
        output_title.setObjectName("MetricGroupTitle")
        output_column.addWidget(output_title)
        output_column.addWidget(self.output_chars_metric)
        output_column.addWidget(self.tokens_metric)
        output_column.addStretch(1)

        health_column = QVBoxLayout()
        health_column.setContentsMargins(0, 0, 0, 0)
        health_column.setSpacing(8)
        health_title = QLabel("Health")
        health_title.setObjectName("MetricGroupTitle")
        health_column.addWidget(health_title)
        health_column.addWidget(self.truncated_metric)
        health_column.addWidget(self.errors_metric)
        health_column.addStretch(1)

        columns_row.addLayout(volume_column, 1)
        columns_row.addLayout(output_column, 1)
        columns_row.addLayout(health_column, 1)

        stats_layout.addLayout(columns_row)

        layout.addWidget(stats_card)

        layout.addStretch(1)

        self.collect_button = QPushButton("Collect && Copy")
        self.collect_button.setObjectName("PrimaryButton")
        self.collect_button.setFixedHeight(52)

        layout.addWidget(self.collect_button)

        return page

    def _current_mode(self) -> str:
        checked_id = self.mode_group.checkedId()

        if checked_id == 0:
            return "files"

        if checked_id == 1:
            return "folder"

        if checked_id == 2:
            return "git"

        return "tree"

    def _change_page(self, index: int) -> None:
        if index == 2:
            self._refresh_settings_page()

        self.pages.setCurrentIndex(index)

    def _current_mode_name(self) -> str:
        mode = self._current_mode()

        return {
            "files": "Selected Files",
            "folder": "Full Folder",
            "git": "Git Changed Files",
            "tree": "Project Tree",
        }.get(mode, "Unknown")

    def _settings_header(self) -> QWidget:
        header = QWidget()
        header.setObjectName("TransparentWidget")
        header.setFixedHeight(34)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        title = self._section_title("Settings")
        title.setFixedHeight(34)
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        subtitle = QLabel("Runtime configuration and app behavior controls.")
        subtitle.setObjectName("PageSubtitle")
        subtitle.setFixedHeight(34)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)

        return header

    def _settings_row(
        self,
        title: str,
        description: str,
        control: QWidget | None = None,
        value: str | None = None,
    ) -> QFrame:
        row = QFrame()
        row.setObjectName("SettingsRow")
        row.setFixedHeight(58)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(12)

        text_box = QWidget()
        text_box.setObjectName("TransparentWidget")
        text_layout = QVBoxLayout(text_box)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("SettingsRowTitle")

        description_label = QLabel(description)
        description_label.setObjectName("SettingsRowDescription")

        text_layout.addWidget(title_label)
        text_layout.addWidget(description_label)

        layout.addWidget(text_box, 1)

        if control is not None:
            layout.addWidget(control, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        if value is not None:
            value_label = QLabel(value)
            value_label.setObjectName("SettingsRowValue")
            value_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            layout.addWidget(value_label, 0)

            row.value_label = value_label

        return row

    def _settings_toggle(self, text: str, checked: bool) -> QCheckBox:
        checkbox = QCheckBox(text)
        checkbox.setObjectName("SettingsToggle")
        checkbox.setChecked(checked)
        checkbox.setFixedHeight(28)
        return checkbox

    def _settings_group(self, title: str, rows: list[QWidget]) -> QFrame:
        group = QFrame()
        group.setObjectName("SettingsGroup")
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        layout.addWidget(self._settings_section_title(title))

        for row in rows:
            layout.addWidget(row)

        return group

    def _refresh_settings_page(self) -> None:
        if hasattr(self, "settings_current_mode"):
            self.settings_current_mode.value_label.setText(self._current_mode_name())

        if hasattr(self, "settings_compact_mode"):
            self.settings_compact_mode.value_label.setText(
                "Enabled" if self.compact_checkbox.isChecked() else "Disabled"
            )

        if hasattr(self, "settings_current_max_chars"):
            self.settings_current_max_chars.value_label.setText(
                self.max_chars_input.text().strip() or "Not set"
            )

        if hasattr(self, "settings_hotkey"):
            self.settings_hotkey.value_label.setText(self._hotkey_status_message)

    def _select_source(self) -> None:
        mode = self._current_mode()

        if mode == "files":
            selected, _ = QFileDialog.getOpenFileNames(
                self,
                "Select context files",
                "",
                qt_context_file_filter(),
            )

            if not selected:
                self._set_status("Source selection cancelled.")
                return

            new_paths = [Path(path) for path in selected]

            existing_paths = {
                path.resolve()
                for path in self.selected_paths
                if path.exists()
            }

            added_count = 0

            for path in new_paths:
                resolved_path = path.resolve()

                if resolved_path in existing_paths:
                    continue

                self.selected_paths.append(path)
                existing_paths.add(resolved_path)
                added_count += 1

            self.project_root = None

            total_count = len(self.selected_paths)
            self.source_input.setText(f"{total_count} file{'s' if total_count != 1 else ''} selected")

            if added_count == 0:
                self._set_status("Selected files already added.")
            else:
                self._set_status(
                    f"Added {added_count} file{'s' if added_count != 1 else ''}. "
                    f"Total: {total_count}."
                )

            self._save_current_settings()
            self._refresh_settings_page()
            return

        selected_folder = QFileDialog.getExistingDirectory(
            self,
            "Select project folder",
            "",
        )

        if not selected_folder:
            self._set_status("Source selection cancelled.")
            return

        folder = Path(selected_folder)

        if mode == "git" and not is_git_repository(folder):
            self._set_status("Selected folder is not a Git repository.")
            QMessageBox.warning(
                self,
                "XCC",
                "Selected folder is not a Git repository.",
            )
            return

        self.selected_paths = []
        self.project_root = folder
        self.source_input.setText(str(folder))

        if mode == "git":
            self._set_status("Git repository selected.")
        else:
            self._set_status("Project folder selected.")

        self._save_current_settings()
        self._refresh_settings_page()

    def _collect_and_copy(self) -> None:
        try:
            max_output_chars = self._read_max_output_chars()
            mode = self._current_mode()

            mode_name = {
                "files": "Selected Files",
                "folder": "Full Folder",
                "git": "Git Changed Files",
                "tree": "Project Tree",
            }.get(mode, "Unknown")

            selected_paths, project_root = self._resolve_selected_paths(mode)

            if mode == "tree":
                if project_root is None:
                    raise ValueError("Select a source folder first.")

                result = format_project_tree(
                    project_root,
                    compact=self.compact_checkbox.isChecked(),
                    mode_name=mode_name,
                    max_output_chars=max_output_chars,
                )

                if not result.text.strip():
                    self._set_status("Nothing to copy.")
                    QMessageBox.warning(self, "XCC", "Nothing to copy.")
                    return

                copy_to_clipboard(result.text)

                output_chars = len(result.text)
                output_tokens = output_chars // 4

                self._update_metrics(
                    files=result.stats.files,
                    lines=result.stats.lines,
                    source_chars=result.stats.chars,
                    output_chars=output_chars,
                    output_tokens=output_tokens,
                    truncated=result.was_truncated,
                    errors=len(result.errors),
                )
                self._add_history_entry(
                    mode_name=mode_name,
                    source=self._current_source_label(mode, project_root),
                    files=result.stats.files,
                    lines=result.stats.lines,
                    source_chars=result.stats.chars,
                    output_chars=output_chars,
                    output_tokens=output_tokens,
                    truncated=result.was_truncated,
                    errors=len(result.errors),
                )

                self._show_success_feedback()
                return

            if not selected_paths:
                self._set_status("No files selected or found.")
                QMessageBox.warning(self, "XCC", "No files selected or found.")
                return

            files, errors = collect_files(selected_paths)

            git_diff = None
            if mode == "git" and project_root is not None:
                git_diff = get_git_diff(project_root)

            result = format_collection(
                files,
                errors,
                project_root=project_root,
                compact=self.compact_checkbox.isChecked(),
                mode_name=mode_name,
                max_output_chars=max_output_chars,
                git_diff=git_diff,
                include_project_tree=(mode != "files"),
            )

            if not result.text.strip():
                self._set_status("Nothing to copy.")
                QMessageBox.warning(self, "XCC", "Nothing to copy.")
                return

            copy_to_clipboard(result.text)

            output_chars = len(result.text)
            output_tokens = output_chars // 4

            self._update_metrics(
                files=result.stats.files,
                lines=result.stats.lines,
                source_chars=result.stats.chars,
                output_chars=output_chars,
                output_tokens=output_tokens,
                truncated=result.was_truncated,
                errors=len(result.errors),
            )
            self._add_history_entry(
                mode_name=mode_name,
                source=self._current_source_label(mode, project_root),
                files=result.stats.files,
                lines=result.stats.lines,
                source_chars=result.stats.chars,
                output_chars=output_chars,
                output_tokens=output_tokens,
                truncated=result.was_truncated,
                errors=len(result.errors),
            )

            self._show_success_feedback()

        except Exception as exc:
            self._set_status("Error.")
            QMessageBox.critical(self, "XCC", str(exc))

    def _read_max_output_chars(self) -> int:
        raw_value = self.max_chars_input.text().strip()

        if not raw_value:
            raise ValueError("Max output chars is required.")

        value = int(raw_value)

        if value <= 0:
            raise ValueError("Max output chars must be greater than 0.")

        return value

    def _resolve_selected_paths(self, mode: str) -> tuple[list[Path], Path | None]:
        if mode == "files":
            return self.selected_paths, None

        if self.project_root is None:
            source_text = self.source_input.text().strip()

            if source_text:
                restored_root = Path(source_text)

                if restored_root.exists() and restored_root.is_dir():
                    self.project_root = restored_root

        if self.project_root is None:
            raise ValueError("Select a source folder first.")

        if mode == "tree":
            return [], self.project_root

        if mode == "folder":
            return scan_project_files(self.project_root), self.project_root

        if not is_git_repository(self.project_root):
            raise ValueError("Selected folder is not a Git repository.")

        return get_changed_files(self.project_root), self.project_root

    def _update_metrics(
        self,
        *,
        files: int,
        lines: int,
        source_chars: int,
        output_chars: int,
        output_tokens: int,
        truncated: bool,
        errors: int,
    ) -> None:
        self._set_metric_value(self.files_metric, str(files))
        self._set_metric_value(self.lines_metric, str(lines))
        self._set_metric_value(self.source_chars_metric, str(source_chars))
        self._set_metric_value(self.output_chars_metric, str(output_chars))
        self._set_metric_value(self.tokens_metric, str(output_tokens))
        self._set_metric_value(self.truncated_metric, "Yes" if truncated else "No")
        self._set_metric_value(self.errors_metric, str(errors))

    def _set_metric_value(self, metric: QFrame, value: str) -> None:
        metric.value_label.setText(value)

    def _clear_source(self) -> None:
        self.selected_paths = []
        self.project_root = None
        self.source_input.clear()
        self.source_input.setPlaceholderText("No source selected")
        self._save_current_settings()
        self._refresh_settings_page()
        self._set_status("Source cleared.")

    def _set_status(self, message: str) -> None:
        self.status_label.setText(message)
        self.header_status.setText(message if len(message) <= 18 else "Ready")

    def _show_success_feedback(self) -> None:
        self._set_status("Copied to clipboard.")
        self.header_status.setText("Copied")
        self.collect_button.setText("Copied!")

        QTimer.singleShot(1500, self._reset_success_feedback)

    def _reset_success_feedback(self) -> None:
        self.header_status.setText("Ready")
        self.collect_button.setText("Collect && Copy")

    def _build_settings_page(self) -> QWidget:
        page = QWidget()
        layout = self._page_layout(page)

        layout.addWidget(self._settings_header())

        self.start_with_windows_checkbox = self._settings_toggle(
            "",
            self.app_settings.start_with_windows,
        )
        self.start_minimized_checkbox = self._settings_toggle(
            "",
            self.app_settings.start_minimized_to_tray,
        )
        self.start_maximized_checkbox = self._settings_toggle(
            "",
            self.app_settings.start_maximized,
        )
        self.close_to_tray_checkbox = self._settings_toggle(
            "",
            self.app_settings.close_to_tray,
        )
        self.tray_notifications_checkbox = self._settings_toggle(
            "",
            self.app_settings.show_tray_notifications,
        )

        behavior_group = self._settings_group(
            "Behavior",
            [
                self._settings_row(
                    "Start with Windows",
                    "Launch XCC automatically after Windows login.",
                    control=self.start_with_windows_checkbox,
                ),
                self._settings_row(
                    "Start minimized to tray",
                    "Keep startup silent and restore from the tray icon.",
                    control=self.start_minimized_checkbox,
                ),
                self._settings_row(
                    "Start maximized",
                    "Open the main window in maximized mode.",
                    control=self.start_maximized_checkbox,
                ),
                self._settings_row(
                    "Close to tray",
                    "Keep XCC running when the window is closed.",
                    control=self.close_to_tray_checkbox,
                ),
                self._settings_row(
                    "Tray notifications",
                    "Show a notification when XCC is minimized to tray.",
                    control=self.tray_notifications_checkbox,
                ),
                self._settings_row(
                    "Double click restore",
                    "Restore the main window by double-clicking the tray icon.",
                    value="Enabled",
                ),
            ],
        )

        self.settings_current_mode = self._settings_row(
            "Default mode",
            "Collection mode used for the current saved session.",
            value=self._current_mode_name(),
        )
        self.settings_compact_mode = self._settings_row(
            "Compact mode",
            "Remove repeated empty lines and reduce output noise.",
            value="Enabled" if self.compact_checkbox.isChecked() else "Disabled",
        )
        self.settings_current_max_chars = self._settings_row(
            "Max output chars",
            "Character budget applied to generated context.",
            value=self.max_chars_input.text().strip() or "Not set",
        )

        self.settings_hotkey = self._settings_row(
            "Hotkey",
            "Restore the main window while XCC is running.",
            value=self._hotkey_status_message,
        )

        context_group = self._settings_group(
            "Context & System",
            [
                self.settings_current_mode,
                self.settings_compact_mode,
                self.settings_current_max_chars,
                self.settings_hotkey,
                self._settings_row(
                    "Version",
                    "Current application version.",
                    value=__version__,
                ),
                self._settings_row(
                    "Config file",
                    "Local settings file stored under the user profile.",
                    value="config.json",
                ),
            ],
        )

        groups_row = QWidget()
        groups_row.setObjectName("TransparentWidget")

        groups_layout = QHBoxLayout(groups_row)
        groups_layout.setContentsMargins(0, 0, 0, 0)
        groups_layout.setSpacing(18)
        groups_layout.addWidget(behavior_group, 1)
        groups_layout.addWidget(context_group, 1)

        layout.addWidget(groups_row)
        layout.addStretch(1)

        return page
                
    def _settings_section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SettingsSectionTitle")
        label.setFixedHeight(16)
        return label
    
    def _current_source_label(self, mode: str, project_root: Path | None) -> str:
        if mode == "files":
            count = len(self.selected_paths)
            return f"{count} selected file{'s' if count != 1 else ''}"

        if project_root is not None:
            return str(project_root)

        return "Unknown source"
    
    def _page_layout(self, page: QWidget) -> QVBoxLayout:
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)
        return layout

    def _build_about_page(self) -> QWidget:
        page = QWidget()
        layout = self._page_layout(page)

        layout.addWidget(self._section_title("About"))

        card = self._card()
        card.setObjectName("AboutCard")

        card_layout = self._card_layout(card)
        card_layout.setContentsMargins(28, 24, 28, 24)
        card_layout.setSpacing(18)

        identity_row = QWidget()
        identity_row.setObjectName("TransparentWidget")

        identity_layout = QHBoxLayout(identity_row)
        identity_layout.setContentsMargins(0, 0, 0, 0)
        identity_layout.setSpacing(16)

        icon_label = QLabel()
        icon_label.setObjectName("AboutAppIcon")
        icon_label.setFixedSize(56, 56)

        if APP_ICON_PATH.exists():
            pixmap = QPixmap(str(APP_ICON_PATH))
            icon_label.setPixmap(
                pixmap.scaled(
                    56,
                    56,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        title_box = QWidget()
        title_box.setObjectName("TransparentWidget")

        title_layout = QVBoxLayout(title_box)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(4)

        app_title = QLabel("XCC Context Collector")
        app_title.setObjectName("AboutTitle")

        app_subtitle = QLabel("AI-ready project context collector")
        app_subtitle.setObjectName("AboutSubtitle")

        app_version = QLabel(f"Version {__version__}")
        app_version.setObjectName("AboutVersion")

        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        title_layout.addWidget(app_version)

        identity_layout.addWidget(icon_label)
        identity_layout.addWidget(title_box, 1)

        card_layout.addWidget(identity_row)

        description = QLabel(
            "XCC helps collect clean project context for AI coding assistants "
            "and copies it directly to the clipboard."
        )
        description.setObjectName("AboutDescription")
        description.setWordWrap(True)
        card_layout.addWidget(description)

        badges_row = QWidget()
        badges_row.setObjectName("TransparentWidget")

        badges_layout = QHBoxLayout(badges_row)
        badges_layout.setContentsMargins(0, 0, 0, 0)
        badges_layout.setSpacing(10)

        for badge_text in ["Local-first", "No cloud", "Windows utility", "Tray-ready"]:
            badges_layout.addWidget(self._about_badge(badge_text))

        badges_layout.addStretch(1)
        card_layout.addWidget(badges_row)

        paths_title = QLabel("Paths")
        paths_title.setObjectName("AboutSectionTitle")
        card_layout.addWidget(paths_title)

        card_layout.addWidget(
            self._about_info_row(
                "Config file",
                r"%USERPROFILE%\.xcc\config.json",
            )
        )
        card_layout.addWidget(
            self._about_info_row(
                "Startup folder",
                "shell:startup",
            )
        )
        card_layout.addWidget(
            self._about_info_row(
                "Default hotkey",
                DEFAULT_HOTKEY,
            )
        )

        footer = QLabel("Built for fast AI-context workflow.")
        footer.setObjectName("AboutFooter")
        card_layout.addWidget(footer)

        layout.addWidget(card)
        layout.addStretch(1)

        return page

    def _section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SectionTitle")
        return label

    def _card_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("CardTitle")
        label.setFixedHeight(18)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return label

    def _card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("Card")
        return card
    
    def _card_layout(self, card: QFrame) -> QVBoxLayout:
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        return layout
    
    def _add_history_entry(
        self,
        *,
        mode_name: str,
        source: str,
        files: int,
        lines: int,
        source_chars: int,
        output_chars: int,
        output_tokens: int,
        truncated: bool,
        errors: int,
    ) -> None:
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "mode_name": mode_name,
            "source": source,
            "files": files,
            "lines": lines,
            "source_chars": source_chars,
            "output_chars": output_chars,
            "output_tokens": output_tokens,
            "truncated": truncated,
            "errors": errors,
        }

        self.history_entries.insert(0, entry)
        self._render_history_entries()
        
    def _render_history_entries(self) -> None:
        while self.history_list_layout.count():
            item = self.history_list_layout.takeAt(0)
            widget = item.widget()

            if widget is not None:
                widget.deleteLater()

        if not self.history_entries:
            self.history_list_layout.addWidget(self.history_empty_label)
            self.history_list_layout.addStretch(1)
            return

        for entry in self.history_entries[:20]:
            self.history_list_layout.addWidget(self._history_entry_widget(entry))

        self.history_list_layout.addStretch(1)

    def _history_entry_widget(self, entry: dict[str, object]) -> QWidget:
        row = QFrame()
        row.setObjectName("HistoryEntry")
        row.setFixedHeight(96)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(7)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        time_label = QLabel(str(entry["time"]))
        time_label.setObjectName("HistoryTime")

        mode_label = QLabel(str(entry["mode_name"]))
        mode_label.setObjectName("HistoryModeCapsule")
        mode_label.setFixedHeight(26)

        top_row.addWidget(time_label)
        top_row.addStretch(1)
        top_row.addWidget(mode_label)

        source_label = QLabel(str(entry["source"]))
        source_label.setObjectName("HistorySource")
        source_label.setWordWrap(False)

        stats_label = QLabel(
            f"Files {entry['files']} · "
            f"Lines {entry['lines']} · "
            f"Source {entry['source_chars']} chars · "
            f"Output {entry['output_chars']} chars"
        )
        stats_label.setObjectName("HistoryStats")

        health_label = QLabel(
            f"Tokens {entry['output_tokens']} · "
            f"Truncated {'Yes' if entry['truncated'] else 'No'} · "
            f"Errors {entry['errors']}"
        )
        health_label.setObjectName("HistoryHealth")

        layout.addLayout(top_row)
        layout.addWidget(source_label)
        layout.addWidget(stats_label)
        layout.addWidget(health_label)

        return row
    
    def _about_info_row(self, label: str, value: str) -> QFrame:
        row = QFrame()
        row.setObjectName("AboutInfoRow")
        row.setFixedHeight(42)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(12)

        label_widget = QLabel(label)
        label_widget.setObjectName("AboutInfoLabel")

        value_widget = QLabel(value)
        value_widget.setObjectName("AboutInfoValue")
        value_widget.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(label_widget)
        layout.addWidget(value_widget, 1)

        return row
    
    def _about_badge(self, text: str) -> QLabel:
        badge = QLabel(text)
        badge.setObjectName("AboutBadge")
        badge.setFixedHeight(28)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return badge

    def _metric_capsule(self, label: str, value: str) -> QFrame:
        capsule = QFrame()
        capsule.setObjectName("MetricCapsule")
        capsule.setMinimumWidth(0)
        capsule.setFixedHeight(52)

        layout = QVBoxLayout(capsule)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(2)

        label_widget = QLabel(label)
        label_widget.setObjectName("MetricLabel")

        value_widget = QLabel(value)
        value_widget.setObjectName("MetricValue")

        capsule.value_label = value_widget

        layout.addWidget(label_widget)
        layout.addWidget(value_widget)

        return capsule
    
    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background: #0F0F10;
            }

            QWidget {
                background: #0F0F10;
                color: #F2F2F2;
                font-family: Segoe UI;
                font-size: 13px;
            }

            #Header {
                background: #151515;
                border-bottom: 1px solid #2F2A1C;
            }

            #HeaderTitle {
                font-size: 15px;
                font-weight: 700;
                color: #D6A93A;
                background: transparent;
            }

            #StatusCapsule,
            #HotkeyCapsule {
                background: #1A1A1A;
                border: 1px solid #5A4820;
                border-radius: 10px;
                padding: 4px 12px;
                color: #F2F2F2;
            }

            #HotkeyCapsule {
                color: #D6A93A;
            }

            #Sidebar {
                background: #121212;
                border-right: 1px solid #2F2A1C;
                padding: 10px;
                outline: none;
            }

            #Sidebar::item {
                padding: 12px 14px;
                margin: 4px 0;
                border-radius: 10px;
                color: #C9C9C9;
                background: transparent;
            }

            #Sidebar::item:hover {
                background: #241F10;
                color: #D6A93A;
            }

            #Sidebar::item:selected {
                background: #D6A93A;
                color: #111111;
                font-weight: 700;
            }

            #Sidebar::item:selected:hover {
                background: #E8BE55;
                color: #111111;
            }

            #SectionTitle {
                font-size: 22px;
                font-weight: 700;
                color: #F2F2F2;
                background: transparent;
            }

            #Card {
                background: #161616;
                border: 1px solid #5A4820;
                border-radius: 14px;
            }

            #CardTitle {
                color: #D6A93A;
                font-size: 13px;
                font-weight: 800;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }
            #FieldLabel {
                color: #D6D6D6;
                font-weight: 700;
                background: transparent;
            }

            #FieldLabelSmall {
                color: #B8B8B8;
                background: transparent;
            }

            QLineEdit {
                background: #101010;
                border: 1px solid #5A4820;
                border-radius: 10px;
                padding: 8px 10px;
                color: #F2F2F2;
                selection-background-color: #D6A93A;
                selection-color: #111111;
            }

            QLineEdit:hover {
                border: 1px solid #C79A2E;
            }

            QLineEdit:focus {
                border: 1px solid #D6A93A;
            }

            QPushButton {
                background: #1A1A1A;
                border: 1px solid #5A4820;
                border-radius: 10px;
                padding: 9px 14px;
                color: #F2F2F2;
            }

            QPushButton:hover {
                background: #232323;
                border: 1px solid #D6A93A;
                color: #D6A93A;
            }

            QPushButton:pressed {
                background: #2A2412;
            }

            #PrimaryButton {
                background: #D6A93A;
                color: #111111;
                font-size: 15px;
                font-weight: 800;
                border: 1px solid #D6A93A;
                border-radius: 12px;
            }

            #PrimaryButton:hover {
                background: #E8BE55;
                border: 1px solid #E8BE55;
                color: #111111;
            }

            #PrimaryButton:pressed {
                background: #C99831;
                border: 1px solid #C99831;
            }

            QRadioButton,
            QCheckBox {
                spacing: 8px;
                padding: 2px 0;
                background: transparent;
            }

            QRadioButton:hover,
            QCheckBox:hover {
                color: #D6A93A;
            }

            QRadioButton::indicator,
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background: #101010;
                border: 1px solid #5A4820;
            }

            QRadioButton::indicator {
                border-radius: 8px;
            }

            QCheckBox::indicator {
                border-radius: 4px;
            }

            QRadioButton::indicator:hover,
            QCheckBox::indicator:hover {
                border: 1px solid #D6A93A;
            }

            QRadioButton::indicator:checked,
            QCheckBox::indicator:checked {
                background: #D6A93A;
                border: 1px solid #D6A93A;
            }

            #MetricCapsule {
                background: #181818;
                border: 1px solid #463817;
                border-radius: 10px;
            }

            #MetricCapsule:hover {
                background: #1E1B12;
                border: 1px solid #D6A93A;
            }

            #MetricLabel {
                color: #AFAFAF;
                font-size: 11px;
                background: transparent;
            }

            #MetricValue {
                color: #D6A93A;
                font-size: 15px;
                font-weight: 800;
                background: transparent;
            }

            #StatusBar {
                background: #151515;
                border-top: 1px solid #2F2A1C;
                padding-left: 16px;
                color: #B8B8B8;
            }
            #MetricGroupTitle {
                color: #E0E0E0;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                margin-bottom: 2px;
            }
            #TransparentWidget {
                background: transparent;
            }
            #HistoryEntry {
                background: #181818;
                border: 1px solid #3A3018;
                border-radius: 10px;
            }

            #HistoryEntry:hover {
                background: #1E1B12;
                border: 1px solid #D6A93A;
            }

            #HistoryTime {
                color: #D6A93A;
                font-size: 12px;
                font-weight: 800;
                background: transparent;
            }

            #HistoryModeCapsule {
                background: #101010;
                border: 1px solid #5A4820;
                border-radius: 8px;
                padding: 3px 10px;
                color: #F2F2F2;
                font-size: 11px;
                font-weight: 700;
            }

            #HistorySource {
                color: #D6D6D6;
                font-size: 12px;
                background: transparent;
            }

            #HistoryStats {
                color: #AFAFAF;
                font-size: 11px;
                background: transparent;
            }

            #HistoryHealth {
                color: #8F8F8F;
                font-size: 11px;
                background: transparent;
            }

            #HistoryEmpty {
                color: #8F8F8F;
                font-size: 13px;
                background: transparent;
            }
            #HistoryScrollArea {
                background: transparent;
                border: none;
            }

            #HistoryScrollArea QWidget {
                background: transparent;
            }

            QScrollBar:vertical {
                background: #101010;
                width: 10px;
                margin: 0px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background: #463817;
                min-height: 28px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #D6A93A;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            #PageSubtitle {
                color: #8F8F8F;
                font-size: 12px;
                background: transparent;
                padding: 0px;
                margin: 0px;
            }

            #HeaderAppIcon {
                background: transparent;
            }
            #SettingsSectionTitle {
                color: #D6A93A;
                font-size: 12px;
                font-weight: 800;
                background: transparent;
                margin-top: 0px;
            }
            #SettingsToggle {
                background: transparent;
                border: none;
                color: #D6D6D6;
                font-size: 11px;
                font-weight: 700;
            }

            #SettingsToggle:hover {
                color: #D6A93A;
            }
            #SettingsGroup {
                background: #141414;
                border: 1px solid #2F2A1C;
                border-radius: 12px;
            }

            #SettingsGroup:hover {
                border: 1px solid #5A4820;
            }

            #SettingsRow {
                background: #181818;
                border: 1px solid #2F2A1C;
                border-radius: 10px;
            }

            #SettingsRow:hover {
                background: #1E1B12;
                border: 1px solid #5A4820;
            }

            #SettingsRowTitle {
                color: #F2F2F2;
                font-size: 12px;
                font-weight: 800;
                background: transparent;
            }

            #SettingsRowDescription {
                color: #8F8F8F;
                font-size: 11px;
                background: transparent;
            }

            #SettingsRowValue {
                color: #D6A93A;
                font-size: 13px;
                font-weight: 800;
                background: transparent;
                min-width: 110px;
            }
            #AboutCard {
                background: #161616;
                border: 1px solid #5A4820;
                border-radius: 14px;
            }

            #AboutAppIcon {
                background: transparent;
            }

            #AboutTitle {
                color: #F2F2F2;
                font-size: 22px;
                font-weight: 800;
                background: transparent;
            }

            #AboutSubtitle {
                color: #D6A93A;
                font-size: 14px;
                font-weight: 700;
                background: transparent;
            }

            #AboutVersion {
                color: #8F8F8F;
                font-size: 12px;
                background: transparent;
            }

            #AboutDescription {
                color: #C9C9C9;
                font-size: 13px;
                background: transparent;
            }

            #AboutBadge {
                background: #181818;
                border: 1px solid #2F2A1C;
                border-radius: 10px;
                padding: 4px 12px;
                color: #D6A93A;
                font-size: 11px;
                font-weight: 800;
            }

            #AboutBadge:hover {
                background: #1E1B12;
                border: 1px solid #5A4820;
            }

            #AboutSectionTitle {
                color: #D6A93A;
                font-size: 13px;
                font-weight: 800;
                background: transparent;
            }

            #AboutInfoRow {
                background: #181818;
                border: 1px solid #2F2A1C;
                border-radius: 10px;
            }

            #AboutInfoLabel {
                color: #AFAFAF;
                font-size: 11px;
                font-weight: 700;
                background: transparent;
            }

            #AboutInfoValue {
                color: #D6A93A;
                font-size: 12px;
                font-weight: 800;
                background: transparent;
            }

            #AboutFooter {
                color: #8F8F8F;
                font-size: 12px;
                background: transparent;
                padding-top: 4px;
            }
            #SourceInputBox {
                background: #101010;
                border: 1px solid #5A4820;
                border-radius: 10px;
            }

            #SourceInputBox:hover {
                border: 1px solid #C79A2E;
            }

            #SourceInputEmbedded {
                background: transparent;
                border: none;
                border-radius: 0px;
                padding: 0px;
                color: #F2F2F2;
                selection-background-color: #D6A93A;
                selection-color: #111111;
            }

            #SourceInputEmbedded:hover,
            #SourceInputEmbedded:focus {
                border: none;
            }

            #ClearSourceButton {
                background: transparent;
                border: 1px solid #5A4820;
                border-radius: 12px;
                color: #D6A93A;
                font-size: 14px;
                font-weight: 800;
                padding: 0px;
                margin: 0px;
                text-align: center;
            }

            #ClearSourceButton:hover {
                background: #2A2412;
                border: 1px solid #D6A93A;
                color: #F2F2F2;
            }

            #ClearSourceButton:pressed {
                background: #D6A93A;
                border: 1px solid #D6A93A;
                color: #111111;
            }
            """
        )


def run_gui() -> None:
    app = QApplication(sys.argv)

    instance_lock = QLockFile(str(INSTANCE_LOCK_PATH))
    instance_lock.setStaleLockTime(0)

    if not instance_lock.tryLock(100):
        if _notify_existing_instance():
            sys.exit(0)

        try:
            instance_lock.removeStaleLockFile()
        except Exception:
            pass

        if not instance_lock.tryLock(100):
            QMessageBox.warning(
                None,
                "XCC",
                (
                    "XCC could not start because the single-instance lock is active, "
                    "but no existing instance responded.\n\n"
                    f"Lock file:\n{INSTANCE_LOCK_PATH}\n\n"
                    "Close old XCC processes or delete the lock file manually."
                ),
            )
            sys.exit(1)

    window: XccMainWindow | None = None

    try:
        window = XccMainWindow()
        window._single_instance_server = SingleInstanceServer(window)
        window._setup_global_hotkey()

        tray_ready = hasattr(window, "tray_icon") and window.tray_icon.isVisible()

        if window.app_settings.start_minimized_to_tray and tray_ready:
            window.hide()
        else:
            window._show_main_window()

        exit_code = app.exec()

    finally:
        if window is not None:
            window._cleanup_global_hotkey()

        instance_lock.unlock()

    sys.exit(exit_code)