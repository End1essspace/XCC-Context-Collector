from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
REQUIRED_OS_RELEASES = {"Windows 10", "Windows 11"}
REQUIRED_GATES = (
    "packaged_startup",
    "selected_files_mode",
    "full_folder_mode",
    "git_changed_files_mode",
    "project_tree_mode",
    "large_project_responsiveness",
    "cooperative_cancellation",
    "second_job_prevented",
    "clipboard_unchanged_after_cancel",
    "tray_restore",
    "tray_quit",
    "native_hotkey_restore",
    "hotkey_conflict_non_fatal",
    "autostart_shortcut",
    "invalid_config_recovery",
    "single_instance_restore",
)
_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class ReleaseEvidenceError(RuntimeError):
    """Raised when manual release evidence is incomplete or inconsistent."""


@dataclass(frozen=True, slots=True)
class EvidenceSummary:
    version: str
    archive_sha256: str
    os_releases: frozenset[str]
    files: tuple[Path, ...]


def _require_mapping(value: Any, *, field: str, path: Path) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReleaseEvidenceError(f"{path}: {field} must be an object.")
    return value


def _load_evidence(path: Path, *, expected_version: str) -> tuple[str, str]:
    if not path.exists() or not path.is_file():
        raise ReleaseEvidenceError(f"Evidence file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReleaseEvidenceError(f"Could not read evidence file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ReleaseEvidenceError(f"{path}: top-level JSON value must be an object.")

    if data.get("schema_version") != SCHEMA_VERSION:
        raise ReleaseEvidenceError(
            f"{path}: schema_version must be {SCHEMA_VERSION}."
        )

    version = data.get("xcc_version")
    if version != expected_version:
        raise ReleaseEvidenceError(
            f"{path}: expected XCC version {expected_version}, found {version!r}."
        )

    archive_sha256 = data.get("archive_sha256")
    if not isinstance(archive_sha256, str) or not _SHA256_RE.fullmatch(
        archive_sha256
    ):
        raise ReleaseEvidenceError(f"{path}: archive_sha256 must be 64 hex characters.")

    operator = data.get("operator")
    if not isinstance(operator, str) or not operator.strip():
        raise ReleaseEvidenceError(f"{path}: operator is required.")

    recorded_at = data.get("recorded_at_utc")
    if not isinstance(recorded_at, str) or not recorded_at.strip():
        raise ReleaseEvidenceError(f"{path}: recorded_at_utc is required.")

    os_info = _require_mapping(data.get("os"), field="os", path=path)
    os_release = os_info.get("release")
    if os_release not in REQUIRED_OS_RELEASES:
        raise ReleaseEvidenceError(
            f"{path}: os.release must be Windows 10 or Windows 11."
        )

    product_name = os_info.get("product_name")
    if not isinstance(product_name, str) or not product_name.strip():
        raise ReleaseEvidenceError(f"{path}: os.product_name is required.")

    gates = _require_mapping(data.get("gates"), field="gates", path=path)
    missing = [name for name in REQUIRED_GATES if name not in gates]
    if missing:
        raise ReleaseEvidenceError(
            f"{path}: missing manual gate(s): {', '.join(missing)}"
        )

    failed = [name for name in REQUIRED_GATES if gates.get(name) is not True]
    if failed:
        raise ReleaseEvidenceError(
            f"{path}: failed or unconfirmed gate(s): {', '.join(failed)}"
        )

    return os_release, archive_sha256.casefold()


def validate_release_evidence(
    evidence_paths: Iterable[Path],
    *,
    expected_version: str,
    expected_archive_sha256: str | None = None,
) -> EvidenceSummary:
    paths = tuple(Path(path).resolve() for path in evidence_paths)
    if not paths:
        raise ReleaseEvidenceError("At least one evidence file is required.")

    releases: set[str] = set()
    hashes: set[str] = set()

    for path in paths:
        os_release, archive_hash = _load_evidence(
            path,
            expected_version=expected_version,
        )
        releases.add(os_release)
        hashes.add(archive_hash)

    missing_releases = sorted(REQUIRED_OS_RELEASES.difference(releases))
    if missing_releases:
        raise ReleaseEvidenceError(
            "Missing clean-host evidence for: " + ", ".join(missing_releases)
        )

    if len(hashes) != 1:
        raise ReleaseEvidenceError(
            "Windows validation records refer to different release archive hashes."
        )

    archive_sha256 = next(iter(hashes))
    if expected_archive_sha256 is not None:
        expected = expected_archive_sha256.casefold()
        if not _SHA256_RE.fullmatch(expected):
            raise ReleaseEvidenceError("Expected archive SHA-256 is invalid.")
        if archive_sha256 != expected:
            raise ReleaseEvidenceError(
                "Manual evidence does not match the final release archive SHA-256."
            )

    return EvidenceSummary(
        version=expected_version,
        archive_sha256=archive_sha256,
        os_releases=frozenset(releases),
        files=paths,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate XCC Windows 10/11 manual release evidence."
    )
    parser.add_argument("--expected-version", required=True)
    parser.add_argument(
        "--expected-archive-sha256",
        help="Require every evidence record to reference this archive hash.",
    )
    parser.add_argument(
        "--evidence",
        type=Path,
        action="append",
        required=True,
        help="Manual validation JSON file. Pass once per clean-host record.",
    )
    args = parser.parse_args()

    summary = validate_release_evidence(
        args.evidence,
        expected_version=args.expected_version,
        expected_archive_sha256=args.expected_archive_sha256,
    )
    releases = ", ".join(sorted(summary.os_releases))
    print(
        f"Release evidence validation passed: v{summary.version}; "
        f"{releases}; archive {summary.archive_sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
