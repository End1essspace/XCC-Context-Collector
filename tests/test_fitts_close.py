from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, QRect, Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from xcc.fitts_close import (
    EDGE_CLOSE_POLL_INTERVAL_MS,
    FittsCloseController,
    HoverSource,
)


class HarnessWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.visible_state = True
        self.active_state = True
        self.minimized_state = False
        self.maximized_state = False
        self.screen_geometry = QRect(0, 0, 900, 560)

    def isVisible(self) -> bool:
        return self.visible_state

    def isActiveWindow(self) -> bool:
        return self.active_state

    def isMinimized(self) -> bool:
        return self.minimized_state

    def screen(self):
        geometry = QRect(self.screen_geometry)

        class Screen:
            @staticmethod
            def geometry() -> QRect:
                return QRect(geometry)

        return Screen()


class HarnessCloseButton(QPushButton):
    def __init__(self, parent: QWidget) -> None:
        super().__init__("×", parent)
        self.force_hover = False
        self.setFixedSize(52, 48)

    def set_force_hover(self, enabled: bool) -> None:
        self.force_hover = bool(enabled)


@pytest.fixture(scope="module")
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture()
def harness(qapp: QApplication):
    window = HarnessWindow()
    window.setGeometry(0, 0, 900, 560)

    root_layout = QVBoxLayout(window)
    root_layout.setContentsMargins(0, 0, 0, 0)
    root_layout.setSpacing(0)

    title_bar = QWidget(window)
    title_bar.setFixedHeight(48)
    title_layout = QHBoxLayout(title_bar)
    title_layout.setContentsMargins(0, 0, 0, 0)
    title_layout.setSpacing(0)
    title_layout.addStretch(1)

    close_button = HarnessCloseButton(title_bar)
    title_layout.addWidget(close_button)
    root_layout.addWidget(title_bar)
    root_layout.addStretch(1)

    state = {
        "down": False,
        "cursor": QPoint(0, 0),
    }

    controller = FittsCloseController(
        window=window,
        title_bar=title_bar,
        close_button=close_button,
        is_effectively_maximized=lambda: window.maximized_state,
        button_state_reader=lambda: bool(state["down"]),
        cursor_position_reader=lambda: QPoint(state["cursor"]),
    )

    window.show()
    qapp.processEvents()

    yield window, title_bar, close_button, controller, state

    controller.timer.stop()
    QWidget.close(window)
    qapp.processEvents()


def test_close_target_is_exact_real_button_rectangle(harness) -> None:
    window, title_bar, close_button, controller, state = harness

    global_rect = controller.button_global_rect()
    title_rect = controller.button_rect_in_title_bar()

    assert global_rect.size() == close_button.size()
    assert title_rect.size() == close_button.size()
    assert controller.global_point_is_close(global_rect.topRight())
    assert not controller.global_point_is_close(
        global_rect.topRight() + QPoint(1, 0)
    )
    assert controller.title_point_is_close(title_rect.center())
    assert not controller.title_point_is_close(
        QPoint(title_rect.left() - 1, title_rect.center().y())
    )


def test_corner_fallback_requires_maximized_real_physical_corner(
    harness,
) -> None:
    window, title_bar, close_button, controller, state = harness

    button_rect = controller.button_global_rect()
    # The harness is a normal QWidget, so the offscreen platform may add a
    # synthetic frame offset. Build a fake screen whose physical top-right
    # point exactly matches the real button's global top-right point.
    window.screen_geometry = QRect(
        button_rect.right() - 899,
        button_rect.top(),
        900,
        560,
    )

    window.maximized_state = False
    assert not controller.corner_fallback_enabled()

    window.maximized_state = True
    assert controller.corner_fallback_enabled()

    window.screen_geometry.setWidth(
        window.screen_geometry.width() + 1
    )
    assert not controller.corner_fallback_enabled()


def test_press_elsewhere_drag_inside_release_does_not_close(
    harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window, title_bar, close_button, controller, state = harness
    calls: list[str] = []
    monkeypatch.setattr(
        controller,
        "corner_fallback_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        controller,
        "request_close",
        lambda: calls.append("close"),
    )

    rect = controller.button_global_rect()
    state["cursor"] = QPoint(rect.left() - 10, rect.center().y())
    state["down"] = False
    controller._last_left_down = False

    state["down"] = True
    controller._poll()
    assert not controller.corner_armed

    state["cursor"] = rect.center()
    controller._poll()
    assert not controller.corner_armed

    state["down"] = False
    controller._poll()

    assert calls == []


def test_press_and_release_inside_real_button_closes_once(
    harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window, title_bar, close_button, controller, state = harness
    calls: list[str] = []
    monkeypatch.setattr(
        controller,
        "corner_fallback_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        controller,
        "request_close",
        lambda: calls.append("close"),
    )

    state["cursor"] = controller.button_global_rect().center()
    state["down"] = False
    controller._last_left_down = False

    state["down"] = True
    controller._poll()
    assert controller.corner_armed

    controller._poll()
    assert controller.corner_armed

    state["down"] = False
    controller._poll()

    assert calls == ["close"]
    assert not controller.corner_armed



def test_press_inside_release_outside_cancels(
    harness,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window, title_bar, close_button, controller, state = harness
    calls: list[str] = []
    monkeypatch.setattr(
        controller,
        "corner_fallback_enabled",
        lambda: True,
    )
    monkeypatch.setattr(
        controller,
        "request_close",
        lambda: calls.append("close"),
    )

    rect = controller.button_global_rect()
    state["cursor"] = rect.center()
    state["down"] = False
    controller._last_left_down = False

    state["down"] = True
    controller._poll()
    assert controller.corner_armed

    state["cursor"] = QPoint(rect.left() - 10, rect.center().y())
    state["down"] = False
    controller._poll()

    assert calls == []
    assert not controller.corner_armed

def test_hover_sources_do_not_cancel_each_other(harness) -> None:
    window, title_bar, close_button, controller, state = harness

    controller._set_hover_source(HoverSource.TITLE_BAR, True)
    controller._set_hover_source(HoverSource.CORNER, True)
    controller._set_hover_source(HoverSource.TITLE_BAR, False)

    assert controller.hover_sources == HoverSource.CORNER
    assert close_button.force_hover is True

    controller._set_hover_source(HoverSource.CORNER, False)

    assert controller.hover_sources == HoverSource.NONE
    assert close_button.force_hover is False


def test_timer_runs_only_for_active_maximized_or_armed_window(
    harness,
) -> None:
    window, title_bar, close_button, controller, state = harness

    window.maximized_state = False
    controller._title_armed = False
    controller.sync_timer()
    assert not controller.timer.isActive()

    state["down"] = True
    window.maximized_state = True
    controller.sync_timer()
    assert controller.timer.isActive()
    assert controller.timer.interval() == EDGE_CLOSE_POLL_INTERVAL_MS
    assert controller.timer.timerType() == Qt.TimerType.PreciseTimer
    assert controller._last_left_down is True

    window.active_state = False
    controller.sync_timer()
    assert not controller.timer.isActive()
    assert not controller.corner_armed

    window.active_state = True
    window.visible_state = False
    controller.sync_timer()
    assert not controller.timer.isActive()

    window.visible_state = True
    window.minimized_state = True
    controller.sync_timer()
    assert not controller.timer.isActive()

    window.minimized_state = False
    window.maximized_state = False
    controller._title_armed = True
    controller.sync_timer()
    assert controller.timer.isActive()

    controller._title_armed = False
    controller.sync_timer()
    assert not controller.timer.isActive()


def test_event_filter_ignores_partial_teardown_state(harness) -> None:
    window, title_bar, close_button, controller, state = harness

    title_bar.removeEventFilter(controller)
    window.removeEventFilter(controller)

    saved_title_bar = controller.title_bar
    try:
        del controller.title_bar
        event = QEvent(QEvent.Type.Leave)
        assert controller.eventFilter(saved_title_bar, event) is False
    finally:
        controller.title_bar = saved_title_bar
        title_bar.installEventFilter(controller)
        window.installEventFilter(controller)
