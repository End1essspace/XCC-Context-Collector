from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path, PurePosixPath

APP_DIRECTORY = "XCC Context Collector"
APP_EXECUTABLE = f"{APP_DIRECTORY}/XCC Context Collector.exe"
VERSION_FILE = f"{APP_DIRECTORY}/VERSION.txt"
_FORBIDDEN_SUFFIXES = {".py", ".pyc", ".pyo", ".spec"}
_CHECKSUM_RE = re.compile(r"^(?P<hash>[0-9a-fA-F]{64})\s+\*?(?P<name>.+?)\s*$")


class ReleaseArchiveError(RuntimeError):
    """Raised when a portable release archive violates the release contract."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_archive(
    archive_path: Path,
    *,
    expected_version: str,
    checksum_path: Path | None = None,
) -> None:
    if not archive_path.exists() or not archive_path.is_file():
        raise ReleaseArchiveError(f"Release archive not found: {archive_path}")

    try:
        with zipfile.ZipFile(archive_path) as archive:
            names = archive.namelist()
            if not names:
                raise ReleaseArchiveError("Release archive is empty.")

            normalized_files: list[str] = []
            for raw_name in names:
                if "\\" in raw_name:
                    raise ReleaseArchiveError(
                        f"Archive entry uses a backslash separator: {raw_name}"
                    )

                path = PurePosixPath(raw_name)
                if path.is_absolute() or ".." in path.parts:
                    raise ReleaseArchiveError(
                        f"Archive entry has an unsafe path: {raw_name}"
                    )

                if not path.parts or path.parts[0] != APP_DIRECTORY:
                    raise ReleaseArchiveError(
                        f"Archive entry is outside the application root: {raw_name}"
                    )

                if raw_name.endswith("/"):
                    continue

                normalized_files.append(raw_name)

                lower_parts = {part.casefold() for part in path.parts}
                if "__pycache__" in lower_parts or ".pytest_cache" in lower_parts:
                    raise ReleaseArchiveError(
                        f"Archive contains a cache path: {raw_name}"
                    )
                if path.suffix.casefold() in _FORBIDDEN_SUFFIXES:
                    raise ReleaseArchiveError(
                        f"Archive contains a forbidden source/build file: {raw_name}"
                    )

            required = {APP_EXECUTABLE, VERSION_FILE}
            missing = sorted(required.difference(normalized_files))
            if missing:
                raise ReleaseArchiveError(
                    "Archive is missing required file(s): " + ", ".join(missing)
                )

            version = archive.read(VERSION_FILE).decode("ascii").strip()
            if version != expected_version:
                raise ReleaseArchiveError(
                    f"VERSION.txt mismatch: expected {expected_version}, found {version}"
                )

            if len(normalized_files) < 3:
                raise ReleaseArchiveError(
                    "Archive does not contain a complete packaged application."
                )
    except zipfile.BadZipFile as exc:
        raise ReleaseArchiveError(f"Invalid ZIP archive: {archive_path}") from exc

    if checksum_path is not None:
        _validate_checksum(
            archive_path=archive_path,
            checksum_path=checksum_path,
        )


def _validate_checksum(*, archive_path: Path, checksum_path: Path) -> None:
    if not checksum_path.exists() or not checksum_path.is_file():
        raise ReleaseArchiveError(f"Checksum file not found: {checksum_path}")

    line = checksum_path.read_text(encoding="ascii").strip()
    match = _CHECKSUM_RE.fullmatch(line)
    if match is None:
        raise ReleaseArchiveError(
            "Checksum file must contain '<sha256>  <archive filename>'."
        )

    expected_name = archive_path.name
    if match.group("name") != expected_name:
        raise ReleaseArchiveError(
            f"Checksum filename mismatch: expected {expected_name}, "
            f"found {match.group('name')}"
        )

    actual_hash = sha256_file(archive_path)
    if match.group("hash").casefold() != actual_hash:
        raise ReleaseArchiveError(
            f"Checksum mismatch for {archive_path.name}."
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate an XCC portable release ZIP and checksum."
    )
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--checksum", type=Path)
    args = parser.parse_args()

    validate_archive(
        args.archive.resolve(),
        expected_version=args.expected_version,
        checksum_path=args.checksum.resolve() if args.checksum else None,
    )
    print(f"Release archive validation passed: {args.archive.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
