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
    assert __version__ == "1.2.0"


def test_dependency_groups_keep_runtime_minimal() -> None:
    project = _metadata()["project"]
    runtime = project["dependencies"]
    extras = project["optional-dependencies"]

    assert runtime == [
        "PySide6>=6.8,<6.12",
        "pyperclip>=1.9,<2",
    ]
    assert extras["dev"] == [
        "pytest>=8.3,<10",
        "pytest-cov>=6,<8",
    ]
    assert extras["build"] == ["pyinstaller>=6.11,<7"]
    assert extras["legacy"] == ["keyboard==0.13.5"]
    assert all("keyboard" not in dependency for dependency in runtime)


def test_pyproject_exposes_supported_gui_entry_point() -> None:
    project = _metadata()["project"]

    assert project["gui-scripts"] == {
        "xcc-context-collector": "xcc.gui:run_gui"
    }


def test_requirements_file_is_only_a_compatibility_wrapper() -> None:
    lines = [
        line.strip()
        for line in (PROJECT_ROOT / "requirements.txt")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]

    assert lines == ["-e ."]


def test_build_script_reads_canonical_version() -> None:
    script = (PROJECT_ROOT / "scripts" / "build_release.ps1").read_text(
        encoding="utf-8"
    )

    assert "from xcc import __version__" in script
    assert "generate_version_info.py" in script
    assert "--version-file" in script
    assert "VERSION.txt" in script