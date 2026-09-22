
from __future__ import annotations

from threading import Event
from time import perf_counter

from PySide6.QtCore import QObject, Signal, Slot

from .cancellation import AttachmentBundleCancelled, CollectionCancelled
from .pipeline import CollectionRequest, execute_collection
from .attachment_bundle import create_attachment_bundle


class CollectionWorker(QObject):
    progress = Signal(str, int, int)
    completed = Signal(object)
    failed = Signal(str, float)
    cancelled = Signal(float)

    def __init__(self, request: CollectionRequest) -> None:
        super().__init__()
        self.request = request
        self._cancel_event = Event()

    def request_cancel(self) -> None:
        """Thread-safe cancellation request callable from the GUI thread."""
        self._cancel_event.set()

    @Slot()
    def run(self) -> None:
        started_at = perf_counter()

        try:
            result = execute_collection(
                self.request,
                progress_callback=self.progress.emit,
                cancel_check=self._cancel_event.is_set,
            )
        except CollectionCancelled:
            self.cancelled.emit(max(0.0, perf_counter() - started_at))
        except Exception as exc:
            self.failed.emit(
                str(exc),
                max(0.0, perf_counter() - started_at),
            )
        else:
            self.completed.emit(result)


class AttachmentBundleWorker(QObject):
    progress = Signal(str, int, int, int, int)
    completed = Signal(object)
    failed = Signal(str, float)
    cancelled = Signal(float)

    def __init__(
        self,
        paths,
        *,
        project_root=None,
        directory=None,
    ) -> None:
        super().__init__()
        self.paths = tuple(paths)
        self.project_root = project_root
        self.directory = directory
        self._cancel_event = Event()

    def request_cancel(self) -> None:
        self._cancel_event.set()

    @Slot()
    def run(self) -> None:
        started_at = perf_counter()
        try:
            result = create_attachment_bundle(
                self.paths,
                project_root=self.project_root,
                directory=self.directory,
                progress_callback=self.progress.emit,
                cancel_check=self._cancel_event.is_set,
            )
        except AttachmentBundleCancelled:
            self.cancelled.emit(max(0.0, perf_counter() - started_at))
        except Exception as exc:
            self.failed.emit(str(exc), max(0.0, perf_counter() - started_at))
        else:
            self.completed.emit(result)
