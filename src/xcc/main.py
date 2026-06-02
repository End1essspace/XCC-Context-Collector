from __future__ import annotations

from pathlib import Path
from tkinter import Tk, messagebox

from .clipboard import copy_to_clipboard
from .collector import collect_files
from .formatter import format_collection
from .picker import select_files, select_folder
from .scanner import scan_project_files


def main() -> None:
    mode = ask_mode()

    if mode is None:
        return

    project_root: Path | None = None

    if mode == "files":
        selected_paths = select_files()
    else:
        project_root = select_folder()

        if project_root is None:
            return

        selected_paths = scan_project_files(project_root)

    if not selected_paths:
        show_error("XCC", "No files selected or found.")
        return

    files, errors = collect_files(selected_paths)
    result = format_collection(
        files,
        errors,
        project_root=project_root,
        compact=True,
        max_output_chars=120_000,
    )

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


def ask_mode() -> str | None:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        use_folder = messagebox.askyesnocancel(
            "XCC",
            "Collect project folder?\n\n"
            "Yes = select folder\n"
            "No = select files\n"
            "Cancel = exit",
        )
    finally:
        root.destroy()

    if use_folder is None:
        return None

    return "folder" if use_folder else "files"


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