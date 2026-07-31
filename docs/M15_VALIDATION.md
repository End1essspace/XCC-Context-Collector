# XCC v1.3.0 Release Validation

Status: **ACTIVE — RUN AFTER PRE-RC CLEANUP**

This is the canonical procedure for the exact commit and archive that will become XCC v1.3.0. The compact operational checklist is [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md).

## Release invariant

Do not tag or publish until every automated gate, packaged check, Windows evidence record, repository check, and CI run refers to the same release commit and final archive SHA-256.

## 1. Source and documentation preflight

Required public release surfaces:

```text
README.md
CHANGELOG.md
docs/ARCHITECTURE.md
docs/BUG_REPORTING.md
docs/M15_VALIDATION.md
docs/PORTABLE_ZIP.md
docs/RELEASE_CHECKLIST.md
docs/UI_REFERENCE_v1.3.0.md
docs/releases/v1.3.0.md
docs/roadmap.md
docs/screenshots/xcc-collect.png
docs/screenshots/xcc-history.png
```

Confirm:

- canonical version markers are `1.3.0`;
- release notes contain `## Summary` and `## Validation`;
- screenshots represent the final UI and disclose no credentials, user-profile names, private repositories, client data, or unrelated clipboard content;
- deliberate paths to public demonstration repositories are acceptable;
- the supported runtime is `gui.py -> xcc.gui -> xcc.pipeline`;
- obsolete legacy launchers, `docs/M10_VALIDATION.md`, and `assets/original_icons/` are absent.

Run:

```powershell
python -m compileall -q src tests scripts gui.py; python scripts\check_version_consistency.py; python -m pytest -q
```

## 2. Source UI gate

Validate at minimum:

```text
920×620
normal desktop window
maximized 2K
Windows scaling 100%, 125%, 150%
```

Confirm:

- no clipping or accidental scrollbar in the shell;
- Setup, Last Run, primary action, dialogs, Settings, History, and About remain readable;
- header runtime state and footer event guidance have distinct roles;
- long paths, `Mixed locations`, 100+ selected files, disabled controls, and keyboard focus remain clear;
- all four pages are reachable by mouse and keyboard.

### Sidebar wheel contract

Test wheel input over brand elements, labels, buttons, separators, and empty sidebar space:

- down/up moves one page in the expected direction;
- one event changes at most one page;
- partial high-resolution deltas accumulate;
- reversing direction clears the partial accumulator;
- movement stops at Collect and About;
- no sidebar `QScrollArea` or visible scrollbar exists;
- focus follows the active page;
- wheel input over page content keeps normal page scrolling.

## 3. Selected Files gate

Confirm:

- Paste Paths is visible only in Selected Files mode;
- guarded `Ctrl+V` does not hijack editable text fields;
- plain, Markdown, numbered, quoted, backtick, and fenced lists are parsed;
- relative paths require a valid visible project root;
- canonical traversal outside the root is rejected;
- absolute files remain supported;
- duplicate paths are not added twice;
- missing, directory, unsupported, invalid, outside-root, and external states are reported;
- stale roots require a new root selection;
- unrelated repositories produce `Mixed locations`;
- Source opens transactional Selected Files Review;
- extended selection, `Delete`, Remove Selected, Clear All, Cancel, and Apply Changes behave correctly;
- final output uses stable distinguishable paths.

## 4. Four-mode regression gate

Validate Selected Files, Full Folder, Git Changed Files, and Project Tree.

Across the relevant modes confirm:

- exact source payload fidelity;
- staged and unstaged Git separation;
- rename, copy, delete, untracked, spaces, and Unicode handling;
- `.gitignore`, `.xccignore`, and built-in exclusions;
- warning-only safety detection and optional confirmation;
- explicit budget summaries without partial source payloads;
- cooperative cancellation without clipboard replacement;
- Last Run and metadata-only Runtime History;
- tray, native `Ctrl+Alt+X`, autostart, config recovery, and single instance.

## 5. Automated release-candidate gate

Run from repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

The report must declare:

```text
xcc_version: 1.3.0
passed: true
gates.selected_files_regression: true
```

The report must bind itself to the exact archive filename and SHA-256.

## 6. Packaged application gate

Extract the generated ZIP to a clean writable directory and verify:

- the application starts without Python installed;
- `XCC Context Collector.exe`, `_internal`, and `VERSION.txt` are present;
- About, footer, and `VERSION.txt` show `1.3.0`;
- every required application, tray, navigation, card, metric, dialog, and action asset is present;
- no console window appears during normal startup;
- a second launch restores the existing instance;
- tray toggle/restore/Quit, close-to-tray, `Esc`, `Ctrl+Alt+X`, and Start with Windows work;
- sections 2–4 also pass in the packaged build.

## 7. Windows 10 and Windows 11 evidence

Create one complete record on each OS for the same final ZIP SHA-256, then run:

```powershell
python scripts\validate_release_evidence.py --expected-version 1.3.0 --expected-archive-sha256 <FINAL_SHA256> --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Evidence JSON is private release material and must not be attached to the public release.

## 8. Final readiness

Run:

```powershell
python scripts\check_release_readiness.py --archive artifacts\XCC-Context-Collector-v1.3.0-win64.zip --checksum artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --automated-report artifacts\XCC-v1.3.0-automated-gate.json --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Expected result:

```text
Release readiness passed for v1.3.0.
```

Before tagging also confirm:

- branch is `main`;
- working tree is clean;
- local `main` equals `origin/main`;
- Windows CI is green for the same release commit.

## 9. Tag and draft release

```powershell
git tag -a v1.3.0 -m "XCC Context Collector v1.3.0"
```

```powershell
git push origin v1.3.0
```

```powershell
gh release create v1.3.0 artifacts\XCC-Context-Collector-v1.3.0-win64.zip artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --title "XCC Context Collector v1.3.0" --notes-file docs\releases\v1.3.0.md --draft
```

Publish only the ZIP and checksum as release assets.

## 10. Public artifact verification

After publication:

- download the public ZIP and checksum independently;
- verify SHA-256;
- extract and launch the downloaded package;
- confirm version surfaces, Paste Paths, one collection, sidebar wheel/focus behavior, and both public assets;
- update the roadmap to `DONE — RELEASED`;
- publish the release announcement.

The release is complete only after the public downloadable artifact passes this verification.
