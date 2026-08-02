from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, QSize, Qt
from PySide6.QtWidgets import QApplication, QSizePolicy

from xcc.gui import (
    HTBOTTOMRIGHT,
    HTCAPTION,
    HTTOPLEFT,
    XccMainWindow,
)
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
    assert window.setup_card.height() >= 278
    assert window.stats_card.height() >= 292
    assert window.stats_card.height() <= 340
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




def test_maximized_density_balances_setup_and_last_run(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(1688, 900)
    window.show()
    _settle(qapp, window)

    assert window.windowFlags() & Qt.WindowType.FramelessWindowHint
    assert window.window_title_bar.height() == 48
    assert window.sidebar_brand_header.height() == 48
    assert (
        window.sidebar_brand_header.height()
        == window.window_title_bar.height()
    )
    brand_bottom = window.sidebar_brand_header.mapTo(
        window.window_frame,
        QPoint(0, window.sidebar_brand_header.height()),
    ).y()
    title_bottom = window.window_title_bar.mapTo(
        window.window_frame,
        QPoint(0, window.window_title_bar.height()),
    ).y()
    assert brand_bottom == title_bottom
    assert window.status_bar.height() == 36
    assert not hasattr(window, "sidebar_footer")
    assert window.sidebar_brand_header.width() == window.nav.width()
    assert window.sidebar_shell.width() == window.nav.width()
    assert window.sidebar_shell.height() == window.content_shell.height()
    assert window.sidebar_shell.height() == window.shell_body.height()
    frame_contents = window.window_frame.contentsRect()
    assert (
        window.shell_body.height() + window.status_bar.height()
        == frame_contents.height()
    )
    assert window.status_bar.width() == frame_contents.width()
    assert window.status_label.alignment() & Qt.AlignmentFlag.AlignLeft
    assert window.sidebar_status_group.parent() is window.status_bar
    assert window.status_bar_layout.contentsMargins().left() == 20
    assert window.status_bar_layout.contentsMargins().right() == 20
    assert window.sidebar_status_layout.spacing() == 7
    assert window.sidebar_brand_header.layout().contentsMargins().left() == 14
    assert window.sidebar_brand_header.layout().contentsMargins().right() == 8
    assert window.sidebar_brand_header.layout().contentsMargins().top() == 7
    assert window.sidebar_brand_header.layout().contentsMargins().bottom() == 7
    assert window.sidebar_brand_header.layout().spacing() == 10
    assert window.sidebar_brand_icon.size().width() == 34
    assert window.sidebar_brand_icon.pixmap().deviceIndependentSize().width() == 34
    assert window.sidebar_brand_title.text() == "XCC"
    assert window.sidebar_brand_subtitle.text() == "Context Collector"
    assert window.sidebar_brand_separator.size() == QSize(1, 16)
    assert window.sidebar_brand_text_layout.spacing() == 0
    assert window.sidebar_brand_title.x() < window.sidebar_brand_separator.x()
    assert window.sidebar_brand_separator.x() < window.sidebar_brand_subtitle.x()
    assert (
        window.sidebar_brand_text_layout.itemAt(0).alignment()
        & Qt.AlignmentFlag.AlignVCenter
    )
    assert not (
        window.sidebar_brand_text_layout.itemAt(0).alignment()
        & Qt.AlignmentFlag.AlignBaseline
    )
    assert (
        window.sidebar_brand_text_layout.itemAt(2).alignment()
        & Qt.AlignmentFlag.AlignVCenter
    )
    assert (
        window.sidebar_brand_text_layout.itemAt(4).alignment()
        & Qt.AlignmentFlag.AlignVCenter
    )
    assert window.sidebar_brand_separator.isVisible()
    assert window.sidebar_brand_subtitle.isVisible()
    assert not hasattr(window, "window_brand_icon")
    assert not hasattr(window, "window_brand_title")
    assert not hasattr(window, "window_brand_subtitle")
    assert not hasattr(window, "status_version_label")
    assert window.window_controls_layout.spacing() == 4
    assert window.window_controls_layout.contentsMargins().right() == 6
    assert all(
        button.text() == ""
        and button.width() == 52
        and button.height() == 48
        and button.iconSize().width() == 16
        and button.focusPolicy() == Qt.FocusPolicy.NoFocus
        and not button.icon().isNull()
        for button in (
            window.window_minimize_button,
            window.window_maximize_button,
            window.window_close_button,
        )
    )
    assert window.setup_card_layout.contentsMargins().top() == 22
    assert window.setup_grid.verticalSpacing() == 12
    assert window.stats_card_layout.contentsMargins().top() == 14
    assert window.stats_card_layout.spacing() == 10
    assert window.last_run_state_label.height() == 28
    assert all(metric.maximumHeight() <= 60 for metric in window.metric_capsules)

    window._is_quitting = True
    window.close()

def test_large_mode_selector_remains_compact_and_left_aligned(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(1688, 900)
    window.show()
    _settle(qapp, window)

    assert window._collect_layout_mode is CollectLayoutMode.LARGE
    assert window.mode_buttons.objectName() == "ModeSelectorGroup"
    assert (
        window.mode_buttons.sizePolicy().horizontalPolicy()
        == QSizePolicy.Policy.Maximum
    )
    assert window.mode_buttons.maximumWidth() == 650
    assert window.mode_buttons.width() <= 650
    assert window.mode_buttons_layout.columnStretch(4) == 1
    assert all(
        window.mode_buttons_layout.columnStretch(column) == 0
        for column in range(4)
    )

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
    assert window.sidebar_shell.width() == 196
    assert not window.sidebar_brand_separator.isVisible()
    assert not window.sidebar_brand_subtitle.isVisible()
    assert window.sidebar_brand_title.isVisible()
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


def test_frameless_window_exposes_native_resize_and_caption_regions(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(1280, 760)
    window.show()
    _settle(qapp, window)

    origin = window.mapToGlobal(QPoint(0, 0))
    assert window._window_hit_test(origin + QPoint(2, 2)) == HTTOPLEFT
    assert (
        window._window_hit_test(
            origin + QPoint(window.width() - 2, window.height() - 2)
        )
        == HTBOTTOMRIGHT
    )

    title_point = window.window_title_bar.mapToGlobal(QPoint(220, 24))
    assert window._window_hit_test(title_point) == HTCAPTION

    brand_point = window.sidebar_brand_header.mapToGlobal(QPoint(100, 24))
    assert window._window_hit_test(brand_point) == HTCAPTION

    footer_point = window.status_bar.mapToGlobal(QPoint(100, 18))
    assert window._window_hit_test(footer_point) is None

    controls_point = window.window_controls.mapToGlobal(QPoint(4, 4))
    assert window._window_hit_test(controls_point) is None

    window._is_quitting = True
    window.close()
