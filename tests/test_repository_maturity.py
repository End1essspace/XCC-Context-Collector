from __future__ import annotations

from pathlib import Path

from scripts.check_version_consistency import validate_version_consistency
from xcc import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RUNTIME_ASSETS = (
    "xcc_app.ico",
    "xcc_app.png",
    "xcc_tray.ico",
    "xcc_tray.png",
    "nav-collect.svg",
    "nav-history.svg",
    "nav-settings.svg",
    "nav-about.svg",
    "ui-setup.svg",
    "ui-last-run.svg",
    "ui-volume.svg",
    "ui-output.svg",
    "ui-coverage.svg",
    "ui-health.svg",
    "ui-paste-paths.svg",
    "ui-collect-copy.svg",
)


def test_repository_governance_files_exist() -> None:
    required = (
        "LICENSE",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "docs/ARCHITECTURE.md",
        "docs/BUG_REPORTING.md",
        "docs/PORTABLE_ZIP.md",
        "docs/RELEASE_CHECKLIST.md",
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
    )

    missing = [path for path in required if not (PROJECT_ROOT / path).exists()]
    assert missing == []


def test_windows_ci_contains_the_minimum_release_gate() -> None:
    workflow = (
        PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
    ).read_text(encoding="utf-8")

    for marker in (
        "runs-on: windows-latest",
        '"3.13"',
        "cache: pip",
        "compileall",
        "pytest -q",
        "build_release.ps1",
        "smoke_packaged_app.ps1",
        "package_release.ps1",
        "upload-artifact@v4",
    ):
        assert marker in workflow


def test_readme_exposes_public_release_and_screenshot_links() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for marker in (
        "actions/workflows/ci.yml/badge.svg",
        "xcc-context-collector/releases",
        "docs/screenshots/xcc-collect.png",
        "docs/screenshots/xcc-history.png",
        "docs/PORTABLE_ZIP.md",
    ):
        assert marker in readme


def test_repository_version_consistency() -> None:
    assert validate_version_consistency(PROJECT_ROOT) == __version__


def test_release_packaging_uses_private_artifacts_and_checksum_validation() -> None:
    script = (
        PROJECT_ROOT / "scripts" / "package_release.ps1"
    ).read_text(encoding="utf-8-sig")

    assert '[string]$OutputDirectory = "artifacts"' in script
    assert "Get-FileHash" in script
    assert "validate_release_archive.py" in script


def test_workspace_hygiene_covers_generated_outputs() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    cleanup = (
        PROJECT_ROOT / "scripts" / "clean_workspace.ps1"
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
        r"src\xcc_context_collector.egg-info",
    ):
        assert generated_path in cleanup


def test_release_build_includes_every_runtime_asset() -> None:
    build = (
        PROJECT_ROOT / "scripts" / "build_release.ps1"
    ).read_text(encoding="utf-8-sig")

    assert 'Remove-DirectoryWithRetry "build"' in build
    assert "Test-Path $SpecPath" in build
    assert '--add-data "assets;assets"' not in build

    for asset_name in RUNTIME_ASSETS:
        assert (PROJECT_ROOT / "assets" / asset_name).is_file()
        assert asset_name in build

def test_historical_material_is_release_scoped_and_active_tree_is_clean() -> None:
    assert (
        PROJECT_ROOT / "docs" / "releases" / "v1.2.0-validation.md"
    ).is_file()
    assert not (PROJECT_ROOT / "docs" / "M10_VALIDATION.md").exists()
    assert not (PROJECT_ROOT / "assets" / "original_icons").exists()

