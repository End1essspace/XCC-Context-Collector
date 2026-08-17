from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QEvent, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
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


def render_dpi_aware_raster(
    image_path: str | Path,
    size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap:
    """Scale a raster asset for one logical square at the requested DPR."""
    if size <= 0:
        raise ValueError("size must be greater than 0")

    path = Path(image_path)
    if not path.is_file():
        return QPixmap()

    source = QPixmap(str(path))
    if source.isNull():
        return QPixmap()

    ratio = max(1.0, float(device_pixel_ratio))
    physical_size = max(1, round(size * ratio))
    pixmap = source.scaled(
        physical_size,
        physical_size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    pixmap.setDevicePixelRatio(ratio)
    return pixmap


class DpiAwareImageLabel(QLabel):
    """Fixed logical-size raster label that owns its DPR-aware pixmap.

    QLabel may normalize the DPR of a pixmap passed through setPixmap() on
    some PySide6/Windows backends. Keeping the rendered pixmap ourselves and
    painting it directly preserves both the logical widget size and the
    higher-resolution raster buffer at fractional display scales.
    """

    def __init__(
        self,
        image_path: str | Path,
        size: int,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if size <= 0:
            raise ValueError("size must be greater than 0")

        self._image_path = Path(image_path)
        self._logical_size = size
        self._dpi_pixmap = QPixmap()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.refresh_pixmap()

    def pixmap(self) -> QPixmap:
        """Return the currently rendered DPR-aware pixmap by value."""

        return QPixmap(self._dpi_pixmap)

    def refresh_pixmap(
        self,
        device_pixel_ratio: float | None = None,
    ) -> None:
        ratio = (
            max(1.0, float(device_pixel_ratio))
            if device_pixel_ratio is not None
            else max(1.0, float(self.devicePixelRatioF()))
        )
        self._dpi_pixmap = render_dpi_aware_raster(
            self._image_path,
            self._logical_size,
            device_pixel_ratio=ratio,
        )
        self.update()

    def paintEvent(self, event: QEvent) -> None:
        del event

        if self._dpi_pixmap.isNull():
            return

        painter = QPainter(self)
        logical_size = self._dpi_pixmap.deviceIndependentSize()
        target = QRectF(
            (self.width() - logical_size.width()) / 2.0,
            (self.height() - logical_size.height()) / 2.0,
            logical_size.width(),
            logical_size.height(),
        )
        painter.drawPixmap(target, self._dpi_pixmap, QRectF(self._dpi_pixmap.rect()))
        painter.end()

    def event(self, event: QEvent) -> bool:
        handled = super().event(event)
        if event.type() == QEvent.Type.DevicePixelRatioChange:
            self.refresh_pixmap()
        return handled


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


class ElidedLabel(QLabel):
    """One-line label that gives priority to adjacent controls."""

    def __init__(
        self,
        text: str,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._full_text = text
        self.setText(text)
        self.setToolTip(text)
        self.setWordWrap(False)
        self.setMinimumWidth(0)
        self.setSizePolicy(
            QSizePolicy.Policy.Ignored,
            QSizePolicy.Policy.Fixed,
        )

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh_elision()

    def _refresh_elision(self) -> None:
        available = max(0, self.contentsRect().width())
        self.setText(
            self.fontMetrics().elidedText(
                self._full_text,
                Qt.TextElideMode.ElideRight,
                available,
            )
        )


class PageHeader(QWidget):
    """Single-row page title, elided subtitle, and low-emphasis actions."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("PageHeader")
        self.setFixedHeight(42)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("SectionTitle")
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.title_label.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )

        self.subtitle_label = ElidedLabel(subtitle, parent=self)
        self.subtitle_label.setObjectName("PageSubtitle")
        self.subtitle_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.actions_widget = QWidget(self)
        self.actions_widget.setObjectName("PageHeaderActions")
        self.actions_widget.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Fixed,
        )
        self.actions_layout = QHBoxLayout(self.actions_widget)
        self.actions_layout.setContentsMargins(0, 0, 0, 0)
        self.actions_layout.setSpacing(10)

        layout.addWidget(self.title_label, 0)
        layout.addWidget(self.subtitle_label, 1)
        layout.addWidget(self.actions_widget, 0)

    def add_action(self, widget: QWidget) -> None:
        self.actions_layout.addWidget(widget)


class DpiAwareSvgLabel(QLabel):
    """Fixed logical-size SVG label that preserves fractional DPR metadata."""

    def __init__(
        self,
        icon_path: str | Path,
        size: int,
        color: str,
        *,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        if size <= 0:
            raise ValueError("size must be greater than 0")

        self._icon_path = Path(icon_path)
        self._logical_size = size
        self._color = color
        self._dpi_pixmap = QPixmap()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.refresh_pixmap()

    def pixmap(self) -> QPixmap:
        """Return the currently rendered DPR-aware pixmap by value."""

        return QPixmap(self._dpi_pixmap)

    def refresh_pixmap(
        self,
        device_pixel_ratio: float | None = None,
    ) -> None:
        ratio = (
            max(1.0, float(device_pixel_ratio))
            if device_pixel_ratio is not None
            else max(1.0, float(self.devicePixelRatioF()))
        )
        self._dpi_pixmap = render_tinted_svg(
            self._icon_path,
            self._logical_size,
            self._color,
            device_pixel_ratio=ratio,
        )
        self.update()

    def paintEvent(self, event: QEvent) -> None:
        del event

        if self._dpi_pixmap.isNull():
            return

        painter = QPainter(self)
        logical_size = self._dpi_pixmap.deviceIndependentSize()
        target = QRectF(
            (self.width() - logical_size.width()) / 2.0,
            (self.height() - logical_size.height()) / 2.0,
            logical_size.width(),
            logical_size.height(),
        )
        painter.drawPixmap(
            target,
            self._dpi_pixmap,
            QRectF(self._dpi_pixmap.rect()),
        )
        painter.end()

    def event(self, event: QEvent) -> bool:
        handled = super().event(event)
        if event.type() == QEvent.Type.DevicePixelRatioChange:
            self.refresh_pixmap()
        return handled


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

        self._icon_path = Path(icon_path)
        self._icon_size = icon_size
        self._icon_color = icon_color

        self.icon_label = DpiAwareSvgLabel(
            self._icon_path,
            self._icon_size,
            self._icon_color,
            parent=self,
        )
        self.icon_label.setObjectName(icon_object_name)

        self.text_label = QLabel(text, self)
        self.text_label.setObjectName(text_object_name)
        self.text_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addStretch(1)

    def refresh_icon(
        self,
        device_pixel_ratio: float | None = None,
    ) -> None:
        self.icon_label.refresh_pixmap(device_pixel_ratio)

    def event(self, event: QEvent) -> bool:
        handled = super().event(event)
        if event.type() == QEvent.Type.DevicePixelRatioChange:
            self.refresh_icon()
        return handled


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
        self.setAccessibleName(f"{label} metric")
        self.setMinimumWidth(0)
        self._layout = QHBoxLayout(self)
        self._layout.setSpacing(12)
        self.set_density(
            METRICS.metric_row_height,
            horizontal_padding=14,
        )

        layout = self._layout

        self.label_widget = QLabel(label, self)
        self.label_widget.setObjectName("MetricLabel")
        self.label_widget.setAccessibleName(f"{label} metric label")
        self.label_widget.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.value_label = QLabel(value, self)
        self.value_label.setObjectName("MetricValue")
        self.value_label.setAccessibleName(f"{label} metric value")
        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.label_widget, 1)
        layout.addWidget(self.value_label, 0)

        if value == "-":
            self.set_state("neutral")

    def set_density(
        self,
        height: int,
        *,
        horizontal_padding: int,
        minimum_height: int | None = None,
        maximum_height: int | None = None,
    ) -> None:
        """Set a preferred responsive height while allowing equal expansion."""
        if height <= 0:
            raise ValueError("height must be greater than 0")
        if horizontal_padding < 0:
            raise ValueError("horizontal_padding must not be negative")

        minimum = height if minimum_height is None else minimum_height
        maximum = height if maximum_height is None else maximum_height
        if minimum <= 0:
            raise ValueError("minimum_height must be greater than 0")
        if maximum < minimum:
            raise ValueError("maximum_height must be at least minimum_height")
        if not minimum <= height <= maximum:
            raise ValueError("height must be inside the minimum/maximum range")

        self._preferred_height = height
        self.setMinimumHeight(minimum)
        self.setMaximumHeight(maximum)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            (
                QSizePolicy.Policy.Expanding
                if maximum > minimum
                else QSizePolicy.Policy.Fixed
            ),
        )
        self._layout.setContentsMargins(
            horizontal_padding,
            0,
            horizontal_padding,
            0,
        )
        self.updateGeometry()

    def sizeHint(self) -> QSize:
        hint = super().sizeHint()
        return QSize(hint.width(), getattr(self, "_preferred_height", hint.height()))

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
