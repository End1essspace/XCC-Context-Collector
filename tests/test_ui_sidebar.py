from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QKeyEvent, QWheelEvent
from PySide6.QtWidgets import QApplication, QScrollArea

from xcc.resources import resource_path
from xcc.ui_sidebar import SidebarNavButton, SidebarNavigation


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _sidebar() -> SidebarNavigation:
    return SidebarNavigation(
        items=(
            (resource_path("assets", "nav-collect.svg"), "Collect"),
            (resource_path("assets", "nav-history.svg"), "History"),
            (resource_path("assets", "nav-settings.svg"), "Settings"),
            (resource_path("assets", "nav-about.svg"), "About"),
        ),
    )


def _wheel_event(delta: int) -> QWheelEvent:
    return QWheelEvent(
        QPointF(10, 10),
        QPointF(10, 10),
        QPoint(),
        QPoint(0, delta),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,
    )


def test_sidebar_uses_four_real_buttons_without_item_views(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()

    assert sidebar.objectName() == "Sidebar"
    assert len(sidebar.buttons) == 4
    assert all(isinstance(button, SidebarNavButton) for button in sidebar.buttons)
    assert [button.text() for button in sidebar.buttons] == [
        "Collect",
        "History",
        "Settings",
        "About",
    ]
    assert all(button.height() == 50 for button in sidebar.buttons)
    assert sidebar.button(2).text() == "Settings"


def test_sidebar_selection_is_exclusive_and_emits_page_index(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()
    emitted: list[int] = []
    sidebar.currentRowChanged.connect(emitted.append)

    sidebar.setCurrentRow(2)

    assert sidebar.currentRow == 2
    assert sidebar.button(2).property("selected") is True
    assert sum(button.isChecked() for button in sidebar.buttons) == 1
    assert emitted[-1] == 2


def test_sidebar_arrow_navigation_includes_about(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()
    sidebar.setCurrentRow(2)

    event = QKeyEvent(
        QKeyEvent.Type.KeyPress,
        Qt.Key.Key_Down,
        Qt.KeyboardModifier.NoModifier,
    )
    sidebar.button(2).keyPressEvent(event)

    assert sidebar.currentRow == 3
    assert sidebar.button(3).text() == "About"


def test_sidebar_body_starts_with_navigation_without_duplicate_brand(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()

    assert sidebar.section_label.text() == "WORKSPACE"
    assert sidebar.section_label.objectName() == "SidebarSectionLabel"
    assert not hasattr(sidebar, "identity_widget")
    assert not hasattr(sidebar, "identity_icon")
    assert not hasattr(sidebar, "brand_title")
    assert not hasattr(sidebar, "brand_subtitle")

def test_sidebar_wheel_switches_pages_from_the_complete_sidebar_surface(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()
    sidebar.setCurrentRow(0)

    QApplication.sendEvent(sidebar.section_label, _wheel_event(-120))
    assert sidebar.currentRow == 1

    QApplication.sendEvent(sidebar.button(1), _wheel_event(-120))
    assert sidebar.currentRow == 2

    QApplication.sendEvent(sidebar, _wheel_event(120))
    assert sidebar.currentRow == 1


def test_sidebar_wheel_accumulates_partial_trackpad_deltas(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()
    sidebar.setCurrentRow(0)

    for target in (
        sidebar.section_label,
        sidebar.button(0),
        sidebar.button(1),
    ):
        QApplication.sendEvent(target, _wheel_event(-30))
        assert sidebar.currentRow == 0

    QApplication.sendEvent(sidebar, _wheel_event(-30))
    assert sidebar.currentRow == 1


def test_sidebar_wheel_changes_at_most_one_page_per_event(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()
    sidebar.setCurrentRow(0)

    QApplication.sendEvent(sidebar, _wheel_event(-360))

    assert sidebar.currentRow == 1


def test_sidebar_wheel_stops_at_first_and_last_page(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()

    sidebar.setCurrentRow(0)
    QApplication.sendEvent(sidebar, _wheel_event(120))
    assert sidebar.currentRow == 0

    sidebar.setCurrentRow(3)
    QApplication.sendEvent(sidebar.section_label, _wheel_event(-120))
    assert sidebar.currentRow == 3


def test_sidebar_wheel_navigation_does_not_add_scroll_areas(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()

    assert sidebar.findChildren(QScrollArea) == []

def test_sidebar_wheel_moves_focus_to_the_new_active_button(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()
    sidebar.show()
    sidebar.setCurrentRow(1)
    sidebar.button(1).setFocus(Qt.FocusReason.MouseFocusReason)
    qapp.processEvents()

    assert sidebar.button(1).hasFocus()

    QApplication.sendEvent(sidebar, _wheel_event(-120))
    qapp.processEvents()

    assert sidebar.currentRow == 2
    assert not sidebar.button(1).hasFocus()
    assert sidebar.button(2).hasFocus()

    sidebar.close()
