from __future__ import annotations

import pytest

from src.xcc.native_hotkey import (
    MOD_ALT,
    MOD_CONTROL,
    MOD_NOREPEAT,
    NativeHotkeyError,
    parse_hotkey,
    HOTKEY_ID_RESTORE_WINDOW,
)

def test_restore_hotkey_id_is_valid_win32_application_id() -> None:
    assert 0x0000 <= HOTKEY_ID_RESTORE_WINDOW <= 0xBFFF

def test_parse_default_restore_hotkey() -> None:
    modifiers, vk = parse_hotkey("ctrl+alt+x")

    assert modifiers == MOD_NOREPEAT | MOD_CONTROL | MOD_ALT
    assert vk == ord("X")


def test_parse_function_key_hotkey() -> None:
    modifiers, vk = parse_hotkey("ctrl+alt+f12")

    assert modifiers == MOD_NOREPEAT | MOD_CONTROL | MOD_ALT
    assert vk == 0x7B


def test_rejects_hotkey_without_main_key() -> None:
    with pytest.raises(NativeHotkeyError):
        parse_hotkey("ctrl+alt")


def test_rejects_hotkey_with_multiple_main_keys() -> None:
    with pytest.raises(NativeHotkeyError):
        parse_hotkey("ctrl+alt+x+y")
