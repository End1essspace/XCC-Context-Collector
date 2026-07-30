from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from .config import is_allowed_context_file
from .path_list_parser import is_absolute_path_text, parse_path_list

_PROJECT_MARKERS = (
    ".git",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "CMakeLists.txt",
    ".sln",
)


@dataclass(frozen=True, slots=True)
class SelectedFilesImportResult:
    parsed: tuple[str, ...] = ()
    added: tuple[Path, ...] = ()
    duplicates: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    directories: tuple[str, ...] = ()
    unsupported: tuple[str, ...] = ()
    invalid: tuple[str, ...] = ()
    outside_root: tuple[str, ...] = ()
    root_required: tuple[str, ...] = ()
    external: tuple[Path, ...] = ()
    root_error: str | None = None

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def issue_count(self) -> int:
        return sum(
            len(group)
            for group in (
                self.missing,
                self.directories,
                self.unsupported,
                self.invalid,
                self.outside_root,
                self.root_required,
            )
        ) + (1 if self.root_error else 0)

    @property
    def has_reportable_details(self) -> bool:
        return bool(self.duplicates or self.issue_count)


def import_selected_files(
    text: str,
    *,
    project_root: str | Path | None = None,
    existing_paths: Sequence[str | Path] = (),
) -> SelectedFilesImportResult:
    parsed = parse_path_list(text)
    if not parsed:
        return SelectedFilesImportResult()

    root = Path(project_root).expanduser() if project_root is not None else None
    resolved_root: Path | None = None
    root_error: str | None = None

    if root is not None:
        try:
            resolved_root = root.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            root_error = f"Project root is unavailable: {exc}"
        else:
            if not resolved_root.is_dir():
                root_error = f"Project root is not a folder: {root}"
                resolved_root = None

    existing_keys = {
        _dedupe_key(Path(path))
        for path in existing_paths
    }
    seen_keys = set(existing_keys)

    added: list[Path] = []
    duplicates: list[str] = []
    missing: list[str] = []
    directories: list[str] = []
    unsupported: list[str] = []
    invalid: list[str] = []
    outside_root: list[str] = []
    root_required: list[str] = []
    external: list[Path] = []

    for raw_path in parsed:
        absolute = is_absolute_path_text(raw_path)

        if absolute:
            candidate = _path_from_text(raw_path)
            if candidate is None:
                invalid.append(raw_path)
                continue
        else:
            if root_error is not None:
                invalid.append(raw_path)
                continue
            if resolved_root is None:
                root_required.append(raw_path)
                continue

            relative = _path_from_text(raw_path)
            if relative is None:
                invalid.append(raw_path)
                continue

            try:
                candidate = (resolved_root / relative).resolve(strict=False)
            except (OSError, RuntimeError):
                invalid.append(raw_path)
                continue

            if not _is_relative_to(candidate, resolved_root):
                outside_root.append(raw_path)
                continue

        try:
            resolved_candidate = candidate.expanduser().resolve(strict=False)
        except (OSError, RuntimeError):
            invalid.append(raw_path)
            continue

        key = _dedupe_key(resolved_candidate)
        if key in seen_keys:
            duplicates.append(raw_path)
            continue

        if not resolved_candidate.exists():
            missing.append(raw_path)
            continue

        if resolved_candidate.is_dir():
            directories.append(raw_path)
            continue

        if not resolved_candidate.is_file():
            invalid.append(raw_path)
            continue

        if not is_allowed_context_file(resolved_candidate):
            unsupported.append(raw_path)
            continue

        seen_keys.add(key)
        added.append(resolved_candidate)

        if resolved_root is not None and not _is_relative_to(
            resolved_candidate,
            resolved_root,
        ):
            external.append(resolved_candidate)

    return SelectedFilesImportResult(
        parsed=tuple(parsed),
        added=tuple(added),
        duplicates=tuple(duplicates),
        missing=tuple(missing),
        directories=tuple(directories),
        unsupported=tuple(unsupported),
        invalid=tuple(invalid),
        outside_root=tuple(outside_root),
        root_required=tuple(root_required),
        external=tuple(external),
        root_error=root_error,
    )


def infer_project_root(paths: Sequence[str | Path]) -> Path | None:
    resolved_paths: list[Path] = []

    for raw_path in paths:
        path = Path(raw_path)
        try:
            resolved = path.resolve(strict=False)
        except (OSError, RuntimeError):
            continue

        resolved_paths.append(resolved)

    if not resolved_paths:
        return None

    marker_roots = [_find_marker_root(path.parent) for path in resolved_paths]
    concrete_marker_roots = [root for root in marker_roots if root is not None]

    if len(concrete_marker_roots) == len(resolved_paths):
        first = concrete_marker_roots[0]
        if all(_dedupe_key(root) == _dedupe_key(first) for root in concrete_marker_roots):
            return first

    try:
        common = Path(os.path.commonpath([str(path.parent) for path in resolved_paths]))
    except (ValueError, OSError):
        return None

    if common.parent == common:
        return None

    return common


def _find_marker_root(start: Path) -> Path | None:
    current = start

    while True:
        for marker in _PROJECT_MARKERS:
            if marker == ".sln":
                try:
                    if any(current.glob("*.sln")):
                        return current
                except OSError:
                    pass
            elif (current / marker).exists():
                return current

        if current.parent == current:
            return None

        current = current.parent


def _path_from_text(value: str) -> Path | None:
    text = value.strip()
    if not text or "\x00" in text:
        return None

    # pathlib follows the host platform. XCC runs on Windows, while this
    # separator normalization keeps the pure importer testable elsewhere.
    if os.sep == "/":
        text = text.replace("\\", "/")
    else:
        text = text.replace("/", "\\")

    try:
        return Path(text)
    except (OSError, ValueError):
        return None


def _dedupe_key(path: Path) -> str:
    try:
        value = str(path.resolve(strict=False))
    except (OSError, RuntimeError):
        value = str(path.absolute())

    return os.path.normcase(value).casefold()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False
