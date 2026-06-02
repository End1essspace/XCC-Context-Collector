from __future__ import annotations

from pathlib import Path
from tkinter import Tk, filedialog


def select_files() -> list[Path]:
    root = _create_hidden_root()

    try:
        selected = filedialog.askopenfilenames(
            title="Select code files",
            filetypes=[
                ("Code and config files", "*.py *.pyw *.md *.txt *.json *.yaml *.yml *.toml *.ini *.cfg"),
                ("Python files", "*.py *.pyw"),
                ("All files", "*.*"),
            ],
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