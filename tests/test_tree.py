from pathlib import Path

from src.xcc.tree import build_project_tree


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