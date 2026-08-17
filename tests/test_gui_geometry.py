from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtWidgets import QApplication, QSizePolicy

from xcc.fitts_close import EDGE_CLOSE_POLL_INTERVAL_MS
from xcc.gui import (
    HTBOTTOMRIGHT,
    HTCAPTION,
    HTCLIENT,
    HTTOPLEFT,
    XccMainWindow,
)
from xcc.ui_responsive import (
    LARGE_USEFUL_PAGE_MAX_WIDTH,
    CollectLayoutMode,
)


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
    assert window._collect_page_width_spec is not None
    assert window._collect_page_width_spec.left_inset == 0
    assert window._collect_page_width_spec.right_inset == 0
    assert window.collect_page_layout.contentsMargins().left() == 28
    assert window.collect_page_layout.contentsMargins().right() == 28
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
    assert window.sidebar_brand_header.layout().contentsMargins().top() == 8
    assert window.sidebar_brand_header.layout().contentsMargins().bottom() == 8
    assert window.sidebar_brand_header.layout().spacing() == 9
    assert window.sidebar_brand_icon.size().width() == 32
    assert window.sidebar_brand_icon.pixmap().deviceIndependentSize().width() == 32
    assert window.sidebar_brand_label.text() == "XCC Context Collector"
    assert window.sidebar_brand_label.isVisible()
    assert window.sidebar_brand_label.alignment() & Qt.AlignmentFlag.AlignVCenter
    assert not hasattr(window, "sidebar_brand_title")
    assert not hasattr(window, "sidebar_brand_subtitle")
    assert not hasattr(window, "sidebar_brand_separator")
    assert not hasattr(window, "sidebar_brand_text_layout")
    assert (
        window.sidebar_brand_label.geometry().right()
        <= window.sidebar_brand_header.width()
        - window.sidebar_brand_header.layout().contentsMargins().right()
    )
    assert not hasattr(window, "window_brand_icon")
    assert not hasattr(window, "window_brand_title")
    assert not hasattr(window, "window_brand_subtitle")
    assert not hasattr(window, "status_version_label")
    assert window.window_controls_layout.spacing() == 0
    assert window.window_controls_layout.contentsMargins().right() == 0
    assert window.window_controls_layout.contentsMargins().top() == 0
    assert window.window_controls_layout.contentsMargins().bottom() == 0
    assert (
        window.window_close_button.geometry().right()
        == window.window_controls.contentsRect().right()
    )
    assert (
        window.window_controls.geometry().right()
        == window.window_title_bar.contentsRect().right()
    )
    assert window.window_frame.contentsRect() == window.window_frame.rect()
    assert window.window_frame_overlay.geometry() == window.window_frame.rect()
    assert window.window_frame_overlay.testAttribute(
        Qt.WidgetAttribute.WA_TransparentForMouseEvents
    )
    window_origin = window.mapToGlobal(QPoint(0, 0))
    close_top_right = window.window_close_button.mapToGlobal(
        QPoint(window.window_close_button.width() - 1, 0)
    )
    assert close_top_right == window_origin + QPoint(window.width() - 1, 0)
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
    assert all(
        button.cursor().shape() == Qt.CursorShape.ArrowCursor
        for button in (
            window.window_minimize_button,
            window.window_maximize_button,
            window.window_close_button,
        )
    )
    assert window.window_close_button.force_hover is False
    window.window_close_button.set_force_hover(True)
    assert window.window_close_button.force_hover is True
    assert window.window_close_button.is_effectively_hovered()
    window.window_close_button.set_force_hover(False)
    assert window.setup_card_layout.contentsMargins().top() == 22
    assert window.setup_grid.verticalSpacing() == 12
    assert window.stats_card_layout.contentsMargins().top() == 14
    assert window.stats_card_layout.spacing() == 10
    assert window.last_run_state_label.height() == 28
    assert all(metric.maximumHeight() <= 60 for metric in window.metric_capsules)

    window._is_quitting = True
    window.close()

def test_extreme_large_viewport_centers_bounded_collect_workspace(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.resize(2560, 1000)
    window.show()
    _settle(qapp, window)

    assert window._collect_layout_mode is CollectLayoutMode.LARGE
    assert window._collect_layout_spec is not None
    assert window._collect_page_width_spec is not None

    viewport_width = window.collect_page_viewport.width()
    page_width = window._collect_page_width_spec
    base_margin = window._collect_layout_spec.page_margin
    margins = window.collect_page_layout.contentsMargins()

    assert viewport_width > LARGE_USEFUL_PAGE_MAX_WIDTH
    assert page_width.available_width == viewport_width
    assert page_width.useful_width == LARGE_USEFUL_PAGE_MAX_WIDTH
    assert page_width.left_inset > 0
    assert abs(page_width.left_inset - page_width.right_inset) <= 1
    assert (
        page_width.left_inset
        + page_width.useful_width
        + page_width.right_inset
        == viewport_width
    )
    assert margins.left() == base_margin + page_width.left_inset
    assert margins.right() == base_margin + page_width.right_inset

    expected_surface_width = (
        LARGE_USEFUL_PAGE_MAX_WIDTH - (2 * base_margin)
    )
    assert window.setup_card.width() == expected_surface_width
    assert window.stats_card.width() == expected_surface_width
    assert window.collect_button.width() == expected_surface_width
    assert window._collect_layout_spec.metric_columns == 4

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
    assert window.sidebar_brand_label.text() == "XCC"
    assert window.sidebar_brand_label.isVisible()
    assert not hasattr(window, "sidebar_brand_title")
    assert not hasattr(window, "sidebar_brand_subtitle")
    assert not hasattr(window, "sidebar_brand_separator")
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
    assert window._window_hit_test(controls_point) == HTCLIENT

    top_right = origin + QPoint(window.width() - 1, 0)
    assert window._window_hit_test(top_right) == HTCLIENT

    close_global_rect = window._fitts_close.button_global_rect()
    assert close_global_rect.contains(top_right)
    assert not close_global_rect.contains(
        close_global_rect.topRight() + QPoint(1, 0)
    )

    close_title_rect = window._fitts_close.button_rect_in_title_bar()
    assert window._fitts_close.title_point_is_close(
        close_title_rect.center()
    )
    assert not window._fitts_close.title_point_is_close(
        QPoint(
            close_title_rect.left() - 1,
            close_title_rect.center().y(),
        )
    )

    window._is_custom_maximized = True
    window._sync_title_bar_state()
    assert window._window_hit_test(origin + QPoint(2, 2)) != HTTOPLEFT
    assert window._window_hit_test(top_right) == HTCLIENT
    window._is_custom_maximized = False
    window._sync_title_bar_state()

    assert (
        window._fitts_close.timer.interval()
        == EDGE_CLOSE_POLL_INTERVAL_MS
    )
    assert (
        window._fitts_close.timer.timerType()
        == Qt.TimerType.PreciseTimer
    )

    window._is_quitting = True
    window.close()


def test_close_request_is_queued_and_idempotent(
    qapp: QApplication,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = XccMainWindow()
    window.resize(1280, 760)
    window.show()
    _settle(qapp, window)

    controller = window._fitts_close
    calls: list[str] = []
    monkeypatch.setattr(
        controller,
        "_perform_close",
        lambda: calls.append("close"),
    )

    window.window_close_button.set_force_hover(True)
    controller.request_close()
    controller.request_close()

    assert controller.close_requested is True
    assert window.window_close_button.force_hover is False

    qapp.processEvents()
    assert calls == ["close"]

    controller._close_requested = False
    window._is_quitting = True
    window.close()

def test_collect_event_filter_does_not_dereference_scroll_area_wrapper(
    qapp: QApplication,
) -> None:
    window = XccMainWindow()
    window.show()
    _settle(qapp, window)

    viewport = window.collect_page_viewport
    original_scroll = window.collect_page_scroll

    class DeletedScrollAreaProbe:
        def viewport(self):
            raise RuntimeError("simulated deleted QScrollArea C++ object")

    window.collect_page_scroll = DeletedScrollAreaProbe()
    try:
        # A non-resize teardown-style event must not ask the QScrollArea for
        # its viewport. The cached viewport identity is sufficient.
        handled = window.eventFilter(
            viewport,
            QEvent(QEvent.Type.Hide),
        )
        assert handled is False
    finally:
        window.collect_page_scroll = original_scroll
        window._is_quitting = True
        window.close()
