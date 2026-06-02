from __future__ import annotations

from tkinter import Tk, messagebox

from .clipboard import copy_to_clipboard
from .collector import collect_files
from .formatter import format_collection
from .picker import select_files


def main() -> None:
    selected_files = select_files()

    if not selected_files:
        return

    files, errors = collect_files(selected_files)
    result = format_collection(files, errors)

    if not result.text.strip():
        show_error("XCC", "Nothing to copy.")
        return

    copy_to_clipboard(result.text)

    show_info(
        "XCC",
        (
            "Copied context to clipboard.\n\n"
            f"Files: {result.stats.files}\n"
            f"Lines: {result.stats.lines}\n"
            f"Characters: {result.stats.chars}\n"
            f"Errors: {len(result.errors)}"
        ),
    )


def show_info(title: str, message: str) -> None:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        messagebox.showinfo(title, message)
    finally:
        root.destroy()


def show_error(title: str, message: str) -> None:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        messagebox.showerror(title, message)
    finally:
        root.destroy()


if __name__ == "__main__":
    main()