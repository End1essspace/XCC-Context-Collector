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
├── pipeline.py                       GUI-independent orchestration
├── qt_worker.py                      QThread bridge + cancellation
├── settings.py                       validated local config + UI scale
├── autostart.py / native_hotkey.py
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

Settings reflows from two columns to one below the large breakpoint. History follows the workbench width policy. About uses a narrower readability surface and scales that cap only by the explicit XCC Interface scale.

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

- Collect, History, Settings, and About are real navigation buttons;
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

Settings are stored at `%USERPROFILE%\.xcc\config.json`. Runtime History is in-memory and metadata-only. XCC has no account, cloud upload, or telemetry.

Sensitive-context detection is heuristic and warning-only. Detected secret values are not displayed in warning summaries or Runtime History.

## Packaging boundary

The PyInstaller directory package must contain `XCC Context Collector.exe`, `VERSION.txt`, `_internal`, and every explicitly listed runtime asset. `build_release.ps1` reads the canonical `xcc.__version__`; `package_release.ps1` creates the versioned ZIP and SHA-256 file.

Release readiness binds source version, dated changelog, release notes, archive filename/hash, automated gate, Windows 10/11 evidence, Git state, and CI to one release commit.
