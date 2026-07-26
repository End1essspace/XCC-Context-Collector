from __future__ import annotations

from pathlib import Path
from time import perf_counter
from tkinter import Tk, messagebox

from .clipboard import copy_to_clipboard
from .collector import collect_files
from .formatter import format_collection, make_display_paths
from .git_utils import (
    get_collectable_changed_files,
    get_git_context,
    is_git_repository,
)
from .models import GitContext
from .picker import select_files, select_folder
from .scanner import scan_project_files
from .safety import (
    build_warning_confirmation_text,
    merge_warnings,
    scan_files_for_warnings,
    scan_git_context_for_warnings,
)


def main() -> None:
    started_at = perf_counter()
    mode = ask_mode()

    if mode is None:
        return

    project_root: Path | None = None
    git_context: GitContext | None = None

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

        try:
            git_context = get_git_context(project_root)
        except Exception as exc:
            show_error("XCC", str(exc))
            return

        selected_paths = get_collectable_changed_files(
            project_root,
            git_context.changes,
        )

    if not selected_paths:
        if mode == "git" and git_context is not None:
            if not git_context.has_changes:
                show_error("XCC", "No supported Git changes found.")
                return
            # Deleted-only Git context remains valid without file payloads.
        else:
            show_error("XCC", "No files selected or found.")
            return

    files, errors = collect_files(selected_paths)
    display_paths = make_display_paths(
        [file.path for file in files],
        project_root=project_root,
    )
    warnings = merge_warnings(
        scan_files_for_warnings(
            files,
            display_paths=display_paths,
        ),
        (
            scan_git_context_for_warnings(git_context)
            if git_context is not None
            else []
        ),
    )

    if warnings and not confirm_safety_warnings(warnings):
        return

    mode_name = {
        "files": "Selected Files",
        "folder": "Full Folder",
        "git": "Git Changed Files",
    }.get(mode, "Unknown")

    result = format_collection(
        files,
        errors,
        project_root=project_root,
        compact=True,
        mode_name=mode_name,
        max_output_chars=120_000,
        git_context=git_context,
        warnings=warnings,
        include_project_tree=(mode != "files"),
    )

    estimated_tokens = sum(file.char_count for file in files) // 4

    result.stats.duration_seconds = max(0.0, perf_counter() - started_at)
    output_chars = len(result.text)
    output_tokens = output_chars // 4

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
            f"Outcome: {result.outcome.value}\n"
            f"Duration: {result.stats.duration_seconds:.2f} s\n"
            f"Truncated: {'Yes' if result.was_truncated else 'No'}\n"
            f"Warnings: {result.stats.warning_count}\n"
            f"Errors: {result.stats.error_count}"
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


def confirm_safety_warnings(warnings) -> bool:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        return messagebox.askyesno(
            "XCC Safety Warning",
            build_warning_confirmation_text(warnings),
            default=messagebox.NO,
        )
    finally:
        root.destroy()


if __name__ == "__main__":
    main()
