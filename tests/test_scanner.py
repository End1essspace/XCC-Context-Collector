from pathlib import Path

import pytest

from src.xcc.scanner import scan_project_files


def test_scans_python_files_recursively(tmp_path: Path) -> None:
    root = tmp_path / "project"
    src = root / "src"
    src.mkdir(parents=True)

    main = src / "main.py"
    utils = src / "utils.py"
    notes = src / "notes.exe"

    main.write_text("print('main')", encoding="utf-8")
    utils.write_text("print('utils')", encoding="utf-8")
    notes.write_text("notes", encoding="utf-8")

    files = scan_project_files(root)

    assert len(files) == 2
    assert main in files
    assert utils in files


def test_excludes_ignored_directories(tmp_path: Path) -> None:
    root = tmp_path / "project"
    src = root / "src"
    venv = root / "venv"

    src.mkdir(parents=True)
    venv.mkdir(parents=True)

    main = src / "main.py"
    ignored = venv / "ignored.py"

    main.write_text("print('main')", encoding="utf-8")
    ignored.write_text("print('ignored')", encoding="utf-8")

    files = scan_project_files(root)

    assert len(files) == 1
    assert main in files


def test_raises_for_missing_folder(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        scan_project_files(missing)


def test_raises_for_file_instead_of_folder(tmp_path: Path) -> None:
    file_path = tmp_path / "main.py"
    file_path.write_text("print('hello')", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        scan_project_files(file_path)

def test_scans_allowed_filename_without_extension(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()

    dockerfile = root / "Dockerfile"
    dockerfile.write_text("FROM python:3.13\n", encoding="utf-8")

    files = scan_project_files(root)

    assert dockerfile in files


def test_respects_xccignore_and_gitignore(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()

    visible = root / "visible.py"
    git_ignored = root / "generated.py"
    xcc_ignored = root / "private.py"

    visible.write_text("VISIBLE = True\n", encoding="utf-8")
    git_ignored.write_text("GENERATED = True\n", encoding="utf-8")
    xcc_ignored.write_text("PRIVATE = True\n", encoding="utf-8")
    (root / ".gitignore").write_text("generated.py\n", encoding="utf-8")
    (root / ".xccignore").write_text("private.py\n", encoding="utf-8")

    files = scan_project_files(root)

    assert visible in files
    assert git_ignored not in files
    assert xcc_ignored not in files


def test_can_disable_gitignore_respect(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    generated = root / "generated.py"
    generated.write_text("GENERATED = True\n", encoding="utf-8")
    (root / ".gitignore").write_text("generated.py\n", encoding="utf-8")

    files = scan_project_files(root, respect_gitignore=False)

    assert generated in files


def test_builtin_excluded_directory_cannot_be_reenabled(tmp_path: Path) -> None:
    root = tmp_path / "project"
    build = root / "build"
    build.mkdir(parents=True)
    generated = build / "keep.py"
    generated.write_text("KEEP = True\n", encoding="utf-8")
    (root / ".xccignore").write_text("!build/keep.py\n", encoding="utf-8")

    files = scan_project_files(root)

    assert generated not in files

def test_scanner_reports_discovered_file_count(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    (root / "a.py").write_text("A = 1\n", encoding="utf-8")
    (root / "b.py").write_text("B = 2\n", encoding="utf-8")
    progress: list[tuple[int, int]] = []

    scan_project_files(
        root,
        progress_callback=lambda current, total: progress.append((current, total)),
    )

    assert progress[-1] == (2, 0)
