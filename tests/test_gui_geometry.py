from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication

from xcc.gui import XccMainWindow
from xcc.ui_responsive import CollectLayoutMode


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _settle(qapp: QApplication, window: XccMainWindow) -> None:
    for _ in range(4):
        qapp.processEvents()
        window._apply_collect_layout(force=True)


def test_maximized_geometry_has_no_scrollbar_and_keeps_cta_visible(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(1688, 900)
    window.show()
    _settle(qapp, window)

    assert window._collect_layout_mode is CollectLayoutMode.LARGE
    assert (
        window.collect_page_scroll.verticalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert window.setup_card.height() >= 248
    assert window.stats_card.height() >= 310
    assert all(button.isVisible() for button in window.nav.buttons)
    assert window.nav.button(2).text() == "Settings"
    assert window.nav.button(2).height() == 50

    button_bottom = window.collect_button.mapTo(
        window.collect_page_scroll.viewport(),
        QPoint(0, window.collect_button.height()),
    ).y()
    assert button_bottom <= window.collect_page_scroll.viewport().height()

    window._is_quitting = True
    window.close()


def test_minimum_window_uses_vertical_scroll_without_horizontal_scroll(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(920, 620)
    window.show()
    _settle(qapp, window)

    assert window._collect_layout_mode is CollectLayoutMode.COMPACT
    assert (
        window.collect_page_scroll.horizontalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )
    assert (
        window.collect_page_scroll.verticalScrollBarPolicy()
        == Qt.ScrollBarPolicy.ScrollBarAsNeeded
    )

    window._is_quitting = True
    window.close()
