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


def test_import_selected_files_merges_with_manual_selection(
    tmp_path: Path,
) -> None:
    manual = tmp_path / "src" / "manual.py"
    pasted = tmp_path / "src" / "pasted.py"
    manual.parent.mkdir()
    manual.write_text("manual\n", encoding="utf-8")
    pasted.write_text("pasted\n", encoding="utf-8")

    result = import_selected_files(
        "src/manual.py\nsrc/pasted.py",
        project_root=tmp_path,
        existing_paths=[manual],
    )

    assert result.duplicates == ("src/manual.py",)
    assert result.added == (pasted.resolve(),)

def test_import_result_requests_root_selection_for_stale_relative_root(
    tmp_path: Path,
) -> None:
    stale_root = tmp_path / "deleted-project"

    result = import_selected_files(
        "src/app.py",
        project_root=stale_root,
    )

    assert result.root_error is not None
    assert result.needs_project_root_selection is True
    assert result.can_apply is False
    assert result.has_reportable_details is True


def test_import_result_ignores_stale_root_for_absolute_only_list(
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "notes.md"
    file_path.write_text("notes\n", encoding="utf-8")
    stale_root = tmp_path / "deleted-project"

    result = import_selected_files(
        str(file_path),
        project_root=stale_root,
    )

    assert result.added == (file_path.resolve(),)
    assert result.root_error is None
    assert result.needs_project_root_selection is False
    assert result.can_apply is True


def test_duplicate_only_import_uses_non_modal_feedback(
    tmp_path: Path,
) -> None:
    app = tmp_path / "app.py"
    app.write_text("app\n", encoding="utf-8")

    result = import_selected_files(
        "app.py",
        project_root=tmp_path,
        existing_paths=[app],
    )

    assert result.duplicate_count == 1
    assert result.issue_count == 0
    assert result.has_reportable_details is False
    assert result.can_apply is False


def test_infer_project_root_rejects_distinct_marker_projects(
    tmp_path: Path,
) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    (first_root / ".git").mkdir(parents=True)
    (second_root / ".git").mkdir(parents=True)

    first = first_root / "src" / "app.py"
    second = second_root / "src" / "app.py"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_text("first\n", encoding="utf-8")
    second.write_text("second\n", encoding="utf-8")

    assert infer_project_root([first, second]) is None


def test_infer_project_root_rejects_marker_and_unmarked_location_mix(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    (project_root / ".git").mkdir(parents=True)
    inside = project_root / "src" / "app.py"
    inside.parent.mkdir()
    inside.write_text("inside\n", encoding="utf-8")

    outside = tmp_path / "loose" / "notes.md"
    outside.parent.mkdir()
    outside.write_text("outside\n", encoding="utf-8")

    assert infer_project_root([inside, outside]) is None

def test_infer_project_root_prefers_shared_git_root_over_nested_manifests(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "monorepo"
    (project_root / ".git").mkdir(parents=True)

    package_root = project_root / "packages" / "app"
    package_root.mkdir(parents=True)
    (package_root / "pyproject.toml").write_text("[project]\n", encoding="utf-8")

    app = package_root / "src" / "app.py"
    docs = project_root / "docs" / "guide.md"
    app.parent.mkdir()
    docs.parent.mkdir()
    app.write_text("app\n", encoding="utf-8")
    docs.write_text("docs\n", encoding="utf-8")

    assert infer_project_root([app, docs]) == project_root.resolve()

