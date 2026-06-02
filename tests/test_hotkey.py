from src.xcc.config import DEFAULT_HOTKEY
from src.xcc.hotkey import DEFAULT_HOTKEY as HOTKEY_MODULE_DEFAULT


def test_hotkey_uses_config_default() -> None:
    assert HOTKEY_MODULE_DEFAULT == DEFAULT_HOTKEY
    assert DEFAULT_HOTKEY == "ctrl+alt+x"