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

The parser and importer do not execute pasted content, expand environment variables, interpret globs, or search arbitrary filesystem locations. Relative paths are resolved only under the explicit project root. Canonically resolved paths that escape that root are rejected. Absolute files may be accepted as external selections and cause the UI to report mixed locations when no single reliable root exists.

Selected Files Review operates on a temporary ordered copy. `Cancel` leaves the active selection unchanged; `Apply Changes` commits the reviewed list. This keeps UI state mutation transactional and independently testable through the helper models.

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
