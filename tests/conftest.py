from __future__ import annotations

import gc
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"

if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))


@pytest.fixture(scope="session", autouse=True)
def _keep_qapplication_alive_for_test_session():
    """Keep one QApplication wrapper alive across all Qt test modules.

    XCC uses a src-layout package, so the existing SOURCE_ROOT bootstrap above
    must remain intact for direct ``python -m pytest`` runs from the repository.

    Several GUI test modules expose their own module-scoped ``qapp`` fixture.
    Keeping a session-long Python reference prevents the process-wide
    QApplication wrapper from being finalized between Qt test modules on
    Windows/PySide6.
    """

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        return None

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    return app


@pytest.fixture(autouse=True)
def _destroy_qt_top_level_widgets_after_test():
    """Fully dispose test-owned Qt windows between tests.

    ``QWidget.close()`` only closes or hides a top-level widget; it does not
    guarantee destruction. Because the test session intentionally keeps one
    QApplication alive, closed XCC windows can otherwise accumulate together
    with timers, event filters, and Python/Qt ownership cycles.

    Hide roots first and drain normal queued callbacks while their C++ objects
    are still alive. Only then schedule destruction and flush DeferredDelete
    events. Do not process general events after native deletion: XCC's window
    lifecycle intentionally schedules zero-delay callbacks, and running those
    after the QWidget has been destroyed creates stale-wrapper teardown races.
    """

    yield

    try:
        from PySide6.QtCore import QCoreApplication, QEvent
        from PySide6.QtWidgets import QApplication
    except ImportError:
        return

    app = QApplication.instance()
    if app is None:
        return

    roots = []
    for widget in list(app.topLevelWidgets()):
        try:
            if widget.parentWidget() is None:
                roots.append(widget)
        except RuntimeError:
            continue

    # Hiding can schedule window-state callbacks. Process them now, while every
    # root widget and its QObject children are still alive.
    for widget in roots:
        try:
            widget.hide()
        except RuntimeError:
            continue

    app.processEvents()

    # Destroy only after the normal queued callbacks above have drained.
    for widget in roots:
        try:
            widget.deleteLater()
        except RuntimeError:
            continue

    QCoreApplication.sendPostedEvents(
        None,
        QEvent.Type.DeferredDelete,
    )

    # Release Python-side ownership cycles after Qt native destruction.
    gc.collect()
