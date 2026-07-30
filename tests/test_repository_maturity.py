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
        "docs/M10_VALIDATION.md",
        "docs/M15_VALIDATION.md",
        "docs/releases/v1.2.0.md",
        "docs/releases/v1.3.0.md",
        "scripts/validate_release_candidate.ps1",
        "scripts/record_manual_validation.ps1",
        "scripts/validate_release_evidence.py",
        "scripts/check_release_readiness.py",
        "scripts/clean_workspace.ps1",
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
    assert "docs/screenshots/xcc-collect.png" in readme
    assert "docs/screenshots/xcc-history.png" in readme
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

def test_workspace_hygiene_covers_generated_outputs() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    cleanup = (
        PROJECT_ROOT / "scripts" / "clean_workspace.ps1"
    ).read_text(encoding="utf-8-sig")
    build = (
        PROJECT_ROOT / "scripts" / "build_release.ps1"
    ).read_text(encoding="utf-8-sig")

    for pattern in (
        "__pycache__/",
        ".pytest_cache/",
        "*.egg-info/",
        "build/",
        "dist/",
        "artifacts/",
        "release/",
        "*.spec",
    ):
        assert pattern in gitignore

    for generated_path in (
        "__pycache__",
        ".pytest_cache",
        "build",
        "dist",
        "XCC Context Collector.spec",
        "src\\xcc_context_collector.egg-info",
    ):
        assert generated_path in cleanup

    assert 'Remove-DirectoryWithRetry "build"' in build
    assert "Test-Path $SpecPath" in build
    assert '--add-data "assets;assets"' not in build
    for asset_name in (
        "xcc_app.ico",
        "xcc_app.png",
        "xcc_tray.ico",
        "xcc_tray.png",
        "nav-collect.svg",
        "nav-history.svg",
        "nav-settings.svg",
        "nav-about.svg",
    ):
        assert asset_name in build

def test_v130_selected_files_release_documentation_is_aligned() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    architecture = (PROJECT_ROOT / "docs" / "ARCHITECTURE.md").read_text(encoding="utf-8")
    roadmap = (PROJECT_ROOT / "docs" / "roadmap.md").read_text(encoding="utf-8")
    notes = (PROJECT_ROOT / "docs" / "releases" / "v1.3.0.md").read_text(encoding="utf-8")

    assert "Selected Files AI workflow" in readme
    assert "AI-workflow для Selected Files" in readme
    assert "path_list_parser.py" in architecture
    assert "selected_files_importer.py" in architecture
    assert "M15 — v1.3.0 Validation and Release" in roadmap
    assert "Version: 1.3.0" in notes
    assert "## Validation" in notes
