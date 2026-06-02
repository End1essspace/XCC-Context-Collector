from __future__ import annotations

import keyboard

from .main import main


DEFAULT_HOTKEY = "ctrl+alt+x"


def run_hotkey_listener(hotkey: str = DEFAULT_HOTKEY) -> None:
    keyboard.add_hotkey(hotkey, main)

    print(f"XCC is running.")
    print(f"Hotkey: {hotkey}")
    print("Press Ctrl+C in this console to exit.")

    keyboard.wait()