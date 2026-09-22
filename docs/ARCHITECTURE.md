# XCC Architecture

## Product boundary

XCC is a Windows-first PySide6 desktop utility with one supported runtime path:

```text
gui.py -> xcc.gui:run_gui -> xcc.pipeline
```

Installed entry point: `xcc-context-collector`.

The root launcher exists for repository execution. Collection behavior is implemented under `src/xcc`; no Tkinter or third-party global-keyboard runtime is supported.

## Runtime layers

```text
src/xcc/
├── config.py                         supported files and defaults
├── models.py                         typed results, Git changes, history
├── scanner.py / collector.py / tree.py
├── git_utils.py                      status + staged/unstaged diffs
├── ignore.py / safety.py             ignore rules + warning-only detection
├── formatter.py / optimizer.py / budget.py
├── path_list_parser.py
├── selected_files_importer.py / selected_files_review.py
├── attachment_importer.py / attachment_bundle.py
├── clipboard.py / native_input.py         file handoff + guarded Win32 paste input
├── history_store.py                       persistent metadata-only history
├── pipeline.py                       GUI-independent orchestration
├── qt_worker.py                      QThread bridge + cancellation
├── settings.py                       validated local config + UI scale
├── hotkeys.py                       pure shortcut validation/normalization
├── autostart.py / native_hotkey.py   Win32 registration + transactional rollback
├── resources.py                      source/PyInstaller asset resolution
├── ui_theme.py                       palette, metrics, QSS
├── ui_components.py                  reusable DPI-aware primitives
├── ui_sidebar.py / ui_shell.py
├── ui_collect.py / ui_metrics.py
├── ui_responsive.py                  width/height/work-area policy
└── gui.py                            shell, pages, dialogs, tray, window lifecycle
```

## Collection flow

```text
UI -> CollectionRequest -> CollectionWorker/QThread -> pipeline
   -> scanner/Git/collector/safety -> formatter/budget -> CollectionResult
   -> optional safety confirmation -> clipboard -> Last Run / Runtime History
```

`pipeline.execute_collection()` has no widget or clipboard dependency. Clipboard writes, dialogs, and widget mutation remain on the GUI thread.

## Selected Files boundary

```text
Clipboard/path picker
    -> path_list_parser
    -> selected_files_importer
    -> explicit project-root resolution when required
    -> canonical validation + supported-type checks + Windows-aware deduplication
    -> transactional Selected Files Review
    -> normal collection pipeline
```

Pasted text is data only. XCC does not execute it, expand shell expressions, interpret globs, or search the whole disk. Relative paths cannot escape the explicit project root after canonical resolution.

## Source-fidelity boundary

Collected source payloads and Git diffs are source-like input and must not be compacted, stripped, newline-normalized, or rewritten. Compact mode may change only XCC-generated framing and metadata.

Budgeting plans complete sections before rendering. Omitted or summarized content is reported explicitly; source files and Git diffs are never silently cut in the middle.


## Global hotkey boundary

v1.4.0 uses Win32 `RegisterHotKey` through `native_hotkey.py`; no third-party
keyboard hook package is supported.

Three bindings exist:

```text
Restore / Show XCC    default: Ctrl+Alt+X   enabled by default
Collect & Copy        default: Ctrl+Alt+C   disabled by default
Attachment Handoff    default: Ctrl+Alt+V   disabled by default
```

Hotkey strings are normalized by the GUI-independent `hotkeys.py` parser before
they are persisted. Settings never persist an invalid shortcut. When an enabled
binding changes, `NativeHotkeyManager.replace()` probes the new combination
while the old binding is still active. If final registration fails, the previous
binding is restored before the error is surfaced, so a failed edit cannot leave
XCC silently without its last known-good shortcut.

Enabled bindings use distinct Win32 IDs and may not reuse the same shortcut. Disabled bindings remain persisted but are not registered. `Collect & Copy` invokes the current Collect workflow only. `Attachment Handoff` arms/cancels the ordered one-file-per-paste compatibility workflow and never submits a message.

## UI architecture

Presentation policy is separated from orchestration:

- `ui_theme.py`: semantic palette, geometry tokens, application/tray styles;
- `ui_components.py`: headers, capsules, buttons, DPI-aware raster/SVG labels;
- `ui_sidebar.py`: exclusive navigation, keyboard and wheel behavior;
- `ui_collect.py`: mode labels/actions/helpers;
- `ui_metrics.py`: metric formatting and semantic states;
- `ui_responsive.py`: responsive and work-area geometry;
- `gui.py`: composition and runtime interaction.

The header reports short runtime state. The footer reports event/progress guidance; the `X-SERIES` wordmark is presentation-only and non-interactive.

## Responsive boundary

Responsive decisions use **Qt logical geometry**, not physical monitor-resolution branches.

Core contract:

```text
minimum window: 920×620
width modes: compact <820, medium 820–1119, large >=1120
height modes: short <700, standard 700–799, tall >=800
normal horizontal page scrolling: disabled
```

Width and height are independent. The same widget instances are rearranged; controls and signal connections are not duplicated.

Large workbench surfaces use a Full-HD-referenced logical width of `1692`. Beyond that reference, 75% of additional logical width is admitted into the workbench and 25% becomes centered outer space, with a hard useful-width ceiling of `3200`. This is composition policy, not a resolution detector.

Settings reflows from two columns to one below the large breakpoint. Attachments, History, Settings, and About share the same progressive workbench width policy. About keeps its own internal card/badge reflow, but no longer has a separate fixed-width page cap.

Dialogs use the current screen `availableGeometry()` with a 24 px logical edge margin. Their horizontal scrollbar is disabled; vertical overflow is allowed when required.

## DPI and Interface scale

Windows/Qt owns native DPI. XCC owns composition.

DPI-sensitive raster/SVG assets are rerendered for the active device-pixel ratio when the window changes screen or DPI. Layout widths are never divided by DPR a second time.

`settings.py` supports:

```text
Auto, 90%, 100%, 110%, 120%, 125%, 150%
```

`Auto` leaves `QT_SCALE_FACTOR` untouched. An explicit choice sets the Qt global multiplier **before `QApplication` is created**, so a restart is required. The setting is persisted in `%USERPROFILE%\.xcc\config.json`.

## Window and monitor lifecycle

The custom frameless shell keeps its normal geometry inside the current screen work area. Maximize uses `availableGeometry()`. Restore, tray/hotkey restore, screen changes, and work-area changes refit geometry when needed.

Native hit-testing and the Fitts-close controller must not create invisible close targets outside the real close-button rectangle.

## Sidebar contract

- Collect, Attachments, History, Settings, and About are real navigation buttons;
- selection is exclusive;
- Up/Down reaches all pages;
- wheel input over the complete sidebar changes at most one page per event;
- high-resolution deltas accumulate;
- navigation stops at the first/last page;
- focus follows the active page;
- page-content scrolling remains independent.

## Threading and cancellation

Worker thread: scanning, Git, file reads, safety analysis, formatting, budgeting, progress and cancellation checks.

GUI thread: widgets, dialogs, clipboard, tray/window state, history rendering and final feedback.

Cancellation is cooperative and never publishes partial clipboard output.

## Local data and privacy

Settings are stored at `%USERPROFILE%\.xcc\config.json`. Runtime History is persisted separately at `%USERPROFILE%\.xcc\history.json` as bounded metadata-only JSON (schema v1, newest-first, maximum 200 records). XCC has no account, cloud upload, or telemetry.

Sensitive-context detection is heuristic and warning-only. Detected secret values are not displayed in warning summaries or Runtime History. Persistent History never stores collected source bodies, Git diff bodies, raw failure bodies, or detected secret values; absolute collection source paths are reduced to non-path labels before persistence/export.

## Packaging boundary

The PyInstaller directory package must contain `XCC Context Collector.exe`, `VERSION.txt`, `_internal`, and every explicitly listed runtime asset. `build_release.ps1` reads the canonical `xcc.__version__`; `package_release.ps1` creates the versioned ZIP and SHA-256 file.

Release readiness binds source version, dated changelog, release notes, archive filename/hash, automated gate, Windows 10/11 evidence, Git state, and CI to one release commit.

## Attachments transfer boundary (M17.3–M17.5)

Attachments is a separate original-file handoff pipeline. `attachment_importer.py` owns explicit-file selection and metadata; `clipboard.py` owns GUI-thread file-object clipboard publication; `attachment_bundle.py` owns ZIP64 planning, safe archive member mapping, streaming, transactional finalization, and managed-bundle cleanup; `qt_worker.py` runs ZIP creation cooperatively in a worker thread while final clipboard publication remains on the GUI thread.

The managed bundle directory is `%USERPROFILE%\.xcc\attachment-bundles\`. XCC retains completed bundles for 7 days and cleans only its own stale `XCC-Attachments-*.zip` artifacts. Source files are never moved or deleted.

Attachment safety is path-only. XCC may warn on sensitive filenames, but does not silently content-scan binary/original attachments. Runtime History for attachment transfers stores only operation type/outcome, file count, aggregate bytes, duration, warning count, and an optional sanitized bundle filename; it stores no attachment bodies or absolute source paths.


## Persistent Runtime History

`src/xcc/history_store.py` is the persistence boundary for operational History.

- file: `%USERPROFILE%\.xcc\history.json`;
- schema: `xcc-runtime-history`, version `1`;
- retention: newest-first, at most 200 records;
- writes: UTF-8 JSON through a same-directory temporary file followed by atomic replace;
- corruption: unreadable/unsupported documents are moved to `history.corrupt-YYYYMMDD-HHMMSS.json`, then XCC recreates a clean store; structurally bad individual records are skipped and the valid subset is rewritten;
- export: the History page writes the same documented metadata-only JSON schema to a user-selected file;
- privacy: persistence/export sanitize absolute source paths and bundle paths and contain no collected source bodies, Git diffs, secret values, attachment bytes, or raw exception/failure bodies.

The legacy v1.3.x/v1.4 pre-M17.7 History was process-memory-only and therefore has no historical disk artifact to migrate. First M17.7 startup starts with an empty persistent store unless `history.json` already exists.
