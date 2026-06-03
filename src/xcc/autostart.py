from __future__ import annotations

import sys
from pathlib import Path

APP_SHORTCUT_NAME = "XCC Context Collector.lnk"


def startup_folder() -> Path:
    return Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def shortcut_path() -> Path:
    return startup_folder() / APP_SHORTCUT_NAME


def is_autostart_enabled() -> bool:
    return shortcut_path().exists()


def set_autostart_enabled(enabled: bool) -> None:
    path = shortcut_path()

    if enabled:
        create_autostart_shortcut(path)
        return

    if path.exists():
        path.unlink()


def create_autostart_shortcut(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    project_root = Path(__file__).resolve().parents[2]
    gui_launcher = project_root / "gui.py"
    python_exe = Path(sys.executable)

    target = str(python_exe)
    arguments = str(gui_launcher)
    working_dir = str(project_root)

    ps_script = f"""
$WScriptShell = New-Object -ComObject WScript.Shell
$Shortcut = $WScriptShell.CreateShortcut("{_escape_powershell_string(str(path))}")
$Shortcut.TargetPath = "{_escape_powershell_string(target)}"
$Shortcut.Arguments = "{_escape_powershell_string(arguments)}"
$Shortcut.WorkingDirectory = "{_escape_powershell_string(working_dir)}"
$Shortcut.Save()
"""

    import subprocess

    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            ps_script,
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to create autostart shortcut.")


def _escape_powershell_string(value: str) -> str:
    return value.replace("`", "``").replace('"', '`"')