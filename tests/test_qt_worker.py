from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QCoreApplication

from src.xcc.pipeline import CollectionRequest
from src.xcc.qt_worker import CollectionWorker


def _request(tmp_path: Path) -> CollectionRequest:
    return CollectionRequest(
        mode="folder",
        mode_name="Full Folder",
        selected_paths=(),
        project_root=tmp_path,
        compact=True,
        max_output_chars=100_000,
    )


def test_qt_worker_emits_cancelled_with_duration_for_pre_cancelled_job(
    tmp_path: Path,
) -> None:
    app = QCoreApplication.instance() or QCoreApplication([])
    worker = CollectionWorker(_request(tmp_path))
    emitted: list[float] = []
    worker.cancelled.connect(lambda duration: emitted.append(duration))

    worker.request_cancel()
    worker.run()

    assert app is not None
    assert len(emitted) == 1
    assert emitted[0] >= 0


def test_qt_worker_emits_failure_with_duration(tmp_path: Path) -> None:
    app = QCoreApplication.instance() or QCoreApplication([])
    missing = tmp_path / "missing"
    worker = CollectionWorker(_request(missing))
    emitted: list[tuple[str, float]] = []
    worker.failed.connect(
        lambda message, duration: emitted.append((message, duration))
    )

    worker.run()

    assert app is not None
    assert len(emitted) == 1
    message, duration = emitted[0]
    assert "Project folder not found" in message
    assert duration >= 0
