# XCC Architecture

## Product boundary

XCC Context Collector is a Windows-first PySide6 desktop application.

Supported release path:

```text
gui.py -> xcc.gui:run_gui -> xcc.pipeline
```

Installed entry point:

```text
xcc-context-collector
```

The package uses a standard `src` layout and is imported as `xcc`. The root `gui.py` launcher adds `src` to `sys.path` only for direct execution from a repository checkout. There is no secondary Tkinter or third-party-keyboard product path.

## Runtime layers

```text
Root launcher
└── gui.py       supported PySide6 application

src/xcc
├── config.py
│   └── supported files, built-in exclusions, defaults
├── models.py
│   └── typed Git changes, results, outcomes, statistics, history records
├── scanner.py / collector.py / tree.py
│   └── project discovery, file acquisition, project-tree construction
├── git_utils.py
│   └── repository validation, typed status, changed files, staged/unstaged diffs
├── ignore.py / safety.py
│   └── project ignore rules and warning-only sensitive-context detection
├── formatter.py / optimizer.py / budget.py
│   └── fidelity-preserving output and structure-aware character budgeting
├── path_list_parser.py
│   └── ordered extraction of path-like lines from plain text and Markdown
├── selected_files_importer.py / selected_files_review.py
│   └── root resolution, validation, deduplication, display, transactional review
├── pipeline.py
│   └── GUI-independent collection orchestration
├── qt_worker.py
│   └── QThread bridge, progress, cooperative cancellation
├── clipboard.py
│   └── clipboard write boundary
├── settings.py
│   └── local configuration, validation, persistence, recovery
├── autostart.py / native_hotkey.py
│   └── Windows Startup shortcut and native restore hotkey
├── resources.py
│   └── source and PyInstaller asset resolution
├── ui_theme.py
│   └── palette, geometry tokens, application QSS, tray-menu QSS
├── ui_components.py
│   └── reusable headers, icons, capsules, metric rows, buttons, helper text
├── ui_shell.py
│   └── runtime-state vocabulary, footer guidance, hotkey display
├── ui_sidebar.py
│   └── real navigation buttons, exclusive selection, keyboard and wheel navigation
├── ui_collect.py / ui_metrics.py
│   └── mode presentation and Last Run formatting/state policy
├── ui_responsive.py
│   └── viewport breakpoints and height-aware Collect geometry
└── gui.py
    └── shell, pages, dialogs, tray, settings, history, single-instance behavior
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
typed CollectionResult
          ↓
GUI thread performs optional safety confirmation
          ↓
GUI thread copies complete output to clipboard
          ↓
Last Run and metadata-only Runtime History update
```

`pipeline.execute_collection()` has no GUI or clipboard dependency. Collection behavior remains testable without Qt widgets.

## Selected Files import boundary

```text
Clipboard text
      ↓
path_list_parser.parse_path_list()
      ↓
selected_files_importer.import_selected_files()
      ↓
visible project-root resolution when required
      ↓
canonical validation + supported-type checks + Windows-aware deduplication
      ↓
transactional merge into XccMainWindow.selected_paths
      ↓
optional Selected Files Review
      ↓
normal CollectionRequest and execute_collection() flow
```

The parser and importer do not execute pasted content, expand environment variables, interpret globs, or search arbitrary filesystem locations.

Relative paths are resolved only under the explicit project root. Canonically resolved paths that escape the root are rejected. Absolute files may remain external selections and produce `Mixed locations` when no reliable common root exists.

Selected Files Review operates on a temporary ordered copy. **Cancel** leaves the active selection unchanged; **Apply Changes** commits the reviewed list.

## Presentation architecture

The final v1.3.0 interface separates policy from orchestration:

- `ui_theme.py` owns shared visual tokens and selectors;
- `ui_components.py` owns reusable presentation primitives;
- `ui_shell.py` owns short runtime states and footer guidance;
- `ui_sidebar.py` owns navigation interaction;
- `ui_collect.py` owns mode labels, source actions, helper text, and source summaries;
- `ui_metrics.py` owns number formatting and semantic metric states;
- `ui_responsive.py` owns responsive width and height policy;
- `gui.py` composes the layers and owns runtime interaction.

The header reports short runtime state: Ready, Working, Cancelling, Copied, Warnings, Failed, or Cancelled.

The footer reports progress, event results, and next-action guidance. Header and footer roles must remain distinct.

## Sidebar interaction boundary

The sidebar is a navigation surface, not a scrollable content area.

Interaction contract:

- Collect, History, Settings, and About are real `QPushButton` actions;
- selection is exclusive;
- Up/Down keyboard navigation includes all four pages;
- the complete visual sidebar accepts wheel input, including brand, labels, buttons, separators, and empty space;
- no sidebar `QScrollArea` or visible scrollbar is created;
- one wheel event changes at most one page;
- partial high-resolution wheel or touchpad deltas accumulate until one standard step is reached;
- direction changes reset the partial accumulator;
- wheel navigation stops at the first and last page;
- keyboard focus moves to the newly active button so the previous page cannot retain a stale focus treatment;
- wheel input outside the sidebar remains available to the active page.

## Responsive-layout boundary

Width policy is derived from the Collect content viewport, not the full window width. Height density is calculated independently.

The same widgets are moved between layouts; widgets and signal connections are not duplicated.

Supported range:

```text
minimum window: 920×620
normal desktop window
maximized 2K
Windows scaling: 100%, 125%, 150%
```

Horizontal scrolling is disabled. Vertical scrolling appears only when natural Collect content cannot fit.

## Accessibility boundary

Primary actions, status surfaces, metrics, dialogs, Source review, and navigation expose meaningful accessible names.

Standard radio and checkbox behavior is preserved. Selected Files Review retains ExtendedSelection and `Delete`.

Focus, hover, pressed, selected, and disabled states are part of the frozen UI contract. Mouse-wheel navigation must not create a second visual active state.

The stored hotkey remains `ctrl+alt+x` for native registration; product surfaces display `Ctrl+Alt+X`.

## Threading boundary

### Worker thread

The worker may perform:

- folder and project-tree scanning;
- Git status and diff commands;
- file reads and decoding fallbacks;
- sensitive-context analysis;
- formatting and budget planning;
- progress emission and cancellation checks.

### GUI thread

The GUI thread owns:

- widget mutation;
- modal dialogs;
- clipboard writes;
- tray and window state;
- run-history rendering;
- final success/failure feedback.

Cancellation is cooperative. Scanner, collector, safety, and tree operations check cancellation between units of work. A cancelled task emits no partial clipboard output.

## Source-fidelity contract

Collected source payloads and Git diff data are source-like input. They must not be compacted, stripped, normalized, or rewritten.

The formatter may add framing:

```text
===== file: relative/path.py =====
```

It must append the file payload verbatim after that framing.

Compact mode may change only XCC-generated metadata, headings, trees, summaries, and spacing.

Character-budget planning operates on complete structural sections. Normal source files and Git diffs are never silently cut in the middle. Large-file summaries are explicit and typed.

## Git boundary

Git mode uses null-delimited porcelain status and a typed change model.

Supported states include:

- staged;
- unstaged;
- untracked;
- renamed;
- copied;
- deleted;
- paths with spaces;
- Unicode paths.

Staged and unstaged diffs remain separate. Deleted changes remain visible in Git context even when no current file payload exists.

## Ignore and safety boundary

Built-in excluded directories cannot be re-enabled by project rules.

- Full Folder and Project Tree use root `.gitignore` and `.xccignore`.
- Git Changed Files uses Git status and applies `.xccignore` as an additional layer.
- Selected Files treats explicit selection as intentional.

Safety detection is heuristic and warning-only. Reports contain sanitized metadata—path, line number, and category—not detected values. Disabling **Safety confirmation** affects only the modal prompt.

## Local-data and release boundary

Persistent settings:

```text
%USERPROFILE%\.xcc\config.json
```

Runtime History is in-memory and metadata-only.

Official package:

```text
XCC-Context-Collector-v1.3.0-win64.zip
XCC-Context-Collector-v1.3.0-win64.zip.sha256
```

The release gate binds the canonical version, archive filename, SHA-256, automated report, Windows 10/11 evidence, clean `main`, synchronization with `origin/main`, and green CI to the same release candidate.
