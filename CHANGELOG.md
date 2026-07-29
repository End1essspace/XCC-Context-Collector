# Changelog

All notable changes to XCC Context Collector are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow semantic versioning.

## [Unreleased]

## [1.2.0] - 2026-07-27

### Added

- Source-content fidelity guarantees and regression coverage.
- Complete typed Git change handling for staged, unstaged, renamed, copied, deleted, and untracked files.
- Stable relative paths for selected files, including duplicate filenames and cross-root selections.
- Structure-aware output budgeting with explicit included, omitted, summarized, and partial-file statistics.
- `.xccignore`, root `.gitignore` integration, and pre-copy sensitive-context warnings.
- Responsive background collection pipeline with progress phases and cooperative cancellation.
- Typed run outcomes, duration, coverage metrics, and metadata-only runtime history.
- Standard installable `src` layout, canonical `pyproject.toml`, and separated dependency groups.
- Windows GitHub Actions CI, packaged startup smoke testing, portable ZIP validation, and SHA-256 generation.
- Repository contribution, security, bug-reporting, portable-use, and release documentation.
- Automated release-candidate gate and machine-readable Windows 10/11 validation evidence contract.
- Persistent Safety confirmation setting; enabled by default and optional for repeated trusted-project workflows.

### Changed

- The supported runtime is the PySide6 GUI on CPython 3.13.x and Windows 10/11 x64.
- Legacy Tkinter and `keyboard` workflows are retained only as unsupported development compatibility tools.
- Release builds read the application version from `xcc.__version__` and embed the same value in executable metadata and `VERSION.txt`.
- Runtime history now records successful, warning-bearing, cancelled, and failed operations without storing collected payloads.
- Disabling Safety confirmation suppresses only the modal prompt; warning detection, generated summaries, counters, and outcomes remain active.

### Fixed

- Compact mode no longer rewrites source payload whitespace.
- Git mode no longer silently loses staged-only, rename, copy, delete, Unicode-path, or untracked changes.
- Selected files with identical basenames no longer receive ambiguous output headers.
- Character budgeting no longer cuts source files or Git diff sections in the middle.
- Cancellation no longer copies partial output or leaves conflicting controls active.
- Packaged builds now resolve application and tray artwork from the PyInstaller runtime data directory.

### Security

- Warning summaries and runtime history exclude detected secret values and collected file contents.
- Release archives are validated for safe paths, required files, canonical version, and companion checksum.
- Built-in excluded directories cannot be re-enabled through project ignore rules.

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

[Unreleased]: https://github.com/End1essspace/xcc-context-collector/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/End1essspace/xcc-context-collector/compare/v1.1.2...v1.2.0
[1.1.2]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.1.2
[1.1.0]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.1.0
[1.0.0]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.0.0
