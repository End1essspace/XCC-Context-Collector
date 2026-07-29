from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from scripts.validate_release_archive import (
    ReleaseArchiveError,
    validate_archive,
)


def _write_release_archive(
    path: Path,
    *,
    version: str = "1.2.0",
    unsafe_name: str | None = None,
) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "XCC Context Collector/XCC Context Collector.exe",
            b"MZ-test-binary",
        )
        archive.writestr(
            "XCC Context Collector/VERSION.txt",
            version,
        )
        archive.writestr(
            "XCC Context Collector/_internal/runtime.dat",
            b"runtime",
        )
        if unsafe_name is not None:
            archive.writestr(unsafe_name, b"unsafe")


def _write_checksum(archive_path: Path, checksum_path: Path) -> None:
    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    checksum_path.write_text(
        f"{digest}  {archive_path.name}\n",
        encoding="ascii",
    )


def test_release_archive_and_checksum_validation_pass(tmp_path: Path) -> None:
    archive_path = tmp_path / "XCC-Context-Collector-v1.2.0-win64.zip"
    checksum_path = tmp_path / f"{archive_path.name}.sha256"
    _write_release_archive(archive_path)
    _write_checksum(archive_path, checksum_path)

    validate_archive(
        archive_path,
        expected_version="1.2.0",
        checksum_path=checksum_path,
    )


def test_release_archive_rejects_version_mismatch(tmp_path: Path) -> None:
    archive_path = tmp_path / "release.zip"
    _write_release_archive(archive_path, version="9.9.9")

    with pytest.raises(ReleaseArchiveError, match="VERSION.txt mismatch"):
        validate_archive(
            archive_path,
            expected_version="1.2.0",
        )


def test_release_archive_rejects_path_traversal(tmp_path: Path) -> None:
    archive_path = tmp_path / "release.zip"
    _write_release_archive(
        archive_path,
        unsafe_name="../outside.txt",
    )

    with pytest.raises(ReleaseArchiveError, match="unsafe path"):
        validate_archive(
            archive_path,
            expected_version="1.2.0",
        )


def test_release_archive_rejects_source_files(tmp_path: Path) -> None:
    archive_path = tmp_path / "release.zip"
    _write_release_archive(
        archive_path,
        unsafe_name="XCC Context Collector/source.py",
    )

    with pytest.raises(ReleaseArchiveError, match="forbidden"):
        validate_archive(
            archive_path,
            expected_version="1.2.0",
        )


def test_release_archive_rejects_modified_checksum(tmp_path: Path) -> None:
    archive_path = tmp_path / "release.zip"
    checksum_path = tmp_path / "release.zip.sha256"
    _write_release_archive(archive_path)
    checksum_path.write_text(
        f"{'0' * 64}  {archive_path.name}\n",
        encoding="ascii",
    )

    with pytest.raises(ReleaseArchiveError, match="Checksum mismatch"):
        validate_archive(
            archive_path,
            expected_version="1.2.0",
            checksum_path=checksum_path,
        )
