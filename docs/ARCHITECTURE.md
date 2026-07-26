# XCC Architecture

## Supported Product Boundary

XCC Context Collector is a Windows-first PySide6 desktop application. The supported release entry point is:

```text
gui.py -> xcc.gui:run_gui
```

The installed GUI command is:

```text
xcc-context-collector
```

The application package lives under `src/xcc` and is imported as `xcc`. Root launchers add `src` to `sys.path` only so the repository can still be run directly before installation.

## Package Layers

```text
root launchers
    gui.py
        -> supported PySide6 desktop application
    run.py
        -> unsupported legacy Tkinter picker
    hotkey.py
        -> unsupported legacy keyboard listener

src/xcc
    config.py
        -> application constants and supported context-file rules
    models.py
        -> typed collection results, outcomes, statistics, and history records
    scanner.py / collector.py / git_utils.py / tree.py
        -> source discovery and acquisition
    ignore.py / safety.py
        -> project exclusions and warning-only context safety checks
    formatter.py / optimizer.py / budget.py
        -> fidelity-preserving output construction and structure-aware budgeting
    pipeline.py
        -> GUI-independent collection orchestration
    qt_worker.py
        -> QThread bridge, progress signals, and cancellation
    clipboard.py
        -> GUI-thread clipboard boundary
    settings.py / autostart.py / native_hotkey.py
        -> Windows runtime integration
    gui.py
        -> supported desktop product shell
    main.py / picker.py / hotkey.py
        -> unsupported legacy development compatibility tools
```

## Dependency Boundaries

`pyproject.toml` is the canonical dependency manifest.

| Group | Purpose | Packages |
|---|---|---|
| Runtime | Supported GUI execution | `PySide6`, `pyperclip` |
| Dev | Tests and coverage | `pytest`, `pytest-cov` |
| Build | Windows packaging | `pyinstaller` |
| Legacy | Unsupported standalone hotkey tool | `keyboard` |

The supported application must import and run without the `legacy` group. `keyboard` is loaded lazily only when the unsupported standalone listener starts.

## Version Contract

`src/xcc/__init__.py` is the single source of the application version:

```python
__version__ = "1.1.2"
```

`pyproject.toml` reads this value through setuptools dynamic metadata. The PyInstaller build script reads the same attribute to:

- generate Windows executable version resources;
- display the build version;
- write `VERSION.txt` beside the packaged executable.

No release process should hard-code the version in the build script.

## Supported Python Baseline

The v1.2.0 source and release-build baseline is CPython 3.13.x on Windows 10/11 x64. This deliberately narrow range matches the tested release environment. Additional Python versions must not be claimed until they are added to the CI matrix and release gate.

## Legacy Decision

The Tkinter picker and `keyboard` listener are retained for v1.2.0 to avoid deleting old development workflows during a reliability release. They are explicitly unsupported:

- they are not installed as console or GUI entry points;
- they are not used by the packaged application;
- the `keyboard` dependency is optional;
- new product features must target the PySide6 GUI and native hotkey path only.

Removal can be reconsidered in a later breaking cleanup after repository users have had a deprecation window.

## Validation Gates

M8 provides two distinct validation paths:

```text
scripts/validate_clean_install.ps1
    -> new Python 3.13 virtual environment
    -> editable install with dev + build groups
    -> compileall
    -> full pytest suite
    -> installed metadata/version consistency
    -> GUI module import
    -> confirms keyboard was not installed

scripts/build_release.ps1
    -> canonical version read
    -> Windows version resource generation
    -> clean PyInstaller build
    -> VERSION.txt emission
```

Packaged executable startup and release archive validation remain part of M9 and M10.
