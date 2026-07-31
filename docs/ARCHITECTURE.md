# XCC Architecture

## Product boundary

XCC Context Collector is a Windows-first PySide6 desktop application. The supported release path is:

```text
gui.py -> xcc.gui:run_gui -> xcc.pipeline
```

After installation, the supported GUI entry point is:

```text
xcc-context-collector
```

The package uses the standard `src` layout and is imported as `xcc`. Root launchers insert `src` into `sys.path` only for direct execution from a repository checkout.

The legacy Tkinter picker and standalone `keyboard` listener remain unsupported development-compatibility tools. New product behavior must target the PySide6 path.

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
├── path_list_parser.py
│   └── ordered extraction of path-like lines from plain text and Markdown
├── selected_files_importer.py / selected_files_review.py
│   └── project-root resolution, validation, deduplication, and review models
├── pipeline.py
│   └── GUI-independent collection orchestration
├── qt_worker.py
│   └── QThread bridge, progress signals, and cooperative cancellation
├── clipboard.py
│   └── clipboard write boundary
├── settings.py
│   └── local configuration loading, validation, persistence, and recovery
├── autostart.py / native_hotkey.py
│   └── Windows Startup shortcut and native restore-hotkey integration
├── resources.py
│   └── source and PyInstaller runtime asset resolution
├── ui_theme.py
│   └── palette, geometry tokens, application QSS, and tray-menu QSS
├── ui_components.py
│   └── reusable headers, icons, capsules, metric rows, buttons, and helper text
├── ui_shell.py / ui_sidebar.py
│   └── runtime-state vocabulary, footer policy, hotkey display, and keyboard-accessible navigation
├── ui_collect.py / ui_metrics.py
│   └── mode-specific presentation policy and Last Run formatting/state policy
├── ui_responsive.py
│   └── content-viewport breakpoints and height-aware Collect geometry
├── gui.py
│   └── supported desktop shell, dialogs, tray, pages, settings, history, and single-instance behavior
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

`pipeline.execute_collection()` has no GUI or clipboard dependency. Collection behavior is therefore testable independently of Qt widgets.

## Selected Files import boundary

Pasted path import occurs before collection and does not bypass the normal pipeline:

```text
Clipboard text
      ↓
path_list_parser.parse_path_list()
      ↓
selected_files_importer.import_selected_files()
      ↓
visible project-root resolution when relative paths require it
      ↓
canonical validation, supported-type checks, and Windows-aware deduplication
      ↓
transactional merge into XccMainWindow.selected_paths
      ↓
optional Selected Files Review
      ↓
normal CollectionRequest and execute_collection() flow
```

The parser and importer do not execute pasted content, expand environment variables, interpret globs, or search arbitrary filesystem locations. Relative paths are resolved only under the explicit project root. Canonically resolved paths that escape that root are rejected. Absolute files may remain external selections and produce `Mixed locations` when no reliable common root exists.

Selected Files Review operates on a temporary ordered copy. `Cancel` leaves the active selection unchanged; `Apply Changes` commits the reviewed list.

## Presentation architecture

The final v1.3.0 interface separates product policy from widget orchestration:

- `ui_theme.py` owns shared visual tokens and selectors;
- `ui_components.py` owns reusable presentation primitives;
- `ui_shell.py` owns the short runtime-state vocabulary and footer guidance policy;
- `ui_sidebar.py` owns navigation buttons, exclusive selection, and Up/Down keyboard movement;
- `ui_collect.py` owns mode labels, action labels, helper text, and Selected Files summaries;
- `ui_metrics.py` owns number formatting and semantic metric states;
- `ui_responsive.py` owns responsive width and height policy;
- `gui.py` composes these layers and owns runtime interaction.

The header reports short runtime state such as Ready, Working, Cancelling, Copied, Warnings, Failed, or Cancelled. The footer reports detailed progress, event results, and next-action guidance. These roles must remain distinct.

## Responsive-layout boundary

Width policy is derived from the Collect content viewport rather than the complete window width. Height density is calculated independently. The same widgets are moved between layouts; they are not duplicated and signal connections are not recreated.

The supported range begins at `920×620` and extends through maximized 2K displays. Horizontal scrolling is disabled. Vertical scrolling is enabled only when the natural content height exceeds the viewport.

## Accessibility boundary

Primary actions, status surfaces, metrics, dialogs, Source review, and navigation expose meaningful accessible names. Standard radio and checkbox behavior is preserved. Selected Files Review retains ExtendedSelection and `Delete`. Focus, hover, pressed, and disabled states are part of the frozen UI contract.

The stored hotkey remains `ctrl+alt+x` for native registration, while product surfaces display `Ctrl+Alt+X`.

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

Cancellation is cooperative. Scanner, collector, safety, and tree operations check the cancellation state between units of work. A cancelled task emits no partial clipboard output.

## Source-fidelity contract

Collected source payloads and Git diff data are source-like input. They must not be compacted, stripped, normalized, or rewritten.

The formatter may add framing:

```text
===== file: relative/path.py =====

<verbatim file payload>
```

Compact mode applies only to XCC-generated headings, metadata, summaries, and tree text. Structure-aware budgeting includes complete source and diff sections or omits them with an explicit budget summary.

## Security and privacy boundary

XCC is local-first and has no upload path. Sensitive-context detection is heuristic and warning-only. Warning summaries contain paths, line numbers, and categories, not detected secret values. Disabling the modal safety confirmation does not disable detection, counters, outcomes, or warning summaries.

Runtime History stores metadata only. It does not store collected source, Git diff payloads, detected values, or failure-message bodies.

## Packaging and release boundary

The portable release is built with PyInstaller and contains one application root with the executable, `_internal`, packaged assets, and `VERSION.txt`. The release process generates a ZIP, a SHA-256 checksum, and a machine-readable automated-gate report.

Publication is blocked until source tests, clean-install validation, packaged smoke, archive validation, matching Windows 10/11 evidence, repository synchronization, and final readiness all pass for the same archive.
