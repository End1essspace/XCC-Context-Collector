from pathlib import Path

import pytest

from src.xcc.scanner import scan_project_files


def test_scans_python_files_recursively(tmp_path: Path) -> None:
    root = tmp_path / "project"
    src = root / "src"
    src.mkdir(parents=True)

    main = src / "main.py"
    utils = src / "utils.py"
    notes = src / "notes.txt"

    main.write_text("print('main')", encoding="utf-8")
    utils.write_text("print('utils')", encoding="utf-8")
    notes.write_text("notes", encoding="utf-8")

    files = scan_project_files(root)

    assert files == [main, utils]


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

    assert files == [main]


def test_raises_for_missing_folder(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        scan_project_files(missing)


def test_raises_for_file_instead_of_folder(tmp_path: Path) -> None:
    file_path = tmp_path / "main.py"
    file_path.write_text("print('hello')", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        scan_project_files(file_path)