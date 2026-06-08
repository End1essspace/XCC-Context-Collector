from __future__ import annotations

from pathlib import Path
from tkinter import Tk, filedialog
from .config import tkinter_context_filetypes


def select_files() -> list[Path]:
    root = _create_hidden_root()

    try:
        selected = filedialog.askopenfilenames(
            title="Select code files",
            filetypes=tkinter_context_filetypes(),
        )
    finally:
        root.destroy()

    return [Path(path) for path in selected]


def select_folder() -> Path | None:
    root = _create_hidden_root()

    try:
        selected = filedialog.askdirectory(
            title="Select project folder",
        )
    finally:
        root.destroy()

    if not selected:
        return None

    return Path(selected)


def _create_hidden_root() -> Tk:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return root