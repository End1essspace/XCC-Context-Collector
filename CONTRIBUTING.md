# Contributing to XCC Context Collector

XCC is a Windows-first Python desktop utility. Contributions should preserve source fidelity, deterministic output, safe context handling, and a responsive GUI.

## Supported development environment

- Windows 10 or Windows 11 x64
- CPython 3.13.x
- PowerShell
- Git

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,build]"
```

## Required local gate

```powershell
python -m compileall -q src tests scripts gui.py run.py hotkey.py
python scripts/check_version_consistency.py
python -m pytest -q
```

Changes to packaging or release automation must also run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
powershell -ExecutionPolicy Bypass -File scripts\smoke_packaged_app.ps1
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1
```

## Workspace cleanup

Generated caches, packaging metadata, PyInstaller intermediates, and local build outputs can be removed with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1
```

The default cleanup preserves `.venv`, `artifacts`, and the legacy local `release` archive. Remove them explicitly only when appropriate:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1 `
    -IncludeArtifacts `
    -IncludeLegacyReleaseArchives `
    -IncludeVirtualEnvironment
```

Do not replace this with `git clean -xfd`: that command can delete release-candidate evidence and local environments without distinguishing generated data from intentional local files.

## Pull requests

Keep each pull request focused on one roadmap milestone or defect. Include regression tests for behavior changes. Do not commit:

- collected project contexts;
- credentials, tokens, keys, or private paths;
- `dist`, `build`, `release`, `*.egg-info`, cache folders, or generated executables;
- local `.xcc` configuration.

Use the pull request template and report the exact validation commands executed.

## Architecture boundaries

The supported product path is:

```text
gui.py -> xcc.gui -> xcc.pipeline -> collection modules
```

The Tkinter picker and `keyboard` listener are unsupported compatibility tools. New product features must target the PySide6 GUI and native hotkey path.

Read `docs/ARCHITECTURE.md`, `docs/roadmap.md`, and `docs/BUG_REPORTING.md` before making cross-cutting changes.