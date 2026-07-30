from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .ui_theme import METRICS, PALETTE


def render_tinted_svg(
    icon_path: str | Path,
    size: int,
    color: str,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap:
    """Render an SVG into a transparent pixmap and force one semantic color.

    Lucide SVG files commonly use ``currentColor`` or an explicit dark stroke.
    Qt does not inherit QSS text color into standalone SVG assets, so rendering
    them directly through QIcon can leave the icon black on a dark surface.
    SourceIn tinting makes source and packaged builds deterministic regardless
    of how the original SVG encodes its stroke color.
    """
    if size <= 0:
        raise ValueError("size must be greater than 0")

    ratio = max(1.0, float(device_pixel_ratio))
    physical_size = max(1, round(size * ratio))
    pixmap = QPixmap(physical_size, physical_size)
    pixmap.setDevicePixelRatio(ratio)
    pixmap.fill(Qt.GlobalColor.transparent)

    path = Path(icon_path)
    if not path.is_file():
        return QPixmap()

    renderer = QSvgRenderer(str(path))
    if not renderer.isValid():
        return QPixmap()

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    renderer.render(painter, QRectF(0.0, 0.0, float(size), float(size)))
    painter.setCompositionMode(
        QPainter.CompositionMode.CompositionMode_SourceIn
    )
    painter.fillRect(
        QRectF(0.0, 0.0, float(size), float(size)),
        QColor(color),
    )
    painter.end()
    return pixmap


def make_tinted_svg_icon(
    icon_path: str | Path,
    size: int,
    color: str,
) -> QIcon:
    """Return a high-DPI QIcon whose visible SVG pixels use ``color``."""
    icon = QIcon()
    for ratio in (1.0, 2.0):
        pixmap = render_tinted_svg(
            icon_path,
            size,
            color,
            device_pixel_ratio=ratio,
        )
        if not pixmap.isNull():
            icon.addPixmap(pixmap)
    return icon


def set_tinted_button_icon(
    button: QPushButton,
    icon_path: str | Path,
    *,
    size: int,
    color: str,
) -> None:
    button.setIcon(make_tinted_svg_icon(icon_path, size, color))
    button.setIconSize(QSize(size, size))


class PageHeader(QWidget):
    """Page title, subtitle, and low-emphasis page actions."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("PageHeader")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(12)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("SectionTitle")

        self.actions_widget = QWidget(self)
        self.actions_widget.setObjectName("PageHeaderActions")
        self.actions_layout = QHBoxLayout(self.actions_widget)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(10)

        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        title_row.addWidget(self.actions_widget)

        self.subtitle_label = QLabel(subtitle, self)
        self.subtitle_label.setObjectName("PageSubtitle")
        self.subtitle_label.setWordWrap(False)

        layout.addLayout(title_row)
        layout.addWidget(self.subtitle_label)

    def add_action(self, widget: QWidget) -> None:
        self.actions_layout.addWidget(widget)


class IconTitle(QWidget):
    """Small icon + title row used by cards and metric groups."""

    def __init__(
        self,
        text: str,
        icon_path: str | Path,
        *,
        object_name: str,
        text_object_name: str,
        icon_object_name: str,
        icon_size: int = 18,
        icon_color: str = PALETTE.accent,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.icon_label = QLabel(self)
        self.icon_label.setObjectName(icon_object_name)
        self.icon_label.setFixedSize(icon_size, icon_size)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = render_tinted_svg(
            icon_path,
            icon_size,
            icon_color,
            device_pixel_ratio=max(1.0, float(self.devicePixelRatioF())),
        )
        if not pixmap.isNull():
            self.icon_label.setPixmap(pixmap)

        self.text_label = QLabel(text, self)
        self.text_label.setObjectName(text_object_name)
        self.text_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch(1)


class MetricCapsule(QFrame):
    """Lightweight metric row with aligned label and value."""

    def __init__(
        self,
        label: str,
        value: str = "-",
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("MetricCapsule")
        self.setMinimumWidth(0)
        self.setFixedHeight(METRICS.metric_row_height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(12)

        self.label_widget = QLabel(label, self)
        self.label_widget.setObjectName("MetricLabel")
        self.label_widget.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.value_label = QLabel(value, self)
        self.value_label.setObjectName("MetricValue")
        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.label_widget, 1)
        layout.addWidget(self.value_label, 0)

        if value == "-":
            self.set_state("neutral")

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

    def set_state(self, state: str | None) -> None:
        _set_dynamic_state(self.value_label, state)


class RuntimeStatusCapsule(QFrame):
    """Runtime state with a restrained semantic indicator and fixed text API."""

    def __init__(
        self,
        text: str,
        *,
        height: int = 34,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("RuntimeStatusCapsule")
        self.setFixedHeight(height)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        self.indicator = QLabel(self)
        self.indicator.setObjectName("RuntimeStatusDot")
        self.indicator.setFixedSize(8, 8)

        self.text_label = QLabel(text, self)
        self.text_label.setObjectName("RuntimeStatusText")
        self.text_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.indicator, 0, Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.text_label)

    def text(self) -> str:
        return self.text_label.text()

    def setText(self, text: str) -> None:
        self.text_label.setText(text)

    def set_state(self, state: str | None) -> None:
        _set_dynamic_state(self, state)
        _set_dynamic_state(self.indicator, state)


class StatusCapsule(QLabel):
    """Shared capsule for hotkey and low-emphasis metadata."""

    def __init__(
        self,
        text: str,
        *,
        object_name: str = "StatusCapsule",
        height: int = 34,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName(object_name)
        self.setFixedHeight(height)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_state(self, state: str | None) -> None:
        _set_dynamic_state(self, state)


def make_page_header(
    title: str,
    subtitle: str,
    *,
    parent: QWidget | None = None,
) -> PageHeader:
    return PageHeader(title, subtitle, parent=parent)


def make_icon_title(
    text: str,
    icon_path: str | Path,
    *,
    object_name: str = "CardTitleRow",
    text_object_name: str = "CardTitle",
    icon_object_name: str = "CardTitleIcon",
    icon_size: int = 18,
    icon_color: str = PALETTE.accent,
    parent: QWidget | None = None,
) -> IconTitle:
    return IconTitle(
        text,
        icon_path,
        object_name=object_name,
        text_object_name=text_object_name,
        icon_object_name=icon_object_name,
        icon_size=icon_size,
        icon_color=icon_color,
        parent=parent,
    )


def make_section_title(
    text: str,
    *,
    object_name: str = "SectionTitle",
    parent: QWidget | None = None,
) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName(object_name)
    return label


def make_card_title(
    text: str,
    *,
    object_name: str = "CardTitle",
    parent: QWidget | None = None,
) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName(object_name)
    label.setFixedHeight(20)
    label.setAlignment(
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
    )
    return label


def make_card(
    *,
    object_name: str = "Card",
    parent: QWidget | None = None,
) -> QFrame:
    card = QFrame(parent)
    card.setObjectName(object_name)
    return card


def make_card_layout(
    card: QFrame,
    *,
    left: int = 24,
    top: int = 18,
    right: int = 24,
    bottom: int = 18,
    spacing: int = 20,
) -> QVBoxLayout:
    layout = QVBoxLayout(card)
    layout.setContentsMargins(left, top, right, bottom)
    layout.setSpacing(spacing)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    return layout


def make_runtime_status_capsule(
    text: str,
    *,
    height: int = 34,
    parent: QWidget | None = None,
) -> RuntimeStatusCapsule:
    return RuntimeStatusCapsule(
        text,
        height=height,
        parent=parent,
    )


def make_status_capsule(
    text: str,
    *,
    object_name: str = "StatusCapsule",
    height: int = 34,
    parent: QWidget | None = None,
) -> StatusCapsule:
    return StatusCapsule(
        text,
        object_name=object_name,
        height=height,
        parent=parent,
    )


def make_primary_button(
    text: str,
    *,
    object_name: str = "PrimaryButton",
    height: int = METRICS.control_height,
    minimum_width: int | None = None,
    icon_path: str | Path | None = None,
    icon_size: int = 18,
    icon_color: str = PALETTE.dark_text,
    parent: QWidget | None = None,
) -> QPushButton:
    button = QPushButton(text, parent)
    button.setObjectName(object_name)
    button.setFixedHeight(height)
    if minimum_width is not None:
        button.setMinimumWidth(minimum_width)
    if icon_path is not None:
        set_tinted_button_icon(
            button,
            icon_path,
            size=icon_size,
            color=icon_color,
        )
    return button


def make_secondary_button(
    text: str,
    *,
    object_name: str = "SecondaryButton",
    height: int = METRICS.control_height,
    minimum_width: int | None = None,
    parent: QWidget | None = None,
) -> QPushButton:
    button = QPushButton(text, parent)
    button.setObjectName(object_name)
    button.setFixedHeight(height)
    if minimum_width is not None:
        button.setMinimumWidth(minimum_width)
    return button


def make_helper_text(
    text: str,
    *,
    object_name: str = "HelperText",
    word_wrap: bool = True,
    parent: QWidget | None = None,
) -> QLabel:
    label = QLabel(text, parent)
    label.setObjectName(object_name)
    label.setWordWrap(word_wrap)
    return label


def set_metric_value(metric: MetricCapsule | QFrame, value: str) -> None:
    value_label = getattr(metric, "value_label", None)
    if not isinstance(value_label, QLabel):
        raise TypeError("metric must expose a QLabel value_label")

    value_label.setText(value)


def set_widget_state(widget: QWidget, state: str | None) -> None:
    _set_dynamic_state(widget, state)


def set_widget_property(
    widget: QWidget,
    name: str,
    value: object,
) -> None:
    widget.setProperty(name, value)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def _set_dynamic_state(widget: QWidget, state: str | None) -> None:
    normalized = state if state in {"success", "warning", "error", "neutral"} else ""
    widget.setProperty("state", normalized)
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()
