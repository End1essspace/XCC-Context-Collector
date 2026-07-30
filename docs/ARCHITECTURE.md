# XCC Architecture

## Product boundary

XCC Context Collector is a Windows-first PySide6 desktop application. The supported release path is:

```text
gui.py -> xcc.gui:run_gui
```

After installation, the supported GUI entry point is:

```text
xcc-context-collector
```

The package uses the standard `src` layout and is imported as `xcc`. Root launchers insert `src` into `sys.path` only to support direct execution from a repository checkout.

## Runtime layers

```text
Root launchers
├── gui.py       supported PySide6 desktop application
├── run.py       unsupported legacy Tkinter picker
└── hotkey.py    unsupported legacy keyboard listener

src/xcc
├── config.py
│   └── application constants, supported files, and built-in exclusions
├── models.py
│   └── typed Git changes, collection results, outcomes, statistics, and history records
├── scanner.py / collector.py / tree.py
│   └── project discovery, file acquisition, and project-tree construction
├── git_utils.py
│   └── repository validation, typed status parsing, changed-file selection, and staged/unstaged diff extraction
├── ignore.py / safety.py
│   └── project ignore rules and warning-only sensitive-context detection
├── formatter.py / optimizer.py / budget.py
│   └── fidelity-preserving output construction and structure-aware budgeting
├── pipeline.py
│   └── GUI-independent collection orchestration
├── qt_worker.py
│   └── QThread bridge, progress signals, and cooperative cancellation
├── clipboard.py
│   └── clipboard write boundary
├── settings.py
│   └── local configuration loading, validation, persistence, and recovery
├── autostart.py / native_hotkey.py
│   └── Windows Startup shortcut and native restore hotkey integration
├── resources.py
│   └── source/PyInstaller runtime asset resolution
├── gui.py
│   └── supported desktop shell, tray, navigation, settings, history, and single-instance behavior
└── main.py / picker.py / hotkey.py
    └── unsupported legacy development compatibility tools
```

## Collection data flow

```text
User selects mode and source
          ↓
XccMainWindow builds CollectionRequest
          ↓
CollectionWorker runs execute_collection() in QThread
          ↓
scanner / git_utils / collector / safety
          ↓
formatter + structure-aware budget planner
          ↓
CollectionJobResult with typed CollectionResult
          ↓
GUI thread performs optional safety confirmation
          ↓
GUI thread copies complete output to clipboard
          ↓
Last Run and metadata-only Runtime History update
```

`pipeline.execute_collection()` has no GUI or clipboard dependency. This keeps collection behavior testable independently of Qt widgets.

## Threading boundary

### Worker thread

The worker thread may perform:

- folder and project-tree scanning;
- Git status and diff commands;
- file reads and decoding fallbacks;
- sensitive-context analysis;
- formatting and budget planning;
- progress emission and cancellation checks.

### GUI thread

The GUI thread owns:

- all widget mutation;
- modal dialogs;
- clipboard writes;
- tray and window state;
- run-history rendering;
- final success/failure feedback.

Cancellation is cooperative. The GUI sets a thread-safe event; scanner, collector, safety, and tree operations check it between units of work. A cancelled task emits no partial clipboard output.

## Source-fidelity contract

Collected payloads and Git diff data are source-like input. They must not be passed through structural compaction or arbitrary string trimming.

The formatter may add section framing:

```text
===== file: relative/path.py =====

<exact payload>
```

The payload itself must remain byte-for-character equivalent after decoding. Compact mode is limited to headings, metadata, trees, summaries, and other XCC-generated structure.

## Git contract

Git mode uses:

```text
git status --porcelain=v1 -z --untracked-files=all
git diff --cached
git diff
```

The typed `GitChange` model stores index and worktree status separately. Renames and copies retain original and destination paths. Deleted changes remain represented in status and diff even when no current file exists on disk.

Git command errors raise `GitCommandError`; they must not be converted into an apparently clean repository.

## Ignore and safety contract

Built-in excluded directories are enforced independently of project rules and cannot be re-enabled.

Project rules are loaded in this order:

1. root `.gitignore` when enabled for the mode;
2. root `.xccignore` as the XCC-specific override layer.

The last matching project rule wins. Selected Files mode bypasses project ignore rules because explicit selection is treated as intentional.

Safety detection is warning-only. It can add sanitized `SafetyWarning` records but cannot mutate source payloads. Warning records contain path, category, and optional line number; they do not contain the detected value.

## Budget contract

The configured character budget is a hard output ceiling. The formatter plans complete sections before inclusion and reserves room for a deterministic budget summary.

v1.2.0 does not partially include ordinary source-file payloads. When a section cannot fit, it is omitted and reported. Project Tree mode may include a complete-line prefix of the generated tree and marks the tree as partial.

## Result model

`CollectionResult` contains:

- rendered text;
- `CollectionStats`;
- recoverable errors;
- safety warnings;
- omitted display paths;
- truncation state;
- a derived `CollectionOutcome`.

Outcomes are:

```text
SUCCESS
SUCCESS_WITH_WARNINGS
CANCELLED
FAILED
```

`CollectionRunRecord` is a metadata-only snapshot for UI history. It intentionally excludes file contents, Git diffs, secret values, and failure-message bodies.

## Settings and local state

Settings are stored at:

```text
%USERPROFILE%\.xcc\config.json
```

Invalid configuration is recovered to validated defaults. The application persists mode, character budget, compact mode, last folder source, tray/startup behavior, and Safety confirmation.

Runtime history is not persisted in v1.2.0.

## Windows integration

### Single instance

A `QLockFile` prevents concurrent instances. A `QLocalServer`/`QLocalSocket` channel asks the existing instance to restore when a second launch occurs.

### Native hotkey

`NativeHotkeyManager` registers `Ctrl+Alt+X` through `RegisterHotKey`. Failure is non-fatal and is surfaced in Settings and status feedback.

### Tray and autostart

`QSystemTrayIcon` owns Show, Hide, and Quit actions. Autostart is implemented as a Windows Startup-folder shortcut and can be added or removed from Settings.

## Runtime resources

`resources.application_root()` resolves assets from:

- the repository root in source mode;
- `sys._MEIPASS` in PyInstaller mode.

Required packaged resources include application, header/About, tray, and Lucide navigation artwork. Release smoke checks verify their presence under `_internal\assets`.

## Dependency boundaries

`pyproject.toml` is canonical.

| Group | Purpose | Packages |
|---|---|---|
| Runtime | Supported GUI execution | `PySide6`, `pyperclip` |
| Dev | Tests and coverage | `pytest`, `pytest-cov` |
| Build | Windows packaging | `pyinstaller` |
| Legacy | Unsupported standalone hotkey tool | `keyboard` |

The supported application must import and run without the `legacy` group. `keyboard` is loaded lazily only by the unsupported listener.

## Version contract

`src/xcc/__init__.py` is the single source of version truth:

```python
__version__ = "1.2.0"
```

The same value drives:

- package metadata through setuptools dynamic versioning;
- README and release-document validation;
- Windows executable version resources;
- packaged `VERSION.txt`;
- archive naming and release-readiness checks.

Release automation must not hard-code a conflicting version.

## Supported baseline

The v1.2.0 baseline is:

- Windows 10/11 x64;
- CPython 3.13.x for source and release builds;
- packaged PyInstaller application for end users.

Additional Python versions or operating systems must not be claimed until added to CI and the release gate.

## Validation layers

```text
check_version_consistency.py
    canonical code, metadata, README, changelog, release notes, and LICENSE

validate_clean_install.ps1
    isolated Python 3.13 environment, editable install, compileall, tests, metadata, GUI import

build_release.ps1
    clean PyInstaller build, runtime assets, executable metadata, VERSION.txt

smoke_packaged_app.ps1
    packaged offscreen startup, process-liveness check, deterministic cleanup, asset presence

package_release.ps1 + validate_release_archive.py
    versioned ZIP, checksum, safe paths, required files, canonical packaged version

validate_release_candidate.ps1
    complete automated release-candidate gate and machine-readable report

record_manual_validation.ps1 + validate_release_evidence.py
    clean-host Windows 10/11 evidence for the same archive hash

check_release_readiness.py
    final documents, archive, evidence, clean main, and origin/main synchronization
```

The `v1.2.0` tag is blocked until the final readiness command passes.

## Legacy boundary

The Tkinter picker and `keyboard` listener remain for v1.2.0 only as unsupported compatibility tools:

- they are not installed as product entry points;
- they are not used by the packaged application;
- they do not define the release architecture;
- new features must not depend on them.

Removal can be considered in a later breaking cleanup after a deprecation window.
