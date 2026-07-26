from __future__ import annotations

from threading import Event
from time import perf_counter

from PySide6.QtCore import QObject, Signal, Slot

from .cancellation import CollectionCancelled
from .pipeline import CollectionRequest, execute_collection


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
