from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_release_readiness import (
    REQUIRED_AUTOMATED_GATES,
    ReleaseReadinessError,
    validate_automated_gate_report,
)


def _write_report(
    path: Path,
    *,
    version: str = "1.3.1",
    archive_name: str = "XCC-Context-Collector-v1.3.1-win64.zip",
    archive_hash: str = "a" * 64,
    passed: bool = True,
    failed_gate: str | None = None,
) -> None:
    gates = {name: True for name in REQUIRED_AUTOMATED_GATES}
    if failed_gate is not None:
        gates[failed_gate] = False

    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "xcc_version": version,
                "passed": passed,
                "completed_at_utc": "2026-07-30T12:00:00Z",
                "python": "Python 3.13.5",
                "os": {
                    "product_name": "Microsoft Windows 11 Pro",
                    "version": "10.0.26100",
                    "build": "26100",
                    "architecture": "64-bit",
                    "computer_name": "TESTHOST",
                },
                "archive": {
                    "filename": archive_name,
                    "sha256": archive_hash,
                    "checksum_filename": f"{archive_name}.sha256",
                },
                "gates": gates,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_automated_gate_report_matches_final_archive(tmp_path: Path) -> None:
    report = tmp_path / "automated.json"
    archive_name = "XCC-Context-Collector-v1.3.1-win64.zip"
    archive_hash = "b" * 64
    _write_report(
        report,
        archive_name=archive_name,
        archive_hash=archive_hash,
    )

    validate_automated_gate_report(
        report,
        expected_version="1.3.1",
        expected_archive_name=archive_name,
        expected_archive_sha256=archive_hash,
    )


def test_automated_gate_report_rejects_archive_hash_mismatch(
    tmp_path: Path,
) -> None:
    report = tmp_path / "automated.json"
    archive_name = "XCC-Context-Collector-v1.3.1-win64.zip"
    _write_report(
        report,
        archive_name=archive_name,
        archive_hash="c" * 64,
    )

    with pytest.raises(ReleaseReadinessError, match="SHA-256"):
        validate_automated_gate_report(
            report,
            expected_version="1.3.1",
            expected_archive_name=archive_name,
            expected_archive_sha256="d" * 64,
        )


def test_automated_gate_report_rejects_skipped_clean_install(
    tmp_path: Path,
) -> None:
    report = tmp_path / "automated.json"
    archive_name = "XCC-Context-Collector-v1.3.1-win64.zip"
    archive_hash = "e" * 64
    _write_report(
        report,
        archive_name=archive_name,
        archive_hash=archive_hash,
        failed_gate="clean_install",
    )

    with pytest.raises(ReleaseReadinessError, match="clean_install"):
        validate_automated_gate_report(
            report,
            expected_version="1.3.1",
            expected_archive_name=archive_name,
            expected_archive_sha256=archive_hash,
        )


def test_automated_gate_report_rejects_failed_release_gate(
    tmp_path: Path,
) -> None:
    report = tmp_path / "automated.json"
    archive_name = "XCC-Context-Collector-v1.3.1-win64.zip"
    archive_hash = "f" * 64
    _write_report(
        report,
        archive_name=archive_name,
        archive_hash=archive_hash,
        passed=False,
    )

    with pytest.raises(ReleaseReadinessError, match="did not pass"):
        validate_automated_gate_report(
            report,
            expected_version="1.3.1",
            expected_archive_name=archive_name,
            expected_archive_sha256=archive_hash,
        )


def test_required_automated_gates_include_release_regressions() -> None:
    assert "selected_files_regression" in REQUIRED_AUTOMATED_GATES
    assert "responsive_regression" in REQUIRED_AUTOMATED_GATES
