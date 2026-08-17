# Changelog

All notable changes to XCC Context Collector are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses semantic versioning.

## [Unreleased]

## [1.3.1] - 2026-08-17

### Added

- User-selectable **Interface scale** with `Auto`, `90%`, `100%`, `110%`, `120%`, `125%`, and `150%`; explicit overrides are applied before `QApplication` starts and persist in the local config.
- Dedicated responsive regression suites for breakpoint boundaries, height thresholds, large-screen workbench behavior, resize round-trips, widget/state preservation, dialogs, and horizontal-scroll invariants.
- Subtle `X-SERIES` footer wordmark with DPI-aware rendering and packaged-asset validation.

### Changed

- Collect now uses independent width and height policies with a progressive Full-HD-referenced workbench on wide logical viewports.
- Settings and History use the same responsive workbench policy; Settings reflows from two columns to one when constrained.
- About keeps a readability-oriented bounded surface while respecting the explicit XCC Interface scale.
- Paste Paths and Selected Files Review now clamp to the active screen work area and use vertical overflow instead of horizontal page scrolling.
- Window restore/maximize behavior now fits the current work area and tracks screen/work-area changes.
- Raster and SVG UI assets are rerendered for the active device-pixel ratio instead of relying on stale QLabel/QIcon raster state.

### Fixed

- QHD/125% and other scaled layouts no longer depend on physical-resolution branches or double-apply Windows DPI.
- Hidden stacked pages no longer select responsive modes from stale `~640×480` child viewport geometry.
- Responsive callbacks and Fitts-close event handling tolerate Qt teardown without stale-wrapper exceptions.
- Interface-scale selector arrow, selected-row accent, and `Auto (recommended)` sizing now match the XCC design system without clipping.
- Normal-window restore geometry is clamped to the current screen work area after maximize, tray/hotkey restore, and monitor changes.

### Validation

- Manual responsive/DPI review completed for the implemented v1.3.1 surfaces and correction cycle.
- Release tooling now has an explicit responsive-regression gate and v1.3.1 manual evidence requirements.

## [1.3.0] - 2026-07-31

### Added

- **Paste Paths** action for Selected Files mode and guarded `Ctrl+V` import when focus is not inside an editable text field.
- Path-list parsing for plain lines, Markdown bullets, numbered lists, quotes, backticks, and fenced code blocks.
- Explicit project-root resolution for relative paths with validation before selection state is changed.
- Selected Files Review dialog with relative paths, root visibility, multi-select removal, `Delete`, `Clear All`, `Cancel`, and transactional `Apply Changes`.
- End-to-end regression coverage for AI path list import, review, removal, and final collection output.
- Final reusable PySide6 interface system with shared theme tokens, reusable components, semantic capsules, responsive geometry policy, and real sidebar navigation buttons.
- Wheel-based page navigation across the complete sidebar surface without a visible scrollbar or scroll container.
- GUI semantic and accessibility regression coverage for dialogs, long paths, large selections, collection-active states, status roles, and version surfaces.

### Changed

- Selected Files source state now summarizes the project root and selected-file count, or clearly reports mixed locations.
- Manual file selection and pasted-path import now share one ordered, de-duplicated selection model.
- Git repository markers take precedence when inferring a common project root, including monorepository layouts.
- Documentation, architecture, release validation, package names, and canonical version metadata are aligned for v1.3.0.
- Final release readiness now binds the automated-gate report and Windows 10/11 evidence to the exact archive filename and SHA-256.
- Manual evidence now records explicit Paste Paths, root-boundary, issue-reporting, mixed-location, review, and relative-output gates for v1.3.0.
- The Collect page now uses a compact product sidebar, responsive Setup composition, four semantic Last Run groups, and distinct header runtime and footer event-status roles.
- Paste Paths and Selected Files Review now share the final application typography, spacing, button hierarchy, validation states, focus treatment, and disabled-state clarity.
- The interface adapts from `920×620` through maximized 2K layouts while reusing the same widget instances and preserving tab order and collection behavior.
- Sidebar wheel input changes at most one page per event, accumulates high-resolution touchpad deltas, stops at the first and last page, and moves keyboard focus with the active tab.
- Public documentation and final Collect/History screenshots were rebuilt around the release-candidate interface.
- Repository regression tests now enforce stable package, governance, release-tool, and runtime boundaries instead of exact implementation text or milestone-history wording.
- Release documentation was consolidated into one canonical v1.3.0 procedure, a non-duplicating operational checklist, and a release-scoped historical v1.2.0 validation record.
- The roadmap now records release-level outcomes and the active path instead of duplicating Git history as an implementation diary.
- Final v1.3.0 documentation was re-frozen after C1–C4 cleanup so the release-candidate gate starts from one clean, synchronized repository state.

### Fixed

- Repeated imports no longer add the same Windows path twice when slash style or letter case differs.
- Stale or deleted remembered roots no longer prevent a new relative-path import.
- Files from separate repositories no longer receive a misleading common project root.
- Absolute external files remain importable without being incorrectly resolved under the selected project root.
- Review changes are not applied when the dialog is cancelled, and `Apply Changes` stays disabled until the selection actually changes.
- Sidebar brand scale and vertical spacing no longer overpower the navigation or waste the top workspace area.
- Restore-hotkey labels now display `Ctrl+Alt+X` consistently instead of exposing the lowercase configuration form.
- Long project roots, `Mixed locations`, 100+ file selections, and disabled collection controls retain readable, accessible UI states.
- Wheel navigation no longer leaves a stale focus treatment on the previously active sidebar button.

### Removed

- Unsupported Tkinter launchers, the standalone third-party `keyboard` listener, their optional dependency group, and their dedicated compatibility tests.
- Brittle source-snippet, QSS-fragment, and roadmap-narrative assertions that duplicated behavioral regression coverage.
- The active-path `docs/M10_VALIDATION.md` copy and unreferenced `assets/original_icons/` archival duplicates.

### Security

- Relative traversal outside the chosen project root is rejected after canonical path resolution.
- Pasted text is treated as data only: XCC does not execute commands, expand shell expressions, or search the whole disk for suffix matches.

## [1.2.0] - 2026-07-30

### Added

- Exact source-payload fidelity guarantees with regression coverage for whitespace-sensitive content.
- Typed Git change handling for staged, unstaged, untracked, renamed, copied, and deleted files.
- Stable relative display paths for Selected Files mode, including duplicate basenames and cross-root selections.
- Structure-aware character budgeting with explicit included, omitted, summarized, and partial-file statistics.
- `.xccignore` support and root `.gitignore` integration for folder and tree workflows.
- Heuristic sensitive-context warnings for filenames, private-key material, tokens, credentials, and credential-bearing connection strings.
- Persistent **Safety confirmation** setting, enabled by default and optional for trusted repeated workflows.
- Background collection pipeline with progress phases, one-job enforcement, and cooperative cancellation.
- Typed run outcomes, duration and coverage metrics, Last Run health, and metadata-only runtime history.
- Standard installable `src` layout, canonical PEP 621 metadata, and separated runtime, development, build, and legacy dependency groups.
- Native Windows restore hotkey, single-instance restore behavior, tray workflow, and optional Windows autostart integration.
- Windows GitHub Actions CI, clean-install validation, packaged startup smoke, portable ZIP validation, and SHA-256 generation.
- Machine-readable automated release report and Windows 10/11 manual evidence contract.
- Deterministic PowerShell workspace cleanup for caches, packaging metadata, and local build outputs.
- Lucide-based sidebar navigation and final v1.2.0 desktop UI polish.

### Changed

- Compact mode now affects only XCC-generated structure and never rewrites collected source payloads or Git diff content.
- Git mode now keeps staged and unstaged diff sections separate and reports Git command failures instead of presenting an empty result.
- Output budgeting now plans complete sections before rendering and emits a bounded budget summary when content is omitted.
- Obsolete internal compatibility wrappers and unused helper symbols were removed without changing the supported collection pipeline.
- Safety confirmation can be disabled without disabling detection, generated warning summaries, counters, outcomes, or history metadata.
- Runtime history records successful, warning-bearing, cancelled, and failed runs without storing collected payloads.
- The supported product boundary is the PySide6 GUI on CPython 3.13.x and Windows 10/11 x64.
- Unsupported Tkinter and third-party `keyboard` workflows were removed; the PySide6 application is now the only runtime path.
- Release builds read the canonical version from `xcc.__version__`, embed Windows version resources, and write matching `VERSION.txt` metadata.
- PyInstaller packages now include only required runtime artwork and navigation assets.
- Successful builds remove intermediate `build` data and generated spec files automatically.
- Project governance, architecture, diagnostics, portable-use, validation, release, and bilingual user documentation were aligned for v1.2.0.

### Fixed

- Repeated blank lines, trailing spaces, multiline strings, YAML block content, and final source newlines are preserved.
- Staged-only, rename, copy, delete, Unicode-path, and untracked Git changes are no longer silently lost.
- Files with identical basenames no longer receive ambiguous output headers.
- Character limits no longer cut source files or Git diff sections in the middle.
- Cancellation no longer copies partial output or leaves conflicting controls enabled.
- Packaged builds resolve application, header, About, taskbar, and tray artwork from the PyInstaller runtime directory.
- Settings groups are top-aligned when their content heights differ.
- Sidebar SVG icons render sharply at Windows DPI scaling with consistent spacing and state colors.
- The cleanup script now works with Windows PowerShell 5.1 without relying on `System.IO.Path.GetRelativePath`.

### Security

- Warning summaries contain only relative paths, line numbers, and categories; detected values are not displayed or stored in runtime history.
- XCC remains warning-only and does not silently redact or mutate collected source code.
- Built-in excluded directories cannot be re-enabled through project ignore rules.
- Release archives are checked for safe paths, one application root, required runtime files, canonical version, and a matching SHA-256 checksum.
- Official release publication is blocked until automated validation and matching clean-host Windows 10/11 evidence pass.

## [1.1.2]

### Added

- Standalone Project Tree collection mode.

### Changed

- Expanded project-context workflow and release documentation.

## [1.1.0]

### Added

- Broader source, frontend, backend, system, scripting, and project-filename coverage.

### Security

- Sensitive environment files, keys, databases, logs, archives, and binaries remain excluded by default.

## [1.0.0]

### Added

- Initial Windows desktop release with Selected Files, Full Folder, and Git Changed Files workflows.

[Unreleased]: https://github.com/End1essspace/xcc-context-collector/compare/v1.3.1...HEAD
[1.3.1]: https://github.com/End1essspace/xcc-context-collector/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/End1essspace/xcc-context-collector/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/End1essspace/xcc-context-collector/compare/v1.1.2...v1.2.0
[1.1.2]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.1.2
[1.1.0]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.1.0
[1.0.0]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.0.0
