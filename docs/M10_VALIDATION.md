# M10 — v1.2.0 Validation Procedure

M10 is the final release blocker. It combines repeatable automation with two clean-host manual records. A green unit-test suite alone is not sufficient to create the `v1.2.0` tag.

## 1. Prepare the release candidate

Close every running packaged XCC process, including tray instances, then run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1
```

The script performs:

- source/test/script compilation;
- canonical version consistency;
- the full pytest suite;
- isolated clean-install validation;
- a clean PyInstaller build;
- packaged startup smoke;
- portable ZIP generation;
- release ZIP and SHA-256 validation;
- an automated gate report under `artifacts\`.

Expected release assets:

```text
artifacts\XCC-Context-Collector-v1.2.0-win64.zip
artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256
artifacts\XCC-v1.2.0-automated-gate.json
```

## 2. Validate packaged visual assets

Use the packaged executable and confirm:

- the Windows title bar and taskbar show the XCC application icon;
- the header and About page show the XCC artwork;
- the notification-area icon is visible (it may initially be inside the Windows overflow menu);
- the tray icon menu can be opened and is not a blank/invisible entry.

## 3. Validate the four collection modes

Use the packaged executable, not `python gui.py`.

- Selected Files: select files from at least two directories, including duplicate basenames.
- Full Folder: collect a real project with nested source and documentation files.
- Git Changed Files: verify staged, unstaged, untracked, rename, and delete representation.
- Project Tree: verify structure-only output and character-budget behavior.

For each successful run, confirm the clipboard output, Last Run metrics, outcome, and History entry.

## 4. Validate responsiveness and cancellation

Use a repository large enough for progress to remain visible.

- Start Full Folder collection.
- Move, resize, minimize, and restore the window while work is active.
- Attempt a second collection and confirm it cannot start.
- Cancel the active collection.
- Confirm controls return to the idle state.
- Confirm History records `Cancelled`.
- Confirm the clipboard still contains the pre-test value and no partial context.
- Repeat and allow a complete collection to finish.

This closes the remaining M6 manual acceptance gate.

## 5. Validate Windows integration

On each clean host:

- tray hide, single-click toggle, double-click restore, and Quit;
- `Ctrl+Alt+X` restore;
- non-fatal behavior when another process owns the hotkey;
- Start with Windows shortcut creation and removal;
- invalid `%USERPROFILE%\.xcc\config.json` recovery;
- second launch restores the existing instance;
- packaged application starts without Python installed.

## 6. Record one evidence file per OS

Run on the host after completing all checks:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\record_manual_validation.ps1
```

The script detects the OS, asks for an explicit result for every manual gate, and writes a JSON record to `artifacts\manual-validation\`.

Required records:

```text
one complete Windows 10 record
one complete Windows 11 record
```

The records contain OS metadata, booleans, operator name, UTC time, and optional notes. They do not contain project files, clipboard content, secrets, or user configuration values.

## 7. Validate combined evidence

```powershell
python scripts\validate_release_evidence.py `
  --expected-version 1.2.0 `
  --evidence artifacts\manual-validation\<windows-10-record>.json `
  --evidence artifacts\manual-validation\<windows-11-record>.json
```

The validator rejects missing operating systems, mixed versions, absent gates, and any failed check.

## 8. Publication gate

After the release candidate commit is pushed and Windows CI is green:

```powershell
python scripts\check_release_readiness.py `
  --archive artifacts\XCC-Context-Collector-v1.2.0-win64.zip `
  --checksum artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256 `
  --evidence artifacts\manual-validation\<windows-10-record>.json `
  --evidence artifacts\manual-validation\<windows-11-record>.json
```

Only after this command passes should the annotated `v1.2.0` tag and GitHub draft release be created.
