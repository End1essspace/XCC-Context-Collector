from __future__ import annotations

from src.xcc.autostart import APP_SHORTCUT_NAME, shortcut_path, startup_folder


def test_startup_folder_points_to_windows_startup() -> None:
    path = startup_folder()

    assert "Startup" in str(path)
    assert "Programs" in str(path)


def test_shortcut_path_uses_expected_name() -> None:
    path = shortcut_path()

    assert path.name == APP_SHORTCUT_NAME
    assert path.parent == startup_folder()