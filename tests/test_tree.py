from pathlib import Path

from src.xcc.tree import build_directory_tree, build_project_tree


def test_builds_project_tree_with_relative_paths(tmp_path: Path) -> None:
    root = tmp_path / "project"
    src = root / "src"
    src.mkdir(parents=True)

    main = src / "main.py"
    utils = src / "utils.py"

    main.write_text("print('main')", encoding="utf-8")
    utils.write_text("print('utils')", encoding="utf-8")

    tree = build_project_tree([utils, main], root)

    assert "# Project Tree" in tree
    assert "src/main.py" in tree
    assert "src/utils.py" in tree


def test_returns_empty_tree_for_no_paths() -> None:
    tree = build_project_tree([])

    assert tree == ""

def test_build_directory_tree_includes_files_and_directories(tmp_path: Path) -> None:
    root = tmp_path / "project"
    src = root / "src"
    docs = root / "docs"

    src.mkdir(parents=True)
    docs.mkdir()

    main = src / "main.py"
    readme = root / "README.md"

    main.write_text("print('hello')\n", encoding="utf-8")
    readme.write_text("# Project\n", encoding="utf-8")

    tree, file_count, directory_count = build_directory_tree(root)

    assert "# Project Tree" in tree
    assert "src/" in tree
    assert "docs/" in tree
    assert "src/main.py" in tree
    assert "README.md" in tree
    assert file_count == 2
    assert directory_count == 2


def test_build_directory_tree_excludes_ignored_directories(tmp_path: Path) -> None:
    root = tmp_path / "project"
    src = root / "src"
    git = root / ".git"
    venv = root / "venv"

    src.mkdir(parents=True)
    git.mkdir()
    venv.mkdir()

    main = src / "main.py"
    git_file = git / "config"
    venv_file = venv / "ignored.py"

    main.write_text("print('main')\n", encoding="utf-8")
    git_file.write_text("git config", encoding="utf-8")
    venv_file.write_text("print('ignored')\n", encoding="utf-8")

    tree, file_count, directory_count = build_directory_tree(root)

    assert "src/" in tree
    assert "src/main.py" in tree
    assert ".git" not in tree
    assert "venv" not in tree
    assert file_count == 1
    assert directory_count == 1