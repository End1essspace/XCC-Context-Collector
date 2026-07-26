from __future__ import annotations

import pytest

from xcc import hotkey as legacy_hotkey
from xcc.config import DEFAULT_HOTKEY


def test_hotkey_uses_config_default() -> None:
    assert legacy_hotkey.DEFAULT_HOTKEY == DEFAULT_HOTKEY
    assert DEFAULT_HOTKEY == "ctrl+alt+x"


def test_legacy_keyboard_dependency_is_loaded_lazily(monkeypatch) -> None:
    def missing_backend(name: str):
        raise ModuleNotFoundError(name=name)

    monkeypatch.setattr(legacy_hotkey, "import_module", missing_backend)

    with pytest.raises(RuntimeError, match=r"\.\[legacy\]"):
        legacy_hotkey._load_keyboard_backend()
