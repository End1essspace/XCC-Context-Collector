from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon, QKeyEvent, QPixmap
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 16)
        layout.setSpacing(0)

        layout.addWidget(self._build_identity(app_icon_path))
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

    @property
    def buttons(self) -> tuple[SidebarNavButton, ...]:
        return tuple(self._buttons)

    @property
    def currentRow(self) -> int:
        return self._current_row

    def button(self, row: int) -> SidebarNavButton:
        return self._buttons[row]

    def set_sidebar_width(self, width: int) -> None:
        self.setFixedWidth(max(188, width))

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

    def _build_identity(self, app_icon_path: str | Path) -> QWidget:
        identity = QFrame(self)
        identity.setObjectName("SidebarIdentity")
        identity.setFixedHeight(62)

        layout = QHBoxLayout(identity)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(11)

        icon_label = QLabel(identity)
        icon_label.setObjectName("SidebarBrandIcon")
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_path = Path(app_icon_path)
        if icon_path.is_file():
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                icon_label.setPixmap(
                    pixmap.scaled(
                        30,
                        30,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )

        text_box = QWidget(identity)
        text_box.setObjectName("TransparentWidget")
        text_layout = QVBoxLayout(text_box)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        title = QLabel("XCC", text_box)
        title.setObjectName("SidebarBrandTitle")
        subtitle = QLabel("Context Collector", text_box)
        subtitle.setObjectName("SidebarBrandSubtitle")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)

        layout.addWidget(icon_label)
        layout.addWidget(text_box, 1)
        return identity

    def _separator(self) -> QFrame:
        separator = QFrame(self)
        separator.setObjectName("SidebarSeparator")
        separator.setFixedHeight(1)
        separator.setFrameShape(QFrame.Shape.HLine)
        return separator
