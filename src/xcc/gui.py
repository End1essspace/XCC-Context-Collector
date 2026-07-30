from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from PySide6.QtCore import QObject, QLockFile, QRect, QRectF, QSize, QThread, Qt, QTimer, Signal
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
    QStyledItemDelegate,
    QStyle,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QFont,
    QIcon,
    QIntValidator,
    QKeySequence,
    QPainter,
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
    make_card,
    make_card_layout,
    make_card_title,
    make_helper_text,
    make_primary_button,
    make_secondary_button,
    make_section_title,
    make_status_capsule,
    set_metric_value,
)
from .ui_theme import (
    METRICS,
    PALETTE,
    build_application_stylesheet,
    build_tray_menu_stylesheet,
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
INSTANCE_SERVER_NAME = "xcc-context-collector-single-instance"
INSTANCE_LOCK_PATH = Path(tempfile.gettempdir()) / "xcc-context-collector.lock"

NAV_ICON_PATH_ROLE = int(Qt.ItemDataRole.UserRole) + 1


class SidebarItemDelegate(QStyledItemDelegate):
    """Paint crisp Lucide navigation items with controlled spacing and states."""

    ITEM_HEIGHT = 52
    ITEM_MARGIN_X = 10
    ITEM_MARGIN_Y = 4
    CONTENT_LEFT = 16
    ICON_SIZE = 20
    ICON_TEXT_GAP = 12

    def __init__(self, parent: QListWidget) -> None:
        super().__init__(parent)
        self._icon_cache: dict[tuple[str, str, float], QPixmap] = {}

    def sizeHint(self, option, index) -> QSize:
        return QSize(option.rect.width(), self.ITEM_HEIGHT)

    def paint(self, painter: QPainter, option, index) -> None:
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        enabled = bool(option.state & QStyle.StateFlag.State_Enabled)

        item_rect = option.rect.adjusted(
            self.ITEM_MARGIN_X,
            self.ITEM_MARGIN_Y,
            -self.ITEM_MARGIN_X,
            -self.ITEM_MARGIN_Y,
        )

        if selected:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(PALETTE.accent))
            painter.drawRoundedRect(QRectF(item_rect), 10.0, 10.0)
        elif hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#211D12"))
            painter.drawRoundedRect(QRectF(item_rect), 10.0, 10.0)

        if not enabled:
            icon_color = PALETTE.disabled_text
            text_color = PALETTE.muted_text
        elif selected:
            icon_color = PALETTE.dark_text
            text_color = PALETTE.dark_text
        elif hovered:
            icon_color = PALETTE.accent
            text_color = PALETTE.primary_text
        else:
            icon_color = PALETTE.secondary_text
            text_color = PALETTE.primary_text

        icon_x = item_rect.left() + self.CONTENT_LEFT
        icon_y = item_rect.top() + (item_rect.height() - self.ICON_SIZE) // 2
        icon_rect = QRect(icon_x, icon_y, self.ICON_SIZE, self.ICON_SIZE)

        icon_path_value = index.data(NAV_ICON_PATH_ROLE)
        if icon_path_value:
            self._paint_svg_icon(
                painter,
                Path(str(icon_path_value)),
                icon_rect,
                icon_color,
                option.widget,
            )

        text_left = icon_rect.right() + 1 + self.ICON_TEXT_GAP
        text_rect = QRect(
            text_left,
            item_rect.top(),
            max(0, item_rect.right() - text_left - 12),
            item_rect.height(),
        )

        font = QFont(option.font)
        font.setPointSizeF(max(10.0, font.pointSizeF()))
        font.setWeight(QFont.Weight.DemiBold if selected else QFont.Weight.Normal)
        painter.setFont(font)
        painter.setPen(QColor(text_color))
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            str(index.data(Qt.ItemDataRole.DisplayRole) or ""),
        )
        painter.restore()

    def _paint_svg_icon(
        self,
        painter: QPainter,
        path: Path,
        target_rect: QRect,
        color: str,
        widget: QWidget | None,
    ) -> None:
        if not path.exists():
            return

        device_ratio = 1.0
        if widget is not None:
            device_ratio = max(1.0, float(widget.devicePixelRatioF()))
        cache_ratio = round(device_ratio, 2)
        cache_key = (str(path), color, cache_ratio)

        pixmap = self._icon_cache.get(cache_key)
        if pixmap is None:
            physical_size = max(1, round(self.ICON_SIZE * device_ratio))
            pixmap = QPixmap(physical_size, physical_size)
            pixmap.setDevicePixelRatio(device_ratio)
            pixmap.fill(Qt.GlobalColor.transparent)

            renderer = QSvgRenderer(str(path))
            if not renderer.isValid():
                return

            icon_painter = QPainter(pixmap)
            icon_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            icon_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
            renderer.render(
                icon_painter,
                QRectF(1.0, 1.0, self.ICON_SIZE - 2.0, self.ICON_SIZE - 2.0),
            )
            icon_painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_SourceIn
            )
            icon_painter.fillRect(
                QRectF(0.0, 0.0, self.ICON_SIZE, self.ICON_SIZE),
                QColor(color),
            )
            icon_painter.end()
            self._icon_cache[cache_key] = pixmap

        painter.drawPixmap(target_rect.topLeft(), pixmap)


class SidebarNavigation(QFrame):
    """Two-zone sidebar with primary navigation above and About anchored below."""

    currentRowChanged = Signal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Sidebar")
        self.setFixedWidth(METRICS.sidebar_width)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        self._top_nav = self._make_list(
            [
                (NAV_COLLECT_ICON_PATH, "Collect"),
                (NAV_HISTORY_ICON_PATH, "History"),
                (NAV_SETTINGS_ICON_PATH, "Settings"),
            ]
        )
        self._bottom_nav = self._make_list(
            [(NAV_ABOUT_ICON_PATH, "About")]
        )

        self._top_nav.currentRowChanged.connect(self._on_top_row_changed)
        self._bottom_nav.currentRowChanged.connect(self._on_bottom_row_changed)

        layout.addWidget(self._top_nav)
        layout.addStretch(1)
        layout.addWidget(self._bottom_nav)

    def _make_list(
        self,
        items: list[tuple[Path, str]],
    ) -> QListWidget:
        nav = QListWidget(self)
        nav.setObjectName("SidebarList")
        nav.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        nav.setSpacing(0)
        nav.setMouseTracking(True)
        nav.setUniformItemSizes(True)
        nav.setFrameShape(QFrame.Shape.NoFrame)
        nav.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        nav.setItemDelegate(SidebarItemDelegate(nav))
        nav.setFixedHeight(len(items) * SidebarItemDelegate.ITEM_HEIGHT)

        for icon_path, title in items:
            item = QListWidgetItem(title)
            item.setData(NAV_ICON_PATH_ROLE, str(icon_path))
            item.setSizeHint(QSize(0, SidebarItemDelegate.ITEM_HEIGHT))
            nav.addItem(item)

        return nav

    def setCurrentRow(self, row: int) -> None:
        if row < 0 or row > 3:
            return

        if row < 3:
            self._set_list_row(self._top_nav, row)
            self._clear_list_selection(self._bottom_nav)
        else:
            self._clear_list_selection(self._top_nav)
            self._set_list_row(self._bottom_nav, 0)

        self.currentRowChanged.emit(row)

    def _on_top_row_changed(self, row: int) -> None:
        if row < 0:
            return

        self._clear_list_selection(self._bottom_nav)
        self.currentRowChanged.emit(row)

    def _on_bottom_row_changed(self, row: int) -> None:
        if row < 0:
            return

        self._clear_list_selection(self._top_nav)
        self.currentRowChanged.emit(3)

    @staticmethod
    def _set_list_row(nav: QListWidget, row: int) -> None:
        nav.blockSignals(True)
        nav.setCurrentRow(row)
        nav.blockSignals(False)

    @staticmethod
    def _clear_list_selection(nav: QListWidget) -> None:
        nav.blockSignals(True)
        nav.setCurrentRow(-1)
        nav.clearSelection()
        nav.blockSignals(False)


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

        status_bar = QFrame()
        status_bar.setObjectName("StatusBar")
        status_bar.setFixedHeight(METRICS.footer_height)

        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(18, 0, 18, 0)
        status_layout.setSpacing(12)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("StatusText")

        self.status_version_label = QLabel(f"v{__version__}")
        self.status_version_label.setObjectName("StatusVersion")
        self.status_version_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
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

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("Header")
        header.setFixedHeight(METRICS.header_height)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 0, 18, 0)
        layout.setSpacing(12)

        icon_label = QLabel()
        icon_label.setObjectName("HeaderAppIcon")
        icon_label.setFixedSize(28, 28)

        app_image_path = APP_IMAGE_PATH if APP_IMAGE_PATH.exists() else APP_ICON_PATH
        if app_image_path.exists():
            pixmap = QPixmap(str(app_image_path))
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

        self.header_status = make_status_capsule(
            "Ready",
            object_name="StatusCapsule",
        )

        hotkey = make_status_capsule(
            f"Hotkey: {DEFAULT_HOTKEY}",
            object_name="HotkeyCapsule",
        )

        layout.addWidget(icon_label)
        layout.addWidget(title, 1)
        layout.addWidget(self.header_status)
        layout.addWidget(hotkey)

        return header

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
        return SidebarNavigation(self)

    def _build_collect_page(self) -> QWidget:
        page = QWidget()
        layout = self._page_layout(page)

        layout.addWidget(self._section_title("Collect Context"))

        setup_card = self._card()
        setup_card.setMinimumHeight(214)

        setup_layout = self._card_layout(setup_card)
        setup_layout.setContentsMargins(22, 18, 22, 18)
        setup_layout.setSpacing(15)
        setup_layout.addWidget(self._card_title("Setup"))

        setup_grid = QGridLayout()
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

        self.mode_folder.setChecked(True)

        mode_buttons = QWidget()
        mode_buttons.setObjectName("TransparentWidget")
        mode_buttons_layout = QHBoxLayout(mode_buttons)
        mode_buttons_layout.setContentsMargins(0, 0, 0, 0)
        mode_buttons_layout.setSpacing(20)

        for index, button in enumerate(
            [self.mode_files, self.mode_folder, self.mode_git, self.mode_tree]
        ):
            self.mode_group.addButton(button, index)
            mode_buttons_layout.addWidget(button)

        mode_buttons_layout.addStretch(1)

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

        self.select_source_button = QPushButton("Select Source")
        self.select_source_button.setMinimumWidth(148)
        self.select_source_button.setFixedHeight(40)

        self.paste_paths_button = QPushButton("Paste Paths")
        self.paste_paths_button.setObjectName("PastePathsButton")
        self.paste_paths_button.setMinimumWidth(138)
        self.paste_paths_button.setFixedHeight(40)
        self.paste_paths_button.setToolTip(
            "Paste a file list from the clipboard into Selected Files"
        )

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
        setup_grid.addWidget(mode_buttons, 0, 1, 1, 3)

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
        setup_grid.addWidget(self.paste_paths_button, 1, 3)

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

        setup_grid.addWidget(options_box, 2, 1, 1, 3)

        setup_grid.setColumnStretch(0, 0)
        setup_grid.setColumnStretch(1, 1)
        setup_grid.setColumnStretch(2, 0)
        setup_grid.setColumnStretch(3, 0)

        setup_layout.addLayout(setup_grid)

        layout.addWidget(setup_card)

        stats_card = self._card()
        stats_card.setMinimumHeight(210)

        stats_layout = self._card_layout(stats_card)

        stats_header = QWidget()
        stats_header.setObjectName("TransparentWidget")
        stats_header_layout = QHBoxLayout(stats_header)
        stats_header_layout.setContentsMargins(0, 0, 0, 0)
        stats_header_layout.setSpacing(12)

        stats_header_layout.addWidget(self._card_title("Last Run"))
        stats_header_layout.addStretch(1)

        self.last_run_state_label = QLabel("No collection yet")
        self.last_run_state_label.setObjectName("LastRunState")
        self.last_run_state_label.setFixedHeight(28)
        self.last_run_state_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        stats_header_layout.addWidget(self.last_run_state_label)

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

        columns_row = QHBoxLayout()
        columns_row.setSpacing(14)
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
        output_column.addWidget(self.truncated_metric)

        coverage_column = QVBoxLayout()
        coverage_column.setContentsMargins(0, 0, 0, 0)
        coverage_column.setSpacing(8)
        coverage_title = QLabel("Coverage")
        coverage_title.setObjectName("MetricGroupTitle")
        coverage_column.addWidget(coverage_title)
        coverage_column.addWidget(self.included_metric)
        coverage_column.addWidget(self.omitted_metric)
        coverage_column.addWidget(self.coverage_metric)

        health_column = QVBoxLayout()
        health_column.setContentsMargins(0, 0, 0, 0)
        health_column.setSpacing(8)
        health_title = QLabel("Health")
        health_title.setObjectName("MetricGroupTitle")
        health_column.addWidget(health_title)
        health_column.addWidget(self.outcome_metric)
        health_column.addWidget(self.duration_metric)
        health_column.addWidget(self.issues_metric)

        columns_row.addLayout(volume_column, 1)
        columns_row.addLayout(output_column, 1)
        columns_row.addLayout(coverage_column, 1)
        columns_row.addLayout(health_column, 1)

        stats_layout.addLayout(columns_row)

        layout.addWidget(stats_card)

        layout.addSpacing(18)

        self.collect_button = make_primary_button(
            "Collect && Copy",
            height=METRICS.primary_action_height,
        )
        self.collect_button.setMinimumHeight(METRICS.primary_action_height)
        self.collect_button.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

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

    def _refresh_source_controls(self) -> None:
        if not hasattr(self, "paste_paths_button"):
            return

        selected_files_mode = self._current_mode() == "files"
        self.paste_paths_button.setVisible(selected_files_mode)
        self.select_source_button.setText(
            "Select Files" if selected_files_mode else "Select Source"
        )

        if selected_files_mode:
            self.source_input.setPlaceholderText(
                "No files selected — choose files or paste paths"
            )
            self.clear_source_button.setToolTip("Clear selected files")
            self._refresh_selected_files_source()
            has_source = bool(self.selected_paths)
        else:
            self.source_input.setPlaceholderText("No source selected")
            self.clear_source_button.setToolTip("Clear selected source")
            has_source = self.project_root is not None or bool(
                self.source_input.text().strip()
            )

        self.clear_source_button.setEnabled(
            has_source and not self._collection_active
        )

    def _refresh_selected_files_source(self) -> None:
        if not self.selected_paths:
            self.source_input.clear()
            self.source_input.setToolTip("")
            self.source_input.setCursor(Qt.CursorShape.ArrowCursor)
            return

        self.source_input.setCursor(Qt.CursorShape.PointingHandCursor)

        count = len(self.selected_paths)
        suffix = "file" if count == 1 else "files"
        root = self.project_root

        if root is not None and self._all_selected_paths_inside_root(root):
            root_name = root.name or str(root)
            self.source_input.setText(
                f"{root_name} · {count} {suffix} selected"
            )
            self.source_input.setToolTip(
                f"Project root:\n{root}\n\nClick to review selected files."
            )
            return

        self.source_input.setText(
            f"{count} {suffix} selected · Mixed locations"
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
        initial_directory = (
            str(self._recent_project_root)
            if self._recent_project_root is not None
            else ""
        )

        if mode == "files":
            selected, _ = QFileDialog.getOpenFileNames(
                self,
                "Select context files",
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
            "Select project folder",
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
        self.header_status.setText("Cancelling")

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

        self.status_label.setText(message)
        self.header_status.setText(phase if len(phase) <= 18 else "Working")

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
            self.header_status.setText("Failed")
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
                self.header_status.setText("Cancelled")
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
            self.header_status.setText("Failed")
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
            self.header_status.setText("No changes")
            QMessageBox.information(self, "XCC", message)
            return

        if message == "No files selected or found.":
            self._set_status(message)
            self.header_status.setText("No files")
            QMessageBox.warning(self, "XCC", message)
            return

        self._set_status("Error.")
        self.header_status.setText("Failed")
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
        self.header_status.setText("Cancelled")

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

    def _update_metrics(self, record: CollectionRunRecord) -> None:
        self._set_metric_value(self.files_metric, str(record.files))
        self._set_metric_value(self.lines_metric, str(record.lines))
        self._set_metric_value(self.source_chars_metric, str(record.source_chars))
        self._set_metric_value(self.output_chars_metric, str(record.output_chars))
        self._set_metric_value(self.tokens_metric, str(record.output_tokens))
        self._set_metric_value(
            self.truncated_metric,
            "Yes" if record.truncated else "No",
        )
        self._set_metric_value(self.included_metric, str(record.included_files))
        self._set_metric_value(self.omitted_metric, str(record.omitted_files))
        self._set_metric_value(
            self.coverage_metric,
            f"{record.summarized_files} / {record.partial_files}",
        )
        self._set_metric_value(self.outcome_metric, record.outcome.metric_label)
        self._set_metric_value(self.duration_metric, record.duration_label)
        self._set_metric_value(
            self.issues_metric,
            f"{record.warning_count} / {record.error_count}",
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
        self.status_label.setText(message)
        self.header_status.setText(message if len(message) <= 18 else "Ready")

    def _show_success_feedback(self, record: CollectionRunRecord) -> None:
        if record.outcome == CollectionOutcome.SUCCESS_WITH_WARNINGS:
            self._set_status("Copied to clipboard with warnings.")
            self.header_status.setText("Warnings")
        else:
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