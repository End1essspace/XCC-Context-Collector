from __future__ import annotations

import ctypes
import os
import sys
from ctypes import wintypes

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_V = 0x56


class NativeInputError(RuntimeError):
    """Raised when XCC cannot safely inject the requested Windows input."""


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class _INPUTUNION(ctypes.Union):
    # The full Win32 union is required even though XCC emits only keyboard
    # events: SendInput validates cbSize against the platform INPUT structure.
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", _INPUTUNION),
    ]


def _require_windows() -> None:
    if sys.platform != "win32":
        raise NativeInputError("Automated attachment paste is only supported on Windows.")


def _load_user32():
    _require_windows()
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.GetForegroundWindow.argtypes = []
    user32.GetForegroundWindow.restype = wintypes.HWND
    user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.SendInput.argtypes = [
        wintypes.UINT,
        ctypes.POINTER(INPUT),
        ctypes.c_int,
    ]
    user32.SendInput.restype = wintypes.UINT
    return user32


def get_foreground_window(*, _user32=None) -> int:
    """Return the current foreground HWND as an integer, or 0 if unavailable."""

    user32 = _user32 or _load_user32()
    hwnd = user32.GetForegroundWindow()
    return int(hwnd or 0)


def window_process_id(hwnd: int, *, _user32=None) -> int:
    """Return the owning process id for one HWND, or 0 if it cannot be resolved."""

    if not hwnd:
        return 0
    user32 = _user32 or _load_user32()
    process_id = wintypes.DWORD(0)
    user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(process_id))
    return int(process_id.value)


def window_belongs_to_current_process(hwnd: int, *, _user32=None) -> bool:
    return bool(hwnd) and window_process_id(hwnd, _user32=_user32) == os.getpid()


def is_foreground_window(hwnd: int, *, _user32=None) -> bool:
    return bool(hwnd) and get_foreground_window(_user32=_user32) == int(hwnd)


def _keyboard_input(vk: int, *, key_up: bool = False) -> INPUT:
    return INPUT(
        type=INPUT_KEYBOARD,
        ki=KEYBDINPUT(
            wVk=vk,
            wScan=0,
            dwFlags=KEYEVENTF_KEYUP if key_up else 0,
            time=0,
            dwExtraInfo=0,
        ),
    )


def send_ctrl_v_to_foreground(target_hwnd: int, *, _user32=None) -> None:
    """Send exactly one Ctrl+V chord, but only while ``target_hwnd`` is foreground.

    XCC never calls ``SetForegroundWindow`` here. The user chooses the destination
    by focusing it first; if focus changes, the operation fails closed instead of
    pasting into an unexpected application.
    """

    if not target_hwnd:
        raise NativeInputError("No target window is available for attachment paste.")

    user32 = _user32 or _load_user32()
    foreground = get_foreground_window(_user32=user32)
    if foreground != int(target_hwnd):
        raise NativeInputError("Target window lost focus; automated paste stopped safely.")

    inputs = (INPUT * 4)(
        _keyboard_input(VK_CONTROL),
        _keyboard_input(VK_V),
        _keyboard_input(VK_V, key_up=True),
        _keyboard_input(VK_CONTROL, key_up=True),
    )
    sent = int(user32.SendInput(len(inputs), inputs, ctypes.sizeof(INPUT)))
    if sent != len(inputs):
        error_code = ctypes.get_last_error()
        error_text = ctypes.FormatError(error_code).strip() if error_code else "Unknown error"
        raise NativeInputError(
            f"Could not send Ctrl+V to the target window: {error_text} ({error_code})."
        )
