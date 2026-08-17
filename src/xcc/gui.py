from __future__ import annotations

import sys
import tempfile
from datetime import datetime
from PySide6.QtCore import (
    QEvent,
    QObject,
    QLockFile,
    QPoint,
    QRect,
    QRectF,
    QSize,
    QThread,
    Qt,
    QTimer,
    Signal,
)
from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtWidgets import (
    QApplication,
    QAbstractButton,
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
    QToolButton,
)
from PySide6.QtGui import (
    QAction,
    QCursor,
    QColor,
    QIcon,
    QIntValidator,
    QKeySequence,
    QPainter,
    QPen,
    QRegion,
    QScreen,
    QShortcut,
)
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
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
from .fitts_close import FittsCloseController
from .ui_components import (
    DpiAwareImageLabel,
    IconTitle,
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
from .ui_shell import (
    RuntimeState,
    default_footer_message,
    format_hotkey_for_display,
)
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
    DialogSizeSpec,
    PageSurfaceSpec,
    PageWidthSpec,
    about_page_spec,
    collect_content_min_height,
    collect_geometry_spec,
    collect_layout_spec,
    collect_page_width_spec,
    dialog_size_spec,
    history_page_spec,
    settings_page_spec,
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
WINDOW_MINIMIZE_ICON_PATH = resource_path("assets", "window-minimize.svg")
WINDOW_MAXIMIZE_ICON_PATH = resource_path("assets", "window-maximize.svg")
WINDOW_RESTORE_ICON_PATH = resource_path("assets", "window-restore.svg")
WINDOW_CLOSE_ICON_PATH = resource_path("assets", "window-close.svg")
INSTANCE_SERVER_NAME = "xcc-context-collector-single-instance"
INSTANCE_LOCK_PATH = Path(tempfile.gettempdir()) / "xcc-context-collector.lock"
DISPLAY_HOTKEY = format_hotkey_for_display(DEFAULT_HOTKEY)
WM_NCHITTEST = 0x0084
HTCLIENT = 1
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17
HTCAPTION = 2
FRAME_RESIZE_MARGIN = 6
FULL_BRAND_MIN_SIDEBAR_WIDTH = 212

PASTE_PATHS_DIALOG_PREFERRED_SIZE = QSize(820, 590)
SELECTED_FILES_DIALOG_PREFERRED_SIZE = QSize(860, 610)
RESPONSIVE_DIALOG_MINIMUM_SIZE = QSize(640, 420)


def _dialog_work_area_size(dialog: QDialog) -> QSize:
    parent = dialog.parentWidget()
    screen = parent.screen() if parent is not None else dialog.screen()
    if screen is None:
        screen = QApplication.primaryScreen()

    if screen is None:
        return QSize()

    return screen.availableGeometry().size()


def _fit_dialog_to_work_area(
    dialog: QDialog,
    *,
    preferred_size: QSize,
    minimum_size: QSize = RESPONSIVE_DIALOG_MINIMUM_SIZE,
) -> DialogSizeSpec:
    work_area = _dialog_work_area_size(dialog)
    if work_area.isEmpty():
        # No QScreen is unusual but possible during synthetic teardown. Keep
        # the normal preferred desktop contract rather than manufacturing a
        # monitor-resolution assumption.
        work_area = QSize(
            preferred_size.width() + 48,
            preferred_size.height() + 48,
        )

    spec = dialog_size_spec(
        work_area.width(),
        work_area.height(),
        preferred_width=preferred_size.width(),
        preferred_height=preferred_size.height(),
        minimum_width=minimum_size.width(),
        minimum_height=minimum_size.height(),
    )
    dialog.setMinimumSize(spec.minimum_width, spec.minimum_height)
    dialog.resize(spec.width, spec.height)
    return spec



def fit_window_geometry_to_available(
    geometry: QRect,
    available: QRect,
    *,
    minimum_size: QSize | None = None,
) -> QRect:
    """Clamp normal-window geometry to one logical screen work area."""
    result = QRect(geometry)
    if not available.isValid() or available.width() <= 0 or available.height() <= 0:
        return result

    minimum = minimum_size or QSize(1, 1)
    min_width = min(max(1, minimum.width()), available.width())
    min_height = min(max(1, minimum.height()), available.height())
    width = min(max(min_width, result.width()), available.width())
    height = min(max(min_height, result.height()), available.height())
    result.setSize(QSize(width, height))

    max_x = available.right() - width + 1
    max_y = available.bottom() - height + 1
    result.moveLeft(max(available.left(), min(result.left(), max_x)))
    result.moveTop(max(available.top(), min(result.top(), max_y)))
    return result

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


class WindowFrameBorderOverlay(QWidget):
    """Paint the outer shell border without shrinking the client layout."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("WindowFrameBorderOverlay")
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

    def paintEvent(self, event) -> None:
        parent = self.parentWidget()
        if parent is None or bool(parent.property("maximized")):
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(PALETTE.frame_border), 1.0))

        # Keep the decorative border above the shell, but let the close-button
        # hover surface own the physical top-right corner like a native Windows
        # caption button. The exclusion is active only while that control is hot.
        clip = QRegion(self.rect())
        close_button = getattr(self.window(), "window_close_button", None)
        if (
            close_button is not None
            and close_button.isVisible()
            and close_button.is_effectively_hovered()
        ):
            close_origin = close_button.mapTo(self, QPoint(0, 0))
            close_edge_rect = QRect(
                close_origin.x(),
                0,
                max(0, self.width() - close_origin.x()),
                max(
                    METRICS.window_titlebar_height,
                    close_origin.y() + close_button.height(),
                ),
            )
            clip = clip.subtracted(QRegion(close_edge_rect))

        painter.setClipRegion(clip)
        frame_rect = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        painter.drawRoundedRect(frame_rect, 11.5, 11.5)


class WindowFrame(QFrame):
    """Root shell frame with a non-layout-affecting painted border."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.border_overlay = WindowFrameBorderOverlay(self)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.border_overlay.setGeometry(self.rect())
        self.border_overlay.raise_()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.border_overlay.setGeometry(self.rect())
        self.border_overlay.raise_()


class WindowControlButton(QToolButton):
    """Manually painted caption control with an externally forceable hover."""

    def __init__(
        self,
        role: str,
        icon_path: Path,
        *,
        alternate_icon_path: Path | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if role not in {"minimize", "maximize", "close"}:
            raise ValueError(f"Unsupported window control role: {role}")

        self.control_role = role
        self._icon_path = icon_path
        self._alternate_icon_path = alternate_icon_path
        self._restore_state = False
        self._force_hover = False
        self._normal_icon = QIcon()
        self._active_icon = QIcon()

        self.setObjectName("WindowControlButton")
        self.setProperty("role", role)
        self.setProperty("maximized", False)
        self.setText("")
        self.setFixedSize(
            METRICS.window_control_width,
            METRICS.window_titlebar_height,
        )
        self.setIconSize(QSize(16, 16))
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setAutoRaise(False)
        self.setMouseTracking(True)
        self._refresh_icon()

    @property
    def force_hover(self) -> bool:
        return self._force_hover

    def set_force_hover(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if self._force_hover == enabled:
            return

        self._force_hover = enabled
        self.update()
        self._refresh_frame_border()

    def is_effectively_hovered(self) -> bool:
        return self.underMouse() or self._force_hover or self.isDown()

    def set_restore_state(self, restore: bool) -> None:
        if self._restore_state == restore:
            return

        self._restore_state = restore
        self._refresh_icon()
        self.update()

    def _refresh_icon(self) -> None:
        icon_path = (
            self._alternate_icon_path
            if self._restore_state and self._alternate_icon_path is not None
            else self._icon_path
        )
        self._normal_icon = make_tinted_svg_icon(
            icon_path,
            16,
            "#D5D9DF",
        )
        self._active_icon = make_tinted_svg_icon(
            icon_path,
            16,
            "#FFFFFF",
        )
        # Preserve the ordinary QAbstractButton icon contract for accessibility
        # and tests even though paintEvent renders it manually.
        self.setIcon(self._normal_icon)

    def paintEvent(self, event) -> None:
        del event

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        hovered = self.underMouse() or self._force_hover
        pressed = self.isDown()

        if pressed:
            background = (
                QColor("#C13B49")
                if self.control_role == "close"
                else QColor("#303238")
            )
            painter.fillRect(self.rect(), background)
        elif hovered:
            background = (
                QColor("#A8323E")
                if self.control_role == "close"
                else QColor("#24262A")
            )
            painter.fillRect(self.rect(), background)

        icon = self._active_icon if hovered or pressed else self._normal_icon
        pixmap = icon.pixmap(
            self.iconSize(),
            max(1.0, float(self.devicePixelRatioF())),
        )
        if not pixmap.isNull():
            target = QRect(
                (self.width() - self.iconSize().width()) // 2,
                (self.height() - self.iconSize().height()) // 2,
                self.iconSize().width(),
                self.iconSize().height(),
            )
            painter.drawPixmap(target.topLeft(), pixmap)

        painter.end()

    def enterEvent(self, event) -> None:
        super().enterEvent(event)
        self.update()
        self._refresh_frame_border()

    def leaveEvent(self, event) -> None:
        super().leaveEvent(event)
        self.update()
        self._refresh_frame_border()

    def _refresh_frame_border(self) -> None:
        overlay = getattr(self.window(), "window_frame_overlay", None)
        if overlay is not None:
            overlay.update()


class WindowTitleBar(QFrame):
    """Compact custom title bar that keeps the dark product shell stable."""

    def __init__(
        self,
        window: "XccMainWindow",
        *,
        object_name: str = "WindowTitleBar",
    ) -> None:
        super().__init__(window)
        self._window = window
        self.setObjectName(object_name)
        self.setFixedHeight(METRICS.window_titlebar_height)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if not isinstance(child, QAbstractButton):
                if self._window._is_effectively_maximized():
                    self._window._restore_for_system_move(
                        event.globalPosition().toPoint()
                    )

                handle = self.window().windowHandle()
                if handle is not None and handle.startSystemMove():
                    event.accept()
                    return

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            child = self.childAt(event.position().toPoint())
            if not isinstance(child, QAbstractButton):
                self._window._toggle_maximize_restore()
                event.accept()
                return

        super().mouseDoubleClickEvent(event)


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
        self._dialog_size_spec: DialogSizeSpec | None = None

        self._original_paths = tuple(paths)
        self._selected_paths = list(paths)
        self.project_root = review_project_root(
            self._selected_paths,
            preferred_root=project_root,
        )

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.body_scroll = QScrollArea()
        self.body_scroll.setObjectName("DialogBodyScroll")
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.body_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.body_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        body = QWidget()
        self.body_content = body
        body.setObjectName("DialogBodyContent")
        body.setMinimumWidth(0)
        body.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout = QVBoxLayout(body)
        self.body_layout = layout
        layout.setContentsMargins(26, 24, 26, 16)
        layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("DialogHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(14)

        header_layout.addWidget(
            make_icon_title(
                "Selected Files",
                NAV_COLLECT_ICON_PATH,
                object_name="DialogTitleRow",
                text_object_name="DialogTitle",
                icon_object_name="DialogTitleIcon",
                icon_size=20,
            )
        )
        header_layout.addStretch(1)

        self.count_label = QLabel()
        self.count_label.setObjectName("SelectedFilesCount")
        self.count_label.setFixedHeight(30)
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setAccessibleName("Selected file count")
        header_layout.addWidget(self.count_label)
        layout.addWidget(header)

        description = make_helper_text(
            "Review the final ordered selection. Remove individual files or "
            "clear the selection before collecting context.",
            object_name="DialogDescription",
        )
        layout.addWidget(description)

        root_section = QFrame()
        root_section.setObjectName("DialogSection")
        root_layout = QVBoxLayout(root_section)
        root_layout.setContentsMargins(16, 14, 16, 16)
        root_layout.setSpacing(10)

        root_header = QHBoxLayout()
        root_header.setContentsMargins(0, 0, 0, 0)
        root_header.setSpacing(10)

        root_label = QLabel("Selection scope")
        root_label.setObjectName("DialogSectionTitle")
        root_header.addWidget(root_label)
        root_header.addStretch(1)

        root_hint = QLabel("Project root or mixed locations")
        root_hint.setObjectName("DialogSectionMeta")
        root_hint.setWordWrap(True)
        root_hint.setMinimumWidth(0)
        root_header.addWidget(root_hint)
        root_layout.addLayout(root_header)

        self.root_value = QLineEdit()
        self.root_value.setObjectName("ReviewRootInput")
        self.root_value.setReadOnly(True)
        self.root_value.setFixedHeight(42)
        self.root_value.setAccessibleName("Selected files project root")
        root_layout.addWidget(self.root_value)
        layout.addWidget(root_section)

        files_section = QFrame()
        files_section.setObjectName("DialogSection")
        files_layout = QVBoxLayout(files_section)
        files_layout.setContentsMargins(16, 14, 16, 16)
        files_layout.setSpacing(10)

        files_header = QHBoxLayout()
        files_header.setContentsMargins(0, 0, 0, 0)
        files_header.setSpacing(10)

        files_label = QLabel("Files")
        files_label.setObjectName("DialogSectionTitle")
        files_header.addWidget(files_label)
        files_header.addStretch(1)

        files_hint = QLabel("Ctrl/Shift for multi-select · Delete to remove")
        files_hint.setObjectName("DialogSectionMeta")
        files_hint.setWordWrap(True)
        files_hint.setMinimumWidth(0)
        files_header.addWidget(files_hint)
        files_layout.addLayout(files_header)

        self.files_list = QListWidget()
        self.files_list.setObjectName("SelectedFilesReviewList")
        self.files_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.files_list.setAlternatingRowColors(False)
        self.files_list.setMinimumHeight(170)
        self.files_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.files_list.setTextElideMode(Qt.TextElideMode.ElideMiddle)
        self.files_list.setAccessibleName("Selected files list")
        self.files_list.itemSelectionChanged.connect(
            self._refresh_action_states
        )
        files_layout.addWidget(self.files_list, 1)

        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 0, 0, 0)
        actions_row.setSpacing(10)

        self.remove_button = make_secondary_button(
            "Remove Selected",
            object_name="DialogSecondaryButton",
            minimum_width=154,
        )
        self.remove_button.setAccessibleName("Remove selected files")

        self.clear_button = make_secondary_button(
            "Clear All",
            object_name="DialogQuietButton",
            minimum_width=112,
        )
        self.clear_button.setAccessibleName("Clear all selected files")

        actions_row.addWidget(self.remove_button)
        actions_row.addWidget(self.clear_button)
        actions_row.addStretch(1)
        files_layout.addLayout(actions_row)
        layout.addWidget(files_section, 1)

        self.body_scroll.setWidget(body)
        outer_layout.addWidget(self.body_scroll, 1)

        footer = QFrame()
        footer.setObjectName("DialogFooter")
        footer_row = QHBoxLayout(footer)
        footer_row.setContentsMargins(26, 14, 26, 22)
        footer_row.setSpacing(10)
        footer_row.addStretch(1)

        self.cancel_button = make_secondary_button(
            "Cancel",
            object_name="DialogSecondaryButton",
            minimum_width=104,
        )

        self.apply_button = make_primary_button(
            "Apply Changes",
            object_name="DialogPrimaryButton",
            minimum_width=144,
        )

        footer_row.addWidget(self.cancel_button)
        footer_row.addWidget(self.apply_button)
        outer_layout.addWidget(footer, 0)

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

        self.setTabOrder(self.root_value, self.files_list)
        self.setTabOrder(self.files_list, self.remove_button)
        self.setTabOrder(self.remove_button, self.clear_button)
        self.setTabOrder(self.clear_button, self.cancel_button)
        self.setTabOrder(self.cancel_button, self.apply_button)

        self._render_files()
        self._apply_work_area_geometry()

    def _apply_work_area_geometry(self) -> None:
        self._dialog_size_spec = _fit_dialog_to_work_area(
            self,
            preferred_size=SELECTED_FILES_DIALOG_PREFERRED_SIZE,
        )

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_work_area_geometry()

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

        mixed_locations = self.project_root is None and count > 0
        root_text = (
            str(self.project_root)
            if self.project_root is not None
            else "Mixed locations" if mixed_locations else "No files selected"
        )
        self.root_value.setText(root_text)
        self.root_value.setToolTip(root_text)
        set_widget_property(
            self.root_value,
            "scope",
            "mixed" if mixed_locations else "empty" if count == 0 else "project",
        )
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
        self._dialog_size_spec: DialogSizeSpec | None = None

        self._existing_paths = list(existing_paths)
        self.import_result = SelectedFilesImportResult()
        self.project_root: Path | None = None

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.body_scroll = QScrollArea()
        self.body_scroll.setObjectName("DialogBodyScroll")
        self.body_scroll.setWidgetResizable(True)
        self.body_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.body_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.body_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        body = QWidget()
        self.body_content = body
        body.setObjectName("DialogBodyContent")
        body.setMinimumWidth(0)
        body.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout = QVBoxLayout(body)
        self.body_layout = layout
        layout.setContentsMargins(26, 24, 26, 16)
        layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("DialogHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(14)
        header_layout.addWidget(
            make_icon_title(
                "Paste File Paths",
                UI_PASTE_PATHS_ICON_PATH,
                object_name="DialogTitleRow",
                text_object_name="DialogTitle",
                icon_object_name="DialogTitleIcon",
                icon_size=20,
            )
        )
        header_layout.addStretch(1)
        layout.addWidget(header)

        description = make_helper_text(
            "Paste a path list from an AI response. Relative paths are resolved "
            "against one visible project root before anything is added.",
            object_name="DialogDescription",
        )
        layout.addWidget(description)

        root_section = QFrame()
        root_section.setObjectName("DialogSection")
        root_layout = QVBoxLayout(root_section)
        root_layout.setContentsMargins(16, 14, 16, 16)
        root_layout.setSpacing(10)

        root_header = QHBoxLayout()
        root_header.setContentsMargins(0, 0, 0, 0)
        root_header.setSpacing(10)

        root_label = QLabel("Project root")
        root_label.setObjectName("DialogSectionTitle")
        root_header.addWidget(root_label)
        root_header.addStretch(1)

        root_hint = QLabel("Required for relative paths")
        root_hint.setObjectName("DialogSectionMeta")
        root_hint.setWordWrap(True)
        root_hint.setMinimumWidth(0)
        root_header.addWidget(root_hint)
        root_layout.addLayout(root_header)

        root_row = QHBoxLayout()
        root_row.setContentsMargins(0, 0, 0, 0)
        root_row.setSpacing(10)

        self.root_input = QLineEdit(
            str(initial_root) if initial_root is not None else ""
        )
        self.root_input.setObjectName("DialogPathInput")
        self.root_input.setPlaceholderText("Select the repository or project folder")
        self.root_input.setFixedHeight(42)
        self.root_input.setMinimumWidth(0)
        self.root_input.setAccessibleName("Project root")

        self.browse_button = make_secondary_button(
            "Browse",
            object_name="DialogSecondaryButton",
            minimum_width=108,
            height=42,
        )
        self.browse_button.setAccessibleName("Browse for project root")

        root_row.addWidget(self.root_input, 1)
        root_row.addWidget(self.browse_button)
        root_layout.addLayout(root_row)
        layout.addWidget(root_section)

        paths_section = QFrame()
        paths_section.setObjectName("DialogSection")
        paths_layout = QVBoxLayout(paths_section)
        paths_layout.setContentsMargins(16, 14, 16, 16)
        paths_layout.setSpacing(10)

        paths_header = QHBoxLayout()
        paths_header.setContentsMargins(0, 0, 0, 0)
        paths_header.setSpacing(10)

        paths_label = QLabel("File paths")
        paths_label.setObjectName("DialogSectionTitle")
        paths_header.addWidget(paths_label)
        paths_header.addStretch(1)

        paths_hint = QLabel("Plain text, Markdown lists, quotes, or code blocks")
        paths_hint.setObjectName("DialogSectionMeta")
        paths_hint.setWordWrap(True)
        paths_hint.setMinimumWidth(0)
        paths_header.addWidget(paths_hint)
        paths_layout.addLayout(paths_header)

        self.paths_input = QPlainTextEdit()
        self.paths_input.setObjectName("PathListInput")
        self.paths_input.setPlainText(text)
        self.paths_input.setPlaceholderText(
            "src/package/module.py\ndocs/ROADMAP.md"
        )
        self.paths_input.setMinimumHeight(150)
        self.paths_input.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.paths_input.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.paths_input.setAccessibleName("Pasted file paths")
        paths_layout.addWidget(self.paths_input, 1)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("DialogSummary")
        self.summary_label.setWordWrap(True)
        self.summary_label.setMinimumHeight(44)
        self.summary_label.setMinimumWidth(0)
        self.summary_label.setAccessibleName("Path validation summary")
        paths_layout.addWidget(self.summary_label)
        layout.addWidget(paths_section, 1)

        self.body_scroll.setWidget(body)
        outer_layout.addWidget(self.body_scroll, 1)

        footer = QFrame()
        footer.setObjectName("DialogFooter")
        button_row = QHBoxLayout(footer)
        button_row.setContentsMargins(26, 14, 26, 22)
        button_row.setSpacing(10)
        button_row.addStretch(1)

        self.cancel_button = make_secondary_button(
            "Cancel",
            object_name="DialogSecondaryButton",
            minimum_width=104,
        )

        self.add_button = make_primary_button(
            "Add Files",
            object_name="DialogPrimaryButton",
            minimum_width=138,
        )

        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.add_button)
        outer_layout.addWidget(footer, 0)

        self.browse_button.clicked.connect(self._browse_root)
        self.cancel_button.clicked.connect(self.reject)
        self.add_button.clicked.connect(self._accept_import)
        self.root_input.textChanged.connect(self._refresh_preview)
        self.paths_input.textChanged.connect(self._refresh_preview)

        self.setTabOrder(self.root_input, self.browse_button)
        self.setTabOrder(self.browse_button, self.paths_input)
        self.setTabOrder(self.paths_input, self.cancel_button)
        self.setTabOrder(self.cancel_button, self.add_button)

        self._refresh_preview()
        self._apply_work_area_geometry()

    def _apply_work_area_geometry(self) -> None:
        self._dialog_size_spec = _fit_dialog_to_work_area(
            self,
            preferred_size=PASTE_PATHS_DIALOG_PREFERRED_SIZE,
        )

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._apply_work_area_geometry()

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
        self.root_input.setToolTip(root_text)
        root = Path(root_text) if root_text else None
        result = import_selected_files(
            self.paths_input.toPlainText(),
            project_root=root,
            existing_paths=self._existing_paths,
        )
        self.import_result = result

        if not result.parsed:
            summary = "Paste one or more file paths to continue."
            state = "neutral"
        elif result.root_required:
            summary = (
                f"Project root required · {len(result.parsed)} path(s) detected."
            )
            state = "warning"
        elif result.root_error:
            summary = result.root_error
            state = "error"
        else:
            other_issues = max(
                0,
                result.issue_count - len(result.missing),
            )
            counts = (
                f"Add {result.added_count} · "
                f"Missing {len(result.missing)} · "
                f"Duplicates {result.duplicate_count} · "
                f"External {len(result.external)} · "
                f"Other issues {other_issues}"
            )
            if result.can_apply and result.issue_count == 0:
                summary = f"Ready · {counts}"
                state = "success"
            elif result.can_apply:
                summary = f"Ready with review items · {counts}"
                state = "warning"
            elif result.duplicate_count and result.issue_count == 0:
                summary = f"Already selected · {counts}"
                state = "neutral"
            else:
                summary = f"Nothing can be added yet · {counts}"
                state = "warning"

        self.summary_label.setText(summary)
        self.summary_label.setAccessibleDescription(summary)
        set_widget_state(self.summary_label, state)
        self.summary_label.setToolTip(summary)
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
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
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
        self._collect_page_width_spec: PageWidthSpec | None = None
        self._settings_page_spec: PageSurfaceSpec | None = None
        self._history_page_spec: PageSurfaceSpec | None = None
        self._about_page_spec: PageSurfaceSpec | None = None
        self._settings_columns: int | None = None
        self._about_badge_columns: int | None = None
        self._effective_setup_height = 0
        self._effective_stats_min_height = 0
        self._is_custom_maximized = False
        self._normal_geometry: QRect | None = None
        self._window_screen_signal_bound = False
        self._tracked_screen: QScreen | None = None
        self._restore_maximized_on_show = bool(
            self.app_settings.start_maximized
        )

        self._setup_ui()
        self._fitts_close = FittsCloseController(
            window=self,
            title_bar=self.window_title_bar,
            close_button=self.window_close_button,
            is_effectively_maximized=self._is_effectively_maximized,
        )
        self._apply_collect_layout(force=True)
        self._apply_responsive_pages(force=True)
        self._apply_loaded_settings()
        if settings_result.recovered_from_error:
            self._set_event_status(self._settings_recovery_message)
        self._is_loading_settings = False
        self._apply_theme()
        self._setup_tray()

    def _setup_ui(self) -> None:
        root = WindowFrame()
        self.window_frame = root
        self.window_frame_overlay = root.border_overlay
        root.setObjectName("WindowFrame")

        root_layout = QVBoxLayout(root)
        self.window_shell_layout = root_layout
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        shell_body = QWidget()
        self.shell_body = shell_body
        shell_body.setObjectName("ShellBody")
        shell_body_layout = QHBoxLayout(shell_body)
        self.shell_body_layout = shell_body_layout
        shell_body_layout.setContentsMargins(0, 0, 0, 0)
        shell_body_layout.setSpacing(0)

        self.sidebar_shell = QWidget()
        self.sidebar_shell.setObjectName("SidebarShell")
        sidebar_shell_layout = QVBoxLayout(self.sidebar_shell)
        self.sidebar_shell_layout = sidebar_shell_layout
        sidebar_shell_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_shell_layout.setSpacing(0)

        self.content_shell = QWidget()
        self.content_shell.setObjectName("ContentShell")
        content_shell_layout = QVBoxLayout(self.content_shell)
        self.content_shell_layout = content_shell_layout
        content_shell_layout.setContentsMargins(0, 0, 0, 0)
        content_shell_layout.setSpacing(0)

        self.sidebar_brand_header = self._build_sidebar_brand_header()
        self.window_title_bar = self._build_title_bar()

        self.nav = self._build_nav()
        self.pages = QStackedWidget()
        self.pages.setObjectName("PageStack")

        self.collect_page = self._build_collect_page()
        self.history_page = self._build_history_page()
        self.settings_page = self._build_settings_page()
        self.about_page = self._build_about_page()

        self.pages.addWidget(self.collect_page)
        self.pages.addWidget(self.history_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.about_page)

        body = QWidget()
        body.setObjectName("WindowBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)
        body_layout.addWidget(self.pages, 1)

        status_bar = QFrame()
        self.status_bar = status_bar
        status_bar.setObjectName("StatusBar")
        status_bar.setFixedHeight(METRICS.footer_height)
        status_bar.setAccessibleName("Application footer")

        status_bar_layout = QHBoxLayout(status_bar)
        self.status_bar_layout = status_bar_layout
        status_bar_layout.setContentsMargins(20, 0, 20, 0)
        status_bar_layout.setSpacing(0)

        self.sidebar_status_group = QWidget(status_bar)
        self.sidebar_status_group.setObjectName("SidebarStatusGroup")
        sidebar_status_layout = QHBoxLayout(self.sidebar_status_group)
        self.sidebar_status_layout = sidebar_status_layout
        sidebar_status_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_status_layout.setSpacing(7)

        self.footer_status_dot = QLabel()
        self.footer_status_dot.setObjectName("FooterStatusDot")
        self.footer_status_dot.setFixedSize(8, 8)
        set_widget_state(
            self.footer_status_dot,
            RuntimeState.READY.semantic_state,
        )

        self.status_label = QLabel("Ready · Select a source")
        self.status_label.setObjectName("StatusText")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.status_label.setAccessibleName("Current event status")
        self.status_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )

        sidebar_status_layout.addWidget(
            self.footer_status_dot,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        sidebar_status_layout.addWidget(
            self.status_label,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        status_bar_layout.addWidget(
            self.sidebar_status_group,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )
        status_bar_layout.addStretch(1)

        sidebar_shell_layout.addWidget(self.sidebar_brand_header, 0)
        sidebar_shell_layout.addWidget(self.nav, 1)

        content_shell_layout.addWidget(self.window_title_bar, 0)
        content_shell_layout.addWidget(body, 1)

        shell_body_layout.addWidget(self.sidebar_shell, 0)
        shell_body_layout.addWidget(self.content_shell, 1)
        root_layout.addWidget(shell_body, 1)
        root_layout.addWidget(status_bar, 0)

        self.setCentralWidget(root)
        self._set_shell_sidebar_width(METRICS.sidebar_width)
        self._sync_title_bar_state()

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

    def _build_sidebar_brand_header(self) -> WindowTitleBar:
        header = WindowTitleBar(self, object_name="SidebarBrandHeader")
        header.setFixedHeight(METRICS.sidebar_brand_header_height)
        header.setAccessibleName("XCC Context Collector")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(14, 8, 8, 8)
        layout.setSpacing(9)

        self.sidebar_brand_icon = DpiAwareImageLabel(
            APP_IMAGE_PATH,
            32,
            parent=header,
        )
        self.sidebar_brand_icon.setObjectName("SidebarBrandIcon")
        self.sidebar_brand_icon.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        self.sidebar_brand_label = QLabel("XCC Context Collector", header)
        self.sidebar_brand_label.setObjectName("SidebarBrandLabel")
        self.sidebar_brand_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.sidebar_brand_label.setAccessibleName("XCC Context Collector")
        self.sidebar_brand_label.setToolTip("XCC Context Collector")
        self.sidebar_brand_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        self.sidebar_brand_label.setMinimumWidth(0)
        self.sidebar_brand_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        layout.addWidget(
            self.sidebar_brand_icon,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(
            self.sidebar_brand_label,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addStretch(1)
        return header

    def _build_title_bar(self) -> WindowTitleBar:
        title_bar = WindowTitleBar(self)
        title_bar.setAccessibleName("Window title bar")
        title_bar.setMouseTracking(True)

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.window_version_capsule = QLabel(f"v{__version__}")
        self.window_version_capsule.setObjectName("WindowVersionCapsule")
        self.window_version_capsule.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.window_version_capsule.setAccessibleName("Application version")
        self.window_version_capsule.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )

        controls = QWidget()
        self.window_controls = controls
        controls.setObjectName("WindowControls")
        controls_layout = QHBoxLayout(controls)
        self.window_controls_layout = controls_layout
        # Window controls form one edge-aligned native-style cluster. The
        # close button must reach the right edge instead of floating inside
        # the title bar behind an artificial margin.
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(0)

        self.window_minimize_button = WindowControlButton(
            "minimize",
            WINDOW_MINIMIZE_ICON_PATH,
        )
        self.window_minimize_button.setAccessibleName("Minimize window")
        self.window_minimize_button.setToolTip("Minimize")
        self.window_minimize_button.clicked.connect(self._minimize_window)

        self.window_maximize_button = WindowControlButton(
            "maximize",
            WINDOW_MAXIMIZE_ICON_PATH,
            alternate_icon_path=WINDOW_RESTORE_ICON_PATH,
        )
        self.window_maximize_button.setAccessibleName("Maximize window")
        self.window_maximize_button.clicked.connect(self._toggle_maximize_restore)

        self.window_close_button = WindowControlButton(
            "close",
            WINDOW_CLOSE_ICON_PATH,
        )
        self.window_close_button.setAccessibleName("Close window")
        self.window_close_button.setToolTip("Close")

        for button in (
            self.window_minimize_button,
            self.window_maximize_button,
            self.window_close_button,
        ):
            controls_layout.addWidget(button)

        layout.addStretch(1)
        layout.addWidget(
            self.window_version_capsule,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addSpacing(16)
        layout.addWidget(controls)
        return title_bar

    def _is_effectively_maximized(self) -> bool:
        return self._is_custom_maximized or self.isMaximized()

    def _screen_for_normal_geometry(
        self,
        geometry: QRect | None = None,
    ) -> QScreen | None:
        candidate = geometry if geometry is not None and geometry.isValid() else None
        if candidate is not None:
            screen = QApplication.screenAt(candidate.center())
            if screen is not None:
                return screen
        return self.screen() or QApplication.primaryScreen()

    def _fit_normal_geometry_to_screen(
        self,
        geometry: QRect,
        screen: QScreen | None = None,
    ) -> QRect:
        target_screen = screen or self._screen_for_normal_geometry(geometry)
        if target_screen is None:
            return QRect(geometry)
        return fit_window_geometry_to_available(
            geometry,
            target_screen.availableGeometry(),
            minimum_size=self.minimumSize(),
        )

    def _bind_window_screen_lifecycle(self) -> None:
        handle = self.windowHandle()
        if handle is not None and not self._window_screen_signal_bound:
            handle.screenChanged.connect(self._on_window_screen_changed)
            self._window_screen_signal_bound = True
        self._bind_screen_signals(self.screen())

    def _bind_screen_signals(self, screen: QScreen | None) -> None:
        if screen is self._tracked_screen:
            return

        previous = self._tracked_screen
        if previous is not None:
            for signal, slot in (
                (previous.availableGeometryChanged, self._on_screen_work_area_changed),
                (previous.logicalDotsPerInchChanged, self._on_screen_dpi_changed),
            ):
                try:
                    signal.disconnect(slot)
                except (RuntimeError, TypeError):
                    pass

        self._tracked_screen = screen
        if screen is None:
            return

        screen.availableGeometryChanged.connect(self._on_screen_work_area_changed)
        screen.logicalDotsPerInchChanged.connect(self._on_screen_dpi_changed)

    def _on_window_screen_changed(self, screen: QScreen | None) -> None:
        self._bind_screen_signals(screen)
        if screen is None:
            return

        if self._is_custom_maximized:
            self.setGeometry(screen.availableGeometry())
        elif not self.isMinimized():
            geometry = self.geometry()
            available = screen.availableGeometry()
            needs_fit = (
                geometry.width() > available.width()
                or geometry.height() > available.height()
                or not available.intersects(geometry)
            )
            if needs_fit:
                fitted = self._fit_normal_geometry_to_screen(geometry, screen)
                if fitted != geometry:
                    self.setGeometry(fitted)
                    self._normal_geometry = QRect(fitted)

        self._refresh_dpi_sensitive_assets(screen)

    def _on_screen_work_area_changed(self, available: QRect) -> None:
        if self._tracked_screen is None or not available.isValid():
            return

        if self._is_custom_maximized:
            self.setGeometry(available)
            return

        if self.isMinimized():
            return

        fitted = fit_window_geometry_to_available(
            self.geometry(),
            available,
            minimum_size=self.minimumSize(),
        )
        if fitted != self.geometry():
            self.setGeometry(fitted)
            self._normal_geometry = QRect(fitted)

    def _on_screen_dpi_changed(self, *_args) -> None:
        self._refresh_dpi_sensitive_assets(self._tracked_screen)

    def _refresh_dpi_sensitive_assets(
        self,
        screen: QScreen | None = None,
    ) -> None:
        handle = self.windowHandle()
        if handle is not None:
            ratio = max(1.0, float(handle.devicePixelRatio()))
        elif screen is not None:
            ratio = max(1.0, float(screen.devicePixelRatio()))
        else:
            ratio = max(1.0, float(self.devicePixelRatioF()))

        for icon_title in self.findChildren(IconTitle):
            icon_title.refresh_icon(ratio)

        for label_name in ("sidebar_brand_icon", "about_app_icon"):
            label = getattr(self, label_name, None)
            if isinstance(label, DpiAwareImageLabel):
                label.refresh_pixmap(ratio)

        for button_name in (
            "window_minimize_button",
            "window_maximize_button",
            "window_close_button",
        ):
            button = getattr(self, button_name, None)
            if isinstance(button, WindowControlButton):
                button._refresh_icon()
                button.update()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._bind_window_screen_lifecycle()

    def _maximize_to_available_geometry(self) -> None:
        if not self._is_custom_maximized:
            if self.isMaximized():
                normal_geometry = self.normalGeometry()
                if normal_geometry.isValid():
                    self._normal_geometry = QRect(normal_geometry)
                self.showNormal()
            else:
                self._normal_geometry = QRect(self.geometry())

        self.show()
        screen = self.screen()

        if screen is None:
            self._is_custom_maximized = False
            self.showMaximized()
        else:
            self._is_custom_maximized = True
            self.setGeometry(screen.availableGeometry())

        self._restore_maximized_on_show = True
        self._sync_title_bar_state()

    def _restore_to_normal_geometry(self) -> None:
        restore_geometry = (
            QRect(self._normal_geometry)
            if self._is_custom_maximized
            and self._normal_geometry is not None
            and self._normal_geometry.isValid()
            else QRect(self.geometry())
        )
        if not restore_geometry.isValid():
            restore_geometry = QRect(QPoint(0, 0), QSize(1480, 840))

        # A custom-maximized window must restore against the screen it is
        # currently on, not the monitor that happens to contain the stale
        # normal-geometry center. Passing no geometry keeps that policy inside
        # the common screen resolver and also makes the lifecycle deterministic
        # under the offscreen Qt test platform.
        screen = self._screen_for_normal_geometry(
            None if self._is_custom_maximized else restore_geometry
        )
        restore_geometry = self._fit_normal_geometry_to_screen(
            restore_geometry,
            screen,
        )

        self._is_custom_maximized = False
        self.showNormal()
        self.setGeometry(restore_geometry)
        self._normal_geometry = QRect(restore_geometry)

        self._restore_maximized_on_show = False
        self._sync_title_bar_state()

    def _restore_for_system_move(self, global_position: QPoint) -> None:
        if not self._is_effectively_maximized():
            return

        current_origin = self.frameGeometry().topLeft()
        relative_x = (
            (global_position.x() - current_origin.x())
            / max(1, self.width())
        )
        title_offset = max(
            0,
            min(
                METRICS.window_titlebar_height - 1,
                global_position.y() - current_origin.y(),
            ),
        )

        if self._is_custom_maximized:
            restore_geometry = (
                QRect(self._normal_geometry)
                if self._normal_geometry is not None
                and self._normal_geometry.isValid()
                else QRect(
                    current_origin,
                    QSize(1480, 840),
                )
            )
        else:
            native_normal = self.normalGeometry()
            restore_geometry = (
                QRect(native_normal)
                if native_normal.isValid()
                else QRect(
                    current_origin,
                    QSize(1480, 840),
                )
            )

        screen = QApplication.screenAt(global_position)
        if screen is not None:
            available = screen.availableGeometry()
            restore_geometry.setSize(
                QSize(
                    min(restore_geometry.width(), available.width()),
                    min(restore_geometry.height(), available.height()),
                )
            )

        target_x = global_position.x() - round(
            restore_geometry.width() * relative_x
        )
        target_y = global_position.y() - title_offset

        if screen is not None:
            available = screen.availableGeometry()
            visible_grip = min(120, restore_geometry.width())
            target_x = max(
                available.left() - restore_geometry.width() + visible_grip,
                min(
                    target_x,
                    available.right() - visible_grip + 1,
                ),
            )
            target_y = max(available.top(), target_y)

        restore_geometry.moveTopLeft(QPoint(target_x, target_y))
        self._normal_geometry = QRect(restore_geometry)
        self._is_custom_maximized = False
        self.showNormal()
        self.setGeometry(restore_geometry)
        self._restore_maximized_on_show = False
        self._sync_title_bar_state()

    def _toggle_maximize_restore(self) -> None:
        if self._is_effectively_maximized():
            self._restore_to_normal_geometry()
        else:
            self._maximize_to_available_geometry()

    def _sync_title_bar_state(self) -> None:
        if not hasattr(self, "window_maximize_button"):
            return

        maximized = self._is_effectively_maximized()
        self.window_maximize_button.set_restore_state(maximized)
        self.window_maximize_button.setToolTip(
            "Restore" if maximized else "Maximize"
        )
        self.window_maximize_button.setAccessibleName(
            "Restore window" if maximized else "Maximize window"
        )

        for widget_name in (
            "window_frame",
            "sidebar_brand_header",
            "window_title_bar",
            "status_bar",
            "sidebar_shell",
            "content_shell",
        ):
            widget = getattr(self, widget_name, None)
            if widget is not None:
                set_widget_property(widget, "maximized", maximized)

        for button in (
            getattr(self, "window_minimize_button", None),
            getattr(self, "window_maximize_button", None),
            getattr(self, "window_close_button", None),
        ):
            if button is not None:
                set_widget_property(button, "maximized", maximized)

        overlay = getattr(self, "window_frame_overlay", None)
        if overlay is not None:
            overlay.setVisible(not maximized)
            if not maximized:
                overlay.setGeometry(self.window_frame.rect())
                overlay.raise_()
                overlay.update()

        controller = getattr(self, "_fitts_close", None)
        if controller is not None:
            QTimer.singleShot(0, controller.sync_timer)

    def _window_hit_test(self, global_position: QPoint) -> int | None:
        """Return a native Windows non-client hit-test code for one point."""

        window_origin = self.mapToGlobal(QPoint(0, 0))
        close_button = getattr(self, "window_close_button", None)
        if close_button is not None and close_button.isVisible():
            close_origin = close_button.mapToGlobal(QPoint(0, 0))
            close_rect = QRect(close_origin, close_button.size())
            if close_rect.contains(global_position):
                return HTCLIENT

        controls = getattr(self, "window_controls", None)
        if controls is not None and controls.isVisible():
            controls_origin = controls.mapToGlobal(QPoint(0, 0))
            controls_rect = QRect(controls_origin, controls.size())
            if controls_rect.contains(global_position):
                return HTCLIENT

        local_x = global_position.x() - window_origin.x()
        local_y = global_position.y() - window_origin.y()
        width = self.width()
        height = self.height()

        if not self._is_effectively_maximized():
            margin = FRAME_RESIZE_MARGIN
            on_left = 0 <= local_x < margin
            on_right = width - margin <= local_x < width
            on_top = 0 <= local_y < margin
            on_bottom = height - margin <= local_y < height

            if on_top and on_left:
                return HTTOPLEFT
            if on_top and on_right:
                return HTTOPRIGHT
            if on_bottom and on_left:
                return HTBOTTOMLEFT
            if on_bottom and on_right:
                return HTBOTTOMRIGHT
            if on_left:
                return HTLEFT
            if on_right:
                return HTRIGHT
            if on_top:
                return HTTOP
            if on_bottom:
                return HTBOTTOM

        for widget_name in ("sidebar_brand_header", "window_title_bar"):
            caption_widget = getattr(self, widget_name, None)
            if caption_widget is None or not caption_widget.isVisible():
                continue
            caption_origin = caption_widget.mapToGlobal(QPoint(0, 0))
            caption_rect = QRect(caption_origin, caption_widget.size())
            if caption_rect.contains(global_position):
                return HTCAPTION

        return None

    def nativeEvent(self, event_type, message):
        if sys.platform == "win32":
            try:
                from ctypes import wintypes

                native_message = wintypes.MSG.from_address(int(message))
            except Exception:
                native_message = None

            if native_message is not None and native_message.message == WM_NCHITTEST:
                hit = self._window_hit_test(QCursor.pos())
                if hit is not None:
                    return True, hit

        return super().nativeEvent(event_type, message)

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
        self._hotkey_status_message = DISPLAY_HOTKEY
        self.hotkey_capsule.setText(f"Hotkey: {DISPLAY_HOTKEY}")
        self.hotkey_capsule.set_state(None)
        self._set_runtime_state(RuntimeState.READY)
        self._restore_default_footer_status()
        self._refresh_settings_page()

    def _minimize_window(self) -> None:
        self._restore_maximized_on_show = (
            self._is_effectively_maximized()
        )
        self.showMinimized()

    def _window_should_restore_maximized(self) -> bool:
        if self.isMinimized() or not self.isVisible():
            return self._restore_maximized_on_show

        return self._is_effectively_maximized()

    def _clear_minimized_window_state(self) -> None:
        if not self.isMinimized():
            return

        state = self.windowState()
        state &= ~Qt.WindowState.WindowMinimized
        state &= ~Qt.WindowState.WindowMaximized
        self.setWindowState(state)
        self.showNormal()

    def _restore_running_window(self, status_message: str) -> None:
        self._fitts_close.reset_interaction()
        restore_maximized = self._window_should_restore_maximized()

        # show() does not reliably remove WindowMinimized on Windows,
        # especially when XCC uses its custom available-geometry maximize.
        # Clear the native minimized state first, then restore the exact
        # pre-minimize window mode.
        self._clear_minimized_window_state()

        if restore_maximized:
            self._maximize_to_available_geometry()
        else:
            self._restore_to_normal_geometry()

        self.show()
        self.raise_()
        self.activateWindow()

        handle = self.windowHandle()
        if handle is not None:
            handle.requestActivate()

        self._restore_maximized_on_show = restore_maximized
        QTimer.singleShot(0, self._fitts_close.sync_timer)
        self._set_transient_event_status(status_message)

    def _restore_from_hotkey(self) -> None:
        self._restore_running_window("Window restored by hotkey.")
    
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
        page.setObjectName("HistoryPage")
        page.setMinimumWidth(0)
        layout = self._page_layout(page)
        self.history_page_content = page
        self.history_page_layout = layout

        layout.addWidget(self._section_title("History"))

        history_card = self._card()
        self.history_card = history_card
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
        self._fitts_close.reset_interaction()

        if self.app_settings.start_maximized:
            self._maximize_to_available_geometry()
        else:
            self._restore_to_normal_geometry()

    def _show_from_tray(self) -> None:
        self._restore_running_window("Window restored.")

    def _hide_to_tray(self) -> None:
        if not (hasattr(self, "tray_icon") and self.tray_icon.isVisible()):
            self._set_event_status("Tray is not available.")
            return

        self._fitts_close.reset_interaction()
        self.hide()
        self._fitts_close.sync_timer()
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
        self._fitts_close.reset_interaction()

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
            if self.isVisible() and not self.isMinimized():
                self._hide_to_tray()
            else:
                self._show_from_tray()

    def _build_nav(self) -> SidebarNavigation:
        return SidebarNavigation(
            items=(
                (NAV_COLLECT_ICON_PATH, "Collect"),
                (NAV_HISTORY_ICON_PATH, "History"),
                (NAV_SETTINGS_ICON_PATH, "Settings"),
                (NAV_ABOUT_ICON_PATH, "About"),
            ),
            parent=self,
        )

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.WindowStateChange:
            old_state = event.oldState()
            became_minimized = (
                self.isMinimized()
                and not bool(old_state & Qt.WindowState.WindowMinimized)
            )
            if became_minimized:
                self._restore_maximized_on_show = (
                    self._is_custom_maximized
                    or bool(old_state & Qt.WindowState.WindowMaximized)
                )

        super().changeEvent(event)

        if event.type() == QEvent.Type.WindowStateChange:
            self._sync_title_bar_state()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if hasattr(self, "collect_page_layout"):
            QTimer.singleShot(0, self._apply_collect_layout)
        if hasattr(self, "settings_page_layout"):
            QTimer.singleShot(0, self._apply_responsive_pages)

    def eventFilter(self, watched, event) -> bool:
        # Keep a direct reference to the viewport instead of asking the
        # QScrollArea for it from inside an event-filter callback. During Qt
        # teardown the Python wrapper for collect_page_scroll can outlive its
        # C++ object, and calling viewport() on that stale wrapper raises from
        # the Python override even though the test itself has already passed.
        collect_viewport = getattr(self, "collect_page_viewport", None)
        if (
            collect_viewport is not None
            and watched is collect_viewport
            and event.type() == QEvent.Type.Resize
        ):
            QTimer.singleShot(0, self._apply_collect_layout)

        return super().eventFilter(watched, event)

    def _collect_viewport_size(self) -> QSize:
        viewport = getattr(self, "collect_page_viewport", None)
        if viewport is None:
            return QSize(max(0, self.width()), max(0, self.height()))

        try:
            size = viewport.size()
        except RuntimeError:
            # A queued responsive callback can race Qt object destruction. No
            # layout work is useful once the viewport's C++ object is gone.
            return QSize()

        if size.width() <= 0:
            size.setWidth(max(0, self.pages.width()))
        if size.height() <= 0:
            size.setHeight(max(0, self.pages.height()))
        return size

    def _set_shell_sidebar_width(self, width: int) -> None:
        shell_width = max(190, width)
        self.sidebar_shell.setFixedWidth(shell_width)
        self.nav.set_sidebar_width(shell_width)
        self.sidebar_brand_header.setFixedWidth(shell_width)

        # The complete lockup belongs to both large and medium layouts.
        # Only the compact sidebar uses the short product mark.
        full_brand = shell_width >= FULL_BRAND_MIN_SIDEBAR_WIDTH
        if hasattr(self, "sidebar_brand_label"):
            self.sidebar_brand_label.setText(
                "XCC Context Collector" if full_brand else "XCC"
            )

    def _apply_collect_layout(self, *, force: bool = False) -> None:
        viewport_size = self._collect_viewport_size()
        if viewport_size.isEmpty():
            return

        spec = collect_layout_spec(
            viewport_size.width(),
            current_mode=self._collect_layout_mode,
        )
        geometry = collect_geometry_spec(spec, viewport_size.height())
        page_width = collect_page_width_spec(viewport_size.width())
        width_mode_changed = force or spec.mode is not self._collect_layout_mode

        self._collect_layout_mode = spec.mode
        self._collect_layout_spec = spec
        self._collect_geometry_spec = geometry
        self._collect_page_width_spec = page_width
        self._set_shell_sidebar_width(spec.sidebar_width)

        if width_mode_changed:
            self.collect_page_header.subtitle_label.setVisible(spec.show_subtitle)
            self.source_helper_label.setVisible(spec.show_source_helper)
            self.options_helper_label.setVisible(spec.show_options_helper)
            self._arrange_mode_buttons(spec)
            self._arrange_source_controls(spec)
            self._arrange_metric_groups(spec)

        self._apply_collect_geometry(spec, geometry, page_width)
        QTimer.singleShot(0, self._sync_collect_scroll_policy)
        QTimer.singleShot(0, self._apply_responsive_pages)

        if width_mode_changed:
            QTimer.singleShot(0, self._apply_collect_layout)

    def _apply_collect_geometry(
        self,
        spec: CollectLayoutSpec,
        geometry: CollectGeometrySpec,
        page_width: PageWidthSpec,
    ) -> None:
        compact = spec.mode is CollectLayoutMode.COMPACT
        medium = spec.mode is CollectLayoutMode.MEDIUM

        # Keep responsive mode selection tied to the real viewport while
        # centering only the width that exceeds Collect's useful workspace.
        # Full HD and narrower viewports retain their approved base margins.
        self.collect_page_layout.setContentsMargins(
            spec.page_margin + page_width.left_inset,
            geometry.page_top_margin,
            spec.page_margin + page_width.right_inset,
            geometry.page_bottom_margin,
        )
        self.collect_page_layout.setSpacing(geometry.page_gap)

        setup_horizontal = 18 if compact else 21 if medium else 24
        setup_top = 17 if compact else 19 if medium else 22
        setup_bottom = 17 if compact else 19 if medium else 22
        self.setup_card_layout.setContentsMargins(
            setup_horizontal,
            setup_top,
            setup_horizontal,
            setup_bottom,
        )
        self.setup_card_layout.setSpacing(12 if compact else 14 if medium else 16)
        self.setup_grid.setHorizontalSpacing(10 if compact else 12 if medium else 14)
        self.setup_grid.setVerticalSpacing(8 if compact else 10 if medium else 12)
        self.setup_card.setMinimumHeight(0)
        self.setup_card.setMaximumHeight(16_777_215)
        self.setup_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        stats_horizontal = 18 if compact else 20 if medium else 22
        stats_vertical = 12 if compact else 13 if medium else 14
        self.stats_card_layout.setContentsMargins(
            stats_horizontal,
            stats_vertical,
            stats_horizontal,
            stats_vertical,
        )
        self.stats_card_layout.setSpacing(8 if compact else 9 if medium else 10)
        self.stats_card.setMinimumHeight(0)
        self.stats_card.setMaximumHeight(16_777_215)
        self.stats_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.mode_buttons.setMaximumWidth(spec.mode_group_max_width)
        self.mode_buttons_layout.setHorizontalSpacing(spec.mode_horizontal_gap)
        self.mode_buttons_layout.setVerticalSpacing(spec.mode_vertical_gap)
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
                group_layout.setSpacing(5 if compact else 6)

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
        viewport = getattr(self, "collect_page_viewport", None)
        if viewport is None:
            return

        try:
            available_height = viewport.height()
        except RuntimeError:
            return

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

    @staticmethod
    def _safe_widget_width(widget: QWidget | None, fallback: int = 0) -> int:
        if widget is None:
            return max(0, fallback)
        try:
            width = widget.width()
        except RuntimeError:
            return max(0, fallback)
        return max(0, width or fallback)

    @staticmethod
    def _apply_page_surface_geometry(
        layout: QVBoxLayout,
        spec: PageSurfaceSpec,
    ) -> None:
        layout.setContentsMargins(
            spec.page_margin + spec.width.left_inset,
            24,
            spec.page_margin + spec.width.right_inset,
            24,
        )

    @staticmethod
    def _sync_scroll_content_min_height(
        content: QWidget,
        layout: QVBoxLayout,
    ) -> None:
        # Reset the previous width-dependent minimum before recalculating it.
        # A one-column Settings page becomes naturally taller and therefore
        # scrolls; a two-column/full-height page remains scrollbar-free.
        content.setMinimumHeight(0)
        layout.activate()
        content.setMinimumHeight(max(0, layout.minimumSize().height()))

    def _apply_responsive_pages(self, *, force: bool = False) -> None:
        if not hasattr(self, "pages"):
            return

        # QStackedWidget keeps non-current pages hidden, and Qt may leave a
        # hidden QScrollArea viewport at its default ~640x480 geometry. Using
        # those child widths would therefore make responsive policy depend on
        # which page happens to be visible. PageStack is the stable logical
        # content viewport shared by every page and is also independent of
        # vertical-scrollbar appearance, avoiding width-policy feedback loops.
        content_width = self._safe_widget_width(self.pages, 0)
        if content_width <= 0:
            return

        if hasattr(self, "settings_page_layout"):
            spec = settings_page_spec(content_width)
            self._settings_page_spec = spec
            self._apply_page_surface_geometry(self.settings_page_layout, spec)
            if force or spec.columns != self._settings_columns:
                self._arrange_settings_groups(spec.columns)
                self._settings_columns = spec.columns
            self._sync_scroll_content_min_height(
                self.settings_page_content,
                self.settings_page_layout,
            )

        if hasattr(self, "history_page_layout"):
            spec = history_page_spec(content_width)
            self._history_page_spec = spec
            self._apply_page_surface_geometry(self.history_page_layout, spec)

        if hasattr(self, "about_page_layout"):
            spec = about_page_spec(content_width)
            self._about_page_spec = spec
            self._apply_page_surface_geometry(self.about_page_layout, spec)
            if force or spec.columns != self._about_badge_columns:
                self._arrange_about_badges(spec.columns)
                self._about_badge_columns = spec.columns
            self._sync_scroll_content_min_height(
                self.about_page_content,
                self.about_page_layout,
            )

    def _arrange_settings_groups(self, columns: int) -> None:
        self._take_layout_items(self.settings_groups_layout)
        self._reset_grid_stretches(self.settings_groups_layout, columns=3, rows=2)

        if columns >= 2:
            self.settings_groups_layout.addWidget(
                self.settings_behavior_group,
                0,
                0,
                Qt.AlignmentFlag.AlignTop,
            )
            self.settings_groups_layout.addWidget(
                self.settings_context_group,
                0,
                1,
                Qt.AlignmentFlag.AlignTop,
            )
            self.settings_groups_layout.setColumnStretch(0, 1)
            self.settings_groups_layout.setColumnStretch(1, 1)
            return

        self.settings_groups_layout.addWidget(
            self.settings_behavior_group,
            0,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        self.settings_groups_layout.addWidget(
            self.settings_context_group,
            1,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        self.settings_groups_layout.setColumnStretch(0, 1)

    def _arrange_about_badges(self, columns: int) -> None:
        columns = max(1, columns)
        self._take_layout_items(self.about_badges_layout)
        self._reset_grid_stretches(
            self.about_badges_layout,
            columns=max(5, columns + 1),
            rows=2,
        )

        for index, badge in enumerate(self.about_badges):
            row = index // columns
            column = index % columns
            self.about_badges_layout.addWidget(
                badge,
                row,
                column,
                Qt.AlignmentFlag.AlignLeft,
            )

        self.about_badges_layout.setColumnStretch(columns, 1)

    def _arrange_mode_buttons(self, spec: CollectLayoutSpec) -> None:
        self._take_layout_items(self.mode_buttons_layout)
        self._reset_grid_stretches(self.mode_buttons_layout, columns=5, rows=2)
        columns = max(1, spec.mode_columns)

        for index, button in enumerate(self.mode_buttons_list):
            row = index // columns
            column = index % columns
            self.mode_buttons_layout.addWidget(
                button,
                row,
                column,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            )

        # Mode is one compact choice group. Never distribute its options across
        # the full Setup width; any spare space stays after the final option.
        self.mode_buttons_layout.setColumnStretch(columns, 1)

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
        self.collect_page_viewport = scroll.viewport()
        self.collect_page_content = page
        self.collect_page_layout = layout
        self.collect_page_viewport.installEventFilter(self)

        self.header_status = make_runtime_status_capsule("Ready")
        self.header_status.set_state(RuntimeState.READY.semantic_state)
        self.header_status.setAccessibleName("Runtime status")

        self.hotkey_capsule = make_status_capsule(
            f"Hotkey: {DISPLAY_HOTKEY}",
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
        setup_card.setFixedHeight(278)

        self.setup_card_layout = self._card_layout(setup_card)
        setup_layout = self.setup_card_layout
        setup_layout.setContentsMargins(24, 22, 24, 22)
        setup_layout.setSpacing(16)
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
            button.setSizePolicy(
                QSizePolicy.Policy.Preferred,
                QSizePolicy.Policy.Fixed,
            )

        self.mode_folder.setChecked(True)

        self.mode_buttons = QWidget()
        self.mode_buttons.setObjectName("ModeSelectorGroup")
        self.mode_buttons.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )
        self.mode_buttons.setMaximumWidth(650)
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
        setup_grid.addWidget(
            self.mode_buttons,
            0,
            1,
            1,
            3,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
        )

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
        stats_card.setMinimumHeight(292)
        stats_card.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        self.stats_card_layout = self._card_layout(stats_card)
        stats_layout = self.stats_card_layout
        stats_layout.setContentsMargins(22, 14, 22, 14)
        stats_layout.setSpacing(10)

        stats_header = QWidget()
        stats_header.setObjectName("TransparentWidget")
        stats_header.setFixedHeight(28)
        stats_header_layout = QHBoxLayout(stats_header)
        stats_header_layout.setContentsMargins(0, 0, 0, 0)
        stats_header_layout.setSpacing(10)

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
        self.last_run_state_label.setAccessibleName("Last run state")
        self.last_run_state_label.setFixedHeight(28)
        self.last_run_state_label.setMinimumWidth(146)
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
        self.metrics_layout.setHorizontalSpacing(14)
        self.metrics_layout.setVerticalSpacing(8)

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
        self.collect_button.setAccessibleName("Collect and copy context")
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
        QTimer.singleShot(0, self._apply_responsive_pages)

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
        row.setMinimumHeight(58)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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
        description_label.setWordWrap(True)
        description_label.setMinimumWidth(0)

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
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

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
        scroll = QScrollArea()
        scroll.setObjectName("SettingsPageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        page = QWidget()
        page.setObjectName("SettingsPage")
        page.setMinimumWidth(0)
        page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = self._page_layout(page)
        self.settings_page_scroll = scroll
        self.settings_page_viewport = scroll.viewport()
        self.settings_page_content = page
        self.settings_page_layout = layout

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

        self.settings_behavior_group = behavior_group

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

        self.settings_context_group = context_group

        groups_row = QWidget()
        groups_row.setObjectName("TransparentWidget")
        self.settings_groups_row = groups_row

        groups_layout = QGridLayout(groups_row)
        self.settings_groups_layout = groups_layout
        groups_layout.setContentsMargins(0, 0, 0, 0)
        groups_layout.setHorizontalSpacing(18)
        groups_layout.setVerticalSpacing(18)
        groups_layout.addWidget(
            behavior_group,
            0,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        groups_layout.addWidget(
            context_group,
            0,
            1,
            Qt.AlignmentFlag.AlignTop,
        )
        groups_layout.setColumnStretch(0, 1)
        groups_layout.setColumnStretch(1, 1)

        layout.addWidget(groups_row)
        layout.addStretch(1)

        scroll.setWidget(page)
        return scroll
                
    def _settings_section_title(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SettingsSectionTitle")
        label.setFixedHeight(16)
        return label
    
    def _page_layout(self, page: QWidget) -> QVBoxLayout:
        layout = QVBoxLayout(page)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)
        return layout

    def _build_about_page(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setObjectName("AboutPageScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        page = QWidget()
        page.setObjectName("AboutPage")
        page.setMinimumWidth(0)
        page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout = self._page_layout(page)
        self.about_page_scroll = scroll
        self.about_page_viewport = scroll.viewport()
        self.about_page_content = page
        self.about_page_layout = layout

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

        app_image_path = APP_IMAGE_PATH if APP_IMAGE_PATH.exists() else APP_ICON_PATH
        icon_label = DpiAwareImageLabel(app_image_path, 56)
        self.about_app_icon = icon_label
        icon_label.setObjectName("AboutAppIcon")

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

        badges_layout = QGridLayout(badges_row)
        self.about_badges_layout = badges_layout
        badges_layout.setContentsMargins(0, 0, 0, 0)
        badges_layout.setHorizontalSpacing(10)
        badges_layout.setVerticalSpacing(8)

        self.about_badges = [
            self._about_badge(text)
            for text in ["Local-first", "No cloud", "Windows utility", "Tray-ready"]
        ]
        for index, badge in enumerate(self.about_badges):
            badges_layout.addWidget(
                badge,
                0,
                index,
                Qt.AlignmentFlag.AlignLeft,
            )
        badges_layout.setColumnStretch(4, 1)
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
                DISPLAY_HOTKEY,
            )
        )

        footer = QLabel("Built for fast AI-context workflow.")
        footer.setObjectName("AboutFooter")
        card_layout.addWidget(footer)

        layout.addWidget(card)
        layout.addStretch(1)

        scroll.setWidget(page)
        return scroll

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
        row.setMinimumHeight(142)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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
        source_label.setWordWrap(True)
        source_label.setMinimumWidth(0)

        stats_label = QLabel(
            f"Files {record.files} · Included {record.included_files} · "
            f"Omitted {record.omitted_files} · Summarized "
            f"{record.summarized_files} · Partial {record.partial_files}"
        )
        stats_label.setObjectName("HistoryStats")
        stats_label.setWordWrap(True)
        stats_label.setMinimumWidth(0)

        output_label = QLabel(
            f"Source {record.source_chars} chars · "
            f"Output {record.output_chars} chars · "
            f"Tokens {record.output_tokens} · "
            f"Truncated {'Yes' if record.truncated else 'No'}"
        )
        output_label.setObjectName("HistoryStats")
        output_label.setWordWrap(True)
        output_label.setMinimumWidth(0)

        health_label = QLabel(
            f"Duration {record.duration_label} · "
            f"Warnings {record.warning_count} · "
            f"Errors {record.error_count}"
        )
        health_label.setObjectName("HistoryHealth")
        health_label.setWordWrap(True)
        health_label.setMinimumWidth(0)

        layout.addLayout(top_row)
        layout.addWidget(source_label)
        layout.addWidget(stats_label)
        layout.addWidget(output_label)
        layout.addWidget(health_label)

        return row

    def _about_info_row(self, label: str, value: str) -> QFrame:
        row = QFrame()
        row.setObjectName("AboutInfoRow")
        row.setMinimumHeight(42)
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(12)

        label_widget = QLabel(label)
        label_widget.setObjectName("AboutInfoLabel")

        value_widget = QLabel(value)
        value_widget.setObjectName("AboutInfoValue")
        value_widget.setWordWrap(True)
        value_widget.setMinimumWidth(0)
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
        layout.setSpacing(6)
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
