# Changelog

All notable changes to XCC Context Collector are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow semantic versioning.

## [Unreleased]

### Added

- Source-content fidelity guarantees and regression coverage.
- Complete typed Git change handling for staged, unstaged, renamed, copied, deleted, and untracked files.
- Stable relative paths for selected files.
- Structure-aware output budgeting with explicit coverage statistics.
- `.xccignore`, root `.gitignore` integration, and pre-copy sensitive-context warnings.
- Responsive background collection pipeline with cooperative cancellation.
- Typed run outcomes, duration, coverage metrics, and metadata-only runtime history.
- Standard installable `src` layout, canonical `pyproject.toml`, and separated dependency groups.
- Windows GitHub Actions CI, packaged startup smoke testing, portable ZIP validation, and SHA-256 generation.
- Repository contribution, security, bug-reporting, and release documentation.

### Changed

- The supported runtime is the PySide6 GUI on CPython 3.13.x and Windows 10/11 x64.
- Legacy Tkinter and `keyboard` workflows are retained only as unsupported development compatibility tools.
- Release builds read the application version from `xcc.__version__`.

### Security

- Warning summaries and runtime history exclude detected secret values and collected file contents.
- Release archives are validated for safe paths, required files, canonical version, and companion checksum.

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

[Unreleased]: https://github.com/End1essspace/xcc-context-collector/compare/v1.1.2...HEAD
[1.1.2]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.1.2
[1.1.0]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.1.0
[1.0.0]: https://github.com/End1essspace/xcc-context-collector/releases/tag/v1.0.0
