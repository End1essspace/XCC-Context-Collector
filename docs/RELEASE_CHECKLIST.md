# XCC Release Checklist

This checklist is the operational companion to `docs/M10_VALIDATION.md`. A release is not complete until every applicable item has objective evidence.

## 1. Documentation and version freeze

- [ ] `src/xcc/__init__.py` declares `1.2.0`
- [ ] `pyproject.toml` reads the version dynamically from `xcc.__version__`
- [ ] README contains `Current version: **v1.2.0**`
- [ ] README contains `Текущая версия: **v1.2.0**`
- [ ] README screenshots and documentation links resolve
- [ ] `CHANGELOG.md` contains a dated `[1.2.0]` section
- [ ] `docs/releases/v1.2.0.md` is final and user-facing
- [ ] `docs/roadmap.md` reports the release-candidate state accurately
- [ ] Architecture, security, contributing, diagnostics, portable-use, and validation docs match implemented behavior
- [ ] No documentation contains private paths, secrets, temporary hashes, or local-only instructions

Run:

```powershell
python scripts\check_version_consistency.py
python -m pytest tests\test_project_metadata.py tests\test_repository_maturity.py tests\test_m10_release_candidate.py -q
```

## 2. Repository state

- [ ] Current branch is `main`
- [ ] Working tree is clean
- [ ] `main` equals `origin/main`
- [ ] Final release commit is pushed
- [ ] Windows CI is green for that exact commit
- [ ] Root `LICENSE`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `SECURITY.md` exist
- [ ] No generated `build`, `dist`, `*.spec`, cache, `*.egg-info`, or executable files are tracked

Check:

```powershell
git status
git branch --show-current
git rev-parse HEAD
git rev-parse origin/main
```

## 3. Workspace preparation

- [ ] All packaged XCC processes are closed, including tray instances
- [ ] Cleanup dry run was reviewed
- [ ] Normal generated workspace outputs were removed
- [ ] `artifacts` was preserved for release evidence

```powershell
Get-Process -Name "XCC Context Collector" -ErrorAction SilentlyContinue | Stop-Process -Force
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1 -DryRun
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1
```

## 4. Automated release-candidate gate

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1
```

Verify:

- [ ] Compileall passes
- [ ] Canonical version consistency passes
- [ ] Full pytest suite passes
- [ ] Isolated clean-install gate passes
- [ ] Supported GUI imports without the legacy dependency group
- [ ] Clean PyInstaller build passes
- [ ] Required application, tray, and navigation assets are packaged
- [ ] Packaged executable startup smoke passes
- [ ] Portable ZIP is created
- [ ] Archive contract validation passes
- [ ] SHA-256 generation and verification pass
- [ ] Automated gate JSON reports version `1.2.0`
- [ ] Automated gate JSON reports `passed: true`

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.2.0-win64.zip
artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256
artifacts\XCC-v1.2.0-automated-gate.json
```

## 5. Manual packaged UI gate

- [ ] Title-bar icon is correct
- [ ] Taskbar icon is correct
- [ ] Header and About artwork are visible
- [ ] Tray icon is visible and not blank
- [ ] Tray menu opens correctly
- [ ] Lucide navigation icons are sharp at Windows DPI scaling
- [ ] Sidebar geometry and active/hover states are correct
- [ ] `About` is anchored at the bottom of the sidebar
- [ ] Settings groups align at the top
- [ ] Current screenshots represent the final release UI

## 6. Four-mode behavior gate

- [ ] Selected Files mode
- [ ] Duplicate-basename selected files remain distinguishable
- [ ] Cross-folder or cross-root selection remains stable
- [ ] Full Folder mode
- [ ] Root `.gitignore` behavior
- [ ] `.xccignore` behavior and negation
- [ ] Git Changed Files mode
- [ ] Staged and unstaged diffs remain separate
- [ ] Untracked, rename, copy, and delete semantics
- [ ] Project Tree mode
- [ ] Project Tree output contains no file payload sections
- [ ] All modes obey the configured character limit

## 7. Fidelity, safety, and result-health gate

- [ ] Source whitespace fidelity fixture passes
- [ ] Compact and non-compact file payloads are identical
- [ ] Budget output never exceeds the configured limit
- [ ] No source file or Git diff is silently cut mid-section
- [ ] Omitted and summarized content is reported
- [ ] Safety warning detection works
- [ ] Safety confirmation dialog appears when enabled
- [ ] Safety confirmation can be disabled
- [ ] Disabled state persists after restart
- [ ] Disabling the dialog does not disable detection or metadata
- [ ] No detected secret value is shown in summaries or history
- [ ] Outcomes render correctly: success, warnings, cancelled, failed
- [ ] Runtime history stores metadata only

## 8. Responsiveness and cancellation gate

- [ ] Large-project GUI remains responsive
- [ ] Window can move, resize, minimize, and restore during collection
- [ ] Non-conflicting page navigation remains available
- [ ] Second concurrent collection is prevented
- [ ] Cancel returns controls to idle state
- [ ] Cancelled run is recorded in History
- [ ] Cancellation does not replace existing clipboard content
- [ ] A subsequent full collection succeeds

## 9. Windows integration gate

- [ ] Tray single-click toggle
- [ ] Tray double-click restore
- [ ] Tray Quit terminates the process
- [ ] `Esc` hides to tray
- [ ] Native `Ctrl+Alt+X` restore
- [ ] Hotkey conflict remains non-fatal
- [ ] Start with Windows shortcut creation
- [ ] Start with Windows shortcut removal
- [ ] Start minimized to tray
- [ ] Start maximized
- [ ] Close to tray
- [ ] Invalid-config recovery
- [ ] Second launch restores the existing instance
- [ ] Packaged app starts without Python installed

## 10. Clean-host evidence gate

- [ ] Complete Windows 10 x64 record exists
- [ ] Complete Windows 11 x64 record exists
- [ ] Both records declare XCC `1.2.0`
- [ ] Both records reference the same final archive SHA-256
- [ ] Every required gate is present and passed
- [ ] Evidence contains only the intended operator alias, OS/computer metadata, gate booleans, archive hash, timestamp, and sanitized notes
- [ ] Combined evidence validator passes

```powershell
python scripts\validate_release_evidence.py `
  --expected-version 1.2.0 `
  --expected-archive-sha256 <FINAL_SHA256> `
  --evidence artifacts\manual-validation\<windows-10-record>.json `
  --evidence artifacts\manual-validation\<windows-11-record>.json
```

## 11. Final readiness gate

```powershell
python scripts\check_release_readiness.py `
  --archive artifacts\XCC-Context-Collector-v1.2.0-win64.zip `
  --checksum artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256 `
  --evidence artifacts\manual-validation\<windows-10-record>.json `
  --evidence artifacts\manual-validation\<windows-11-record>.json
```

- [ ] Command prints `Release readiness passed for v1.2.0.`
- [ ] Working tree is still clean after the command
- [ ] Archive name is exactly `XCC-Context-Collector-v1.2.0-win64.zip`
- [ ] Companion checksum file is present

## 12. Tag and GitHub Release

Only after the final readiness gate passes:

```powershell
git tag -a v1.2.0 -m "XCC Context Collector v1.2.0"
git push origin v1.2.0
```

Create the draft release:

```powershell
gh release create v1.2.0 `
  artifacts\XCC-Context-Collector-v1.2.0-win64.zip `
  artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256 `
  --title "XCC Context Collector v1.2.0" `
  --notes-file docs\releases\v1.2.0.md `
  --draft
```

- [ ] Tag is annotated and points to the release commit
- [ ] Draft title is correct
- [ ] Release notes are rendered correctly
- [ ] ZIP is attached
- [ ] `.sha256` is attached
- [ ] No internal evidence JSON is attached publicly
- [ ] Draft is reviewed before publication

## 13. Post-publication verification

- [ ] Downloaded GitHub ZIP matches the published checksum
- [ ] Downloaded package starts successfully
- [ ] About shows `1.2.0`
- [ ] `VERSION.txt` shows `1.2.0`
- [ ] Release badge resolves to v1.2.0
- [ ] GitHub Release contains both expected assets
- [ ] Roadmap is updated from release candidate to complete only after verification
