from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QSize
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QLabel, QPushButton

from xcc.resources import resource_path
from xcc.ui_theme import METRICS, PALETTE

from xcc.ui_components import (
    DpiAwareImageLabel,
    ElidedLabel,
    IconTitle,
    MetricCapsule,
    PageHeader,
    RuntimeStatusCapsule,
    StatusCapsule,
    make_card,
    make_card_layout,
    make_card_title,
    make_helper_text,
    make_icon_title,
    make_page_header,
    make_primary_button,
    make_runtime_status_capsule,
    make_secondary_button,
    make_tinted_svg_icon,
    render_dpi_aware_raster,
    render_tinted_svg,
    make_section_title,
    set_metric_value,
    set_tinted_button_icon,
    set_widget_property,
    set_widget_state,
)




def _opaque_rgb_values(pixmap) -> set[str]:
    image = pixmap.toImage()
    values: set[str] = set()

    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            if color.alpha() > 0:
                values.add(color.name(QColor.NameFormat.HexRgb).upper())

    return values


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_shared_titles_and_card_layout(qapp: QApplication) -> None:
    section = make_section_title("Collect Context")
    card_title = make_card_title("Setup")
    card = make_card()
    layout = make_card_layout(card)

    assert section.objectName() == "SectionTitle"
    assert section.text() == "Collect Context"
    assert card_title.objectName() == "CardTitle"
    assert card_title.text() == "Setup"
    assert card.objectName() == "Card"
    assert layout.contentsMargins().left() == 24
    assert layout.contentsMargins().top() == 18
    assert layout.spacing() == 20




def test_page_header_exposes_title_and_subtitle(qapp: QApplication) -> None:
    header = make_page_header(
        "Collect Context",
        "Configure what to collect and generate an AI-ready context snapshot.",
    )

    assert isinstance(header, PageHeader)
    assert header.objectName() == "PageHeader"
    assert header.title_label.text() == "Collect Context"
    assert header.subtitle_label.objectName() == "PageSubtitle"
    assert "AI-ready context snapshot" in header.subtitle_label.text()
    assert header.height() == 42
    assert isinstance(header.subtitle_label, ElidedLabel)
    assert header.layout().itemAt(0).widget() is header.title_label
    assert header.layout().itemAt(1).widget() is header.subtitle_label
    assert header.layout().itemAt(2).widget() is header.actions_widget

    action = QLabel("Ready")
    header.add_action(action)
    assert header.actions_layout.count() == 1


def test_metric_capsule_preserves_value_label_contract(qapp: QApplication) -> None:
    metric = MetricCapsule("Files", "-")

    assert metric.objectName() == "MetricCapsule"
    assert metric.height() == METRICS.metric_row_height
    assert metric.label_widget.text() == "Files"
    assert metric.accessibleName() == "Files metric"
    assert metric.label_widget.accessibleName() == "Files metric label"
    assert metric.value_label.accessibleName() == "Files metric value"
    assert isinstance(metric.value_label, QLabel)
    assert metric.value_label.property("state") == "neutral"

    set_metric_value(metric, "2,048")
    assert metric.value_label.text() == "2,048"

    metric.set_density(
        58,
        minimum_height=54,
        maximum_height=62,
        horizontal_padding=12,
    )
    assert metric.minimumHeight() == 54
    assert metric.maximumHeight() == 62
    assert metric.sizeHint().height() == 58
    assert metric.layout().contentsMargins().left() == 12
    assert metric.layout().contentsMargins().right() == 12

    with pytest.raises(ValueError):
        metric.set_density(0, horizontal_padding=12)

    with pytest.raises(ValueError):
        metric.set_density(50, horizontal_padding=-1)

    with pytest.raises(ValueError):
        metric.set_density(
            58,
            minimum_height=62,
            maximum_height=54,
            horizontal_padding=12,
        )



def test_icon_title_uses_packaged_svg_asset(qapp: QApplication) -> None:
    title = make_icon_title(
        "Last Run",
        resource_path("assets", "ui-last-run.svg"),
        object_name="MetricGroupHeader",
        text_object_name="MetricGroupTitle",
        icon_object_name="MetricGroupIcon",
    )

    assert isinstance(title, IconTitle)
    assert title.objectName() == "MetricGroupHeader"
    assert title.text_label.text() == "Last Run"
    assert title.icon_label.pixmap() is not None
    assert not title.icon_label.pixmap().isNull()
    assert PALETTE.accent.upper() in _opaque_rgb_values(
        title.icon_label.pixmap()
    )

def test_svg_tinting_overrides_original_lucide_stroke(
    qapp: QApplication,
) -> None:
    pixmap = render_tinted_svg(
        resource_path("assets", "ui-health.svg"),
        24,
        PALETTE.accent,
    )

    assert not pixmap.isNull()
    colors = _opaque_rgb_values(pixmap)
    assert colors
    assert PALETTE.accent.upper() in colors
    assert "#000000" not in colors


def test_dpi_aware_raster_preserves_logical_size_at_fractional_scale(
    qapp: QApplication,
) -> None:
    pixmap = render_dpi_aware_raster(
        resource_path("assets", "xcc_app.png"),
        32,
        device_pixel_ratio=1.5,
    )

    assert not pixmap.isNull()
    assert pixmap.devicePixelRatio() == pytest.approx(1.5)
    assert pixmap.width() == 48
    assert pixmap.height() == 48
    assert pixmap.deviceIndependentSize().width() == pytest.approx(32.0)
    assert pixmap.deviceIndependentSize().height() == pytest.approx(32.0)


def test_dpi_sensitive_labels_can_rerender_for_new_screen_scale(
    qapp: QApplication,
) -> None:
    raster = DpiAwareImageLabel(
        resource_path("assets", "xcc_app.png"),
        32,
    )
    raster.refresh_pixmap(1.5)
    assert raster.pixmap() is not None
    assert raster.pixmap().devicePixelRatio() == pytest.approx(1.5)

    title = make_icon_title(
        "Setup",
        resource_path("assets", "ui-setup.svg"),
        object_name="CardTitleRow",
        text_object_name="CardTitle",
        icon_object_name="CardTitleIcon",
    )
    title.refresh_icon(1.5)
    assert title.icon_label.pixmap() is not None
    assert title.icon_label.pixmap().devicePixelRatio() == pytest.approx(1.5)


def test_tinted_button_icons_use_surface_specific_colors(
    qapp: QApplication,
) -> None:
    paste_icon = make_tinted_svg_icon(
        resource_path("assets", "ui-paste-paths.svg"),
        18,
        PALETTE.accent,
    )
    paste_pixmap = paste_icon.pixmap(QSize(18, 18))
    assert PALETTE.accent.upper() in _opaque_rgb_values(paste_pixmap)

    button = QPushButton("Collect & Copy")
    set_tinted_button_icon(
        button,
        resource_path("assets", "ui-collect-copy.svg"),
        size=20,
        color=PALETTE.dark_text,
    )
    button_pixmap = button.icon().pixmap(QSize(20, 20))
    assert PALETTE.dark_text.upper() in _opaque_rgb_values(button_pixmap)


def test_status_capsule_and_dynamic_state(qapp: QApplication) -> None:
    capsule = StatusCapsule("Ready")
    capsule.set_state("success")

    assert capsule.objectName() == "StatusCapsule"
    assert capsule.text() == "Ready"
    assert capsule.property("state") == "success"

    capsule.set_state("unsupported")
    assert capsule.property("state") == ""


def test_runtime_status_capsule_preserves_text_and_state_api(
    qapp: QApplication,
) -> None:
    capsule = make_runtime_status_capsule("Ready")

    assert isinstance(capsule, RuntimeStatusCapsule)
    assert capsule.objectName() == "RuntimeStatusCapsule"
    assert capsule.text() == "Ready"
    assert capsule.indicator.objectName() == "RuntimeStatusDot"

    capsule.setText("Working")
    capsule.set_state("neutral")

    assert capsule.text() == "Working"
    assert capsule.property("state") == "neutral"
    assert capsule.indicator.property("state") == "neutral"

    set_widget_state(capsule.indicator, "warning")
    assert capsule.indicator.property("state") == "warning"

    set_widget_property(capsule, "reviewable", True)
    assert capsule.property("reviewable") is True


def test_button_and_helper_factories(qapp: QApplication) -> None:
    primary = make_primary_button(
        "Collect & Copy",
        height=52,
        minimum_width=180,
        icon_path=resource_path("assets", "ui-collect-copy.svg"),
        icon_size=20,
    )
    secondary = make_secondary_button("Cancel", minimum_width=100)
    helper = make_helper_text("Source file contents remain unchanged.")

    assert primary.objectName() == "PrimaryButton"
    assert primary.height() == 52
    assert not primary.icon().isNull()
    assert primary.minimumWidth() == 180
    assert secondary.objectName() == "SecondaryButton"
    assert secondary.minimumWidth() == 100
    assert helper.objectName() == "HelperText"
    assert helper.wordWrap() is True
