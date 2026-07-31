from __future__ import annotations

import tomllib
from pathlib import Path

from xcc import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _metadata() -> dict:
    return tomllib.loads(
        (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )


def test_pyproject_defines_canonical_project_metadata() -> None:
    metadata = _metadata()
    project = metadata["project"]

    assert project["name"] == "xcc-context-collector"
    assert project["requires-python"] == ">=3.13,<3.14"
    assert project["dynamic"] == ["version"]
    assert metadata["tool"]["setuptools"]["dynamic"]["version"] == {
        "attr": "xcc.__version__"
    }
    assert project["gui-scripts"] == {
        "xcc-context-collector": "xcc.gui:run_gui"
    }
    assert __version__ == "1.3.0"


def test_dependency_groups_match_the_supported_product_boundary() -> None:
    project = _metadata()["project"]

    assert project["dependencies"] == [
        "PySide6>=6.8,<6.12",
        "pyperclip>=1.9,<2",
    ]
    assert project["optional-dependencies"] == {
        "dev": [
            "pytest>=8.3,<10",
            "pytest-cov>=6,<8",
        ],
        "build": ["pyinstaller>=6.11,<7"],
    }


def test_repository_exposes_one_supported_runtime_path() -> None:
    required_paths = (
        "gui.py",
        "src/xcc/gui.py",
        "src/xcc/pipeline.py",
    )
    removed_legacy_paths = (
        "run.py",
        "hotkey.py",
        "src/xcc/main.py",
        "src/xcc/hotkey.py",
        "src/xcc/picker.py",
        "tests/test_hotkey.py",
    )

    for relative_path in required_paths:
        assert (PROJECT_ROOT / relative_path).is_file()

    for relative_path in removed_legacy_paths:
        assert not (PROJECT_ROOT / relative_path).exists()


def test_requirements_file_delegates_to_canonical_metadata() -> None:
    lines = [
        line.strip()
        for line in (PROJECT_ROOT / "requirements.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    assert lines == ["-e ."]


def test_current_release_documents_exist() -> None:
    required_paths = (
        "CHANGELOG.md",
        "docs/releases/v1.3.0.md",
        "docs/UI_REFERENCE_v1.3.0.md",
        "docs/M15_VALIDATION.md",
        "docs/RELEASE_CHECKLIST.md",
    )

    for relative_path in required_paths:
        assert (PROJECT_ROOT / relative_path).is_file()


def test_build_script_reads_the_canonical_version() -> None:
    script = (PROJECT_ROOT / "scripts" / "build_release.ps1").read_text(
        encoding="utf-8-sig"
    )

    assert "from xcc import __version__" in script
    assert "generate_version_info.py" in script
    assert "--version-file" in script
    assert "VERSION.txt" in script
