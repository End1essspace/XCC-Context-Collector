from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QLabel

from xcc.ui_components import (
    MetricCapsule,
    StatusCapsule,
    make_card,
    make_card_layout,
    make_card_title,
    make_helper_text,
    make_primary_button,
    make_secondary_button,
    make_section_title,
    set_metric_value,
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


def test_metric_capsule_preserves_value_label_api(qapp: QApplication) -> None:
    metric = MetricCapsule("Files", "-")

    assert metric.objectName() == "MetricCapsule"
    assert metric.label_widget.text() == "Files"
    assert isinstance(metric.value_label, QLabel)

    metric.set_value("1,024")
    assert metric.value_label.text() == "1,024"

    set_metric_value(metric, "2,048")
    assert metric.value_label.text() == "2,048"


def test_status_capsule_and_dynamic_state(qapp: QApplication) -> None:
    capsule = StatusCapsule("Ready")
    capsule.set_state("success")

    assert capsule.objectName() == "StatusCapsule"
    assert capsule.text() == "Ready"
    assert capsule.property("state") == "success"

    capsule.set_state("unsupported")
    assert capsule.property("state") == ""


def test_button_and_helper_factories(qapp: QApplication) -> None:
    primary = make_primary_button(
        "Collect & Copy",
        height=48,
        minimum_width=180,
    )
    secondary = make_secondary_button("Cancel", minimum_width=100)
    helper = make_helper_text("Source file contents remain unchanged.")

    assert primary.objectName() == "PrimaryButton"
    assert primary.height() == 48
    assert primary.minimumWidth() == 180
    assert secondary.objectName() == "SecondaryButton"
    assert secondary.minimumWidth() == 100
    assert helper.objectName() == "HelperText"
    assert helper.wordWrap() is True
