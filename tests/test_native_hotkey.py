from __future__ import annotations

import pytest

from xcc.native_hotkey import (
    MOD_ALT,
    MOD_CONTROL,
    MOD_NOREPEAT,
    NativeHotkeyError,
    parse_hotkey,
    HOTKEY_ID_RESTORE_WINDOW,
    HOTKEY_ID_COLLECT_COPY,
    HOTKEY_ID_ATTACHMENT_HANDOFF,
    normalize_hotkey,
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


def test_collect_hotkey_id_is_distinct_and_valid() -> None:
    assert 0x0000 <= HOTKEY_ID_COLLECT_COPY <= 0xBFFF
    assert HOTKEY_ID_COLLECT_COPY != HOTKEY_ID_RESTORE_WINDOW


def test_normalize_hotkey_uses_stable_modifier_order_and_aliases() -> None:
    assert normalize_hotkey("Alt + Control + x") == "ctrl+alt+x"
    assert normalize_hotkey("Shift+Meta+F12") == "shift+win+f12"


def test_rejects_duplicate_modifier() -> None:
    with pytest.raises(NativeHotkeyError):
        parse_hotkey("ctrl+control+x")


def test_attachment_handoff_hotkey_id_is_distinct_and_valid() -> None:
    assert 0x0000 <= HOTKEY_ID_ATTACHMENT_HANDOFF <= 0xBFFF
    assert HOTKEY_ID_ATTACHMENT_HANDOFF not in {
        HOTKEY_ID_RESTORE_WINDOW,
        HOTKEY_ID_COLLECT_COPY,
    }
