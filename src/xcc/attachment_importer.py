from __future__ import annotations

import os
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .path_list_parser import contains_relative_paths, is_absolute_path_text, parse_path_list
from .selected_files_importer import infer_project_root


class AttachmentIssueKind(str, Enum):
    MISSING = "missing"
    DIRECTORY = "directory"
    INACCESSIBLE = "inaccessible"
    INVALID = "invalid"
    OUTSIDE_ROOT = "outside_root"
    ROOT_REQUIRED = "root_required"
    ROOT_ERROR = "root_error"


@dataclass(frozen=True, slots=True)
class AttachmentIssue:
    kind: AttachmentIssueKind
    path: str
    detail: str = ""


@dataclass(frozen=True, slots=True)
class AttachmentFile:
    path: Path
    size_bytes: int


@dataclass(frozen=True, slots=True)
class AttachmentImportResult:
    parsed: tuple[str, ...] = ()
    added: tuple[AttachmentFile, ...] = ()
    duplicates: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()
    directories: tuple[str, ...] = ()
    inaccessible: tuple[str, ...] = ()
    invalid: tuple[str, ...] = ()
    outside_root: tuple[str, ...] = ()
    root_required: tuple[str, ...] = ()
    external: tuple[Path, ...] = ()
    root_error: str | None = None

    @property
    def added_count(self) -> int:
        return len(self.added)

    @property
    def added_paths(self) -> tuple[Path, ...]:
        return tuple(item.path for item in self.added)

    @property
    def added_bytes(self) -> int:
        return sum(item.size_bytes for item in self.added)

    @property
    def duplicate_count(self) -> int:
        return len(self.duplicates)

    @property
    def issue_count(self) -> int:
        return sum(
            len(group)
            for group in (
                self.missing,
                self.directories,
                self.inaccessible,
                self.invalid,
                self.outside_root,
                self.root_required,
            )
        ) + (1 if self.root_error else 0)

    @property
    def needs_project_root_selection(self) -> bool:
        return bool(self.root_required or self.root_error)

    @property
    def can_apply(self) -> bool:
        return self.added_count > 0 and not self.root_required and self.root_error is None

    @property
    def has_reportable_details(self) -> bool:
        return self.issue_count > 0

    @property
    def issues(self) -> tuple[AttachmentIssue, ...]:
        items: list[AttachmentIssue] = []
        for kind, values in (
            (AttachmentIssueKind.MISSING, self.missing),
            (AttachmentIssueKind.DIRECTORY, self.directories),
            (AttachmentIssueKind.INACCESSIBLE, self.inaccessible),
            (AttachmentIssueKind.INVALID, self.invalid),
            (AttachmentIssueKind.OUTSIDE_ROOT, self.outside_root),
            (AttachmentIssueKind.ROOT_REQUIRED, self.root_required),
        ):
            items.extend(AttachmentIssue(kind, value) for value in values)
        if self.root_error:
            items.append(
                AttachmentIssue(
                    AttachmentIssueKind.ROOT_ERROR,
                    "",
                    self.root_error,
                )
            )
        return tuple(items)


@dataclass(frozen=True, slots=True)
class AttachmentSelection:
    files: tuple[AttachmentFile, ...] = ()
    project_root: Path | None = None

    @property
    def paths(self) -> tuple[Path, ...]:
        return tuple(item.path for item in self.files)

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_bytes(self) -> int:
        return sum(item.size_bytes for item in self.files)

    @property
    def is_empty(self) -> bool:
        return not self.files

    @property
    def has_mixed_locations(self) -> bool:
        if not self.files:
            return False
        if self.project_root is None:
            return True
        return any(not _is_relative_to(item.path, self.project_root) for item in self.files)

    @property
    def scope_label(self) -> str:
        if not self.files:
            return "No files selected"
        if self.has_mixed_locations:
            return "Mixed locations"
        return str(self.project_root) if self.project_root is not None else "Mixed locations"


def import_attachments(
    text: str,
    *,
    project_root: str | Path | None = None,
    existing_paths: Sequence[str | Path] = (),
) -> AttachmentImportResult:
    parsed = parse_path_list(text)
    return _import_path_values(
        parsed,
        project_root=project_root,
        existing_paths=existing_paths,
        parsed=tuple(parsed),
    )


def import_attachment_files(
    paths: Sequence[str | Path],
    *,
    project_root: str | Path | None = None,
    existing_paths: Sequence[str | Path] = (),
) -> AttachmentImportResult:
    values = [str(path) for path in paths]
    return _import_path_values(
        values,
        project_root=project_root,
        existing_paths=existing_paths,
        parsed=tuple(values),
        direct_selection=True,
    )


def build_attachment_selection(
    paths: Sequence[str | Path],
    *,
    project_root: str | Path | None = None,
) -> AttachmentSelection:
    files: list[AttachmentFile] = []
    normalized_paths: list[Path] = []
    for raw in paths:
        path = Path(raw)
        try:
            resolved = path.expanduser().resolve(strict=True)
            stat = resolved.stat()
        except (OSError, RuntimeError):
            continue
        if not resolved.is_file():
            continue
        files.append(AttachmentFile(resolved, max(0, int(stat.st_size))))
        normalized_paths.append(resolved)

    root = _validated_root(project_root)
    if root is None and normalized_paths:
        root = infer_project_root(normalized_paths)

    return AttachmentSelection(tuple(files), root)


def revalidate_attachment_files(
    paths: Sequence[str | Path],
) -> tuple[AttachmentFile, ...]:
    """Validate one transfer snapshot without reading file contents."""

    result: list[AttachmentFile] = []
    for raw in paths:
        path = Path(raw)
        try:
            resolved = path.expanduser().resolve(strict=True)
            stat = resolved.stat()
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Attachment no longer exists: {path}") from exc
        except PermissionError as exc:
            raise PermissionError(f"Attachment is inaccessible: {path}") from exc
        except (OSError, RuntimeError) as exc:
            raise OSError(f"Attachment cannot be accessed: {path}: {exc}") from exc
        if not resolved.is_file():
            raise ValueError(f"Attachment is not a regular file: {path}")
        result.append(AttachmentFile(resolved, max(0, int(stat.st_size))))
    return tuple(result)


def _import_path_values(
    values: Sequence[str],
    *,
    project_root: str | Path | None,
    existing_paths: Sequence[str | Path],
    parsed: tuple[str, ...],
    direct_selection: bool = False,
) -> AttachmentImportResult:
    if not values:
        return AttachmentImportResult(parsed=parsed)

    root = Path(project_root).expanduser() if project_root is not None else None
    resolved_root: Path | None = None
    root_error: str | None = None
    relative_paths_present = False if direct_selection else contains_relative_paths(list(values))

    if root is not None:
        try:
            resolved_root = root.resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            if relative_paths_present:
                root_error = f"Project root is unavailable: {exc}"
        else:
            if not resolved_root.is_dir():
                if relative_paths_present:
                    root_error = f"Project root is not a folder: {root}"
                resolved_root = None

    seen_keys = {_dedupe_key(Path(path)) for path in existing_paths}
    added: list[AttachmentFile] = []
    duplicates: list[str] = []
    missing: list[str] = []
    directories: list[str] = []
    inaccessible: list[str] = []
    invalid: list[str] = []
    outside_root: list[str] = []
    root_required: list[str] = []
    external: list[Path] = []

    for raw_path in values:
        raw_text = str(raw_path).strip()
        if not raw_text:
            invalid.append(str(raw_path))
            continue

        absolute = direct_selection or is_absolute_path_text(raw_text)
        if absolute:
            candidate = _path_from_text(raw_text)
            if candidate is None:
                invalid.append(raw_text)
                continue
        else:
            if root_error is not None:
                invalid.append(raw_text)
                continue
            if resolved_root is None:
                root_required.append(raw_text)
                continue
            relative = _path_from_text(raw_text)
            if relative is None:
                invalid.append(raw_text)
                continue
            try:
                candidate = (resolved_root / relative).resolve(strict=False)
            except (OSError, RuntimeError):
                invalid.append(raw_text)
                continue
            if not _is_relative_to(candidate, resolved_root):
                outside_root.append(raw_text)
                continue

        try:
            resolved_candidate = candidate.expanduser().resolve(strict=False)
        except (OSError, RuntimeError):
            invalid.append(raw_text)
            continue

        key = _dedupe_key(resolved_candidate)
        if key in seen_keys:
            duplicates.append(raw_text)
            continue

        try:
            exists = resolved_candidate.exists()
        except OSError:
            inaccessible.append(raw_text)
            continue
        if not exists:
            missing.append(raw_text)
            continue

        try:
            if resolved_candidate.is_dir():
                directories.append(raw_text)
                continue
            if not resolved_candidate.is_file():
                invalid.append(raw_text)
                continue
            stat = resolved_candidate.stat()
        except PermissionError:
            inaccessible.append(raw_text)
            continue
        except OSError:
            inaccessible.append(raw_text)
            continue

        seen_keys.add(key)
        added.append(AttachmentFile(resolved_candidate, max(0, int(stat.st_size))))
        if resolved_root is not None and not _is_relative_to(resolved_candidate, resolved_root):
            external.append(resolved_candidate)

    return AttachmentImportResult(
        parsed=parsed,
        added=tuple(added),
        duplicates=tuple(duplicates),
        missing=tuple(missing),
        directories=tuple(directories),
        inaccessible=tuple(inaccessible),
        invalid=tuple(invalid),
        outside_root=tuple(outside_root),
        root_required=tuple(root_required),
        external=tuple(external),
        root_error=root_error,
    )


def _validated_root(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    try:
        root = Path(value).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    return root if root.is_dir() else None


def _path_from_text(value: str) -> Path | None:
    text = value.strip()
    if not text or "\x00" in text:
        return None
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
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except (OSError, RuntimeError, ValueError):
        return False
