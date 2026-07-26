from __future__ import annotations

from pathlib import Path

import pytest

from src.xcc.cancellation import CollectionCancelled
from src.xcc.pipeline import CollectionRequest, execute_collection


def _request(
    *,
    mode: str,
    project_root: Path | None = None,
    selected_paths: tuple[Path, ...] = (),
) -> CollectionRequest:
    names = {
        "files": "Selected Files",
        "folder": "Full Folder",
        "git": "Git Changed Files",
        "tree": "Project Tree",
    }
    return CollectionRequest(
        mode=mode,
        mode_name=names[mode],
        selected_paths=selected_paths,
        project_root=project_root,
        compact=True,
        max_output_chars=100_000,
    )


def test_folder_pipeline_reports_phases_and_complete_read_progress(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    first = root / "src" / "first.py"
    second = root / "src" / "second.py"
    first.parent.mkdir(parents=True)
    first.write_text("FIRST = True\n", encoding="utf-8")
    second.write_text("SECOND = True\n", encoding="utf-8")

    events: list[tuple[str, int, int]] = []
    job = execute_collection(
        _request(mode="folder", project_root=root),
        progress_callback=lambda phase, current, total: events.append(
            (phase, current, total)
        ),
    )

    phases = [phase for phase, _, _ in events]
    assert phases[0] == "Preparing"
    assert "Scanning" in phases
    assert "Reading files" in phases
    assert "Inspecting context" in phases
    assert "Formatting" in phases
    assert "Applying budget" in phases
    assert ("Reading files", 2, 2) in events
    assert "===== file: src/first.py =====" in job.result.text
    assert "===== file: src/second.py =====" in job.result.text
    assert job.source == str(root)


def test_selected_files_pipeline_preserves_explicit_source_label(
    tmp_path: Path,
) -> None:
    first = tmp_path / "one.py"
    second = tmp_path / "two.py"
    first.write_text("ONE = 1\n", encoding="utf-8")
    second.write_text("TWO = 2\n", encoding="utf-8")

    job = execute_collection(
        _request(
            mode="files",
            selected_paths=(first, second),
        )
    )

    assert job.source == "2 selected files"
    assert job.result.stats.files == 2


def test_pipeline_cancels_cooperatively_between_files(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()

    for index in range(6):
        (root / f"file_{index}.py").write_text(
            f"VALUE = {index}\n",
            encoding="utf-8",
        )

    cancel_requested = False

    def on_progress(phase: str, current: int, total: int) -> None:
        nonlocal cancel_requested
        if phase == "Reading files" and current == 2 and total == 6:
            cancel_requested = True

    with pytest.raises(CollectionCancelled):
        execute_collection(
            _request(mode="folder", project_root=root),
            progress_callback=on_progress,
            cancel_check=lambda: cancel_requested,
        )


def test_pipeline_honors_cancellation_before_work_starts(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()

    with pytest.raises(CollectionCancelled):
        execute_collection(
            _request(mode="folder", project_root=root),
            cancel_check=lambda: True,
        )
