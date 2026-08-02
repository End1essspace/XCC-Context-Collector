from __future__ import annotations

import ctypes
import sys
from collections.abc import Callable
from enum import IntFlag, auto

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QTimer, Qt
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QApplication, QWidget

VK_LBUTTON = 0x01
EDGE_CLOSE_POLL_INTERVAL_MS = 20


def left_button_is_down() -> bool:
    """Return the current physical left-mouse-button state."""

    if sys.platform == "win32":
        return bool(
            ctypes.windll.user32.GetAsyncKeyState(VK_LBUTTON)
            & 0x8000
        )

    return bool(
        QApplication.mouseButtons()
        & Qt.MouseButton.LeftButton
    )


class HoverSource(IntFlag):
    NONE = 0
    TITLE_BAR = auto()
    CORNER = auto()


class FittsCloseController(QObject):
    """Coordinate safe close-button fallbacks for a frameless window.

    The controller never creates an invisible close target outside the real
    close-button rectangle. Exact-corner polling is enabled only while the
    active window is effectively maximized and the real button contains the
    current screen's physical top-right point.
    """

    def __init__(
        self,
        *,
        window: QWidget,
        title_bar: QWidget,
        close_button: QWidget,
        is_effectively_maximized: Callable[[], bool],
        button_state_reader: Callable[[], bool] | None = None,
        cursor_position_reader: Callable[[], QPoint] | None = None,
    ) -> None:
        super().__init__(window)

        self.window = window
        self.title_bar = title_bar
        self.close_button = close_button
        self._is_effectively_maximized = is_effectively_maximized
        self._button_state_reader = button_state_reader or left_button_is_down
        self._cursor_position_reader = cursor_position_reader or QCursor.pos

        self._title_armed = False
        self._corner_armed = False
        self._last_left_down = self._button_state_reader()
        self._hover_sources = HoverSource.NONE
        self._close_requested = False

        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.setInterval(EDGE_CLOSE_POLL_INTERVAL_MS)
        self.timer.timeout.connect(self._poll)

        self.title_bar.setMouseTracking(True)
        self.title_bar.installEventFilter(self)
        self.window.installEventFilter(self)

        self.close_button.clicked.connect(self.request_close)
        self.sync_timer()

    @property
    def close_requested(self) -> bool:
        return self._close_requested

    @property
    def title_armed(self) -> bool:
        return self._title_armed

    @property
    def corner_armed(self) -> bool:
        return self._corner_armed

    @property
    def hover_sources(self) -> HoverSource:
        return self._hover_sources

    def button_rect_in_title_bar(self) -> QRect:
        top_left = self.close_button.mapTo(
            self.title_bar,
            QPoint(0, 0),
        )
        return QRect(top_left, self.close_button.size())

    def button_global_rect(self) -> QRect:
        top_left = self.close_button.mapToGlobal(QPoint(0, 0))
        return QRect(top_left, self.close_button.size())

    def title_point_is_close(self, point: QPoint) -> bool:
        return self.button_rect_in_title_bar().contains(point)

    def global_point_is_close(self, point: QPoint) -> bool:
        return self.button_global_rect().contains(point)

    def corner_fallback_enabled(self) -> bool:
        if (
            not self.window.isVisible()
            or not self.window.isActiveWindow()
            or self.window.isMinimized()
            or not self._is_effectively_maximized()
        ):
            return False

        screen = self.window.screen()
        if screen is None:
            return False

        physical_corner = screen.geometry().topRight()
        return self.button_global_rect().contains(physical_corner)

    def _set_hover_source(
        self,
        source: HoverSource,
        enabled: bool,
    ) -> None:
        if enabled:
            self._hover_sources |= source
        else:
            self._hover_sources &= ~source

        self.close_button.set_force_hover(
            self._hover_sources != HoverSource.NONE
        )

    def _timer_should_run(self) -> bool:
        return (
            self.window.isVisible()
            and self.window.isActiveWindow()
            and not self.window.isMinimized()
            and (
                self._is_effectively_maximized()
                or self._title_armed
            )
        )

    def sync_timer(self) -> None:
        if self._timer_should_run():
            if not self.timer.isActive():
                # Synchronize before polling so an already-held button is not
                # mistaken for a fresh press after activation or maximize.
                self._last_left_down = self._button_state_reader()
                self.timer.start()
            return

        self.timer.stop()
        self._corner_armed = False
        self._set_hover_source(HoverSource.CORNER, False)

    def reset_interaction(self) -> None:
        self._title_armed = False
        self._corner_armed = False
        self._hover_sources = HoverSource.NONE
        self.close_button.set_force_hover(False)
        self._last_left_down = self._button_state_reader()

    def request_close(self) -> None:
        if self._close_requested:
            return

        self._close_requested = True
        self.reset_interaction()

        # Complete the current input callback before entering closeEvent().
        QTimer.singleShot(0, self._perform_close)

    def _perform_close(self) -> None:
        if not self._close_requested:
            return

        closed = bool(self.window.close())

        # closeEvent() may ignore the request for close-to-tray, active work,
        # confirmation, or another product-specific reason.
        if not closed:
            self._close_requested = False
            self.sync_timer()

    def _poll(self) -> None:
        left_down = self._button_state_reader()
        pressed_now = left_down and not self._last_left_down
        released_now = not left_down and self._last_left_down
        self._last_left_down = left_down

        corner_enabled = self.corner_fallback_enabled()
        cursor_in_button = self.button_global_rect().contains(
            self._cursor_position_reader()
        )

        self._set_hover_source(
            HoverSource.CORNER,
            corner_enabled and cursor_in_button,
        )

        if not corner_enabled:
            self._corner_armed = False

        # Arm only on a physical up -> down transition that starts inside the
        # real close-button rectangle.
        if pressed_now and corner_enabled and cursor_in_button:
            self._corner_armed = True

        if released_now:
            armed = self._corner_armed or self._title_armed
            self._corner_armed = False
            self._title_armed = False
            self._set_hover_source(HoverSource.TITLE_BAR, False)

            if armed and cursor_in_button:
                self.request_close()
            else:
                self.sync_timer()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        # Qt can still deliver teardown-time events while the Python wrapper is
        # being partially finalized. In that state instance attributes may
        # already be gone even though the native event-filter callback is still
        # in flight. Treat those events as unhandled instead of raising from a
        # Python override during widget destruction.
        title_bar = getattr(self, "title_bar", None)
        window = getattr(self, "window", None)
        if title_bar is None or window is None:
            return False

        try:
            event_type = event.type()
        except RuntimeError:
            return False

        if watched is title_bar:
            if event_type == QEvent.Type.MouseMove:
                point = event.position().toPoint()
                self._set_hover_source(
                    HoverSource.TITLE_BAR,
                    self.title_point_is_close(point),
                )
                return False

            if event_type == QEvent.Type.Leave:
                self._set_hover_source(HoverSource.TITLE_BAR, False)
                return False

            if event_type == QEvent.Type.MouseButtonDblClick:
                if (
                    event.button() == Qt.MouseButton.LeftButton
                    and self.title_point_is_close(
                        event.position().toPoint()
                    )
                ):
                    return True

            if event_type == QEvent.Type.MouseButtonPress:
                if (
                    event.button() == Qt.MouseButton.LeftButton
                    and self.title_point_is_close(
                        event.position().toPoint()
                    )
                ):
                    self._title_armed = True
                    self._set_hover_source(HoverSource.TITLE_BAR, True)
                    self.sync_timer()
                    return True

            if (
                event_type == QEvent.Type.MouseButtonRelease
                and self._title_armed
                and event.button() == Qt.MouseButton.LeftButton
            ):
                inside = self.title_point_is_close(
                    event.position().toPoint()
                )
                self._title_armed = False
                self._set_hover_source(HoverSource.TITLE_BAR, False)

                if inside:
                    self.request_close()
                else:
                    self.sync_timer()

                return True

        if watched is window:
            if event_type == QEvent.Type.Show:
                self._close_requested = False

            if event_type in {
                QEvent.Type.Show,
                QEvent.Type.Hide,
                QEvent.Type.ActivationChange,
                QEvent.Type.WindowStateChange,
            }:
                QTimer.singleShot(0, self._handle_window_state_change)

        # QObject's default eventFilter implementation returns False. Returning
        # it directly avoids calling back into a partially destroyed C++ base.
        return False

    def _handle_window_state_change(self) -> None:
        window = getattr(self, "window", None)
        if window is None:
            return

        try:
            inactive = (
                not window.isVisible()
                or not window.isActiveWindow()
                or window.isMinimized()
            )
        except RuntimeError:
            # The queued callback may outlive the native QWidget during test or
            # application shutdown. There is no interaction state left to sync.
            timer = getattr(self, "timer", None)
            if timer is not None:
                try:
                    timer.stop()
                except RuntimeError:
                    pass
            return

        if inactive:
            self.reset_interaction()

        self.sync_timer()
