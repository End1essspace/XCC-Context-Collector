# Bug-Report Diagnostics

A useful XCC report is reproducible, versioned, and sanitized. Use the repository bug-report template whenever possible.

## Required environment details

```text
XCC version:
Distribution: packaged portable ZIP or source checkout
Windows version, build, and architecture:
Collection mode or affected component:
Compact mode:
Max output chars:
Outcome shown by XCC:
Warnings / errors counters:
Expected behavior:
Actual behavior:
Minimal reproduction steps:
```

For a packaged build, read the version from the About page or `VERSION.txt`.

For an editable source install:

```powershell
python -c "import xcc; print(xcc.__version__)"
```

## Collection defects

When reporting a collection or formatting problem, describe the smallest sanitized project shape needed to reproduce it:

```text
project/
├── src/
│   └── example.py
└── .xccignore
```

State which files should have been included or excluded and which mode was used. Do not paste the real collected context unless every line is intentionally public and reviewed.

For Git mode, include sanitized status information when relevant:

```powershell
git status --short
git diff --stat
git diff --cached --stat
```

Do not attach confidential diffs.

## GUI, tray, and hotkey defects

Include:

- whether XCC was maximized, minimized, hidden to tray, or restored;
- whether **Start minimized to tray**, **Close to tray**, or **Start with Windows** was enabled;
- whether `Ctrl+Alt+X` was already used by another process;
- display scale and monitor arrangement for DPI or icon-rendering issues;
- a cropped screenshot or short recording with private paths removed.

For single-instance problems, confirm whether an XCC process remains in Task Manager and whether the tray icon is present.

## Build and CI diagnostics

Include the failing command and the final relevant error block. Standard gates are:

```powershell
python -m compileall -q src tests scripts gui.py run.py hotkey.py
python scripts\check_version_consistency.py
python -m pytest -q
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
powershell -ExecutionPolicy Bypass -File scripts\smoke_packaged_app.ps1
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1
```

For release-candidate failures:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1
```

Report whether a packaged XCC process was still running when build cleanup failed. Quit it from the tray before repeating a build.

## Config-recovery defects

The default config path is:

```text
%USERPROFILE%\.xcc\config.json
```

Do not attach the full file when it contains private paths. Provide only the smallest sanitized keys needed to reproduce the issue.

## Sanitization checklist

Remove or replace:

- credentials, tokens, keys, and connection strings;
- private or proprietary source;
- confidential Git diffs;
- usernames and absolute profile paths;
- internal repository URLs;
- clipboard content unrelated to the defect;
- computer names and other personal identifiers.

Usually sufficient:

- XCC version;
- Windows version/build;
- relative paths;
- warning categories and line numbers;
- mode, outcome, counts, and timing;
- the relevant exception or final command output.

Security vulnerabilities must follow `SECURITY.md` and must not be filed publicly.
