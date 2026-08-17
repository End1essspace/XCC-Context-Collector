from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.check_version_consistency import (
    read_canonical_version,
    validate_version_consistency,
)
from scripts.validate_release_archive import sha256_file, validate_archive
from scripts.validate_release_evidence import validate_release_evidence

_RELEASE_HEADING_RE = re.compile(
    r"^## \[(?P<version>\d+\.\d+\.\d+)\] - \d{4}-\d{2}-\d{2}$",
    re.MULTILINE,
)
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")

REQUIRED_AUTOMATED_GATES = (
    "compileall",
    "version_consistency",
    "selected_files_regression",
    "responsive_regression",
    "pytest",
    "clean_install",
    "pyinstaller_build",
    "packaged_startup_smoke",
    "archive_validation",
    "checksum_validation",
)


class ReleaseReadinessError(RuntimeError):
    """Raised when the repository is not ready for the final release tag."""


def _run_git(project_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        raise ReleaseReadinessError(
            f"Git command failed: git {' '.join(args)} ({detail})"
        )
    return result.stdout.strip()


def _require_mapping(
    value: Any,
    *,
    field: str,
    report_path: Path,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReleaseReadinessError(
            f"{report_path}: {field} must be a JSON object."
        )
    return value


def validate_git_release_state(project_root: Path) -> None:
    branch = _run_git(project_root, "branch", "--show-current")
    if branch != "main":
        raise ReleaseReadinessError(
            f"Release must be created from main, found {branch!r}."
        )

    if _run_git(project_root, "status", "--porcelain"):
        raise ReleaseReadinessError(
            "Working tree must be clean before creating the tag."
        )

    local_head = _run_git(project_root, "rev-parse", "HEAD")
    remote_head = _run_git(project_root, "rev-parse", "origin/main")
    if local_head != remote_head:
        raise ReleaseReadinessError(
            "Local main is not synchronized with origin/main."
        )


def validate_release_documents(project_root: Path, *, version: str) -> None:
    changelog = (project_root / "CHANGELOG.md").read_text(encoding="utf-8")
    versions = {
        match.group("version")
        for match in _RELEASE_HEADING_RE.finditer(changelog)
    }
    if version not in versions:
        raise ReleaseReadinessError(
            f"CHANGELOG.md is missing a dated [{version}] release section."
        )

    notes = project_root / "docs" / "releases" / f"v{version}.md"
    if not notes.exists():
        raise ReleaseReadinessError(f"Release notes are missing: {notes}")
    notes_text = notes.read_text(encoding="utf-8")
    for marker in (f"Version: {version}", "## Summary", "## Validation"):
        if marker not in notes_text:
            raise ReleaseReadinessError(
                f"Release notes are missing required marker: {marker}"
            )


def validate_automated_gate_report(
    report_path: Path,
    *,
    expected_version: str,
    expected_archive_name: str,
    expected_archive_sha256: str,
) -> None:
    if not report_path.exists() or not report_path.is_file():
        raise ReleaseReadinessError(
            f"Automated gate report not found: {report_path}"
        )

    try:
        data = json.loads(report_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseReadinessError(
            f"Could not read automated gate report {report_path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise ReleaseReadinessError(
            f"{report_path}: top-level JSON value must be an object."
        )

    if data.get("schema_version") != 1:
        raise ReleaseReadinessError(
            f"{report_path}: schema_version must be 1."
        )

    if data.get("xcc_version") != expected_version:
        raise ReleaseReadinessError(
            f"{report_path}: expected XCC version {expected_version}, "
            f"found {data.get('xcc_version')!r}."
        )

    if data.get("passed") is not True:
        raise ReleaseReadinessError(
            f"{report_path}: automated release gate did not pass."
        )

    completed_at = data.get("completed_at_utc")
    if not isinstance(completed_at, str) or not completed_at.strip():
        raise ReleaseReadinessError(
            f"{report_path}: completed_at_utc is required."
        )

    archive = _require_mapping(
        data.get("archive"),
        field="archive",
        report_path=report_path,
    )
    if archive.get("filename") != expected_archive_name:
        raise ReleaseReadinessError(
            f"{report_path}: automated report archive filename does not "
            "match the final release archive."
        )

    report_hash = archive.get("sha256")
    if not isinstance(report_hash, str) or not _SHA256_RE.fullmatch(report_hash):
        raise ReleaseReadinessError(
            f"{report_path}: archive.sha256 must be 64 hex characters."
        )
    if report_hash.casefold() != expected_archive_sha256.casefold():
        raise ReleaseReadinessError(
            f"{report_path}: automated report archive SHA-256 does not "
            "match the final release archive."
        )

    expected_checksum_name = f"{expected_archive_name}.sha256"
    if archive.get("checksum_filename") != expected_checksum_name:
        raise ReleaseReadinessError(
            f"{report_path}: checksum filename must be "
            f"{expected_checksum_name}."
        )

    gates = _require_mapping(
        data.get("gates"),
        field="gates",
        report_path=report_path,
    )
    missing = [name for name in REQUIRED_AUTOMATED_GATES if name not in gates]
    if missing:
        raise ReleaseReadinessError(
            f"{report_path}: missing automated gate(s): {', '.join(missing)}"
        )

    failed = [
        name
        for name in REQUIRED_AUTOMATED_GATES
        if gates.get(name) is not True
    ]
    if failed:
        raise ReleaseReadinessError(
            f"{report_path}: failed or skipped automated gate(s): "
            f"{', '.join(failed)}"
        )


def validate_release_readiness(
    *,
    project_root: Path,
    archive_path: Path,
    checksum_path: Path,
    automated_report_path: Path,
    evidence_paths: list[Path],
    check_git: bool = True,
) -> str:
    version = validate_version_consistency(project_root)
    if read_canonical_version(project_root) != version:
        raise ReleaseReadinessError(
            "Canonical version changed during validation."
        )

    validate_release_documents(project_root, version=version)

    expected_archive_name = f"XCC-Context-Collector-v{version}-win64.zip"
    if archive_path.name != expected_archive_name:
        raise ReleaseReadinessError(
            f"Release archive must be named {expected_archive_name}."
        )

    validate_archive(
        archive_path,
        expected_version=version,
        checksum_path=checksum_path,
    )
    archive_hash = sha256_file(archive_path)

    validate_automated_gate_report(
        automated_report_path,
        expected_version=version,
        expected_archive_name=expected_archive_name,
        expected_archive_sha256=archive_hash,
    )
    validate_release_evidence(
        evidence_paths,
        expected_version=version,
        expected_archive_sha256=archive_hash,
    )

    if check_git:
        validate_git_release_state(project_root)

    return version


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate final XCC release readiness before tagging."
    )
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--checksum", type=Path, required=True)
    parser.add_argument("--automated-report", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, action="append", required=True)
    parser.add_argument(
        "--skip-git-state",
        action="store_true",
        help="Skip clean main/origin checks. Intended only for isolated tests.",
    )
    args = parser.parse_args()

    version = validate_release_readiness(
        project_root=args.project_root.resolve(),
        archive_path=args.archive.resolve(),
        checksum_path=args.checksum.resolve(),
        automated_report_path=args.automated_report.resolve(),
        evidence_paths=[path.resolve() for path in args.evidence],
        check_git=not args.skip_git_state,
    )
    print(f"Release readiness passed for v{version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
