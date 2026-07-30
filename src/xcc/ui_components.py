from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .ui_theme import METRICS




class PageHeader(QWidget):
    """Page title and subtitle with a stable API for responsive visibility."""

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
        layout.setSpacing(5)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("SectionTitle")

        self.subtitle_label = QLabel(subtitle, self)
        self.subtitle_label.setObjectName("PageSubtitle")
        self.subtitle_label.setWordWrap(False)

        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)


class MetricCapsule(QFrame):
    """Reusable metric display that preserves the existing ``value_label`` API."""

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
        self.setFixedHeight(52)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 6, 14, 6)
        layout.setSpacing(2)

        self.label_widget = QLabel(label, self)
        self.label_widget.setObjectName("MetricLabel")

        self.value_label = QLabel(value, self)
        self.value_label.setObjectName("MetricValue")

        layout.addWidget(self.label_widget)
        layout.addWidget(self.value_label)

    def set_value(self, value: str) -> None:
        self.value_label.setText(value)

    def set_state(self, state: str | None) -> None:
        _set_dynamic_state(self.value_label, state)


class RuntimeStatusCapsule(QFrame):
    """Header runtime state with a restrained semantic indicator and fixed text API."""

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
    """Shared capsule for runtime state, hotkey, and low-emphasis metadata."""

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
    label.setFixedHeight(18)
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
    parent: QWidget | None = None,
) -> QPushButton:
    button = QPushButton(text, parent)
    button.setObjectName(object_name)
    button.setFixedHeight(height)
    if minimum_width is not None:
        button.setMinimumWidth(minimum_width)
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
