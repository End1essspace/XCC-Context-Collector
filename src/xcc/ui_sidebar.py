from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QEvent, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent, QPixmap, QWheelEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .ui_components import make_tinted_svg_icon
from .ui_theme import PALETTE


class SidebarNavButton(QPushButton):
    """One complete navigation action without item-view geometry risks."""

    moveRequested = Signal(int)

    def __init__(
        self,
        text: str,
        icon_path: str | Path,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName("SidebarNavButton")
        self.setCheckable(True)
        self.setAutoExclusive(False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedHeight(50)
        self.setMinimumWidth(0)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.setAccessibleName(text)

        self._icon_path = Path(icon_path)
        self._selected = False
        self._hovered = False
        self.setIconSize(QSize(20, 20))
        self._refresh_icon()

    def set_selected(self, selected: bool) -> None:
        self._selected = bool(selected)
        self.setChecked(self._selected)
        self.setProperty("selected", self._selected)
        self._repolish()
        self._refresh_icon()

    def enterEvent(self, event) -> None:
        self._hovered = True
        self._refresh_icon()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hovered = False
        self._refresh_icon()
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._refresh_icon()
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._refresh_icon()
        super().focusOutEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Up:
            self.moveRequested.emit(-1)
            event.accept()
            return
        if event.key() == Qt.Key.Key_Down:
            self.moveRequested.emit(1)
            event.accept()
            return
        super().keyPressEvent(event)

    def _refresh_icon(self) -> None:
        highlighted = self._selected or self._hovered or self.hasFocus()
        color = PALETTE.accent if highlighted else PALETTE.secondary_text
        icon = make_tinted_svg_icon(self._icon_path, 20, color)
        self.setIcon(icon if not icon.isNull() else QIcon())

    def _repolish(self) -> None:
        style = self.style()
        style.unpolish(self)
        style.polish(self)
        self.update()


class SidebarNavigation(QFrame):
    """Balanced product sidebar built from real buttons, not item views."""

    currentRowChanged = Signal(int)

    def __init__(
        self,
        *,
        app_icon_path: str | Path,
        items: Sequence[tuple[str | Path, str]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if len(items) != 4:
            raise ValueError("sidebar requires Collect, History, Settings, and About")

        self.setObjectName("Sidebar")
        self.setFixedWidth(228)
        self._current_row = -1
        self._buttons: list[SidebarNavButton] = []
        self._wheel_delta = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 16)
        layout.setSpacing(0)

        self.identity_widget = self._build_identity(app_icon_path)
        layout.addWidget(self.identity_widget)
        layout.addSpacing(12)
        layout.addWidget(self._separator())
        layout.addSpacing(14)

        section_label = QLabel("WORKSPACE", self)
        section_label.setObjectName("SidebarSectionLabel")
        section_label.setFixedHeight(18)
        layout.addWidget(section_label)
        layout.addSpacing(8)

        group = QButtonGroup(self)
        group.setExclusive(True)
        self._button_group = group

        for index, (icon_path, title) in enumerate(items[:3]):
            button = self._make_button(index, title, icon_path)
            group.addButton(button, index)
            layout.addWidget(button)
            if index < 2:
                layout.addSpacing(8)

        layout.addStretch(1)
        layout.addWidget(self._separator())
        layout.addSpacing(12)

        about_icon, about_title = items[3]
        about_button = self._make_button(3, about_title, about_icon)
        group.addButton(about_button, 3)
        layout.addWidget(about_button)

        # Treat the complete visual sidebar as one wheel-navigation surface,
        # including its labels, brand lockup, buttons, and empty space.
        for child in self.findChildren(QWidget):
            child.installEventFilter(self)

    @property
    def buttons(self) -> tuple[SidebarNavButton, ...]:
        return tuple(self._buttons)

    @property
    def currentRow(self) -> int:
        return self._current_row

    def button(self, row: int) -> SidebarNavButton:
        return self._buttons[row]

    def set_sidebar_width(self, width: int) -> None:
        self.setFixedWidth(max(190, width))

    def eventFilter(self, watched, event: QEvent) -> bool:
        if event.type() == QEvent.Type.Wheel:
            return self._handle_wheel_event(event)
        return super().eventFilter(watched, event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self._handle_wheel_event(event):
            return
        super().wheelEvent(event)

    def setCurrentRow(self, row: int) -> None:
        if row < 0 or row >= len(self._buttons):
            return
        self._activate(row, emit=True)

    def _make_button(
        self,
        row: int,
        title: str,
        icon_path: str | Path,
    ) -> SidebarNavButton:
        button = SidebarNavButton(title, icon_path, parent=self)
        button.clicked.connect(
            lambda checked=False, target=row: self._activate(target, emit=True)
        )
        button.moveRequested.connect(
            lambda delta, source=row: self._move_from(source, delta)
        )
        self._buttons.append(button)
        return button

    def _activate(self, row: int, *, emit: bool) -> None:
        if row < 0 or row >= len(self._buttons):
            return

        changed = row != self._current_row
        self._wheel_delta = 0
        self._current_row = row
        for index, button in enumerate(self._buttons):
            button.set_selected(index == row)

        if emit and (changed or self.sender() is not None):
            self.currentRowChanged.emit(row)

    def _move_from(self, row: int, delta: int) -> None:
        if not self._buttons:
            return
        target = (row + delta) % len(self._buttons)
        self._activate(target, emit=True)
        self._buttons[target].setFocus(Qt.FocusReason.TabFocusReason)

    def _handle_wheel_event(self, event: QWheelEvent) -> bool:
        delta = event.angleDelta().y()
        if delta == 0:
            delta = event.pixelDelta().y()
        if delta == 0:
            return False

        # High-resolution wheels and touchpads can deliver partial deltas.
        # Accumulate them, but change at most one page for each input event.
        if self._wheel_delta and (self._wheel_delta > 0) != (delta > 0):
            self._wheel_delta = 0
        self._wheel_delta += delta

        if abs(self._wheel_delta) < 120:
            event.accept()
            return True

        direction = -1 if self._wheel_delta > 0 else 1
        self._wheel_delta = 0
        self._move_by_wheel(direction)
        event.accept()
        return True

    def _move_by_wheel(self, direction: int) -> None:
        if not self._buttons:
            return

        current = self._current_row if self._current_row >= 0 else 0
        target = max(0, min(len(self._buttons) - 1, current + direction))
        if target != self._current_row:
            self._activate(target, emit=True)
            # Wheel navigation must move keyboard focus together with the
            # selected page. Otherwise the previously focused button keeps
            # the QSS :focus treatment and looks like a second active item.
            self._buttons[target].setFocus(Qt.FocusReason.MouseFocusReason)

    def _build_identity(self, app_icon_path: str | Path) -> QWidget:
        """Build one product-scale brand lockup aligned with navigation."""

        identity = QFrame(self)
        identity.setObjectName("SidebarIdentity")
        # Keep the product lockup compact so navigation starts sooner without
        # shrinking the approved logo or typography.
        identity.setFixedHeight(64)
        identity.setAccessibleName("XCC Context Collector")

        layout = QHBoxLayout(identity)
        layout.setContentsMargins(0, 3, 4, 3)
        layout.setSpacing(11)

        self.identity_icon = QLabel(identity)
        self.identity_icon.setObjectName("SidebarBrandIcon")
        self.identity_icon.setFixedSize(44, 44)
        self.identity_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.identity_icon.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        icon_path = Path(app_icon_path)
        if icon_path.is_file():
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                self.identity_icon.setPixmap(
                    pixmap.scaled(
                        42,
                        42,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )

        text_box = QWidget(identity)
        text_box.setObjectName("SidebarBrandText")
        text_layout = QVBoxLayout(text_box)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)
        text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.brand_title = QLabel("XCC", text_box)
        self.brand_title.setObjectName("SidebarBrandTitle")
        self.brand_subtitle = QLabel("Context Collector", text_box)
        self.brand_subtitle.setObjectName("SidebarBrandSubtitle")

        text_layout.addWidget(self.brand_title)
        text_layout.addWidget(self.brand_subtitle)

        layout.addWidget(
            self.identity_icon,
            0,
            Qt.AlignmentFlag.AlignVCenter,
        )
        layout.addWidget(text_box, 1, Qt.AlignmentFlag.AlignVCenter)
        return identity

    def _separator(self) -> QFrame:
        separator = QFrame(self)
        separator.setObjectName("SidebarSeparator")
        separator.setFixedHeight(1)
        separator.setFrameShape(QFrame.Shape.HLine)
        return separator
