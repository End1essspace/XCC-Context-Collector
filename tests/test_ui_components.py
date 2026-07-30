from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel

from xcc.resources import resource_path
from xcc.ui_theme import METRICS

from xcc.ui_components import (
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
    make_section_title,
    set_metric_value,
    set_widget_property,
    set_widget_state,
)


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

    action = QLabel("Ready")
    header.add_action(action)
    assert header.actions_layout.count() == 1


def test_metric_capsule_preserves_value_label_api(qapp: QApplication) -> None:
    metric = MetricCapsule("Files", "-")

    assert metric.objectName() == "MetricCapsule"
    assert metric.height() == METRICS.metric_row_height
    assert metric.label_widget.text() == "Files"
    assert isinstance(metric.value_label, QLabel)
    assert metric.value_label.property("state") == "neutral"

    metric.set_value("1,024")
    assert metric.value_label.text() == "1,024"

    set_metric_value(metric, "2,048")
    assert metric.value_label.text() == "2,048"



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
