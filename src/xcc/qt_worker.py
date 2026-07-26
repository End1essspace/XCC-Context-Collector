from __future__ import annotations

from threading import Event

from PySide6.QtCore import QObject, Signal, Slot

from .cancellation import CollectionCancelled
from .pipeline import CollectionRequest, execute_collection


class CollectionWorker(QObject):
    progress = Signal(str, int, int)
    completed = Signal(object)
    failed = Signal(str)
    cancelled = Signal()

    def __init__(self, request: CollectionRequest) -> None:
        super().__init__()
        self.request = request
        self._cancel_event = Event()

    def request_cancel(self) -> None:
        """Thread-safe cancellation request callable from the GUI thread."""
        self._cancel_event.set()

    @Slot()
    def run(self) -> None:
        try:
            result = execute_collection(
                self.request,
                progress_callback=self.progress.emit,
                cancel_check=self._cancel_event.is_set,
            )
        except CollectionCancelled:
            self.cancelled.emit()
        except Exception as exc:
            self.failed.emit(str(exc))
        else:
            self.completed.emit(result)
