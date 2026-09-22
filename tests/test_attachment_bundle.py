from __future__ import annotations

import os
import time
import zipfile
from pathlib import Path

import pytest

from xcc.attachment_bundle import (
    BUNDLE_RETENTION_DAYS,
    attachment_bundle_directory,
    build_bundle_entries,
    cleanup_stale_bundles,
    create_attachment_bundle,
)
from xcc.cancellation import AttachmentBundleCancelled


def test_bundle_preserves_project_relative_structure_and_bytes(tmp_path: Path) -> None:
    root = tmp_path / "project"
    first = root / "Assets" / "Scenes" / "Game.unity"
    second = root / "Assets" / "image.bin"
    first.parent.mkdir(parents=True)
    first.write_bytes(b"scene-bytes")
    second.write_bytes(b"\x00\x01\x02")

    result = create_attachment_bundle(
        [first, second],
        project_root=root,
        directory=tmp_path / "bundles",
    )

    assert result.file_count == 2
    assert result.total_bytes == len(b"scene-bytes") + 3
    assert result.bundle_path.exists()
    with zipfile.ZipFile(result.bundle_path) as archive:
        assert archive.namelist() == [
            "Assets/Scenes/Game.unity",
            "Assets/image.bin",
        ]
        assert archive.read("Assets/Scenes/Game.unity") == b"scene-bytes"
        assert archive.read("Assets/image.bin") == b"\x00\x01\x02"


def test_mixed_locations_use_safe_deterministic_namespaces(tmp_path: Path) -> None:
    left = tmp_path / "left" / "same.bin"
    right = tmp_path / "right" / "same.bin"
    left.parent.mkdir()
    right.parent.mkdir()
    left.write_bytes(b"left")
    right.write_bytes(b"right")

    entries = build_bundle_entries([left, right])

    assert [entry.archive_path for entry in entries] == [
        "location-01/same.bin",
        "location-02/same.bin",
    ]
    assert all(".." not in entry.archive_path for entry in entries)
    assert all(":" not in entry.archive_path for entry in entries)


def test_bundle_cancellation_is_transactional(tmp_path: Path) -> None:
    source = tmp_path / "large.bin"
    source.write_bytes(b"x" * (2 * 1024 * 1024))
    bundle_dir = tmp_path / "bundles"
    calls = 0

    def cancel_check() -> bool:
        nonlocal calls
        calls += 1
        return calls > 2

    with pytest.raises(AttachmentBundleCancelled):
        create_attachment_bundle(
            [source],
            directory=bundle_dir,
            cancel_check=cancel_check,
        )

    assert not list(bundle_dir.glob("*.zip"))
    assert not list(bundle_dir.glob("*.partial"))


def test_bundle_detects_source_change_during_work(tmp_path: Path) -> None:
    first = tmp_path / "first.bin"
    second = tmp_path / "second.bin"
    first.write_bytes(b"1" * 32)
    second.write_bytes(b"2" * 32)
    changed = False

    def progress(phase, files_done, total_files, bytes_done, total_bytes):
        nonlocal changed
        if not changed and files_done >= 1:
            second.write_bytes(b"changed")
            changed = True

    with pytest.raises(RuntimeError, match="changed while bundling"):
        create_attachment_bundle(
            [first, second],
            directory=tmp_path / "bundles",
            progress_callback=progress,
        )

    assert not list((tmp_path / "bundles").glob("*.zip"))


def test_cleanup_removes_only_stale_managed_bundles_and_skips_active(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundles"
    bundle_dir.mkdir()
    stale = bundle_dir / "XCC-Attachments-20260101-000000.zip"
    active = bundle_dir / "XCC-Attachments-20260101-000001.zip"
    unrelated = bundle_dir / "other.zip"
    for path in (stale, active, unrelated):
        path.write_bytes(b"zip")

    old = time.time() - ((BUNDLE_RETENTION_DAYS + 2) * 86400)
    os.utime(stale, (old, old))
    os.utime(active, (old, old))
    os.utime(unrelated, (old, old))

    result = cleanup_stale_bundles(
        directory=bundle_dir,
        active_paths=[active],
    )

    assert result.removed == (stale,)
    assert not stale.exists()
    assert active.exists()
    assert unrelated.exists()


def test_bundle_directory_uses_explicit_xcc_user_cache_boundary(tmp_path: Path) -> None:
    assert attachment_bundle_directory(home=tmp_path) == tmp_path / ".xcc" / "attachment-bundles"


def test_large_selection_has_no_xcc_file_count_limit(tmp_path: Path) -> None:
    files = []
    for index in range(300):
        path = tmp_path / "project" / f"f{index:03d}.bin"
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(bytes([index % 251]))
        files.append(path)

    result = create_attachment_bundle(
        files,
        project_root=tmp_path / "project",
        directory=tmp_path / "bundles",
    )

    assert result.file_count == 300
    with zipfile.ZipFile(result.bundle_path) as archive:
        assert len(archive.namelist()) == 300


def test_symlink_file_resolves_to_regular_file_when_supported(tmp_path: Path) -> None:
    target = tmp_path / "target.bin"
    link = tmp_path / "link.bin"
    target.write_bytes(b"target")
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable on this platform")

    entries = build_bundle_entries([link])
    assert len(entries) == 1
    assert entries[0].source.path == target.resolve()
