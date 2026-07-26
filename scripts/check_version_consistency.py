from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
_VERSION_RE = re.compile(r'__version__\s*=\s*"(?P<version>\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.-]+)?)"')


class VersionConsistencyError(RuntimeError):
    """Raised when repository version declarations do not agree."""


def read_canonical_version(project_root: Path = PROJECT_ROOT) -> str:
    init_path = project_root / "src" / "xcc" / "__init__.py"
    match = _VERSION_RE.search(init_path.read_text(encoding="utf-8"))
    if match is None:
        raise VersionConsistencyError(f"Could not read canonical version from {init_path}.")
    return match.group("version")


def validate_version_consistency(project_root: Path = PROJECT_ROOT) -> str:
    version = read_canonical_version(project_root)

    metadata = tomllib.loads(
        (project_root / "pyproject.toml").read_text(encoding="utf-8")
    )
    project = metadata["project"]
    if project.get("dynamic") != ["version"]:
        raise VersionConsistencyError("pyproject.toml must declare dynamic version metadata.")

    dynamic = metadata["tool"]["setuptools"]["dynamic"]["version"]
    if dynamic != {"attr": "xcc.__version__"}:
        raise VersionConsistencyError(
            "pyproject.toml must read the version from xcc.__version__."
        )

    readme = (project_root / "README.md").read_text(encoding="utf-8")
    required_readme_markers = (
        f"Current version: **v{version}**",
        f"Текущая версия: **v{version}**",
    )
    for marker in required_readme_markers:
        if marker not in readme:
            raise VersionConsistencyError(f"README version marker is missing: {marker}")

    changelog = (project_root / "CHANGELOG.md").read_text(encoding="utf-8")
    if "## [Unreleased]" not in changelog:
        raise VersionConsistencyError("CHANGELOG.md is missing [Unreleased].")
    if f"## [{version}]" not in changelog:
        raise VersionConsistencyError(
            f"CHANGELOG.md is missing the current release section [{version}]."
        )

    release_notes = project_root / "docs" / "releases" / f"v{version}.md"
    if not release_notes.exists():
        raise VersionConsistencyError(
            f"Release notes are missing for the current version: {release_notes}"
        )
    if f"Version: {version}" not in release_notes.read_text(encoding="utf-8"):
        raise VersionConsistencyError(
            f"Release notes do not declare Version: {version}."
        )

    if not (project_root / "LICENSE").exists():
        raise VersionConsistencyError("Root LICENSE file is missing.")

    return version


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate canonical XCC version declarations."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository root to validate.",
    )
    args = parser.parse_args()

    version = validate_version_consistency(args.project_root.resolve())
    print(f"Version consistency passed: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
