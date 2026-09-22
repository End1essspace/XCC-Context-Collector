from __future__ import annotations

import os
import time
import zipfile
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path, PurePosixPath
from uuid import uuid4

from .attachment_importer import AttachmentFile, revalidate_attachment_files
from .cancellation import AttachmentBundleCancelled

BUNDLE_DIRECTORY_NAME = "attachment-bundles"
BUNDLE_PREFIX = "XCC-Attachments-"
BUNDLE_RETENTION_DAYS = 7
COPY_CHUNK_SIZE = 1024 * 1024

ProgressCallback = Callable[[str, int, int, int, int], None]
CancelCheck = Callable[[], bool]


@dataclass(frozen=True, slots=True)
class BundleSourceSnapshot:
    path: Path
    size_bytes: int
    mtime_ns: int


@dataclass(frozen=True, slots=True)
class AttachmentBundleEntry:
    source: BundleSourceSnapshot
    archive_path: str


@dataclass(frozen=True, slots=True)
class AttachmentBundleResult:
    bundle_path: Path
    file_count: int
    total_bytes: int
    archive_bytes: int


@dataclass(frozen=True, slots=True)
class BundleCleanupResult:
    removed: tuple[Path, ...] = ()
    failures: tuple[str, ...] = ()

    @property
    def removed_count(self) -> int:
        return len(self.removed)

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)


def attachment_bundle_directory(*, home: str | Path | None = None) -> Path:
    base = Path(home).expanduser() if home is not None else Path.home()
    return base / ".xcc" / BUNDLE_DIRECTORY_NAME


def unique_bundle_path(
    directory: str | Path,
    *,
    now: datetime | None = None,
) -> Path:
    bundle_dir = Path(directory)
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    candidate = bundle_dir / f"{BUNDLE_PREFIX}{stamp}.zip"
    if not candidate.exists():
        return candidate

    for index in range(2, 10_000):
        candidate = bundle_dir / f"{BUNDLE_PREFIX}{stamp}-{index}.zip"
        if not candidate.exists():
            return candidate

    raise RuntimeError("Could not allocate a collision-safe attachment bundle name")


def cleanup_stale_bundles(
    *,
    directory: str | Path | None = None,
    retention_days: int = BUNDLE_RETENTION_DAYS,
    active_paths: Iterable[str | Path] = (),
    now: float | None = None,
) -> BundleCleanupResult:
    if retention_days < 1:
        raise ValueError("retention_days must be at least 1")

    bundle_dir = Path(directory) if directory is not None else attachment_bundle_directory()
    if not bundle_dir.exists():
        return BundleCleanupResult()

    active_keys = {_path_key(Path(path)) for path in active_paths}
    cutoff = (time.time() if now is None else float(now)) - (retention_days * 86400)
    removed: list[Path] = []
    failures: list[str] = []

    try:
        candidates = tuple(bundle_dir.iterdir())
    except OSError as exc:
        return BundleCleanupResult(failures=(f"Bundle cleanup could not list {bundle_dir}: {exc}",))

    for path in candidates:
        if not path.is_file():
            continue
        if not path.name.startswith(BUNDLE_PREFIX) or path.suffix.lower() != ".zip":
            continue
        if _path_key(path) in active_keys:
            continue

        try:
            if path.stat().st_mtime >= cutoff:
                continue
            path.unlink()
            removed.append(path)
        except OSError as exc:
            failures.append(f"Could not remove stale bundle {path.name}: {exc}")

    return BundleCleanupResult(tuple(removed), tuple(failures))


def build_bundle_entries(
    paths: Sequence[str | Path],
    *,
    project_root: str | Path | None = None,
) -> tuple[AttachmentBundleEntry, ...]:
    validated = revalidate_attachment_files(paths)
    snapshots = tuple(_snapshot(item) for item in validated)
    root = _usable_project_root(project_root, snapshots)

    if root is not None:
        used: set[str] = set()
        entries: list[AttachmentBundleEntry] = []
        for source in snapshots:
            relative = source.path.relative_to(root).as_posix()
            archive_path = _dedupe_archive_path(_sanitize_archive_member(relative), used)
            entries.append(AttachmentBundleEntry(source, archive_path))
        return tuple(entries)

    # Mixed locations deliberately avoid embedding absolute local paths. Files
    # are grouped by their resolved parent in first-seen order and placed under
    # deterministic location-NN namespaces.
    parent_namespaces: dict[str, str] = {}
    used: set[str] = set()
    entries = []
    for source in snapshots:
        parent_key = _path_key(source.path.parent)
        namespace = parent_namespaces.get(parent_key)
        if namespace is None:
            namespace = f"location-{len(parent_namespaces) + 1:02d}"
            parent_namespaces[parent_key] = namespace
        candidate = f"{namespace}/{source.path.name}"
        archive_path = _dedupe_archive_path(_sanitize_archive_member(candidate), used)
        entries.append(AttachmentBundleEntry(source, archive_path))
    return tuple(entries)


def create_attachment_bundle(
    paths: Sequence[str | Path],
    *,
    project_root: str | Path | None = None,
    directory: str | Path | None = None,
    progress_callback: ProgressCallback | None = None,
    cancel_check: CancelCheck | None = None,
) -> AttachmentBundleResult:
    if not paths:
        raise ValueError("Cannot create a bundle from an empty attachment selection")

    bundle_dir = Path(directory) if directory is not None else attachment_bundle_directory()
    bundle_dir.mkdir(parents=True, exist_ok=True)

    entries = build_bundle_entries(paths, project_root=project_root)
    total_files = len(entries)
    total_bytes = sum(entry.source.size_bytes for entry in entries)
    final_path = unique_bundle_path(bundle_dir)
    partial_path = bundle_dir / f".{final_path.name}.{uuid4().hex}.partial"

    files_done = 0
    bytes_done = 0

    def emit(phase: str) -> None:
        if progress_callback is not None:
            progress_callback(phase, files_done, total_files, bytes_done, total_bytes)

    try:
        _raise_if_cancelled(cancel_check)
        emit("Preparing ZIP")
        with zipfile.ZipFile(
            partial_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            allowZip64=True,
        ) as archive:
            for entry in entries:
                _raise_if_cancelled(cancel_check)
                current = _snapshot(revalidate_attachment_files([entry.source.path])[0])
                _assert_unchanged(entry.source, current)

                info = zipfile.ZipInfo.from_file(current.path, arcname=entry.archive_path)
                info.compress_type = zipfile.ZIP_DEFLATED

                with current.path.open("rb") as source_handle, archive.open(
                    info,
                    mode="w",
                    force_zip64=True,
                ) as zip_handle:
                    while True:
                        _raise_if_cancelled(cancel_check)
                        chunk = source_handle.read(COPY_CHUNK_SIZE)
                        if not chunk:
                            break
                        zip_handle.write(chunk)
                        bytes_done += len(chunk)
                        emit("Creating ZIP")

                after = _snapshot(revalidate_attachment_files([entry.source.path])[0])
                _assert_unchanged(entry.source, after)
                files_done += 1
                emit("Creating ZIP")

        _raise_if_cancelled(cancel_check)
        os.replace(partial_path, final_path)
        archive_bytes = max(0, int(final_path.stat().st_size))
        emit("ZIP ready")
        return AttachmentBundleResult(
            bundle_path=final_path,
            file_count=total_files,
            total_bytes=total_bytes,
            archive_bytes=archive_bytes,
        )
    except Exception:
        try:
            partial_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _snapshot(file: AttachmentFile) -> BundleSourceSnapshot:
    try:
        stat = file.path.stat()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Attachment disappeared while bundling: {file.path}") from exc
    except PermissionError as exc:
        raise PermissionError(f"Attachment became inaccessible while bundling: {file.path}") from exc
    except OSError as exc:
        raise OSError(f"Attachment cannot be accessed while bundling: {file.path}: {exc}") from exc
    return BundleSourceSnapshot(
        path=file.path,
        size_bytes=max(0, int(stat.st_size)),
        mtime_ns=int(stat.st_mtime_ns),
    )


def _assert_unchanged(expected: BundleSourceSnapshot, actual: BundleSourceSnapshot) -> None:
    if expected.size_bytes != actual.size_bytes or expected.mtime_ns != actual.mtime_ns:
        raise RuntimeError(f"Attachment changed while bundling: {expected.path}")


def _usable_project_root(
    project_root: str | Path | None,
    snapshots: Sequence[BundleSourceSnapshot],
) -> Path | None:
    if project_root is None or not snapshots:
        return None
    try:
        root = Path(project_root).expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not root.is_dir():
        return None
    try:
        for source in snapshots:
            source.path.relative_to(root)
    except ValueError:
        return None
    return root


def _sanitize_archive_member(value: str) -> str:
    text = value.replace("\\", "/").strip("/")
    if not text:
        raise ValueError("Archive member path must not be empty")
    if ":" in PurePosixPath(text).parts[0]:
        raise ValueError(f"Absolute archive member is not allowed: {value}")
    pure = PurePosixPath(text)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise ValueError(f"Unsafe archive member path: {value}")
    return pure.as_posix()


def _dedupe_archive_path(candidate: str, used: set[str]) -> str:
    key = candidate.casefold()
    if key not in used:
        used.add(key)
        return candidate

    pure = PurePosixPath(candidate)
    parent = pure.parent
    suffix = pure.suffix
    stem = pure.name[: -len(suffix)] if suffix else pure.name
    for index in range(2, 10_000):
        name = f"{stem}-{index}{suffix}"
        resolved = (parent / name).as_posix() if str(parent) != "." else name
        key = resolved.casefold()
        if key not in used:
            used.add(key)
            return resolved
    raise RuntimeError(f"Could not resolve archive member collision for {candidate}")


def _raise_if_cancelled(cancel_check: CancelCheck | None) -> None:
    if cancel_check is not None and cancel_check():
        raise AttachmentBundleCancelled("Attachment bundle creation cancelled.")


def _path_key(path: Path) -> str:
    try:
        value = str(path.resolve(strict=False))
    except (OSError, RuntimeError):
        value = str(path.absolute())
    return os.path.normcase(value).casefold()
