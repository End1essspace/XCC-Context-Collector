# Bug-Report Diagnostics

A useful XCC bug report is reproducible and sanitized.

## Required details

```text
XCC version:
Distribution: packaged ZIP or source checkout
Windows version and architecture:
Collection mode:
Compact mode:
Max output characters:
Outcome:
Warnings / errors:
Reproduction steps:
```

For packaged builds, copy the version from `VERSION.txt` or the About page. For source checkouts, run:

```powershell
python -c "import xcc; print(xcc.__version__)"
```

## Build and CI diagnostics

When the problem involves packaging, include the failing command and the final relevant error block from:

```powershell
python -m compileall -q src tests scripts gui.py run.py hotkey.py
python scripts/check_version_consistency.py
python -m pytest -q
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
powershell -ExecutionPolicy Bypass -File scripts\smoke_packaged_app.ps1
powershell -ExecutionPolicy Bypass -File scripts\package_release.ps1
```

## Sanitization rules

Never attach the collected XCC output unless the repository is intentionally public and reviewed. Remove:

- secret values and credentials;
- private or proprietary source;
- Git diffs containing confidential code;
- usernames and absolute profile paths;
- internal repository URLs;
- unrelated logs.

Warning categories, relative paths, line numbers, counts, and outcome labels are usually sufficient.
