from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_release_readiness import validate_release_documents
from scripts.validate_release_evidence import (
    REQUIRED_GATES,
    ReleaseEvidenceError,
    validate_release_evidence,
)
from xcc import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_evidence(
    path: Path,
    *,
    os_release: str,
    archive_sha256: str,
    version: str = "1.2.0",
    failed_gate: str | None = None,
) -> None:
    gates = {name: True for name in REQUIRED_GATES}
    if failed_gate is not None:
        gates[failed_gate] = False

    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "xcc_version": version,
                "archive_sha256": archive_sha256,
                "recorded_at_utc": "2026-07-27T00:00:00Z",
                "operator": "test-operator",
                "os": {
                    "release": os_release,
                    "product_name": f"Microsoft {os_release} Pro",
                    "version": "10.0",
                    "build": "26100" if os_release == "Windows 11" else "19045",
                    "architecture": "64-bit",
                    "computer_name": "TESTHOST",
                },
                "gates": gates,
                "all_passed": failed_gate is None,
                "notes": "",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_release_evidence_requires_matching_windows_10_and_11_records(
    tmp_path: Path,
) -> None:
    archive_hash = "a" * 64
    windows_10 = tmp_path / "windows-10.json"
    windows_11 = tmp_path / "windows-11.json"
    _write_evidence(
        windows_10,
        os_release="Windows 10",
        archive_sha256=archive_hash,
    )
    _write_evidence(
        windows_11,
        os_release="Windows 11",
        archive_sha256=archive_hash,
    )

    summary = validate_release_evidence(
        [windows_10, windows_11],
        expected_version="1.2.0",
        expected_archive_sha256=archive_hash,
    )

    assert summary.version == "1.2.0"
    assert summary.os_releases == {"Windows 10", "Windows 11"}
    assert summary.archive_sha256 == archive_hash


def test_release_evidence_rejects_missing_windows_10_record(tmp_path: Path) -> None:
    windows_11 = tmp_path / "windows-11.json"
    _write_evidence(
        windows_11,
        os_release="Windows 11",
        archive_sha256="b" * 64,
    )

    with pytest.raises(ReleaseEvidenceError, match="Windows 10"):
        validate_release_evidence(
            [windows_11],
            expected_version="1.2.0",
        )


def test_release_evidence_rejects_failed_manual_gate(tmp_path: Path) -> None:
    windows_10 = tmp_path / "windows-10.json"
    _write_evidence(
        windows_10,
        os_release="Windows 10",
        archive_sha256="c" * 64,
        failed_gate="cooperative_cancellation",
    )

    with pytest.raises(ReleaseEvidenceError, match="cooperative_cancellation"):
        validate_release_evidence(
            [windows_10],
            expected_version="1.2.0",
        )


def test_release_evidence_rejects_different_archive_hashes(tmp_path: Path) -> None:
    windows_10 = tmp_path / "windows-10.json"
    windows_11 = tmp_path / "windows-11.json"
    _write_evidence(
        windows_10,
        os_release="Windows 10",
        archive_sha256="d" * 64,
    )
    _write_evidence(
        windows_11,
        os_release="Windows 11",
        archive_sha256="e" * 64,
    )

    with pytest.raises(ReleaseEvidenceError, match="different release archive"):
        validate_release_evidence(
            [windows_10, windows_11],
            expected_version="1.2.0",
        )


def test_v120_release_documents_are_complete() -> None:
    assert __version__ == "1.2.0"
    validate_release_documents(PROJECT_ROOT, version=__version__)

    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (PROJECT_ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
    validation = (PROJECT_ROOT / "docs" / "M10_VALIDATION.md").read_text(
        encoding="utf-8"
    )

    assert "Current version: **v1.2.0**" in readme
    assert "Текущая версия: **v1.2.0**" in readme
    assert "Status: RELEASE CANDIDATE PREPARED" in roadmap
    assert "validate_release_candidate.ps1" in validation
    assert "Windows 10" in validation
    assert "Windows 11" in validation


def test_release_candidate_scripts_cover_automated_and_manual_gates() -> None:
    automated = (
        PROJECT_ROOT / "scripts" / "validate_release_candidate.ps1"
    ).read_text(encoding="utf-8")
    manual = (
        PROJECT_ROOT / "scripts" / "record_manual_validation.ps1"
    ).read_text(encoding="utf-8")
    build = (PROJECT_ROOT / "scripts" / "build_release.ps1").read_text(
        encoding="utf-8"
    )

    for marker in (
        "compileall",
        "check_version_consistency.py",
        "pytest -q",
        "validate_clean_install.ps1",
        "build_release.ps1",
        "smoke_packaged_app.ps1",
        "package_release.ps1",
        "validate_release_archive.py",
    ):
        assert marker in automated

    for gate in REQUIRED_GATES:
        assert gate in manual

    assert 'Get-Process -Name "XCC Context Collector"' in build
    assert "Remove-DirectoryWithRetry" in build
