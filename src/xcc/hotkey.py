from __future__ import annotations

import threading

import keyboard

from .main import main


DEFAULT_HOTKEY = "ctrl+alt+x"

_is_running = False
_lock = threading.Lock()


def run_hotkey_listener(hotkey: str = DEFAULT_HOTKEY) -> None:
    keyboard.add_hotkey(hotkey, _run_main_safely)

    print("XCC is running.")
    print(f"Hotkey: {hotkey}")
    print("Press Ctrl+C in this console to exit.")

    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("\nXCC stopped.")


def _run_main_safely() -> None:
    global _is_running

    with _lock:
        if _is_running:
            return

        _is_running = True

    try:
        main()
    finally:
        with _lock:
            _is_running = False