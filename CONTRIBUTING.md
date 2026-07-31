# Contributing to XCC Context Collector

XCC is a Windows-first Python desktop utility. Contributions should preserve four core properties:

1. collected source payloads remain exact;
2. output is deterministic and transparent;
3. context safety remains warning-only and privacy-conscious;
4. the PySide6 interface stays responsive during collection.

## Supported development environment

- Windows 10 or Windows 11, 64-bit
- CPython 3.13.x
- Git
- Windows PowerShell 5.1 or PowerShell 7+

Create an isolated environment:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,build]"
```

`pyproject.toml` is the canonical dependency manifest. `requirements.txt` is retained only as a compatibility installer for the supported GUI runtime.

## Supported architecture boundary

New product work must follow:

```text
gui.py
  -> xcc.gui
  -> xcc.pipeline / xcc.qt_worker
  -> scanner, Git, safety, formatter, and budget modules
```

The supported application boundary is intentionally singular: `gui.py -> xcc.gui -> xcc.pipeline`. Removed compatibility launchers and Tkinter workflows must not be reintroduced without a new product-level decision.

Read before cross-cutting changes:

- `docs/ARCHITECTURE.md`
- `docs/roadmap.md`
- `docs/BUG_REPORTING.md`
- `SECURITY.md`

## Required local validation

For every code or documentation change:

```powershell
python -m compileall -q src tests scripts gui.py
python scripts\check_version_consistency.py
python -m pytest -q
```

Behavior changes require regression tests. Documentation changes must preserve version markers, release-note markers, internal links, and the current screenshot paths.

For packaging, runtime assets, tray, startup, or release automation changes, also run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
powershell -ExecutionPolicy Bypass -File scripts\smoke_packaged_app.ps1
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1
```

For a complete release-candidate validation:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

## Change guidelines

### Source fidelity

Never apply whitespace compaction, `strip()`, newline normalization, or content rewriting to collected file payloads or Git diff data. Formatting helpers may only transform XCC-generated metadata and structure.

### Git behavior

Preserve the distinction between index and worktree status. New Git behavior must cover staged, unstaged, untracked, rename/copy, delete, spaces, and Unicode paths where applicable.

### Character budgets

The final output must never exceed the configured character limit. Omission must remain explicit; source files and Git diffs must not be silently cut in the middle.

### Safety behavior

Do not log or persist detected secret values. Safety output may contain only sanitized metadata such as relative path, line number, and warning category. Disabling the modal confirmation must not disable detection.

### Threading and UI

Collection work belongs outside the Qt main thread. Clipboard access, dialogs, and widget mutation remain on the GUI thread. Cancellation must be cooperative and must not publish partial output.

Sidebar changes must preserve the final navigation contract:

- real buttons rather than item-view rows;
- exclusive selection;
- Up/Down access to all four pages;
- wheel input across the complete sidebar surface;
- no sidebar scrollbar or `QScrollArea`;
- one page change per wheel event;
- accumulated partial touchpad deltas;
- bounded first/last-page behavior;
- focus transfer to the active page;
- independent page-content scrolling.

## Documentation and screenshots

Keep terminology aligned across README, architecture, release notes, validation docs, and the UI:

- Selected Files
- Full Folder
- Git Changed Files
- Project Tree
- Safety confirmation
- Collect & Copy
- Last Run
- Runtime History

Update `docs/screenshots/xcc-collect.png` and `docs/screenshots/xcc-history.png` only when they represent the current release UI. Screenshots must not expose credentials, user-profile names, private repositories, client data, or proprietary content. A deliberate path to a public demonstration repository is acceptable.

## Workspace cleanup

Preview cleanup first:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1 -DryRun
```

Remove normal generated outputs:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1
```

The default command preserves `.venv`, `artifacts`, and the legacy local `release` directory. Remove those only through explicit switches:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1 -IncludeArtifacts -IncludeLegacyReleaseArchives -IncludeVirtualEnvironment
```

Do not substitute `git clean -xfd`; it cannot distinguish disposable build outputs from release-candidate evidence or local environments.

## Pull requests

Keep each pull request focused on one defect, milestone, or coherent documentation update.

A pull request should include:

- a clear user-visible or repository-level summary;
- regression tests for behavior changes;
- updated documentation where behavior or workflow changed;
- exact validation commands and results;
- UI screenshots when visual behavior changed.

Do not commit:

- collected project contexts;
- credentials, tokens, private keys, or connection strings;
- proprietary source or confidential Git diffs;
- private absolute paths or personal configuration;
- `build`, `dist`, `artifacts`, `release`, `*.egg-info`, caches, generated executables, or local `.xcc` data.

Use `.github/pull_request_template.md` and resolve all applicable checklist items before review.

## Security reports

Do not report vulnerabilities through a public issue when the report contains exploit details, secrets, private source, or personal data. Follow `SECURITY.md` and use GitHub private vulnerability reporting.
