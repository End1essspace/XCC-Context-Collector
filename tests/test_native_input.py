from __future__ import annotations

import ctypes
from ctypes import wintypes

import pytest

from xcc.native_input import (
    KEYEVENTF_KEYUP,
    VK_CONTROL,
    VK_V,
    NativeInputError,
    get_foreground_window,
    send_ctrl_v_to_foreground,
    window_process_id,
)


class FakeUser32:
    def __init__(self, *, foreground: int = 100, process_id: int = 1234) -> None:
        self.foreground = foreground
        self.process_id = process_id
        self.sent_inputs: list[tuple[int, int]] = []

    def GetForegroundWindow(self):
        return self.foreground

    def GetWindowThreadProcessId(self, hwnd, process_id_ptr):
        ptr = ctypes.cast(process_id_ptr, ctypes.POINTER(wintypes.DWORD))
        ptr.contents.value = self.process_id
        return 1

    def SendInput(self, count, inputs, size):
        self.sent_inputs = [
            (int(inputs[index].ki.wVk), int(inputs[index].ki.dwFlags))
            for index in range(int(count))
        ]
        return count


def test_foreground_and_process_lookup_use_supplied_user32() -> None:
    user32 = FakeUser32(foreground=321, process_id=9876)

    assert get_foreground_window(_user32=user32) == 321
    assert window_process_id(321, _user32=user32) == 9876


def test_ctrl_v_is_sent_as_one_complete_keyboard_chord() -> None:
    user32 = FakeUser32(foreground=777)

    send_ctrl_v_to_foreground(777, _user32=user32)

    assert user32.sent_inputs == [
        (VK_CONTROL, 0),
        (VK_V, 0),
        (VK_V, KEYEVENTF_KEYUP),
        (VK_CONTROL, KEYEVENTF_KEYUP),
    ]


def test_ctrl_v_fails_closed_when_target_is_no_longer_foreground() -> None:
    user32 = FakeUser32(foreground=888)

    with pytest.raises(NativeInputError, match="lost focus"):
        send_ctrl_v_to_foreground(777, _user32=user32)

    assert user32.sent_inputs == []
