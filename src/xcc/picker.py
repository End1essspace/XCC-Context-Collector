from __future__ import annotations

from pathlib import Path
from tkinter import Tk, filedialog


def select_files() -> list[Path]:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        selected = filedialog.askopenfilenames(
            title="Select code files",
            filetypes=[
                ("Python files", "*.py"),
                ("All files", "*.*"),
            ],
        )
    finally:
        root.destroy()

    return [Path(path) for path in selected]