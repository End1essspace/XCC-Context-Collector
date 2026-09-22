from __future__ import annotations

import ctypes
import sys
from ctypes import wintypes
from typing import Callable

from PySide6.QtCore import QAbstractNativeEventFilter, QCoreApplication, QTimer

from .hotkeys import HotkeyValidationError, normalize_hotkey, parse_hotkey_spec

WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

# RegisterHotKey ids for normal applications must be in 0x0000..0xBFFF.
HOTKEY_ID_RESTORE_WINDOW = 1
HOTKEY_ID_COLLECT_COPY = 2
HOTKEY_ID_ATTACHMENT_HANDOFF = 3
HOTKEY_ID_TRANSACTION_PROBE = 0xBFFE

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
    """Own one Win32 RegisterHotKey binding.

    ``replace`` is transactional: the new combination is probed while the old
    binding is still alive. If final registration still fails, the previous
    binding is restored before the error is surfaced.
    """

    def __init__(
        self,
        on_activated: Callable[[], None],
        hotkey_id: int = HOTKEY_ID_RESTORE_WINDOW,
    ) -> None:
        super().__init__()
        if not (0x0000 <= int(hotkey_id) <= 0xBFFF):
            raise ValueError("hotkey_id must be in the Win32 application range")
        if hotkey_id == HOTKEY_ID_TRANSACTION_PROBE:
            raise ValueError("hotkey_id is reserved for transactional probing")

        self.hotkey_id = int(hotkey_id)
        self._on_activated = on_activated
        self._registered = False
        self._registered_hotkey: str | None = None
        self._event_filter_installed = False
        self._user32 = None

    @property
    def registered(self) -> bool:
        return self._registered

    @property
    def registered_hotkey(self) -> str | None:
        return self._registered_hotkey

    def register(self, hotkey: str) -> None:
        canonical = normalize_hotkey(hotkey)
        if self._registered:
            self.unregister()

        app = self._require_application()
        user32 = self._load_user32()
        modifiers, vk = parse_hotkey(canonical)
        self._register_native(user32, self.hotkey_id, modifiers, vk, canonical)

        if not self._event_filter_installed:
            app.installNativeEventFilter(self)
            self._event_filter_installed = True

        self._user32 = user32
        self._registered = True
        self._registered_hotkey = canonical

    def replace(self, hotkey: str) -> None:
        """Replace the current binding without losing a known-good shortcut."""

        canonical = normalize_hotkey(hotkey)
        if not self._registered:
            self.register(canonical)
            return
        if canonical == self._registered_hotkey:
            return

        old_hotkey = self._registered_hotkey
        if old_hotkey is None:
            self.register(canonical)
            return

        user32 = self._user32 or self._load_user32()
        new_modifiers, new_vk = parse_hotkey(canonical)
        old_modifiers, old_vk = parse_hotkey(old_hotkey)

        # Conflict detection happens before the live binding is released.
        self._register_native(
            user32,
            HOTKEY_ID_TRANSACTION_PROBE,
            new_modifiers,
            new_vk,
            canonical,
        )
        self._unregister_native(user32, HOTKEY_ID_TRANSACTION_PROBE)

        self._unregister_native(user32, self.hotkey_id)
        try:
            self._register_native(
                user32,
                self.hotkey_id,
                new_modifiers,
                new_vk,
                canonical,
            )
        except NativeHotkeyError as exc:
            try:
                self._register_native(
                    user32,
                    self.hotkey_id,
                    old_modifiers,
                    old_vk,
                    old_hotkey,
                )
            except NativeHotkeyError as rollback_exc:
                self._registered = False
                self._registered_hotkey = None
                raise NativeHotkeyError(
                    f"{exc} Previous hotkey rollback also failed: {rollback_exc}"
                ) from rollback_exc
            self._registered = True
            self._registered_hotkey = old_hotkey
            raise

        self._registered = True
        self._registered_hotkey = canonical

    def unregister(self) -> None:
        if self._registered and self._user32 is not None:
            self._unregister_native(self._user32, self.hotkey_id)

        app = QCoreApplication.instance()
        if self._event_filter_installed and app is not None:
            app.removeNativeEventFilter(self)

        self._user32 = None
        self._registered = False
        self._registered_hotkey = None
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
            QTimer.singleShot(0, self._on_activated)
            return True, 0

        return False, 0

    @staticmethod
    def _require_application() -> QCoreApplication:
        if sys.platform != "win32":
            raise NativeHotkeyError("Native global hotkeys are only supported on Windows.")
        app = QCoreApplication.instance()
        if app is None:
            raise NativeHotkeyError("QCoreApplication is not running.")
        return app

    @staticmethod
    def _load_user32():
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
        return user32

    @staticmethod
    def _register_native(user32, hotkey_id: int, modifiers: int, vk: int, label: str) -> None:
        if not user32.RegisterHotKey(None, int(hotkey_id), modifiers, vk):
            error_code = ctypes.get_last_error()
            error_text = ctypes.FormatError(error_code).strip() if error_code else "Unknown error"
            raise NativeHotkeyError(
                f"Could not register {label}: {error_text} ({error_code})."
            )

    @staticmethod
    def _unregister_native(user32, hotkey_id: int) -> None:
        user32.UnregisterHotKey(None, int(hotkey_id))


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
    try:
        spec = parse_hotkey_spec(hotkey)
    except HotkeyValidationError as exc:
        raise NativeHotkeyError(str(exc)) from exc

    modifiers = MOD_NOREPEAT
    for modifier in spec.modifiers:
        if modifier == "ctrl":
            modifiers |= MOD_CONTROL
        elif modifier == "alt":
            modifiers |= MOD_ALT
        elif modifier == "shift":
            modifiers |= MOD_SHIFT
        elif modifier == "win":
            modifiers |= MOD_WIN

    return modifiers, _virtual_key_from_name(spec.key)


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
