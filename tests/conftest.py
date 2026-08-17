from __future__ import annotations

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
