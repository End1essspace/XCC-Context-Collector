from __future__ import annotations

import os
import subprocess
from collections.abc import Iterable, Sequence
from pathlib import Path

from .config import ALLOWED_EXTENSIONS, EXCLUDED_DIRS, is_allowed_context_file
from .ignore import ProjectIgnoreMatcher
from .models import GitChange, GitContext


class GitCommandError(RuntimeError):
    """Raised when a required Git command cannot be executed successfully."""


def is_git_repository(path: str | Path) -> bool:
    repo_path = Path(path)

    if not repo_path.exists() or not repo_path.is_dir():
        return False

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError:
        return False

    return result.returncode == 0 and result.stdout.strip() == "true"


def get_git_context(
    path: str | Path,
    *,
    allowed_extensions: set[str] | None = None,
    excluded_dirs: set[str] | None = None,
    respect_xccignore: bool = True,
) -> GitContext:
    repo_path = _validate_repository_path(path)
    changes = get_git_changes(
        repo_path,
        allowed_extensions=allowed_extensions,
        excluded_dirs=excluded_dirs,
        respect_xccignore=respect_xccignore,
    )

    return GitContext(
        changes=changes,
        staged_diff=_get_diff(repo_path, changes, staged=True),
        unstaged_diff=_get_diff(repo_path, changes, staged=False),
    )


def get_git_changes(
    path: str | Path,
    *,
    allowed_extensions: set[str] | None = None,
    excluded_dirs: set[str] | None = None,
    respect_xccignore: bool = True,
) -> list[GitChange]:
    repo_path = _validate_repository_path(path)
    extensions = allowed_extensions or ALLOWED_EXTENSIONS
    excluded = excluded_dirs or EXCLUDED_DIRS
    ignore_matcher = ProjectIgnoreMatcher.from_project_root(
        repo_path,
        respect_xccignore=respect_xccignore,
        respect_gitignore=False,
    )

    status_data = _run_git_bytes(
        repo_path,
        ["status", "--porcelain=v1", "-z", "--untracked-files=all"],
    )
    changes = parse_git_status_z(status_data)

    # Porcelain status normally reports a staged copy as A. Refine staged
    # additions with diff copy/rename detection so copied files retain their
    # original path and C status in the typed model.
    staged_name_status = _run_git_bytes(
        repo_path,
        [
            "diff",
            "--cached",
            "--name-status",
            "-z",
            "-M",
            "-C",
            "--find-copies-harder",
            "--",
            ".",
        ],
    )
    changes = _apply_staged_rename_copy_details(
        changes,
        _parse_name_status_z(staged_name_status),
    )

    return [
        change
        for change in changes
        if _is_supported_change(
            change,
            allowed_extensions=extensions,
            excluded_dirs=excluded,
            ignore_matcher=ignore_matcher,
        )
    ]


def get_collectable_changed_files(
    path: str | Path,
    changes: Sequence[GitChange],
    *,
    allowed_extensions: set[str] | None = None,
    excluded_dirs: set[str] | None = None,
    respect_xccignore: bool = True,
) -> list[Path]:
    repo_path = _validate_repository_path(path)
    extensions = allowed_extensions or ALLOWED_EXTENSIONS
    excluded = excluded_dirs or EXCLUDED_DIRS
    ignore_matcher = ProjectIgnoreMatcher.from_project_root(
        repo_path,
        respect_xccignore=respect_xccignore,
        respect_gitignore=False,
    )

    files: list[Path] = []
    seen: set[Path] = set()

    for change in changes:
        relative_path = Path(change.path)

        if _is_excluded_relative_path(relative_path, excluded):
            continue

        if ignore_matcher.is_ignored(relative_path, is_dir=False):
            continue

        if not is_allowed_context_file(
            relative_path,
            allowed_extensions=extensions,
        ):
            continue

        full_path = repo_path / relative_path

        # Deleted changes remain in GitContext and diffs, but there is no
        # current file payload to collect from disk.
        if not full_path.exists() or not full_path.is_file():
            continue

        try:
            dedupe_key = full_path.resolve()
        except OSError:
            dedupe_key = full_path.absolute()

        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        files.append(full_path)

    return files


def parse_git_status_z(data: bytes) -> list[GitChange]:
    """Parse `git status --porcelain=v1 -z` output.

    In null-delimited mode Git emits rename/copy records as destination first,
    followed by the original path in a second NUL-delimited field.
    """
    fields = data.split(b"\0")
    changes: list[GitChange] = []
    index = 0

    while index < len(fields):
        raw_entry = fields[index]
        index += 1

        if not raw_entry:
            continue

        if len(raw_entry) < 3 or raw_entry[2:3] != b" ":
            raise GitCommandError("Git returned malformed porcelain status output.")

        index_status = chr(raw_entry[0])
        worktree_status = chr(raw_entry[1])
        path = _decode_git_path(raw_entry[3:])
        original_path: str | None = None

        if index_status in {"R", "C"} or worktree_status in {"R", "C"}:
            if index >= len(fields) or not fields[index]:
                raise GitCommandError(
                    "Git returned an incomplete rename/copy status record."
                )

            original_path = _decode_git_path(fields[index])
            index += 1

        changes.append(
            GitChange(
                index_status=index_status,
                worktree_status=worktree_status,
                path=_normalize_git_path(path),
                original_path=(
                    _normalize_git_path(original_path)
                    if original_path is not None
                    else None
                ),
            )
        )

    return changes


def _get_diff(
    repo_path: Path,
    changes: Sequence[GitChange],
    *,
    staged: bool,
) -> str:
    if staged:
        relevant = [change for change in changes if change.has_staged_change]
    else:
        relevant = [change for change in changes if change.has_unstaged_change]

    if not relevant:
        return ""

    pathspecs = _diff_pathspecs(relevant)
    args = ["-c", "core.quotepath=false", "diff"]

    if staged:
        args.append("--cached")

    args.extend(["--no-ext-diff", "--no-textconv", "--"])
    args.extend(f":(literal){path}" for path in pathspecs)

    return _decode_git_text(_run_git_bytes(repo_path, args))


def _diff_pathspecs(changes: Iterable[GitChange]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for change in changes:
        for path in (change.original_path, change.path):
            if path is None or path in seen:
                continue

            seen.add(path)
            result.append(path)

    return result


def _parse_name_status_z(data: bytes) -> dict[str, tuple[str, str]]:
    fields = data.split(b"\0")
    result: dict[str, tuple[str, str]] = {}
    index = 0

    while index < len(fields):
        raw_status = fields[index]
        index += 1

        if not raw_status:
            continue

        status = raw_status.decode("ascii", errors="replace")
        kind = status[:1]

        if kind in {"R", "C"}:
            if index + 1 >= len(fields):
                raise GitCommandError("Git returned malformed name-status output.")

            original_path = _normalize_git_path(_decode_git_path(fields[index]))
            destination_path = _normalize_git_path(_decode_git_path(fields[index + 1]))
            index += 2
            result[destination_path] = (kind, original_path)
            continue

        if index >= len(fields):
            raise GitCommandError("Git returned malformed name-status output.")

        index += 1

    return result


def _apply_staged_rename_copy_details(
    changes: Sequence[GitChange],
    details: dict[str, tuple[str, str]],
) -> list[GitChange]:
    refined: list[GitChange] = []

    for change in changes:
        detail = details.get(change.path)

        if detail is None:
            refined.append(change)
            continue

        kind, original_path = detail
        refined.append(
            GitChange(
                index_status=kind,
                worktree_status=change.worktree_status,
                path=change.path,
                original_path=original_path,
            )
        )

    return refined


def _is_supported_change(
    change: GitChange,
    *,
    allowed_extensions: set[str],
    excluded_dirs: set[str],
    ignore_matcher: ProjectIgnoreMatcher,
) -> bool:
    current_path = Path(change.path)

    if _is_excluded_relative_path(current_path, excluded_dirs):
        return False

    if ignore_matcher.is_ignored(current_path, is_dir=False):
        return False

    candidates = [change.path]
    if change.original_path is not None:
        candidates.append(change.original_path)

    for candidate in candidates:
        relative_path = Path(candidate)

        if _is_excluded_relative_path(relative_path, excluded_dirs):
            continue

        if is_allowed_context_file(
            relative_path,
            allowed_extensions=allowed_extensions,
        ):
            return True

    return False


def _is_excluded_relative_path(path: Path, excluded_dirs: Iterable[str]) -> bool:
    excluded = set(excluded_dirs)
    return any(part in excluded for part in path.parts[:-1])


def _validate_repository_path(path: str | Path) -> Path:
    repo_path = Path(path)

    if not repo_path.exists():
        raise FileNotFoundError(f"Git repository folder not found: {repo_path}")

    if not repo_path.is_dir():
        raise NotADirectoryError(f"Not a folder: {repo_path}")

    if not is_git_repository(repo_path):
        raise GitCommandError(f"Selected folder is not a Git repository: {repo_path}")

    return repo_path


def _run_git_bytes(repo_path: Path, args: list[str]) -> bytes:
    command = ["git", *args]

    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise GitCommandError("Git executable was not found.") from exc
    except OSError as exc:
        raise GitCommandError(f"Could not execute Git: {exc}") from exc

    if result.returncode != 0:
        stderr = _decode_git_text(result.stderr).strip()
        command_text = " ".join(command)
        detail = stderr or f"exit code {result.returncode}"
        raise GitCommandError(f"Git command failed: {command_text} ({detail})")

    return result.stdout


def _decode_git_path(value: bytes) -> str:
    return os.fsdecode(value)


def _decode_git_text(value: bytes) -> str:
    for encoding in ("utf-8", "cp1251"):
        try:
            return value.decode(encoding)
        except UnicodeDecodeError:
            continue

    return value.decode("utf-8", errors="replace")


def _normalize_git_path(path: str) -> str:
    return path.replace("\\", "/")
