from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.check_release_readiness import validate_release_documents
from scripts.validate_release_evidence import (
    BASE_REQUIRED_GATES,
    REQUIRED_GATES,
    V130_REQUIRED_GATES,
    V131_REQUIRED_GATES,
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
    version: str = "1.3.1",
    failed_gate: str | None = None,
    gate_names: tuple[str, ...] = REQUIRED_GATES,
) -> None:
    gates = {name: True for name in gate_names}
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
        expected_version="1.3.1",
        expected_archive_sha256=archive_hash,
    )

    assert summary.version == "1.3.1"
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
            expected_version="1.3.1",
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
            expected_version="1.3.1",
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
            expected_version="1.3.1",
        )


def test_v130_evidence_requires_selected_files_workflow_gates(
    tmp_path: Path,
) -> None:
    windows_10 = tmp_path / "windows-10.json"
    _write_evidence(
        windows_10,
        os_release="Windows 10",
        archive_sha256="f" * 64,
        version="1.3.0",
        gate_names=BASE_REQUIRED_GATES,
    )

    with pytest.raises(
        ReleaseEvidenceError,
        match="selected_files_paste_paths_visibility",
    ):
        validate_release_evidence(
            [windows_10],
            expected_version="1.3.0",
        )


def test_v131_evidence_requires_responsive_dpi_gates(
    tmp_path: Path,
) -> None:
    windows_10 = tmp_path / "windows-10-v131.json"
    _write_evidence(
        windows_10,
        os_release="Windows 10",
        archive_sha256="8" * 64,
        gate_names=BASE_REQUIRED_GATES + V130_REQUIRED_GATES,
    )

    with pytest.raises(ReleaseEvidenceError, match="responsive_minimum_window"):
        validate_release_evidence(
            [windows_10],
            expected_version="1.3.1",
        )


def test_v120_evidence_keeps_historical_base_gate_compatibility(
    tmp_path: Path,
) -> None:
    archive_hash = "9" * 64
    windows_10 = tmp_path / "windows-10.json"
    windows_11 = tmp_path / "windows-11.json"

    for path, release in (
        (windows_10, "Windows 10"),
        (windows_11, "Windows 11"),
    ):
        _write_evidence(
            path,
            os_release=release,
            archive_sha256=archive_hash,
            version="1.2.0",
            gate_names=BASE_REQUIRED_GATES,
        )

    summary = validate_release_evidence(
        [windows_10, windows_11],
        expected_version="1.2.0",
        expected_archive_sha256=archive_hash,
    )

    assert summary.version == "1.2.0"


def test_versioned_gate_sets_cover_v130_and_v131_contracts() -> None:
    assert set(V130_REQUIRED_GATES).issubset(REQUIRED_GATES)
    assert set(V131_REQUIRED_GATES).issubset(REQUIRED_GATES)
    assert "selected_files_review_transactionality" in V130_REQUIRED_GATES
    assert "responsive_qhd_scaling" in V131_REQUIRED_GATES
    assert "interface_scale_persistence_restart" in V131_REQUIRED_GATES
    assert "safety_confirmation_setting" in REQUIRED_GATES


def test_current_release_documents_pass_the_readiness_validator() -> None:
    assert __version__ == "1.3.1"
    validate_release_documents(PROJECT_ROOT, version=__version__)


def test_release_candidate_scripts_cover_automated_and_manual_gates() -> None:
    automated = (
        PROJECT_ROOT / "scripts" / "validate_release_candidate.ps1"
    ).read_text(encoding="utf-8-sig")
    manual = (
        PROJECT_ROOT / "scripts" / "record_manual_validation.ps1"
    ).read_text(encoding="utf-8-sig")

    for marker in (
        "compileall",
        "check_version_consistency.py",
        "test_selected_files_workflow.py",
        "selected_files_regression",
        "responsive_regression",
        "test_responsive_regression_matrix.py",
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
