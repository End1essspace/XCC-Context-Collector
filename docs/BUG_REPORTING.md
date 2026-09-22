# Bug-Report Diagnostics

Report the smallest reproducible, sanitized case. Prefer the repository bug-report template.

## Required details

```text
XCC version:
Distribution: packaged ZIP or source checkout
Windows version/build/architecture:
Windows display scale:
XCC Interface scale:
Monitor arrangement, if relevant:
Affected mode/component:
Expected behavior:
Actual behavior:
Minimal reproduction steps:
```

Read packaged version from About or `VERSION.txt`. For source:

```powershell
python -c "import xcc; print(xcc.__version__)"
```

## Collection / Git defects

Describe only the minimal sanitized project shape and the expected include/exclude behavior. For Git issues, sanitized summaries are usually enough:

```powershell
git status --short
```

```powershell
git diff --stat
```

```powershell
git diff --cached --stat
```

Do not attach confidential diffs or generated XCC context unless every line is intentionally public.

## UI / DPI / window defects

Include:

- window state: normal, maximized, minimized, tray-hidden, restored;
- Windows scale and XCC Interface scale;
- resolution and monitor arrangement;
- whether the issue survives a full XCC restart;
- a cropped screenshot/recording with private paths and project content removed;
- for multi-monitor issues, which monitor the window moved from/to;
- for sidebar issues, input type, starting page, direction, cursor location, and resulting page.

## Tray / hotkey / single-instance defects

State whether the tray icon exists, whether another process owns `Ctrl+Alt+X`, and whether an XCC process remains in Task Manager after the visible window closes.

## Attachments / handoff defects

Include the transfer type (`Copy Files`, `Send One-by-One`, or `Create ZIP & Copy`), selected file count, whether locations are mixed, and the exact visible XCC status. For Handoff issues, include whether focus changed during the sequence and whether the target accepted separate paste events. Do not attach the original private files merely to demonstrate the bug.

## Runtime History defects

State whether the problem survives restart and whether it affects display, Export JSON, Clear History, retention, or corruption recovery. Share only sanitized metadata; do not attach `%USERPROFILE%\.xcc\history.json` if it contains private paths or names.

## Build / release defects

Include the exact failing command and final relevant error block.

```powershell
python -m compileall -q src tests scripts gui.py
```

```powershell
python scripts\check_version_consistency.py
```

```powershell
python -m pytest -q
```

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.4.0
```

Quit every packaged/tray XCC instance before rebuilding.

## Config recovery

Default config:

```text
%USERPROFILE%\.xcc\config.json
```

Do not attach the full file if it contains private paths. Share only the smallest sanitized keys required to reproduce the defect.

## Sanitize before posting

Remove credentials, tokens, private keys, connection strings, proprietary source, confidential diffs, usernames, private absolute paths, internal URLs, computer names, and unrelated clipboard content.

Security vulnerabilities belong in GitHub private vulnerability reporting; see `SECURITY.md`.
