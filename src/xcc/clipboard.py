from __future__ import annotations

import pyperclip


def copy_to_clipboard(text: str) -> None:
    if not text:
        raise ValueError("Cannot copy empty text to clipboard")

    pyperclip.copy(text)