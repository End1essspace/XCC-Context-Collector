from __future__ import annotations

from pathlib import Path

from xcc.selected_files_review import (
    build_selected_file_review,
    remove_selected_file_indices,
    review_project_root,
)


def test_build_selected_file_review_uses_relative_paths(tmp_path: Path) -> None:
    app = tmp_path / "src" / "app.py"
    guide = tmp_path / "docs" / "guide.md"
    app.parent.mkdir()
    guide.parent.mkdir()
    app.write_text("app\n", encoding="utf-8")
    guide.write_text("guide\n", encoding="utf-8")

    items = build_selected_file_review(
        [app, guide],
        project_root=tmp_path,
    )

    assert [item.display_path for item in items] == [
        "src/app.py",
        "docs/guide.md",
    ]
    assert not any(item.is_external for item in items)


def test_build_selected_file_review_falls_back_for_mixed_locations(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    inside = root / "app.py"
    outside = tmp_path / "notes.md"
    inside.write_text("app\n", encoding="utf-8")
    outside.write_text("notes\n", encoding="utf-8")

    items = build_selected_file_review(
        [inside, outside],
        project_root=root,
    )

    assert len(items) == 2
    assert len({item.display_path for item in items}) == 2
    assert not any(item.is_external for item in items)


def test_remove_selected_file_indices_preserves_remaining_order(
    tmp_path: Path,
) -> None:
    paths = [tmp_path / "a.py", tmp_path / "b.py", tmp_path / "c.py"]

    remaining = remove_selected_file_indices(paths, [2, 0, 2, 99, -1])

    assert remaining == (paths[1],)


def test_review_project_root_keeps_preferred_root_when_all_files_are_inside(
    tmp_path: Path,
) -> None:
    first = tmp_path / "src" / "a.py"
    second = tmp_path / "docs" / "b.md"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_text("a\n", encoding="utf-8")
    second.write_text("b\n", encoding="utf-8")

    assert review_project_root(
        [first, second],
        preferred_root=tmp_path,
    ) == tmp_path.resolve()


def test_review_project_root_returns_none_for_empty_selection(tmp_path: Path) -> None:
    assert review_project_root([], preferred_root=tmp_path) is None
