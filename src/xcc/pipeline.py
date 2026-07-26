from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from .cancellation import CollectionCancelled
from .collector import collect_files
from .formatter import format_collection, format_project_tree, make_display_paths
from .git_utils import get_collectable_changed_files, get_git_context, is_git_repository
from .models import CollectionResult, GitContext
from .safety import (
    merge_warnings,
    scan_files_for_warnings,
    scan_git_context_for_warnings,
    scan_project_filename_warnings,
)
from .scanner import scan_project_files

ProgressCallback = Callable[[str, int, int], None]
CancelCheck = Callable[[], bool]


@dataclass(frozen=True, slots=True)
class CollectionRequest:
    mode: str
    mode_name: str
    selected_paths: tuple[Path, ...]
    project_root: Path | None
    compact: bool
    max_output_chars: int

    @property
    def source_label(self) -> str:
        if self.mode == "files":
            count = len(self.selected_paths)
            return f"{count} selected file{'s' if count != 1 else ''}"

        if self.project_root is not None:
            return str(self.project_root)

        return "Unknown source"


@dataclass(slots=True)
class CollectionJobResult:
    result: CollectionResult
    mode_name: str
    source: str
    duration_seconds: float


def execute_collection(
    request: CollectionRequest,
    *,
    progress_callback: ProgressCallback | None = None,
    cancel_check: CancelCheck | None = None,
) -> CollectionJobResult:
    """Run one collection job without touching the GUI or clipboard."""
    started_at = perf_counter()
    _emit(progress_callback, "Preparing", 0, 0)
    _raise_if_cancelled(cancel_check)

    mode = request.mode
    project_root = request.project_root
    git_context: GitContext | None = None

    if mode == "tree":
        if project_root is None:
            raise ValueError("Select a source folder first.")

        _emit(progress_callback, "Scanning", 0, 0)
        warnings = scan_project_filename_warnings(
            project_root,
            progress_callback=lambda current, total: _emit(
                progress_callback,
                "Scanning",
                current,
                total,
            ),
            cancel_check=cancel_check,
        )
        _raise_if_cancelled(cancel_check)

        result = format_project_tree(
            project_root,
            compact=request.compact,
            mode_name=request.mode_name,
            max_output_chars=request.max_output_chars,
            warnings=warnings,
            tree_progress_callback=lambda current, total: _emit(
                progress_callback,
                "Scanning",
                current,
                total,
            ),
            cancel_check=cancel_check,
        )
        _raise_if_cancelled(cancel_check)
        _emit(progress_callback, "Formatting", 0, 0)
        _emit(
            progress_callback,
            "Applying budget",
            result.stats.output_chars,
            request.max_output_chars,
        )

        return _complete_job(
            request=request,
            result=result,
            started_at=started_at,
        )

    if mode == "files":
        selected_paths = list(request.selected_paths)

    elif mode == "folder":
        if project_root is None:
            raise ValueError("Select a source folder first.")

        _emit(progress_callback, "Scanning", 0, 0)
        selected_paths = scan_project_files(
            project_root,
            progress_callback=lambda current, total: _emit(
                progress_callback,
                "Scanning",
                current,
                total,
            ),
            cancel_check=cancel_check,
        )

    elif mode == "git":
        if project_root is None:
            raise ValueError("Select a source folder first.")
        if not is_git_repository(project_root):
            raise ValueError("Selected folder is not a Git repository.")

        _emit(progress_callback, "Inspecting Git changes", 0, 0)
        git_context = get_git_context(project_root)
        _raise_if_cancelled(cancel_check)
        selected_paths = get_collectable_changed_files(
            project_root,
            git_context.changes,
        )

    else:
        raise ValueError(f"Unsupported collection mode: {mode}")

    _raise_if_cancelled(cancel_check)

    if not selected_paths:
        if mode == "git" and git_context is not None:
            if not git_context.has_changes:
                raise ValueError("No supported Git changes found.")
            # Deleted-only Git changes remain valid without file payloads.
        else:
            raise ValueError("No files selected or found.")

    _emit(progress_callback, "Reading files", 0, len(selected_paths))
    files, errors = collect_files(
        selected_paths,
        progress_callback=lambda current, total: _emit(
            progress_callback,
            "Reading files",
            current,
            total,
        ),
        cancel_check=cancel_check,
    )
    _raise_if_cancelled(cancel_check)

    display_paths = make_display_paths(
        [file.path for file in files],
        project_root=project_root,
    )

    _emit(progress_callback, "Inspecting context", 0, len(files))
    warnings = merge_warnings(
        scan_files_for_warnings(
            files,
            display_paths=display_paths,
            progress_callback=lambda current, total: _emit(
                progress_callback,
                "Inspecting context",
                current,
                total,
            ),
            cancel_check=cancel_check,
        ),
        (
            scan_git_context_for_warnings(
                git_context,
                cancel_check=cancel_check,
            )
            if git_context is not None
            else []
        ),
    )
    _raise_if_cancelled(cancel_check)

    _emit(progress_callback, "Formatting", 0, 0)
    result = format_collection(
        files,
        errors,
        project_root=project_root,
        compact=request.compact,
        mode_name=request.mode_name,
        max_output_chars=request.max_output_chars,
        git_context=git_context,
        warnings=warnings,
        include_project_tree=(mode != "files"),
    )
    _raise_if_cancelled(cancel_check)
    _emit(
        progress_callback,
        "Applying budget",
        result.stats.output_chars,
        request.max_output_chars,
    )

    return _complete_job(
        request=request,
        result=result,
        started_at=started_at,
    )


def _emit(
    callback: ProgressCallback | None,
    phase: str,
    current: int,
    total: int,
) -> None:
    if callback is not None:
        callback(phase, current, total)


def _raise_if_cancelled(cancel_check: CancelCheck | None) -> None:
    if cancel_check is not None and cancel_check():
        raise CollectionCancelled("Collection cancelled.")


def _complete_job(
    *,
    request: CollectionRequest,
    result: CollectionResult,
    started_at: float,
) -> CollectionJobResult:
    duration_seconds = max(0.0, perf_counter() - started_at)
    result.stats.duration_seconds = duration_seconds

    return CollectionJobResult(
        result=result,
        mode_name=request.mode_name,
        source=request.source_label,
        duration_seconds=duration_seconds,
    )
