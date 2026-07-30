from __future__ import annotations

from pathlib import Path

from xcc.pipeline import CollectionRequest, execute_collection
from xcc.selected_files_importer import import_selected_files
from xcc.selected_files_review import (
    build_selected_file_review,
    remove_selected_file_indices,
    review_project_root,
)


def test_selected_files_workflow_from_ai_list_to_collection(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "project"
    (project_root / ".git").mkdir(parents=True)

    manual = project_root / "src" / "manual.py"
    pasted = project_root / "src" / "pasted.py"
    guide = project_root / "docs" / "guide.md"

    manual.parent.mkdir()
    guide.parent.mkdir()
    manual.write_text("MANUAL = True\n", encoding="utf-8")
    pasted.write_text("PASTED = True\n", encoding="utf-8")
    guide.write_text("# Guide\n", encoding="utf-8")

    ai_response = """
    Пришли эти файлы из проекта:

    ```text
    src/manual.py
    src/pasted.py
    docs/guide.md
    ```
    """

    imported = import_selected_files(
        ai_response,
        project_root=project_root,
        existing_paths=[manual],
    )

    assert imported.added == (pasted.resolve(), guide.resolve())
    assert imported.duplicates == ("src/manual.py",)
    assert imported.issue_count == 0

    selected_paths = [manual, *imported.added]
    review_items = build_selected_file_review(
        selected_paths,
        project_root=project_root,
    )
    assert [item.display_path for item in review_items] == [
        "src/manual.py",
        "src/pasted.py",
        "docs/guide.md",
    ]

    reviewed_paths = remove_selected_file_indices(selected_paths, [0])
    reviewed_root = review_project_root(
        reviewed_paths,
        preferred_root=project_root,
    )

    request = CollectionRequest(
        mode="files",
        mode_name="Selected Files",
        selected_paths=reviewed_paths,
        project_root=reviewed_root,
        compact=True,
        max_output_chars=100_000,
    )
    job = execute_collection(request)

    assert job.source == "2 selected files"
    assert "===== file: src/pasted.py =====" in job.result.text
    assert "===== file: docs/guide.md =====" in job.result.text
    assert "===== file: src/manual.py =====" not in job.result.text
    assert "# Project Tree" not in job.result.text
