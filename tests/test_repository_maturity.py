from __future__ import annotations

from pathlib import Path

from scripts.check_version_consistency import validate_version_consistency
from xcc import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_repository_governance_files_exist() -> None:
    required = [
        "LICENSE",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "docs/BUG_REPORTING.md",
        "docs/PORTABLE_ZIP.md",
        "docs/RELEASE_CHECKLIST.md",
        ".github/pull_request_template.md",
        ".github/ISSUE_TEMPLATE/bug_report.yml",
        ".github/ISSUE_TEMPLATE/feature_request.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
    ]

    missing = [
        path
        for path in required
        if not (PROJECT_ROOT / path).exists()
    ]
    assert missing == []


def test_windows_ci_contains_minimum_gate() -> None:
    workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    assert "runs-on: windows-latest" in workflow
    assert '"3.13"' in workflow
    assert "cache: pip" in workflow
    assert "compileall" in workflow
    assert "pytest -q" in workflow
    assert "build_release.ps1" in workflow
    assert "smoke_packaged_app.ps1" in workflow
    assert "package_release.ps1" in workflow
    assert "upload-artifact@v4" in workflow


def test_readme_contains_ci_release_and_screenshot_links() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    assert "actions/workflows/ci.yml/badge.svg" in readme
    assert "xcc-context-collector/releases" in readme
    assert "docs/screenshots/xcc-collect.svg" in readme
    assert "docs/screenshots/xcc-history.svg" in readme
    assert "docs/PORTABLE_ZIP.md" in readme


def test_repository_version_consistency() -> None:
    assert validate_version_consistency(PROJECT_ROOT) == __version__


def test_release_packaging_defaults_to_non_public_artifacts_directory() -> None:
    script = (
        PROJECT_ROOT / "scripts" / "package_release.ps1"
    ).read_text(encoding="utf-8")

    assert '[string]$OutputDirectory = "artifacts"' in script
    assert "Get-FileHash" in script
    assert "validate_release_archive.py" in script
