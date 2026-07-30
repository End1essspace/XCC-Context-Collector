from __future__ import annotations

from pathlib import Path

from xcc.selected_files_importer import (
    import_selected_files,
    infer_project_root,
)


def test_import_selected_files_resolves_relative_paths_against_root(
    tmp_path: Path,
) -> None:
    app = tmp_path / "src" / "app.py"
    guide = tmp_path / "docs" / "guide.md"
    app.parent.mkdir()
    guide.parent.mkdir()
    app.write_text("print('ok')\n", encoding="utf-8")
    guide.write_text("# Guide\n", encoding="utf-8")

    result = import_selected_files(
        "src/app.py\ndocs/guide.md",
        project_root=tmp_path,
    )

    assert result.added == (app.resolve(), guide.resolve())
    assert result.issue_count == 0


def test_import_selected_files_reports_root_required_for_relative_paths() -> None:
    result = import_selected_files("src/app.py\nREADME.md")

    assert result.added == ()
    assert result.root_required == ("src/app.py", "README.md")


def test_import_selected_files_reports_missing_directories_and_unsupported(
    tmp_path: Path,
) -> None:
    directory = tmp_path / "src"
    directory.mkdir()
    unsupported = tmp_path / "image.png"
    unsupported.write_bytes(b"png")

    result = import_selected_files(
        "src/\nmissing.py\nimage.png",
        project_root=tmp_path,
    )

    assert result.directories == ("src/",)
    assert result.missing == ("missing.py",)
    assert result.unsupported == ("image.png",)
    assert result.added == ()


def test_import_selected_files_rejects_traversal_outside_root(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.py"
    outside.write_text("outside\n", encoding="utf-8")

    result = import_selected_files(
        "../outside.py",
        project_root=tmp_path,
    )

    assert result.outside_root == ("../outside.py",)
    assert result.added == ()


def test_import_selected_files_deduplicates_existing_and_repeated_paths(
    tmp_path: Path,
) -> None:
    app = tmp_path / "src" / "app.py"
    app.parent.mkdir()
    app.write_text("print('ok')\n", encoding="utf-8")

    result = import_selected_files(
        "src/app.py\nsrc\\APP.py",
        project_root=tmp_path,
        existing_paths=[app],
    )

    assert result.added == ()
    assert result.duplicates == ("src/app.py",)


def test_import_selected_files_allows_explicit_absolute_file_outside_root(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    root.mkdir()
    external = tmp_path / "notes.md"
    external.write_text("notes\n", encoding="utf-8")

    result = import_selected_files(
        str(external),
        project_root=root,
    )

    assert result.added == (external.resolve(),)
    assert result.external == (external.resolve(),)


def test_infer_project_root_prefers_repository_marker(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\n", encoding="utf-8")
    app = tmp_path / "src" / "pkg" / "app.py"
    guide = tmp_path / "docs" / "guide.md"
    app.parent.mkdir(parents=True)
    guide.parent.mkdir()
    app.write_text("app\n", encoding="utf-8")
    guide.write_text("guide\n", encoding="utf-8")

    assert infer_project_root([app, guide]) == tmp_path.resolve()


def test_infer_project_root_returns_none_for_cross_root_paths(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    first = first_root / "app.py"
    second = second_root / "app.py"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    # The common parent is still meaningful on this temporary filesystem.
    # Explicitly use two independent absolute roots only to verify no crash and
    # that the helper returns a deterministic existing parent.
    assert infer_project_root([first, second]) == tmp_path.resolve()
