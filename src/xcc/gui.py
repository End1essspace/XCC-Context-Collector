from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from PySide6.QtCore import QEvent, QObject, QLockFile, QSize, QThread, Qt, QTimer, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QGridLayout,
    QScrollArea,
)
from PySide6.QtGui import (
    QAction,
    QIcon,
    QIntValidator,
    QKeySequence,
    QPixmap,
    QShortcut,
)
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtSvg import QSvgRenderer
from . import __version__
from .config import DEFAULT_HOTKEY, MAX_OUTPUT_CHARS, qt_context_file_filter
from pathlib import Path
from .clipboard import copy_to_clipboard
from .git_utils import is_git_repository
from .settings import AppSettings, load_settings_result, save_settings
from .autostart import is_autostart_enabled, set_autostart_enabled
from .native_hotkey import NativeHotkeyError, NativeHotkeyManager
from .models import CollectionOutcome, CollectionRunRecord, SafetyWarning
from .pipeline import CollectionJobResult, CollectionRequest
from .qt_worker import CollectionWorker
from .safety import (
    build_warning_confirmation_text,
    should_show_safety_confirmation,
)
from .resources import resource_path
from .ui_components import (
    MetricCapsule,
    PageHeader,
    make_card,
    make_card_layout,
    make_card_title,
    make_helper_text,
    make_icon_title,
    make_page_header,
    make_primary_button,
    make_runtime_status_capsule,
    make_tinted_svg_icon,
    make_secondary_button,
    make_section_title,
    make_status_capsule,
    set_metric_value,
    set_tinted_button_icon,
    set_widget_property,
    set_widget_state,
)
from .ui_collect import (
    COLLECT_PAGE_SUBTITLE,
    COLLECT_PAGE_TITLE,
    COMPACT_MODE_HELPER,
    collect_mode_presentation,
    selected_files_source_summary,
)
from .ui_shell import RuntimeState, default_footer_message
from .ui_sidebar import SidebarNavigation
from .ui_metrics import (
    coverage_metric_state,
    format_metric_integer,
    issues_metric_state,
    outcome_metric_state,
    truncation_metric_state,
)
from .ui_theme import (
    METRICS,
    PALETTE,
    build_application_stylesheet,
    build_tray_menu_stylesheet,
)
from .ui_responsive import (
    CollectGeometrySpec,
    CollectLayoutMode,
    CollectLayoutSpec,
    collect_content_min_height,
    collect_geometry_spec,
    collect_layout_spec,
)
from .path_list_parser import parse_path_list
from .selected_files_importer import (
    SelectedFilesImportResult,
    import_selected_files,
    infer_project_root,
)
from .selected_files_review import (
    build_selected_file_review,
    remove_selected_file_indices,
    review_project_root,
)

APP_ICON_PATH = resource_path("assets", "xcc_app.ico")
APP_IMAGE_PATH = resource_path("assets", "xcc_app.png")
TRAY_ICON_PATH = resource_path("assets", "xcc_tray.ico")
TRAY_IMAGE_PATH = resource_path("assets", "xcc_tray.png")
NAV_COLLECT_ICON_PATH = resource_path("assets", "nav-collect.svg")
NAV_HISTORY_ICON_PATH = resource_path("assets", "nav-history.svg")
NAV_SETTINGS_ICON_PATH = resource_path("assets", "nav-settings.svg")
NAV_ABOUT_ICON_PATH = resource_path("assets", "nav-about.svg")
UI_SETUP_ICON_PATH = resource_path("assets", "ui-setup.svg")
UI_LAST_RUN_ICON_PATH = resource_path("assets", "ui-last-run.svg")
UI_VOLUME_ICON_PATH = resource_path("assets", "ui-volume.svg")
UI_OUTPUT_ICON_PATH = resource_path("assets", "ui-output.svg")
UI_COVERAGE_ICON_PATH = resource_path("assets", "ui-coverage.svg")
UI_HEALTH_ICON_PATH = resource_path("assets", "ui-health.svg")
UI_PASTE_PATHS_ICON_PATH = resource_path("assets", "ui-paste-paths.svg")
UI_COLLECT_COPY_ICON_PATH = resource_path("assets", "ui-collect-copy.svg")
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



class ClickableSourceLineEdit(QLineEdit):
    """Read-only source summary that opens Selected Files review on click."""

    clicked = Signal()

    def mouseReleaseEvent(self, event) -> None:
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            self.clicked.emit()

    def keyPressEvent(self, event) -> None:
        if event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space}:
            self.clicked.emit()
            event.accept()
            return

        super().keyPressEvent(event)


class SelectedFilesReviewDialog(QDialog):
    """Review and edit the current Selected Files collection before a run."""

    def __init__(
        self,
        paths: list[Path],
        *,
        project_root: Path | None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("SelectedFilesReviewDialog")
        self.setWindowTitle("Selected Files")
        self.setModal(True)
        self.setMinimumSize(700, 480)
        self.resize(780, 540)

        self._original_paths = tuple(paths)
        self._selected_paths = list(paths)
        self.project_root = review_project_root(
            self._selected_paths,
            preferred_root=project_root,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(12)

        title = QLabel("Selected Files")
        title.setObjectName("DialogTitle")

        self.count_label = QLabel()
        self.count_label.setObjectName("SelectedFilesCount")
        self.count_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        title_row.addWidget(title)
        title_row.addStretch(1)
        title_row.addWidget(self.count_label)
        layout.addLayout(title_row)

        description = make_helper_text(
            "Review relative paths, remove individual files, or clear the "
            "selection before collecting context.",
            object_name="DialogDescription",
        )
        layout.addWidget(description)

        root_label = QLabel("Project root")
        root_label.setObjectName("FieldLabel")
        layout.addWidget(root_label)

        self.root_value = QLineEdit()
        self.root_value.setObjectName("ReviewRootInput")
        self.root_value.setReadOnly(True)
        self.root_value.setFixedHeight(40)
        layout.addWidget(self.root_value)

        files_label = QLabel("Files")
        files_label.setObjectName("FieldLabel")
        layout.addWidget(files_label)

        self.files_list = QListWidget()
        self.files_list.setObjectName("SelectedFilesReviewList")
        self.files_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.files_list.setAlternatingRowColors(False)
        self.files_list.setMinimumHeight(250)
        self.files_list.itemSelectionChanged.connect(
            self._refresh_action_states
        )
        layout.addWidget(self.files_list, 1)

        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(10)

        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.setFixedHeight(40)
        self.remove_button.setMinimumWidth(150)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.setFixedHeight(40)
        self.clear_button.setMinimumWidth(110)

        actions_row.addWidget(self.remove_button)
        actions_row.addWidget(self.clear_button)
        actions_row.addStretch(1)
        layout.addLayout(actions_row)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(0, 0, 0, 0)
        footer_row.setSpacing(10)
        footer_row.addStretch(1)

        self.cancel_button = make_secondary_button(
            "Cancel",
            minimum_width=100,
        )

        self.apply_button = make_primary_button(
            "Apply Changes",
            object_name="DialogPrimaryButton",
            minimum_width=138,
        )

        footer_row.addWidget(self.cancel_button)
        footer_row.addWidget(self.apply_button)
        layout.addLayout(footer_row)

        self.remove_button.clicked.connect(self._remove_selected)
        self.clear_button.clicked.connect(self._clear_all)
        self.cancel_button.clicked.connect(self.reject)
        self.apply_button.clicked.connect(self.accept)

        self.delete_shortcut = QShortcut(
            QKeySequence(Qt.Key.Key_Delete),
            self.files_list,
        )
        self.delete_shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
        self.delete_shortcut.activated.connect(self._remove_selected)

        self._render_files()

    @property
    def selected_paths(self) -> list[Path]:
        return list(self._selected_paths)

    def _render_files(self) -> None:
        self.files_list.clear()

        review_items = build_selected_file_review(
            self._selected_paths,
            project_root=self.project_root,
        )
        for review_item in review_items:
            item = QListWidgetItem(review_item.display_path)
            item.setToolTip(str(review_item.path))
            item.setData(
                Qt.ItemDataRole.UserRole,
                str(review_item.path),
            )
            self.files_list.addItem(item)

        count = len(self._selected_paths)
        self.count_label.setText(
            f"{count} file{'s' if count != 1 else ''}"
        )
        self.root_value.setText(
            str(self.project_root)
            if self.project_root is not None
            else "Mixed locations"
        )
        self.root_value.setToolTip(self.root_value.text())
        self._refresh_action_states()

    def _refresh_action_states(self) -> None:
        self.remove_button.setEnabled(bool(self.files_list.selectedItems()))
        self.clear_button.setEnabled(bool(self._selected_paths))
        self.apply_button.setEnabled(
            tuple(self._selected_paths) != self._original_paths
        )

    def _remove_selected(self) -> None:
        rows = [self.files_list.row(item) for item in self.files_list.selectedItems()]
        if not rows:
            return

        self._selected_paths = list(
            remove_selected_file_indices(self._selected_paths, rows)
        )
        self.project_root = review_project_root(
            self._selected_paths,
            preferred_root=self.project_root,
        )
        self._render_files()

    def _clear_all(self) -> None:
        self._selected_paths = []
        self.project_root = None
        self._render_files()


class PastePathsDialog(QDialog):
    """Resolve pasted AI file lists against one visible project root."""

    def __init__(
        self,
        text: str,
        *,
        existing_paths: list[Path],
        initial_root: Path | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.setObjectName("PastePathsDialog")
        self.setWindowTitle("Paste File Paths")
        self.setModal(True)
        self.setMinimumSize(680, 470)
        self.resize(760, 520)

        self._existing_paths = list(existing_paths)
        self.import_result = SelectedFilesImportResult()
        self.project_root: Path | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        title = QLabel("Paste File Paths")
        title.setObjectName("DialogTitle")

        description = make_helper_text(
            "Choose the project root once. Relative paths from the pasted "
            "AI response will be resolved and validated before they are added.",
            object_name="DialogDescription",
        )

        layout.addWidget(title)
        layout.addWidget(description)

        root_label = QLabel("Project root")
        root_label.setObjectName("FieldLabel")
        layout.addWidget(root_label)

        root_row = QHBoxLayout()
        root_row.setContentsMargins(0, 0, 0, 0)
        root_row.setSpacing(10)

        self.root_input = QLineEdit(
            str(initial_root) if initial_root is not None else ""
        )
        self.root_input.setPlaceholderText("Select the repository or project folder")
        self.root_input.setFixedHeight(40)

        self.browse_button = QPushButton("Browse")
        self.browse_button.setFixedHeight(40)
        self.browse_button.setMinimumWidth(104)

        root_row.addWidget(self.root_input, 1)
        root_row.addWidget(self.browse_button)
        layout.addLayout(root_row)

        paths_label = QLabel("File paths")
        paths_label.setObjectName("FieldLabel")
        layout.addWidget(paths_label)

        self.paths_input = QPlainTextEdit()
        self.paths_input.setObjectName("PathListInput")
        self.paths_input.setPlainText(text)
        self.paths_input.setPlaceholderText(
            "src/package/module.py\ndocs/ROADMAP.md"
        )
        self.paths_input.setMinimumHeight(210)
        layout.addWidget(self.paths_input, 1)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("DialogSummary")
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)

        button_row = QHBoxLayout()
        button_row.setContentsMargins(0, 0, 0, 0)
        button_row.setSpacing(10)
        button_row.addStretch(1)

        self.cancel_button = make_secondary_button(
            "Cancel",
            minimum_width=100,
        )

        self.add_button = make_primary_button(
            "Add Files",
            object_name="DialogPrimaryButton",
            minimum_width=132,
        )

        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.add_button)
        layout.addLayout(button_row)

        self.browse_button.clicked.connect(self._browse_root)
        self.cancel_button.clicked.connect(self.reject)
        self.add_button.clicked.connect(self._accept_import)
        self.root_input.textChanged.connect(self._refresh_preview)
        self.paths_input.textChanged.connect(self._refresh_preview)

        self._refresh_preview()

    def _browse_root(self) -> None:
        initial = self.root_input.text().strip()
        selected = QFileDialog.getExistingDirectory(
            self,
            "Select project root",
            initial,
        )
        if selected:
            self.root_input.setText(selected)

    def _refresh_preview(self) -> None:
        root_text = self.root_input.text().strip()
        root = Path(root_text) if root_text else None
        result = import_selected_files(
            self.paths_input.toPlainText(),
            project_root=root,
            existing_paths=self._existing_paths,
        )
        self.import_result = result

        if not result.parsed:
            summary = "No file paths were detected in the pasted text."
        elif result.root_required:
            summary = (
                f"Detected {len(result.parsed)} path(s). Choose a project root "
                "to resolve relative paths."
            )
        elif result.root_error:
            summary = result.root_error
        else:
            other_issues = max(
                0,
                result.issue_count - len(result.missing),
            )
            summary = (
                f"Found {result.added_count} file(s) · "
                f"Missing {len(result.missing)} · "
                f"Duplicates {result.duplicate_count} · "
                f"External {len(result.external)} · "
                f"Other issues {other_issues}"
            )

        self.summary_label.setText(summary)
        self.add_button.setEnabled(result.can_apply)
        self.add_button.setText(
            f"Add {result.added_count} File"
            f"{'s' if result.added_count != 1 else ''}"
        )

    def _accept_import(self) -> None:
        if not self.import_result.can_apply:
            return

        root_text = self.root_input.text().strip()
        if root_text:
            root = Path(root_text)
            try:
                resolved = root.resolve(strict=True)
            except (OSError, RuntimeError):
                resolved = None

            if resolved is not None and resolved.is_dir():
                self.project_root = resolved

        self.accept()


class XccMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("XCC Context Collector")
        if APP_ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(APP_ICON_PATH)))
        self.setMinimumSize(920, 620)
        self.resize(1480, 840)

        self.selected_paths: list[Path] = []
        self.project_root: Path | None = None
        self._recent_project_root: Path | None = None
        self.history_entries: list[CollectionRunRecord] = []
        settings_result = load_settings_result()
        self.app_settings: AppSettings = settings_result.settings
        self._settings_recovery_message = settings_result.message
        self._is_loading_settings = True
        self._is_quitting = False
        self._has_shown_tray_hint = False
        self._hotkey_manager: NativeHotkeyManager | None = None
        self._hotkey_available = False
        self._hotkey_status_message = "Not registered"
        self._collection_thread: QThread | None = None
        self._collection_worker: CollectionWorker | None = None
        self._active_collection_request: CollectionRequest | None = None
        self._collection_active = False
        self._close_after_collection = False
        self._quit_after_collection = False
        self._footer_status_revision = 0
        self._collect_layout_mode: CollectLayoutMode | None = None
        self._collect_layout_spec: CollectLayoutSpec | None = None
        self._collect_geometry_spec: CollectGeometrySpec | None = None
        self._effective_setup_height = 0
        self._effective_stats_min_height = 0

        self._setup_ui()
        self._apply_collect_layout(force=True)
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

        status_bar = QFrame()
        status_bar.setObjectName("StatusBar")
        status_bar.setFixedHeight(METRICS.footer_height)

        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(22, 0, 22, 0)
        status_layout.setSpacing(12)

        self.footer_status_dot = QLabel()
        self.footer_status_dot.setObjectName("FooterStatusDot")
        self.footer_status_dot.setFixedSize(9, 9)
        set_widget_state(
            self.footer_status_dot,
            RuntimeState.READY.semantic_state,
        )

        self.status_label = QLabel("Ready · Select a source to begin")
        self.status_label.setObjectName("StatusText")

        self.status_version_label = QLabel(f"v{__version__}")
        self.status_version_label.setObjectName("StatusVersion")
        self.status_version_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        status_layout.addWidget(
            self.footer_status_dot,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        status_layout.addWidget(self.status_label, 1)
        status_layout.addWidget(self.status_version_label)

        root_layout.addWidget(status_bar)

        self.setCentralWidget(root)

        self.nav.currentRowChanged.connect(self._change_page)
        self.nav.setCurrentRow(0)

        self.select_source_button.clicked.connect(self._select_source)
        self.clear_source_button.clicked.connect(self._clear_source)
        self.mode_group.buttonClicked.connect(self._on_mode_changed)
        self.collect_button.clicked.connect(self._on_collect_button_clicked)
        self.compact_checkbox.stateChanged.connect(self._on_settings_changed)
        self.max_chars_input.editingFinished.connect(self._on_settings_changed)
        self.start_with_windows_checkbox.stateChanged.connect(self._on_autostart_changed)
        self.start_minimized_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.start_maximized_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.close_to_tray_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.tray_notifications_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.safety_confirmation_checkbox.stateChanged.connect(self._on_behavior_settings_changed)
        self.paste_paths_button.clicked.connect(self._paste_paths_from_clipboard)
        self.source_input.clicked.connect(self._open_selected_files_review)

        self.paste_paths_shortcut = QShortcut(
            QKeySequence(QKeySequence.StandardKey.Paste),
            self,
        )
        self.paste_paths_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.paste_paths_shortcut.activated.connect(self._on_paste_paths_shortcut)
        self._refresh_source_controls()

    def _setup_global_hotkey(self) -> None:
        self._cleanup_global_hotkey()

        manager = NativeHotkeyManager(self._restore_from_hotkey)

        try:
            manager.register(DEFAULT_HOTKEY)
        except NativeHotkeyError as exc:
            self._hotkey_manager = None
            self._hotkey_available = False
            self._hotkey_status_message = f"Unavailable: {exc}"
            self.hotkey_capsule.setText("Hotkey unavailable")
            self.hotkey_capsule.set_state("warning")
            self._set_runtime_state(RuntimeState.WARNINGS)
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
        self.hotkey_capsule.setText(f"Hotkey: {DEFAULT_HOTKEY}")
        self.hotkey_capsule.set_state(None)
        self._set_runtime_state(RuntimeState.READY)
        self._restore_default_footer_status()
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

        self._clear_source(announce=False)
        self._refresh_source_controls()
        self._set_status("Collection mode changed.")
    
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
            self._recent_project_root = self.project_root
            self._set_status("Loaded saved settings.")

        try:
            real_autostart_state = is_autostart_enabled()
        except Exception:
            real_autostart_state = self.app_settings.start_with_windows

        self.app_settings.start_with_windows = real_autostart_state

        if hasattr(self, "start_with_windows_checkbox"):
            self.start_with_windows_checkbox.setChecked(real_autostart_state)

        self._refresh_source_controls()
        self._restore_default_footer_status()

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
            confirm_safety_warnings=self.safety_confirmation_checkbox.isChecked(),
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

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        icon_path = next(
            (
                path
                for path in (TRAY_ICON_PATH, TRAY_IMAGE_PATH, APP_ICON_PATH, APP_IMAGE_PATH)
                if path.exists()
            ),
            None,
        )
        tray_icon = QIcon(str(icon_path)) if icon_path is not None else self.windowIcon()
        if tray_icon.isNull():
            self._set_event_status("Tray icon asset is unavailable.")
            return

        self.tray_icon = QSystemTrayIcon(tray_icon, self)
        self.tray_icon.setToolTip("XCC Context Collector")

        tray_menu = QMenu(self)
        tray_menu.setObjectName("TrayMenu")
        tray_menu.setStyleSheet(build_tray_menu_stylesheet())

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

    def _set_runtime_state(self, state: RuntimeState) -> None:
        self.header_status.setText(state.label)
        self.header_status.set_state(state.semantic_state)
        set_widget_state(self.footer_status_dot, state.semantic_state)

    def _default_footer_message(self) -> str:
        mode = self._current_mode() if hasattr(self, "mode_group") else "folder"
        return default_footer_message(
            mode=mode,
            selected_count=len(self.selected_paths),
            has_source=self.project_root is not None,
        )

    def _restore_default_footer_status(self) -> None:
        self._footer_status_revision += 1
        self.status_label.setText(self._default_footer_message())

    def _set_transient_event_status(
        self,
        message: str,
        timeout_ms: int = 1800,
    ) -> None:
        self._footer_status_revision += 1
        revision = self._footer_status_revision
        self.status_label.setText(message)

        def restore() -> None:
            if revision != self._footer_status_revision:
                return
            self._restore_default_footer_status()

        QTimer.singleShot(timeout_ms, restore)

    def _set_event_status(self, message: str) -> None:
        self._footer_status_revision += 1
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
        if self._collection_active:
            self._quit_after_collection = True
            self._cancel_collection()
            return

        self._complete_quit_from_tray()

    def _complete_quit_from_tray(self) -> None:
        self._is_quitting = True

        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()

        self._cleanup_global_hotkey()
        QApplication.quit()

    def _shutdown_collection_worker(self) -> None:
        worker = self._collection_worker
        thread = self._collection_thread

        if worker is not None:
            try:
                worker.request_cancel()
            except RuntimeError:
                pass

        if thread is not None and thread.isRunning():
            thread.quit()
            thread.wait()

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

        if self._collection_active:
            self._close_after_collection = True
            self._cancel_collection()
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

    def _build_nav(self) -> SidebarNavigation:
        return SidebarNavigation(
            app_icon_path=APP_IMAGE_PATH,
            items=(
                (NAV_COLLECT_ICON_PATH, "Collect"),
                (NAV_HISTORY_ICON_PATH, "History"),
                (NAV_SETTINGS_ICON_PATH, "Settings"),
                (NAV_ABOUT_ICON_PATH, "About"),
            ),
            parent=self,
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "collect_page_layout"):
            QTimer.singleShot(0, self._apply_collect_layout)

    def eventFilter(self, watched, event) -> bool:
        if (
            hasattr(self, "collect_page_scroll")
            and watched is self.collect_page_scroll.viewport()
            and event.type() == QEvent.Type.Resize
        ):
            QTimer.singleShot(0, self._apply_collect_layout)
        return super().eventFilter(watched, event)

    def _collect_viewport_size(self) -> QSize:
        if not hasattr(self, "collect_page_scroll"):
            return QSize(max(0, self.width()), max(0, self.height()))

        viewport = self.collect_page_scroll.viewport()
        size = viewport.size()
        if size.width() <= 0:
            size.setWidth(max(0, self.pages.width()))
        if size.height() <= 0:
            size.setHeight(max(0, self.pages.height()))
        return size

    def _apply_collect_layout(self, *, force: bool = False) -> None:
        viewport_size = self._collect_viewport_size()
        spec = collect_layout_spec(
            viewport_size.width(),
            current_mode=self._collect_layout_mode,
        )
        geometry = collect_geometry_spec(spec, viewport_size.height())
        width_mode_changed = force or spec.mode is not self._collect_layout_mode

        self._collect_layout_mode = spec.mode
        self._collect_layout_spec = spec
        self._collect_geometry_spec = geometry
        self.nav.set_sidebar_width(spec.sidebar_width)

        if width_mode_changed:
            self.collect_page_header.subtitle_label.setVisible(spec.show_subtitle)
            self.source_helper_label.setVisible(spec.show_source_helper)
            self.options_helper_label.setVisible(spec.show_options_helper)
            self._arrange_mode_buttons(spec)
            self._arrange_source_controls(spec)
            self._arrange_metric_groups(spec)

        self._apply_collect_geometry(spec, geometry)
        QTimer.singleShot(0, self._sync_collect_scroll_policy)

        if width_mode_changed:
            QTimer.singleShot(0, self._apply_collect_layout)

    def _apply_collect_geometry(
        self,
        spec: CollectLayoutSpec,
        geometry: CollectGeometrySpec,
    ) -> None:
        compact = spec.mode is CollectLayoutMode.COMPACT
        medium = spec.mode is CollectLayoutMode.MEDIUM

        self.collect_page_layout.setContentsMargins(
            spec.page_margin,
            geometry.page_top_margin,
            spec.page_margin,
            geometry.page_bottom_margin,
        )
        self.collect_page_layout.setSpacing(geometry.page_gap)

        setup_horizontal = 18 if compact else 20 if medium else 22
        setup_top = 15 if compact else 16 if medium else 18
        setup_bottom = 15 if compact else 16 if medium else 18
        self.setup_card_layout.setContentsMargins(
            setup_horizontal,
            setup_top,
            setup_horizontal,
            setup_bottom,
        )
        self.setup_card_layout.setSpacing(10 if compact else 11 if medium else 12)
        self.setup_grid.setHorizontalSpacing(10 if compact else 12 if medium else 14)
        self.setup_grid.setVerticalSpacing(6 if compact else 7 if medium else 8)
        self.setup_card.setMinimumHeight(0)
        self.setup_card.setMaximumHeight(16_777_215)
        self.setup_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        stats_horizontal = 18 if compact else 21 if medium else 24
        stats_vertical = 16 if compact else 18 if medium else 20
        self.stats_card_layout.setContentsMargins(
            stats_horizontal,
            stats_vertical,
            stats_horizontal,
            stats_vertical,
        )
        self.stats_card_layout.setSpacing(12 if compact else 14 if medium else 16)
        self.stats_card.setMinimumHeight(0)
        self.stats_card.setMaximumHeight(16_777_215)
        self.stats_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.mode_buttons_layout.setHorizontalSpacing(
            14 if compact else 18 if medium else 20
        )
        self.mode_buttons_layout.setVerticalSpacing(8)
        self.source_controls_layout.setHorizontalSpacing(
            10 if compact else 12 if medium else 14
        )
        self.source_controls_layout.setVerticalSpacing(8 if compact else 10)
        self.metrics_layout.setHorizontalSpacing(spec.metric_group_gap)
        self.metrics_layout.setVerticalSpacing(spec.metric_group_gap)

        for metric in self.metric_capsules:
            metric.set_density(
                geometry.metric_preferred_height,
                minimum_height=geometry.metric_min_height,
                maximum_height=geometry.metric_max_height,
                horizontal_padding=spec.metric_horizontal_padding,
            )

        for group in self.metric_groups:
            group_layout = group.layout()
            if group_layout is not None:
                group_layout.setSpacing(6 if compact else 7 if medium else 8)

        self._effective_setup_height = max(
            geometry.setup_card_height,
            self.setup_card.minimumSizeHint().height(),
        )
        self.setup_card.setFixedHeight(self._effective_setup_height)

        self._effective_stats_min_height = max(
            geometry.stats_card_min_height,
            self.stats_card.minimumSizeHint().height(),
        )
        self.stats_card.setMinimumHeight(self._effective_stats_min_height)
        self.stats_card.setMaximumHeight(
            max(
                self._effective_stats_min_height,
                geometry.stats_card_max_height,
            )
        )

        self.collect_button.setFixedHeight(spec.primary_action_height)
        self.collect_button.setMinimumHeight(spec.primary_action_height)

    def _sync_collect_scroll_policy(self) -> None:
        """Use vertical scrolling only when natural content cannot fit."""

        if (
            self._collect_layout_spec is None
            or self._collect_geometry_spec is None
            or not hasattr(self, "collect_page_scroll")
            or not hasattr(self, "collect_page_content")
        ):
            return

        spec = self._collect_layout_spec
        geometry = self._collect_geometry_spec
        available_height = self.collect_page_scroll.viewport().height()
        required_height = (
            collect_content_min_height(spec, geometry)
            + max(0, self._effective_setup_height - geometry.setup_card_height)
            + max(
                0,
                self._effective_stats_min_height - geometry.stats_card_min_height,
            )
        )
        fits = available_height >= required_height

        if fits:
            self.collect_page_content.setMinimumHeight(0)
            policy = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        else:
            self.collect_page_content.setMinimumHeight(required_height)
            policy = Qt.ScrollBarPolicy.ScrollBarAsNeeded

        if self.collect_page_scroll.verticalScrollBarPolicy() != policy:
            self.collect_page_scroll.setVerticalScrollBarPolicy(policy)

    def _arrange_mode_buttons(self, spec: CollectLayoutSpec) -> None:
        self._take_layout_items(self.mode_buttons_layout)
        self._reset_grid_stretches(self.mode_buttons_layout, columns=4, rows=2)
        columns = max(1, spec.mode_columns)

        for index, button in enumerate(self.mode_buttons_list):
            row = index // columns
            column = index % columns
            self.mode_buttons_layout.addWidget(button, row, column)

        for column in range(4):
            self.mode_buttons_layout.setColumnStretch(
                column,
                1 if column < columns else 0,
            )

    def _arrange_source_controls(self, spec: CollectLayoutSpec) -> None:
        self._take_layout_items(self.source_controls_layout)
        self._reset_grid_stretches(self.source_controls_layout, columns=3, rows=2)
        selected_files_mode = self._current_mode() == "files"

        if not spec.source_actions_below:
            self.source_controls_layout.addWidget(self.source_box, 0, 0)
            self.source_controls_layout.addWidget(self.paste_paths_button, 0, 1)
            self.source_controls_layout.addWidget(self.select_source_button, 0, 2)
            self.source_controls_layout.setColumnStretch(0, 1)
            self.source_controls_layout.setColumnStretch(1, 0)
            self.source_controls_layout.setColumnStretch(2, 0)
            return

        self.source_controls_layout.addWidget(self.source_box, 0, 0, 1, 2)
        if selected_files_mode:
            self.source_controls_layout.addWidget(self.paste_paths_button, 1, 0)
            self.source_controls_layout.addWidget(self.select_source_button, 1, 1)
            self.source_controls_layout.setColumnStretch(0, 1)
            self.source_controls_layout.setColumnStretch(1, 1)
        else:
            self.source_controls_layout.addWidget(
                self.select_source_button,
                1,
                0,
                1,
                2,
            )
            self.source_controls_layout.setColumnStretch(0, 1)
            self.source_controls_layout.setColumnStretch(1, 1)

        self.source_controls_layout.setColumnStretch(2, 0)

    def _arrange_metric_groups(self, spec: CollectLayoutSpec) -> None:
        self._take_layout_items(self.metrics_layout)
        self._reset_grid_stretches(self.metrics_layout, columns=7, rows=2)

        if spec.metric_columns == 4:
            self.metrics_layout.setRowStretch(0, 1)
            for index, group in enumerate(self.metric_groups):
                column = index * 2
                self.metrics_layout.addWidget(group, 0, column)
                self.metrics_layout.setColumnStretch(column, 1)
                if index < len(self.metric_dividers):
                    divider = self.metric_dividers[index]
                    divider.setVisible(True)
                    self.metrics_layout.addWidget(divider, 0, column + 1)
            return

        for divider in self.metric_dividers:
            divider.setVisible(False)

        columns = max(1, spec.metric_columns)
        for index, group in enumerate(self.metric_groups):
            row = index // columns
            column = index % columns
            self.metrics_layout.addWidget(group, row, column)
            self.metrics_layout.setColumnStretch(column, 1)
            self.metrics_layout.setRowStretch(row, 1)

    @staticmethod
    def _take_layout_items(layout) -> None:
        while layout.count():
            layout.takeAt(0)

    @staticmethod
    def _reset_grid_stretches(
        layout: QGridLayout,
        *,
        columns: int,
        rows: int,
    ) -> None:
        for column in range(columns):
            layout.setColumnStretch(column, 0)
        for row in range(rows):
            layout.setRowStretch(row, 0)

    def _build_collect_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setObjectName("CollectPageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        page = QWidget()
        page.setObjectName("CollectPage")
        page.setMinimumWidth(0)
        layout = self._page_layout(page)
        page.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.collect_page_scroll = scroll
        self.collect_page_content = page
        self.collect_page_layout = layout
        scroll.viewport().installEventFilter(self)

        self.header_status = make_runtime_status_capsule("Ready")
        self.header_status.set_state(RuntimeState.READY.semantic_state)
        self.header_status.setAccessibleName("Runtime status")

        self.hotkey_capsule = make_status_capsule(
            f"Hotkey: {DEFAULT_HOTKEY}",
            object_name="HotkeyCapsule",
        )
        self.hotkey_capsule.setAccessibleName("Restore hotkey")

        self.collect_page_header: PageHeader = make_page_header(
            COLLECT_PAGE_TITLE,
            COLLECT_PAGE_SUBTITLE,
        )
        self.collect_page_header.add_action(self.header_status)
        self.collect_page_header.add_action(self.hotkey_capsule)
        layout.addWidget(self.collect_page_header)

        self.setup_card = self._card()
        setup_card = self.setup_card
        setup_card.setFixedHeight(248)

        self.setup_card_layout = self._card_layout(setup_card)
        setup_layout = self.setup_card_layout
        setup_layout.setContentsMargins(22, 18, 22, 18)
        setup_layout.setSpacing(15)
        setup_layout.addWidget(
            make_icon_title(
                "Setup",
                UI_SETUP_ICON_PATH,
                object_name="CardTitleRow",
                text_object_name="CardTitle",
                icon_object_name="CardTitleIcon",
                icon_size=18,
            )
        )

        self.setup_grid = QGridLayout()
        setup_grid = self.setup_grid
        setup_grid.setContentsMargins(0, 2, 0, 0)
        setup_grid.setHorizontalSpacing(14)
        setup_grid.setVerticalSpacing(12)

        mode_label = QLabel("Mode")
        mode_label.setObjectName("FieldLabel")
        mode_label.setFixedWidth(90)

        self.mode_group = QButtonGroup(self)
        self.mode_files = QRadioButton("Selected Files")
        self.mode_folder = QRadioButton("Full Folder")
        self.mode_git = QRadioButton("Git Changed Files")
        self.mode_tree = QRadioButton("Project Tree")

        for button in (
            self.mode_files,
            self.mode_folder,
            self.mode_git,
            self.mode_tree,
        ):
            button.setAccessibleName(f"Collection mode: {button.text()}")

        self.mode_folder.setChecked(True)

        self.mode_buttons = QWidget()
        self.mode_buttons.setObjectName("TransparentWidget")
        self.mode_buttons_layout = QGridLayout(self.mode_buttons)
        self.mode_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.mode_buttons_layout.setHorizontalSpacing(20)
        self.mode_buttons_layout.setVerticalSpacing(8)
        self.mode_buttons_list = [
            self.mode_files,
            self.mode_folder,
            self.mode_git,
            self.mode_tree,
        ]

        for index, button in enumerate(self.mode_buttons_list):
            self.mode_group.addButton(button, index)
            self.mode_buttons_layout.addWidget(button, 0, index)

        source_label = QLabel("Source")
        source_label.setObjectName("FieldLabel")
        source_label.setFixedWidth(90)

        self.source_input = ClickableSourceLineEdit()
        self.source_input.setPlaceholderText("No source selected")
        self.source_input.setReadOnly(True)
        self.source_input.setFixedHeight(38)
        self.source_input.setFrame(False)
        self.source_input.setObjectName("SourceInputEmbedded")
        self.source_input.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.source_input.setAccessibleName("Selected source")

        self.clear_source_button = QPushButton("×")
        self.clear_source_button.setObjectName("ClearSourceButton")
        self.clear_source_button.setFixedSize(24, 24)
        self.clear_source_button.setToolTip("Clear selected source")
        self.clear_source_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.select_source_button = QPushButton("Select Files")
        self.select_source_button.setObjectName("SelectSourceButton")
        self.select_source_button.setMinimumWidth(148)
        self.select_source_button.setFixedHeight(40)
        self.select_source_button.setAccessibleName("Select files")

        self.paste_paths_button = QPushButton("Paste Paths")
        self.paste_paths_button.setObjectName("PastePathsButton")
        self.paste_paths_button.setMinimumWidth(138)
        self.paste_paths_button.setFixedHeight(40)
        self.paste_paths_button.setToolTip(
            "Paste a file list from the clipboard into Selected Files"
        )
        self.paste_paths_button.setAccessibleName(
            "Paste file paths from clipboard"
        )
        self.paste_paths_button.setIcon(
            make_tinted_svg_icon(
                UI_PASTE_PATHS_ICON_PATH,
                18,
                PALETTE.accent,
            )
        )
        self.paste_paths_button.setIconSize(QSize(18, 18))

        self.source_helper_label = make_helper_text(
            "",
            object_name="SourceHelperText",
            word_wrap=False,
        )
        self.source_helper_label.setAccessibleName("Source guidance")

        options_label = QLabel("Options")
        options_label.setObjectName("FieldLabel")
        options_label.setFixedWidth(90)

        self.compact_checkbox = QCheckBox("Compact mode")
        self.compact_checkbox.setAccessibleName("Compact mode")
        self.compact_checkbox.setToolTip(COMPACT_MODE_HELPER)
        self.compact_checkbox.setChecked(True)
        self.compact_checkbox.setFixedHeight(40)

        max_chars_label = QLabel("Max chars")
        max_chars_label.setObjectName("FieldLabelSmall")
        max_chars_label.setFixedHeight(40)

        self.max_chars_input = QLineEdit(str(MAX_OUTPUT_CHARS))
        self.max_chars_input.setValidator(QIntValidator(1, 10_000_000, self))
        self.max_chars_input.setMaximumWidth(160)
        self.max_chars_input.setFixedHeight(40)
        self.max_chars_input.setAccessibleName("Maximum output characters")

        self.options_helper_label = make_helper_text(
            COMPACT_MODE_HELPER,
            object_name="OptionsHelperText",
            word_wrap=False,
        )
        self.options_helper_label.setAccessibleName("Compact mode behavior")

        setup_grid.addWidget(mode_label, 0, 0)
        setup_grid.addWidget(self.mode_buttons, 0, 1, 1, 3)

        self.source_box = QFrame()
        self.source_box.setObjectName("SourceInputBox")
        self.source_box.setFixedHeight(40)
        set_widget_property(self.source_box, "reviewable", False)

        source_box_layout = QHBoxLayout(self.source_box)
        source_box_layout.setContentsMargins(10, 0, 8, 0)
        source_box_layout.setSpacing(6)

        source_box_layout.addWidget(self.source_input, 1)
        source_box_layout.addWidget(
            self.clear_source_button,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )

        self.source_controls = QWidget()
        self.source_controls.setObjectName("TransparentWidget")
        self.source_controls_layout = QGridLayout(self.source_controls)
        self.source_controls_layout.setContentsMargins(0, 0, 0, 0)
        self.source_controls_layout.setHorizontalSpacing(14)
        self.source_controls_layout.setVerticalSpacing(10)
        self.source_controls_layout.addWidget(self.source_box, 0, 0)
        self.source_controls_layout.addWidget(self.paste_paths_button, 0, 1)
        self.source_controls_layout.addWidget(self.select_source_button, 0, 2)
        self.source_controls_layout.setColumnStretch(0, 1)

        setup_grid.addWidget(source_label, 1, 0)
        setup_grid.addWidget(self.source_controls, 1, 1, 1, 3)
        setup_grid.addWidget(self.source_helper_label, 2, 1, 1, 3)

        setup_grid.addWidget(options_label, 3, 0)

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

        setup_grid.addWidget(options_box, 3, 1, 1, 3)
        setup_grid.addWidget(self.options_helper_label, 4, 1, 1, 3)

        setup_grid.setColumnStretch(0, 0)
        setup_grid.setColumnStretch(1, 1)
        setup_grid.setColumnStretch(2, 0)
        setup_grid.setColumnStretch(3, 0)

        setup_layout.addLayout(setup_grid)

        layout.addWidget(setup_card)

        self.stats_card = self._card()
        stats_card = self.stats_card
        stats_card.setMinimumHeight(310)
        stats_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.stats_card_layout = self._card_layout(stats_card)
        stats_layout = self.stats_card_layout
        stats_layout.setContentsMargins(24, 18, 24, 20)
        stats_layout.setSpacing(16)

        stats_header = QWidget()
        stats_header.setObjectName("TransparentWidget")
        stats_header.setFixedHeight(32)
        stats_header_layout = QHBoxLayout(stats_header)
        stats_header_layout.setContentsMargins(0, 0, 0, 0)
        stats_header_layout.setSpacing(12)

        stats_header_layout.addWidget(
            make_icon_title(
                "Last Run",
                UI_LAST_RUN_ICON_PATH,
                object_name="CardTitleRow",
                text_object_name="CardTitle",
                icon_object_name="CardTitleIcon",
                icon_size=18,
            ),
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        stats_header_layout.addStretch(1)

        self.last_run_state_label = QLabel("No collection yet")
        self.last_run_state_label.setObjectName("LastRunState")
        self.last_run_state_label.setFixedHeight(30)
        self.last_run_state_label.setMinimumWidth(150)
        self.last_run_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_header_layout.addWidget(
            self.last_run_state_label,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )

        stats_layout.addWidget(stats_header)

        self.files_metric = self._metric_capsule("Files", "-")
        self.lines_metric = self._metric_capsule("Lines", "-")
        self.source_chars_metric = self._metric_capsule("Source Characters", "-")

        self.output_chars_metric = self._metric_capsule("Output Characters", "-")
        self.tokens_metric = self._metric_capsule("Output Tokens", "-")
        self.truncated_metric = self._metric_capsule("Truncated", "-")

        self.included_metric = self._metric_capsule("Included", "-")
        self.omitted_metric = self._metric_capsule("Omitted", "-")
        self.coverage_metric = self._metric_capsule("Summarized / Partial", "-")

        self.outcome_metric = self._metric_capsule("Outcome", "-")
        self.duration_metric = self._metric_capsule("Duration", "-")
        self.issues_metric = self._metric_capsule("Warnings / Errors", "-")

        self.metrics_layout = QGridLayout()
        self.metrics_layout.setContentsMargins(0, 0, 0, 0)
        self.metrics_layout.setHorizontalSpacing(18)
        self.metrics_layout.setVerticalSpacing(14)

        self.volume_metric_group = self._build_metric_group(
            "Volume",
            UI_VOLUME_ICON_PATH,
            [self.files_metric, self.lines_metric, self.source_chars_metric],
        )
        self.output_metric_group = self._build_metric_group(
            "Output",
            UI_OUTPUT_ICON_PATH,
            [self.output_chars_metric, self.tokens_metric, self.truncated_metric],
        )
        self.coverage_metric_group = self._build_metric_group(
            "Coverage",
            UI_COVERAGE_ICON_PATH,
            [self.included_metric, self.omitted_metric, self.coverage_metric],
        )
        self.health_metric_group = self._build_metric_group(
            "Health",
            UI_HEALTH_ICON_PATH,
            [self.outcome_metric, self.duration_metric, self.issues_metric],
        )
        self.metric_groups = [
            self.volume_metric_group,
            self.output_metric_group,
            self.coverage_metric_group,
            self.health_metric_group,
        ]
        self.metric_capsules = [
            self.files_metric,
            self.lines_metric,
            self.source_chars_metric,
            self.output_chars_metric,
            self.tokens_metric,
            self.truncated_metric,
            self.included_metric,
            self.omitted_metric,
            self.coverage_metric,
            self.outcome_metric,
            self.duration_metric,
            self.issues_metric,
        ]
        self.metric_dividers = [
            self._metric_divider(),
            self._metric_divider(),
            self._metric_divider(),
        ]

        for index, group in enumerate(self.metric_groups):
            column = index * 2
            self.metrics_layout.addWidget(group, 0, column)
            self.metrics_layout.setColumnStretch(column, 1)
            if index < len(self.metric_dividers):
                self.metrics_layout.addWidget(
                    self.metric_dividers[index],
                    0,
                    column + 1,
                )

        stats_layout.addLayout(self.metrics_layout, 1)

        layout.addWidget(stats_card, 1)

        self.collect_button = make_primary_button(
            "Collect && Copy",
            height=METRICS.primary_action_height,
            icon_path=UI_COLLECT_COPY_ICON_PATH,
            icon_size=20,
        )
        self.collect_button.setMinimumHeight(METRICS.primary_action_height)
        self.collect_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        layout.addWidget(self.collect_button, 0)
        layout.setStretch(0, 0)
        layout.setStretch(1, 0)
        layout.setStretch(2, 1)
        layout.setStretch(3, 0)

        scroll.setWidget(page)
        return scroll

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

    def _refresh_source_controls(self) -> None:
        if not hasattr(self, "paste_paths_button"):
            return

        mode = self._current_mode()
        presentation = collect_mode_presentation(mode)
        selected_files_mode = mode == "files"

        self.paste_paths_button.setVisible(
            presentation.paste_paths_visible
        )
        self.select_source_button.setText(presentation.action_label)
        self.select_source_button.setAccessibleName(
            presentation.action_label
        )
        self.select_source_button.setToolTip(presentation.action_label)
        self.source_input.setPlaceholderText(
            presentation.source_placeholder
        )
        self.source_input.setAccessibleDescription(
            presentation.source_helper
        )
        self.source_helper_label.setText(presentation.source_helper)

        if selected_files_mode:
            self.clear_source_button.setToolTip("Clear selected files")
            self.clear_source_button.setAccessibleName("Clear selected files")
            self._refresh_selected_files_source()
            has_source = bool(self.selected_paths)
        else:
            source_text = self.source_input.text().strip()
            self.clear_source_button.setToolTip("Clear selected source")
            self.clear_source_button.setAccessibleName(
                "Clear selected source"
            )
            self.source_input.setCursor(Qt.CursorShape.ArrowCursor)
            self.source_input.setToolTip(source_text)
            set_widget_property(self.source_box, "reviewable", False)
            has_source = self.project_root is not None or bool(source_text)

        self.clear_source_button.setEnabled(
            has_source and not self._collection_active
        )

        if self._collect_layout_spec is not None:
            self._arrange_source_controls(self._collect_layout_spec)

    def _refresh_selected_files_source(self) -> None:
        if not self.selected_paths:
            self.source_input.clear()
            self.source_input.setToolTip("")
            self.source_input.setCursor(Qt.CursorShape.ArrowCursor)
            set_widget_property(self.source_box, "reviewable", False)
            return

        self.source_input.setCursor(Qt.CursorShape.PointingHandCursor)
        set_widget_property(self.source_box, "reviewable", True)

        count = len(self.selected_paths)
        root = self.project_root

        if root is not None and self._all_selected_paths_inside_root(root):
            root_name = root.name or str(root)
            self.source_input.setText(
                selected_files_source_summary(
                    count,
                    project_name=root_name,
                )
            )
            self.source_input.setToolTip(
                f"Project root:\n{root}\n\nClick to review selected files."
            )
            return

        self.source_input.setText(
            selected_files_source_summary(
                count,
                mixed_locations=True,
            )
        )
        self.source_input.setToolTip(
            "Selected files do not share one reliable project root.\n\n"
            "Click to review selected files."
        )

    def _all_selected_paths_inside_root(self, root: Path) -> bool:
        try:
            resolved_root = root.resolve(strict=False)
        except (OSError, RuntimeError):
            return False

        for path in self.selected_paths:
            try:
                path.resolve(strict=False).relative_to(resolved_root)
            except (OSError, RuntimeError, ValueError):
                return False

        return True

    def _on_paste_paths_shortcut(self) -> None:
        if self._collection_active or self._current_mode() != "files":
            return

        focus = QApplication.focusWidget()
        if isinstance(focus, QPlainTextEdit):
            return
        if isinstance(focus, QLineEdit) and not focus.isReadOnly():
            return

        self._paste_paths_from_clipboard()

    def _paste_paths_from_clipboard(self) -> None:
        if self._collection_active or self._current_mode() != "files":
            return

        text = QApplication.clipboard().text()
        parsed = parse_path_list(text)
        if not parsed:
            self._set_status("No file paths found in clipboard.")
            QMessageBox.information(
                self,
                "Paste Paths",
                "The clipboard does not contain a recognizable file list.",
            )
            return

        root = self.project_root
        result = import_selected_files(
            text,
            project_root=root,
            existing_paths=self.selected_paths,
        )

        if result.needs_project_root_selection:
            dialog = PastePathsDialog(
                text,
                existing_paths=self.selected_paths,
                initial_root=self._recent_project_root,
                parent=self,
            )
            if dialog.exec() != QDialog.DialogCode.Accepted:
                self._set_status("Paste paths cancelled.")
                return

            result = dialog.import_result
            if dialog.project_root is not None:
                self.project_root = dialog.project_root
                self._recent_project_root = dialog.project_root

        self._apply_selected_files_import(result)

    def _apply_selected_files_import(
        self,
        result: SelectedFilesImportResult,
    ) -> None:
        if result.added:
            self.selected_paths.extend(result.added)

            if self.project_root is None or not self._all_selected_paths_inside_root(
                self.project_root
            ):
                self.project_root = infer_project_root(self.selected_paths)

            if self.project_root is not None:
                self._recent_project_root = self.project_root

        self._refresh_selected_files_source()
        self._save_current_settings()
        self._refresh_settings_page()

        if result.added_count > 0:
            status_parts = [
                (
                    f"Added {result.added_count} file"
                    f"{'s' if result.added_count != 1 else ''}"
                ),
                f"Total: {len(self.selected_paths)}",
            ]

            if result.duplicate_count:
                status_parts.append(
                    f"{result.duplicate_count} duplicate"
                    f"{'s' if result.duplicate_count != 1 else ''} skipped"
                )

            if result.external:
                status_parts.append(
                    f"{len(result.external)} external"
                )

            if result.issue_count:
                status_parts.append(
                    f"{result.issue_count} path"
                    f"{'s' if result.issue_count != 1 else ''} need review"
                )

            self._set_status(" · ".join(status_parts) + ".")
        elif result.duplicates and result.issue_count == 0:
            self._set_status("All pasted files are already selected.")
        elif result.issue_count:
            self._set_status(
                f"No files added · {result.issue_count} path"
                f"{'s' if result.issue_count != 1 else ''} need review."
            )
        else:
            self._set_status("No files were added from the pasted paths.")

        if result.has_reportable_details:
            self._show_selected_files_import_report(result)


    def _show_selected_files_import_report(
        self,
        result: SelectedFilesImportResult,
    ) -> None:
        lines = [
            f"Added: {result.added_count}",
            f"Already selected: {len(result.duplicates)}",
            f"Not found: {len(result.missing)}",
            f"Directories ignored: {len(result.directories)}",
            f"Unsupported files: {len(result.unsupported)}",
            f"Invalid or outside root: "
            f"{len(result.invalid) + len(result.outside_root)}",
        ]

        detail_groups = (
            ("Not found", result.missing),
            ("Directories ignored", result.directories),
            ("Unsupported files", result.unsupported),
            ("Outside project root", result.outside_root),
            ("Invalid paths", result.invalid),
            ("Already selected", result.duplicates),
        )

        for title, values in detail_groups:
            if not values:
                continue

            lines.extend(["", f"{title}:"])
            lines.extend(f"- {value}" for value in values[:8])
            remaining = len(values) - min(len(values), 8)
            if remaining:
                lines.append(f"- ... {remaining} additional path(s)")

        QMessageBox.information(
            self,
            "Paste Paths Result",
            "\n".join(lines),
        )

    def _open_selected_files_review(self) -> None:
        if (
            self._collection_active
            or self._current_mode() != "files"
            or not self.selected_paths
        ):
            return

        dialog = SelectedFilesReviewDialog(
            self.selected_paths,
            project_root=self.project_root,
            parent=self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        previous_count = len(self.selected_paths)
        self.selected_paths = dialog.selected_paths
        self.project_root = dialog.project_root

        if self.project_root is not None:
            self._recent_project_root = self.project_root

        self._refresh_selected_files_source()
        self._save_current_settings()
        self._refresh_settings_page()

        current_count = len(self.selected_paths)
        if current_count == previous_count:
            self._set_status("Selected files unchanged.")
        elif current_count == 0:
            self._set_status("Selected files cleared.")
        else:
            removed_count = previous_count - current_count
            self._set_status(
                f"Removed {removed_count} file"
                f"{'s' if removed_count != 1 else ''}. "
                f"Total: {current_count}."
            )

    def _select_source(self) -> None:
        mode = self._current_mode()
        presentation = collect_mode_presentation(mode)
        initial_directory = (
            str(self._recent_project_root)
            if self._recent_project_root is not None
            else ""
        )

        if mode == "files":
            selected, _ = QFileDialog.getOpenFileNames(
                self,
                presentation.dialog_title,
                initial_directory,
                qt_context_file_filter(),
            )

            if not selected:
                self._set_status("Source selection cancelled.")
                return

            existing_keys = {
                str(path.resolve(strict=False)).casefold()
                for path in self.selected_paths
            }
            added_count = 0

            for raw_path in selected:
                path = Path(raw_path)
                try:
                    key = str(path.resolve(strict=False)).casefold()
                except (OSError, RuntimeError):
                    key = str(path.absolute()).casefold()

                if key in existing_keys:
                    continue

                self.selected_paths.append(path)
                existing_keys.add(key)
                added_count += 1

            self.project_root = infer_project_root(self.selected_paths)
            if self.project_root is not None:
                self._recent_project_root = self.project_root

            self._refresh_selected_files_source()

            if added_count == 0:
                self._set_status("Selected files already added.")
            else:
                self._set_status(
                    f"Added {added_count} file"
                    f"{'s' if added_count != 1 else ''}. "
                    f"Total: {len(self.selected_paths)}."
                )

            self._save_current_settings()
            self._refresh_settings_page()
            return

        selected_folder = QFileDialog.getExistingDirectory(
            self,
            presentation.dialog_title,
            initial_directory,
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
        self._recent_project_root = folder
        self.source_input.setText(str(folder))
        self.source_input.setToolTip(str(folder))

        if mode == "git":
            self._set_status("Git repository selected.")
        else:
            self._set_status("Project folder selected.")

        self._save_current_settings()
        self._refresh_settings_page()

    def _on_collect_button_clicked(self) -> None:
        if self._collection_active:
            self._cancel_collection()
            return

        self._start_collection()

    def _start_collection(self) -> None:
        if self._collection_active or self._collection_thread is not None:
            return

        try:
            request = self._build_collection_request()
        except Exception as exc:
            self._set_status("Error.")
            QMessageBox.critical(self, "XCC", str(exc))
            return

        thread = QThread(self)
        worker = CollectionWorker(request)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self._on_collection_progress)
        worker.completed.connect(self._on_collection_completed)
        worker.failed.connect(self._on_collection_failed)
        worker.cancelled.connect(self._on_collection_cancelled)

        worker.completed.connect(thread.quit)
        worker.failed.connect(thread.quit)
        worker.cancelled.connect(thread.quit)
        worker.completed.connect(worker.deleteLater)
        worker.failed.connect(worker.deleteLater)
        worker.cancelled.connect(worker.deleteLater)
        thread.finished.connect(self._on_collection_thread_finished)
        thread.finished.connect(thread.deleteLater)

        self._collection_thread = thread
        self._collection_worker = worker
        self._active_collection_request = request
        self._set_collection_active(True)
        self._on_collection_progress("Preparing", 0, 0)
        thread.start()

    def _build_collection_request(self) -> CollectionRequest:
        mode = self._current_mode()
        max_output_chars = self._read_max_output_chars()
        project_root = self.project_root

        if mode == "files":
            selected_paths = tuple(self.selected_paths)
            if not selected_paths:
                raise ValueError("No files selected or found.")
        else:
            if project_root is None:
                source_text = self.source_input.text().strip()
                if source_text:
                    restored_root = Path(source_text)
                    if restored_root.exists() and restored_root.is_dir():
                        project_root = restored_root
                        self.project_root = restored_root

            if project_root is None:
                raise ValueError("Select a source folder first.")

            if mode == "git" and not is_git_repository(project_root):
                raise ValueError("Selected folder is not a Git repository.")

            selected_paths = ()

        return CollectionRequest(
            mode=mode,
            mode_name=self._current_mode_name(),
            selected_paths=selected_paths,
            project_root=project_root,
            compact=self.compact_checkbox.isChecked(),
            max_output_chars=max_output_chars,
        )

    def _cancel_collection(self) -> None:
        worker = self._collection_worker
        if not self._collection_active or worker is None:
            return

        worker.request_cancel()
        self.collect_button.setEnabled(False)
        self.collect_button.setText("Cancelling…")
        self._set_status("Cancelling collection…")
        self._set_runtime_state(RuntimeState.CANCELLING)

    def _on_collection_progress(
        self,
        phase: str,
        current: int,
        total: int,
    ) -> None:
        if not self._collection_active:
            return

        if total > 0:
            message = f"{phase}: {current}/{total}"
        elif current > 0:
            message = f"{phase}: {current}"
        else:
            message = phase

        self._set_event_status(message)
        self._set_runtime_state(RuntimeState.WORKING)

    def _on_collection_completed(self, job: CollectionJobResult) -> None:
        result = job.result
        result.stats.duration_seconds = job.duration_seconds

        if not result.text.strip():
            record = CollectionRunRecord.from_result(
                timestamp=self._current_history_time(),
                mode_name=job.mode_name,
                source=job.source,
                result=result,
                outcome=CollectionOutcome.FAILED,
                output_copied=False,
            )
            self._record_run(record)
            self._set_collection_active(False)
            self._set_status("Nothing to copy.")
            self._set_runtime_state(RuntimeState.FAILED)
            QMessageBox.warning(self, "XCC", "Nothing to copy.")
            return

        if should_show_safety_confirmation(
            result.warnings,
            enabled=self.app_settings.confirm_safety_warnings,
        ):
            self._on_collection_progress("Reviewing warnings", 0, 0)
            if not self._confirm_safety_warnings(result.warnings):
                record = CollectionRunRecord.from_result(
                    timestamp=self._current_history_time(),
                    mode_name=job.mode_name,
                    source=job.source,
                    result=result,
                    outcome=CollectionOutcome.CANCELLED,
                    output_copied=False,
                )
                self._record_run(record)
                self._set_collection_active(False)
                self._set_status("Copy cancelled after safety warning.")
                self._set_runtime_state(RuntimeState.CANCELLED)
                return

        try:
            self._on_collection_progress("Copying", 0, 0)
            copy_to_clipboard(result.text)
        except Exception as exc:
            record = CollectionRunRecord.from_result(
                timestamp=self._current_history_time(),
                mode_name=job.mode_name,
                source=job.source,
                result=result,
                outcome=CollectionOutcome.FAILED,
                output_copied=False,
            )
            self._record_run(record)
            self._set_collection_active(False)
            self._set_status("Clipboard copy failed.")
            self._set_runtime_state(RuntimeState.FAILED)
            QMessageBox.critical(self, "XCC", str(exc))
            return

        record = CollectionRunRecord.from_result(
            timestamp=self._current_history_time(),
            mode_name=job.mode_name,
            source=job.source,
            result=result,
        )
        self._record_run(record)
        self._on_collection_progress("Completed", 0, 0)
        self._set_collection_active(False)
        self._show_success_feedback(record)

    def _on_collection_failed(
        self,
        message: str,
        duration_seconds: float,
    ) -> None:
        mode_name, source = self._active_run_identity()
        self._record_run(
            CollectionRunRecord.terminal(
                timestamp=self._current_history_time(),
                mode_name=mode_name,
                source=source,
                outcome=CollectionOutcome.FAILED,
                duration_seconds=duration_seconds,
            )
        )
        self._set_collection_active(False)

        if message == "No supported Git changes found.":
            self._set_status(message)
            self._set_runtime_state(RuntimeState.WARNINGS)
            QMessageBox.information(self, "XCC", message)
            return

        if message == "No files selected or found.":
            self._set_status(message)
            self._set_runtime_state(RuntimeState.WARNINGS)
            QMessageBox.warning(self, "XCC", message)
            return

        self._set_status("Error.")
        self._set_runtime_state(RuntimeState.FAILED)
        QMessageBox.critical(self, "XCC", message)

    def _on_collection_cancelled(self, duration_seconds: float) -> None:
        mode_name, source = self._active_run_identity()
        self._record_run(
            CollectionRunRecord.terminal(
                timestamp=self._current_history_time(),
                mode_name=mode_name,
                source=source,
                outcome=CollectionOutcome.CANCELLED,
                duration_seconds=duration_seconds,
            )
        )
        self._set_collection_active(False)
        self._set_status("Collection cancelled.")
        self._set_runtime_state(RuntimeState.CANCELLED)

    def _on_collection_thread_finished(self) -> None:
        self._collection_worker = None
        self._collection_thread = None
        self._active_collection_request = None
        self._run_deferred_close_or_quit()

    def _set_collection_active(self, active: bool) -> None:
        self._collection_active = active

        for control in (
            self.select_source_button,
            self.paste_paths_button,
            self.clear_source_button,
            self.source_input,
            self.compact_checkbox,
            self.max_chars_input,
        ):
            control.setEnabled(not active)

        for button in (
            self.mode_files,
            self.mode_folder,
            self.mode_git,
            self.mode_tree,
        ):
            button.setEnabled(not active)

        self.collect_button.setEnabled(True)
        self.collect_button.setText("Cancel" if active else "Collect && Copy")
        if active:
            self.collect_button.setIcon(QIcon())
            self.collect_button.setIconSize(QSize(20, 20))
        else:
            set_tinted_button_icon(
                self.collect_button,
                UI_COLLECT_COPY_ICON_PATH,
                size=20,
                color=PALETTE.dark_text,
            )

        if not active:
            self._refresh_source_controls()

    def _run_deferred_close_or_quit(self) -> None:
        if self._quit_after_collection:
            self._quit_after_collection = False
            QTimer.singleShot(0, self._complete_quit_from_tray)
            return

        if self._close_after_collection:
            self._close_after_collection = False
            QTimer.singleShot(0, self.close)

    def _confirm_safety_warnings(
        self,
        warnings: list[SafetyWarning],
    ) -> bool:
        response = QMessageBox.question(
            self,
            "XCC Safety Warning",
            build_warning_confirmation_text(warnings),
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.Cancel
            ),
            QMessageBox.StandardButton.Cancel,
        )

        return response == QMessageBox.StandardButton.Yes

    def _read_max_output_chars(self) -> int:
        raw_value = self.max_chars_input.text().strip()

        if not raw_value:
            raise ValueError("Max output chars is required.")

        value = int(raw_value)

        if value <= 0:
            raise ValueError("Max output chars must be greater than 0.")

        return value

    def _active_run_identity(self) -> tuple[str, str]:
        request = self._active_collection_request
        if request is not None:
            return request.mode_name, request.source_label

        return self._current_mode_name(), "Unknown source"

    def _current_history_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _record_run(self, record: CollectionRunRecord) -> None:
        self._update_metrics(record)
        self._add_history_entry(record)

        if hasattr(self, "last_run_state_label"):
            self.last_run_state_label.setText(
                f"{record.health_label} · {record.timestamp}"
            )
            set_widget_state(
                self.last_run_state_label,
                outcome_metric_state(record.outcome),
            )

    def _update_metrics(self, record: CollectionRunRecord) -> None:
        self._set_metric_value(
            self.files_metric,
            format_metric_integer(record.files),
        )
        self._set_metric_value(
            self.lines_metric,
            format_metric_integer(record.lines),
        )
        self._set_metric_value(
            self.source_chars_metric,
            format_metric_integer(record.source_chars),
        )
        self._set_metric_value(
            self.output_chars_metric,
            format_metric_integer(record.output_chars),
        )
        self._set_metric_value(
            self.tokens_metric,
            format_metric_integer(record.output_tokens),
        )
        for metric in (
            self.files_metric,
            self.lines_metric,
            self.source_chars_metric,
            self.output_chars_metric,
            self.tokens_metric,
            self.included_metric,
        ):
            metric.set_state(None)

        self._set_metric_value(
            self.truncated_metric,
            "Yes" if record.truncated else "No",
        )
        self.truncated_metric.set_state(
            truncation_metric_state(record.truncated)
        )

        self._set_metric_value(
            self.included_metric,
            format_metric_integer(record.included_files),
        )
        self._set_metric_value(
            self.omitted_metric,
            format_metric_integer(record.omitted_files),
        )
        self._set_metric_value(
            self.coverage_metric,
            (
                f"{format_metric_integer(record.summarized_files)} / "
                f"{format_metric_integer(record.partial_files)}"
            ),
        )
        coverage_state = coverage_metric_state(
            omitted=record.omitted_files,
            summarized=record.summarized_files,
            partial=record.partial_files,
        )
        self.omitted_metric.set_state(coverage_state)
        self.coverage_metric.set_state(coverage_state)

        self._set_metric_value(
            self.outcome_metric,
            record.outcome.metric_label,
        )
        self.outcome_metric.set_state(
            outcome_metric_state(record.outcome)
        )
        self._set_metric_value(self.duration_metric, record.duration_label)
        self.duration_metric.set_state("neutral")
        self._set_metric_value(
            self.issues_metric,
            (
                f"{format_metric_integer(record.warning_count)} / "
                f"{format_metric_integer(record.error_count)}"
            ),
        )
        self.issues_metric.set_state(
            issues_metric_state(
                warnings=record.warning_count,
                errors=record.error_count,
            )
        )

    def _set_metric_value(self, metric: QFrame, value: str) -> None:
        set_metric_value(metric, value)

    def _clear_source(self, *, announce: bool = True) -> None:
        self.selected_paths = []
        self.project_root = None
        self.source_input.clear()
        self.source_input.setToolTip("")
        self._refresh_source_controls()
        self._save_current_settings()
        self._refresh_settings_page()
        if announce:
            self._set_status("Source cleared.")

    def _set_status(self, message: str) -> None:
        self._set_event_status(message)

    def _show_success_feedback(self, record: CollectionRunRecord) -> None:
        if record.outcome == CollectionOutcome.SUCCESS_WITH_WARNINGS:
            self._set_status("Copied to clipboard with warnings.")
            self._set_runtime_state(RuntimeState.WARNINGS)
        else:
            self._set_status("Copied to clipboard.")
            self._set_runtime_state(RuntimeState.COPIED)

        self.collect_button.setText("Copied!")
        QTimer.singleShot(1500, self._reset_success_feedback)

    def _reset_success_feedback(self) -> None:
        self._set_runtime_state(RuntimeState.READY)
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
        self.safety_confirmation_checkbox = self._settings_toggle(
            "",
            self.app_settings.confirm_safety_warnings,
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
            "Reduce XCC-generated structural whitespace; source contents remain unchanged.",
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
                self._settings_row(
                    "Safety confirmation",
                    "Ask before copying when potentially sensitive context is detected.",
                    control=self.safety_confirmation_checkbox,
                ),
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
        groups_layout.addWidget(
            behavior_group,
            1,
            Qt.AlignmentFlag.AlignTop,
        )
        groups_layout.addWidget(
            context_group,
            1,
            Qt.AlignmentFlag.AlignTop,
        )

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

        app_image_path = APP_IMAGE_PATH if APP_IMAGE_PATH.exists() else APP_ICON_PATH
        if app_image_path.exists():
            pixmap = QPixmap(str(app_image_path))
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
        return make_section_title(text)

    def _card_title(self, text: str) -> QLabel:
        return make_card_title(text)

    def _card(self) -> QFrame:
        return make_card()

    def _card_layout(self, card: QFrame) -> QVBoxLayout:
        return make_card_layout(card)

    def _add_history_entry(self, record: CollectionRunRecord) -> None:
        self.history_entries.insert(0, record)
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

        for record in self.history_entries[:20]:
            self.history_list_layout.addWidget(
                self._history_entry_widget(record)
            )

        self.history_list_layout.addStretch(1)

    def _history_entry_widget(self, record: CollectionRunRecord) -> QWidget:
        row = QFrame()
        row.setObjectName("HistoryEntry")
        row.setFixedHeight(142)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(7)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)

        time_label = QLabel(record.timestamp)
        time_label.setObjectName("HistoryTime")

        outcome_label = QLabel(record.health_label)
        outcome_label.setObjectName("HistoryOutcomeCapsule")
        outcome_label.setFixedHeight(26)
        set_widget_state(
            outcome_label,
            outcome_metric_state(record.outcome),
        )

        mode_label = QLabel(record.mode_name)
        mode_label.setObjectName("HistoryModeCapsule")
        mode_label.setFixedHeight(26)

        top_row.addWidget(time_label)
        top_row.addWidget(outcome_label)
        top_row.addStretch(1)
        top_row.addWidget(mode_label)

        source_label = QLabel(record.source)
        source_label.setObjectName("HistorySource")
        source_label.setWordWrap(False)

        stats_label = QLabel(
            f"Files {record.files} · Included {record.included_files} · "
            f"Omitted {record.omitted_files} · Summarized "
            f"{record.summarized_files} · Partial {record.partial_files}"
        )
        stats_label.setObjectName("HistoryStats")

        output_label = QLabel(
            f"Source {record.source_chars} chars · "
            f"Output {record.output_chars} chars · "
            f"Tokens {record.output_tokens} · "
            f"Truncated {'Yes' if record.truncated else 'No'}"
        )
        output_label.setObjectName("HistoryStats")

        health_label = QLabel(
            f"Duration {record.duration_label} · "
            f"Warnings {record.warning_count} · "
            f"Errors {record.error_count}"
        )
        health_label.setObjectName("HistoryHealth")

        layout.addLayout(top_row)
        layout.addWidget(source_label)
        layout.addWidget(stats_label)
        layout.addWidget(output_label)
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

    def _build_metric_group(
        self,
        title: str,
        icon_path: Path,
        metrics: list[MetricCapsule],
    ) -> QWidget:
        group = QWidget()
        group.setObjectName("TransparentWidget")
        group.setMinimumWidth(0)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(
            make_icon_title(
                title,
                icon_path,
                object_name="MetricGroupHeader",
                text_object_name="MetricGroupTitle",
                icon_object_name="MetricGroupIcon",
                icon_size=18,
            )
        )

        for metric in metrics:
            layout.addWidget(metric, 1)

        group.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        return group

    def _metric_divider(self) -> QFrame:
        divider = QFrame()
        divider.setObjectName("MetricDivider")
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding,
        )
        return divider

    def _metric_capsule(self, label: str, value: str) -> MetricCapsule:
        return MetricCapsule(label, value)
    
    def _apply_theme(self) -> None:
        self.setStyleSheet(build_application_stylesheet())


def run_gui() -> None:
    app = QApplication(sys.argv)
    if APP_ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(APP_ICON_PATH)))

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
            window._shutdown_collection_worker()
            window._cleanup_global_hotkey()

        instance_lock.unlock()

    sys.exit(exit_code)
