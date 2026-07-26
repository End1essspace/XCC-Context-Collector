from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QCoreApplication

from src.xcc.pipeline import CollectionRequest
from src.xcc.qt_worker import CollectionWorker


def test_qt_worker_emits_cancelled_for_pre_cancelled_job(tmp_path: Path) -> None:
    app = QCoreApplication.instance() or QCoreApplication([])
    request = CollectionRequest(
        mode="folder",
        mode_name="Full Folder",
        selected_paths=(),
        project_root=tmp_path,
        compact=True,
        max_output_chars=100_000,
    )
    worker = CollectionWorker(request)
    emitted: list[bool] = []
    worker.cancelled.connect(lambda: emitted.append(True))

    worker.request_cancel()
    worker.run()

    assert app is not None
    assert emitted == [True]
