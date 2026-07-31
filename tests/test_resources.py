from __future__ import annotations

import sys
from pathlib import Path

from xcc import resources


def test_source_application_root_uses_repository_root(monkeypatch) -> None:
    monkeypatch.delattr(sys, "_MEIPASS", raising=False)

    expected = Path(resources.__file__).resolve().parents[2]

    assert resources.application_root() == expected
    assert resources.resource_path("assets", "xcc_app.ico") == (
        expected / "assets" / "xcc_app.ico"
    )


def test_frozen_application_root_uses_pyinstaller_runtime_directory(
    monkeypatch,
    tmp_path: Path,
) -> None:
    runtime_root = tmp_path / "_internal"
    monkeypatch.setattr(sys, "_MEIPASS", str(runtime_root), raising=False)

    assert resources.application_root() == runtime_root
    assert resources.resource_path("assets", "xcc_tray.png") == (
        runtime_root / "assets" / "xcc_tray.png"
    )


def test_gui_uses_separate_window_embedded_and_tray_assets() -> None:
    gui_source = (
        Path(__file__).resolve().parents[1] / "src" / "xcc" / "gui.py"
    ).read_text(encoding="utf-8")

    assert 'APP_ICON_PATH = resource_path("assets", "xcc_app.ico")' in gui_source
    assert 'APP_IMAGE_PATH = resource_path("assets", "xcc_app.png")' in gui_source
    assert 'TRAY_ICON_PATH = resource_path("assets", "xcc_tray.ico")' in gui_source
    assert 'TRAY_IMAGE_PATH = resource_path("assets", "xcc_tray.png")' in gui_source
    assert 'UI_SETUP_ICON_PATH = resource_path("assets", "ui-setup.svg")' in gui_source
    assert 'UI_LAST_RUN_ICON_PATH = resource_path("assets", "ui-last-run.svg")' in gui_source
    assert 'UI_COLLECT_COPY_ICON_PATH = resource_path("assets", "ui-collect-copy.svg")' in gui_source
    assert 'WINDOW_MINIMIZE_ICON_PATH = resource_path("assets", "window-minimize.svg")' in gui_source
    assert 'WINDOW_MAXIMIZE_ICON_PATH = resource_path("assets", "window-maximize.svg")' in gui_source
    assert 'WINDOW_RESTORE_ICON_PATH = resource_path("assets", "window-restore.svg")' in gui_source
    assert 'WINDOW_CLOSE_ICON_PATH = resource_path("assets", "window-close.svg")' in gui_source
    assert "app.setWindowIcon" in gui_source
