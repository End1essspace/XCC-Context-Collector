from __future__ import annotations

from pathlib import Path
from tkinter import Tk, messagebox

from .clipboard import copy_to_clipboard
from .collector import collect_files
from .formatter import format_collection
from .picker import select_files, select_folder
from .scanner import scan_project_files
from .git_utils import get_changed_files, is_git_repository

def main() -> None:
    mode = ask_mode()

    if mode is None:
        return

    project_root: Path | None = None

    if mode == "files":
        selected_paths = select_files()

    elif mode == "folder":
        project_root = select_folder()

        if project_root is None:
            return

        selected_paths = scan_project_files(project_root)

    else:
        project_root = select_folder()

        if project_root is None:
            return

        if not is_git_repository(project_root):
            show_error("XCC", "Selected folder is not a Git repository.")
            return

        selected_paths = get_changed_files(project_root)

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

    estimated_tokens = sum(file.char_count for file in files) // 4
    
    output_chars = len(result.text)
    output_tokens = output_chars // 4

    was_truncated = result.was_truncated
        
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
            f"Source Characters: {result.stats.chars}\n"
            f"Output Characters: {output_chars}\n"
            f"Source Tokens: {estimated_tokens}\n"
            f"Output Tokens: {output_tokens}\n"
            f"Truncated: {'Yes' if was_truncated else 'No'}\n"
            f"Errors: {len(result.errors)}"
        ),
    )


def ask_mode() -> str | None:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        use_git = messagebox.askyesnocancel(
            "XCC",
            "Choose collection mode:\n\n"
            "Yes = Git changed files\n"
            "No = Full folder\n"
            "Cancel = Select files",
        )
    finally:
        root.destroy()

    if use_git is None:
        return "files"

    return "git" if use_git else "folder"


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