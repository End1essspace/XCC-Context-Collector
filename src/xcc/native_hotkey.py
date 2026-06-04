from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from typing import Callable

from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication, QTimer

WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

# RegisterHotKey id for normal applications must be in 0x0000..0xBFFF.
# Keep it simple and valid.
HOTKEY_ID_RESTORE_WINDOW = 1

_KEY_NAME_TO_VK = {
    "backspace": 0x08,
    "tab": 0x09,
    "enter": 0x0D,
    "return": 0x0D,
    "escape": 0x1B,
    "esc": 0x1B,
    "space": 0x20,
    "pageup": 0x21,
    "pagedown": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "insert": 0x2D,
    "ins": 0x2D,
    "delete": 0x2E,
    "del": 0x2E,
}


class NativeHotkeyError(RuntimeError):
    """Raised when a native Windows hotkey cannot be registered."""


class NativeHotkeyManager(QAbstractNativeEventFilter):
    def __init__(
        self,
        on_activated: Callable[[], None],
        hotkey_id: int = HOTKEY_ID_RESTORE_WINDOW,
    ) -> None:
        super().__init__()

        self.hotkey_id = hotkey_id
        self._on_activated = on_activated
        self._registered = False
        self._event_filter_installed = False
        self._user32 = None

    @property
    def is_registered(self) -> bool:
        return self._registered

    def register(self, hotkey: str) -> None:
        if sys.platform != "win32":
            raise NativeHotkeyError("Native restore hotkey is only supported on Windows.")

        if self._registered:
            self.unregister()

        app = QCoreApplication.instance()
        if app is None:
            raise NativeHotkeyError("QCoreApplication is not running.")

        modifiers, vk = parse_hotkey(hotkey)

        user32 = ctypes.WinDLL("user32", use_last_error=True)

        user32.RegisterHotKey.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            wintypes.UINT,
            wintypes.UINT,
        ]
        user32.RegisterHotKey.restype = wintypes.BOOL

        user32.UnregisterHotKey.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
        ]
        user32.UnregisterHotKey.restype = wintypes.BOOL

        # IMPORTANT:
        # hwnd=None registers the hotkey on the current GUI thread message queue.
        # This is more reliable for a tray app than binding it to a specific Qt window HWND.
        if not user32.RegisterHotKey(None, self.hotkey_id, modifiers, vk):
            error_code = ctypes.get_last_error()
            error_text = ctypes.FormatError(error_code).strip() if error_code else "Unknown error"
            raise NativeHotkeyError(
                f"Could not register {hotkey}: {error_text} ({error_code})."
            )

        app.installNativeEventFilter(self)

        self._user32 = user32
        self._registered = True
        self._event_filter_installed = True

    def unregister(self) -> None:
        if self._registered and self._user32 is not None:
            self._user32.UnregisterHotKey(None, self.hotkey_id)

        app = QCoreApplication.instance()
        if self._event_filter_installed and app is not None:
            app.removeNativeEventFilter(self)

        self._user32 = None
        self._registered = False
        self._event_filter_installed = False

    def nativeEventFilter(self, event_type, message):
        if _event_type_to_text(event_type) not in {
            "windows_generic_MSG",
            "windows_dispatcher_MSG",
        }:
            return False, 0

        try:
            msg = wintypes.MSG.from_address(int(message))
        except Exception:
            return False, 0

        if msg.message == WM_HOTKEY and int(msg.wParam) == self.hotkey_id:
            # Do not restore directly inside the native event filter.
            # Schedule it back through Qt's event loop.
            QTimer.singleShot(0, self._on_activated)
            return True, 0

        return False, 0


def _event_type_to_text(event_type) -> str:
    if isinstance(event_type, str):
        return event_type

    if isinstance(event_type, bytes):
        return event_type.decode("ascii", errors="ignore")

    try:
        return bytes(event_type).decode("ascii", errors="ignore")
    except Exception:
        return str(event_type)


def parse_hotkey(hotkey: str) -> tuple[int, int]:
    parts = [part.strip().lower() for part in hotkey.split("+") if part.strip()]

    if len(parts) < 2:
        raise NativeHotkeyError(f"Invalid hotkey: {hotkey}")

    modifiers = MOD_NOREPEAT
    key: str | None = None

    for part in parts:
        if part in {"ctrl", "control"}:
            modifiers |= MOD_CONTROL
        elif part == "alt":
            modifiers |= MOD_ALT
        elif part == "shift":
            modifiers |= MOD_SHIFT
        elif part in {"win", "windows", "meta"}:
            modifiers |= MOD_WIN
        else:
            if key is not None:
                raise NativeHotkeyError(f"Invalid hotkey with multiple keys: {hotkey}")
            key = part

    if key is None:
        raise NativeHotkeyError(f"Invalid hotkey without a main key: {hotkey}")

    return modifiers, _virtual_key_from_name(key)


def _virtual_key_from_name(key: str) -> int:
    if len(key) == 1 and "a" <= key <= "z":
        return ord(key.upper())

    if len(key) == 1 and "0" <= key <= "9":
        return ord(key)

    if key.startswith("f") and key[1:].isdigit():
        function_key = int(key[1:])
        if 1 <= function_key <= 24:
            return 0x70 + function_key - 1

    if key in _KEY_NAME_TO_VK:
        return _KEY_NAME_TO_VK[key]

    raise NativeHotkeyError(f"Unsupported hotkey key: {key}")