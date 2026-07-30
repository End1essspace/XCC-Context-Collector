from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QApplication

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
        app_icon_path=resource_path("assets", "xcc_app.png"),
        items=(
            (resource_path("assets", "nav-collect.svg"), "Collect"),
            (resource_path("assets", "nav-history.svg"), "History"),
            (resource_path("assets", "nav-settings.svg"), "Settings"),
            (resource_path("assets", "nav-about.svg"), "About"),
        ),
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


def test_sidebar_identity_uses_product_scale_artwork_without_logo_card(
    qapp: QApplication,
) -> None:
    sidebar = _sidebar()

    identity = sidebar.identity_widget
    icon = sidebar.identity_icon

    assert identity.objectName() == "SidebarIdentity"
    assert identity.height() == 72
    assert identity.accessibleName() == "XCC Context Collector"
    assert icon.objectName() == "SidebarBrandIcon"
    assert icon.size().width() == 44
    assert icon.size().height() == 44
    assert not hasattr(sidebar, "identity_mark")
    assert sidebar.brand_title.text() == "XCC"
    assert sidebar.brand_subtitle.text() == "Context Collector"
