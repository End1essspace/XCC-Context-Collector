from __future__ import annotations

import pytest

from xcc.hotkeys import HotkeyValidationError, normalize_hotkey, parse_hotkey_spec


def test_hotkey_normalization_is_stable() -> None:
    assert normalize_hotkey("Alt + Control + x") == "ctrl+alt+x"
    assert normalize_hotkey("Shift+Meta+F12") == "shift+win+f12"


def test_hotkey_requires_modifier_and_one_main_key() -> None:
    with pytest.raises(HotkeyValidationError):
        normalize_hotkey("x")
    with pytest.raises(HotkeyValidationError):
        normalize_hotkey("ctrl+alt")
    with pytest.raises(HotkeyValidationError):
        normalize_hotkey("ctrl+x+y")


def test_hotkey_aliases_are_canonicalized() -> None:
    assert normalize_hotkey("control+return") == "ctrl+enter"
    assert normalize_hotkey("windows+esc") == "win+escape"


def test_hotkey_spec_preserves_canonical_modifier_order() -> None:
    spec = parse_hotkey_spec("win+alt+ctrl+shift+9")
    assert spec.modifiers == ("ctrl", "alt", "shift", "win")
    assert spec.key == "9"
