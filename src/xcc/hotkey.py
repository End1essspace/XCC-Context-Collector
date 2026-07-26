"""Unsupported legacy standalone hotkey workflow.

The supported desktop application uses the native Windows hotkey manager in
``xcc.native_hotkey``. This module is retained only for development and
backward compatibility and requires the optional ``legacy`` dependency group.
"""

from __future__ import annotations

import threading
from importlib import import_module
from types import ModuleType

from .config import DEFAULT_HOTKEY
from .main import main

_is_running = False
_lock = threading.Lock()


def run_hotkey_listener(hotkey: str = DEFAULT_HOTKEY) -> None:
    keyboard_backend = _load_keyboard_backend()
    print(
        "WARNING: legacy standalone hotkey mode is unsupported. "
        "Use the PySide6 GUI for release workflows."
    )
    keyboard_backend.add_hotkey(hotkey, _run_main_safely)

    print("XCC legacy hotkey listener is running.")
    print(f"Hotkey: {hotkey}")
    print("Press Ctrl+C in this console to exit.")

    try:
        keyboard_backend.wait()
    except KeyboardInterrupt:
        print("\nXCC legacy hotkey listener stopped.")


def _load_keyboard_backend() -> ModuleType:
    try:
        return import_module("keyboard")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Legacy hotkey mode requires the optional dependency group. "
            'Install it with: python -m pip install -e ".[legacy]"'
        ) from exc


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
