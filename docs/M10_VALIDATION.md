# M10 — v1.2.0 Validation Procedure

M10 is the final release blocker for XCC v1.2.0. A green unit-test suite alone is not enough: the final tag requires one reproducible automated artifact and complete manual evidence from clean Windows 10 and Windows 11 hosts.

## Release rules

- Validate the exact commit that will be tagged.
- Use the same final ZIP SHA-256 for both Windows evidence records.
- Use the packaged executable for manual checks, not `python gui.py`.
- Do not create or push `v1.2.0` until `check_release_readiness.py` passes.
- Any code, UI, asset, packaging, or documentation change after validation invalidates the previous release candidate and requires the automated gate to be rerun.

## 1. Freeze and synchronize the release candidate

From the repository root:

```powershell
git switch main
git pull --rebase origin main
git status
```

Required state:

```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

Quit every packaged XCC process, including hidden tray instances:

```powershell
Get-Process -Name "XCC Context Collector" -ErrorAction SilentlyContinue | Stop-Process -Force
```

Preview workspace cleanup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1 -DryRun
```

Clean normal generated outputs while preserving release evidence:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\clean_workspace.ps1
```

## 2. Run the automated release-candidate gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1
```

The script performs:

- source, test, script, and launcher compilation;
- canonical version consistency validation;
- the full pytest suite;
- isolated clean-install validation on CPython 3.13;
- a clean PyInstaller build;
- packaged offscreen startup smoke;
- required runtime-asset checks;
- portable ZIP creation;
- SHA-256 generation and verification;
- release archive contract validation;
- a machine-readable automated gate report.

Expected artifacts:

```text
artifacts\XCC-Context-Collector-v1.2.0-win64.zip
artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256
artifacts\XCC-v1.2.0-automated-gate.json
```

The automated JSON must report:

```text
version: 1.2.0
passed: true
```

Record the final archive hash:

```powershell
(Get-FileHash artifacts\XCC-Context-Collector-v1.2.0-win64.zip -Algorithm SHA256).Hash.ToLowerInvariant()
```

Do not rebuild the ZIP between the Windows 10 and Windows 11 sessions.

## 3. Prepare each clean Windows host

Required hosts:

```text
one Windows 10 x64 host
one Windows 11 x64 host
```

For each host:

1. Transfer the exact final ZIP and `.sha256` file.
2. Verify the SHA-256 before extraction.
3. Before installing any development environment, confirm the packaged application starts without Python.
4. Extract to a new writable directory.
5. Remove or rename any old `%USERPROFILE%\.xcc\config.json` before the clean-start checks.
6. Confirm no previous XCC process or Startup shortcut remains.
7. Keep a clean checkout of the exact release commit available for `record_manual_validation.ps1`; the recorder reads the canonical version from `src/xcc/__init__.py` and therefore requires Python after the no-Python startup check is complete.

The two hosts may be physical computers. Virtual machines are not required by the evidence format.

## 4. Validate packaged visual assets and shell behavior

Open `XCC Context Collector.exe` and confirm:

- the Windows title bar shows the XCC application icon;
- the taskbar button shows the XCC application icon;
- the header and About page show the XCC artwork;
- the notification-area icon is visible and not blank;
- the tray menu opens correctly;
- Lucide sidebar icons are sharp at the host display scale;
- navigation text and icons are aligned consistently;
- `Collect`, `History`, and `Settings` remain in the upper navigation group;
- `About` is anchored at the bottom of the sidebar;
- Settings groups align at the top even when their content heights differ.

The tray icon may initially appear inside the Windows notification-area overflow menu.

## 5. Validate all four collection modes

Use sanitized test projects and verify the clipboard output, Last Run metrics, outcome, and History entry after each run.

### Selected Files

- select files from at least two directories;
- include duplicate basenames;
- verify display paths remain distinct;
- verify explicit selection bypasses project ignore rules;
- verify source whitespace remains unchanged.

### Full Folder

- use a nested project containing source, documentation, and configuration files;
- verify built-in excluded directories are absent;
- verify root `.gitignore` and `.xccignore` behavior;
- verify project tree and file sections are present;
- verify character budget never exceeds the configured limit.

### Git Changed Files

Use a repository containing, where practical:

- staged changes;
- unstaged changes;
- an untracked supported file;
- a rename;
- a delete;
- a path containing spaces or Unicode.

Confirm typed status entries are present and staged/unstaged diffs are labelled separately.

### Project Tree

- verify no `# Files` payload sections are produced;
- verify directories and files appear in deterministic structure;
- verify built-in exclusions and project ignore rules;
- verify small-budget behavior produces explicit truncation metadata.

## 6. Validate source fidelity and budget transparency

Use a sanitized fixture containing:

- repeated blank lines;
- trailing spaces;
- a multiline string;
- a Markdown or YAML block;
- a final blank line.

Compare the file payload inside generated context with the original text. Compact and non-compact modes must preserve identical file payloads.

Use a low character budget and confirm:

- final output does not exceed the limit;
- source files are not cut mid-payload;
- Git diff lines are not cut mid-line;
- omitted files and section states are reported in `# XCC Budget Summary`;
- `Partial files` remains `0` for normal file collection.

## 7. Validate responsiveness and cancellation

Use a project large enough for progress to remain visible.

1. Put a recognizable sentinel value in the clipboard.
2. Start Full Folder collection.
3. Move, resize, minimize, and restore the window while work is active.
4. Navigate to a non-conflicting page.
5. Attempt to start a second collection and confirm it cannot start.
6. Press **Cancel**.
7. Confirm controls return to idle state.
8. Confirm History records `Cancelled`.
9. Confirm the clipboard still contains the sentinel value.
10. Repeat the same collection and allow it to complete.
11. Confirm complete output is copied and result metrics update.

This closes the remaining M6 manual acceptance gate.

## 8. Validate Safety confirmation

Use a sanitized source that reliably triggers at least one safety finding.

1. Enable **Safety confirmation**.
2. Collect the source and confirm the pre-copy dialog appears.
3. Cancel and confirm no clipboard replacement occurs.
4. Repeat and accept; confirm the context is copied with warning metadata.
5. Disable **Safety confirmation** in Settings.
6. Collect the same source and confirm no modal dialog appears.
7. Confirm detection still appears in generated context, warning counters, outcome, and History metadata.
8. Restart XCC and confirm the disabled state persists.
9. Re-enable the setting and confirm the dialog returns.

Do not use real credentials for this test.

## 9. Validate Windows integration

On each host, verify:

- tray hide and restore;
- single-click tray toggle;
- double-click tray restore;
- tray **Quit** terminates the process;
- `Esc` hides the window to tray;
- `Ctrl+Alt+X` restores the window;
- a hotkey conflict is reported but does not crash or block startup;
- **Start with Windows** creates and removes the Startup shortcut;
- **Start minimized to tray** works when the tray is available;
- **Start maximized** works;
- **Close to tray** works;
- a second launch restores the existing instance;
- invalid `%USERPROFILE%\.xcc\config.json` recovers safely;
- the packaged application starts without Python installed.

## 10. Record one evidence file per OS

After all checks pass on a host:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\record_manual_validation.ps1
```

The script writes a JSON record under:

```text
artifacts\manual-validation\
```

Required records:

```text
one complete Windows 10 record
one complete Windows 11 record
```

Each record must contain:

- `xcc_version: 1.2.0`;
- the same final archive SHA-256;
- OS metadata;
- explicit pass/fail values for every required gate;
- operator and UTC timestamp;
- only sanitized optional notes.

Evidence must not contain project files, clipboard content, secrets, private paths, or configuration values. The recorder intentionally stores the operator alias and host OS/computer metadata; keep evidence private and use a non-sensitive operator alias.

## 11. Validate combined evidence

```powershell
python scripts\validate_release_evidence.py `
  --expected-version 1.2.0 `
  --expected-archive-sha256 <FINAL_SHA256> `
  --evidence artifacts\manual-validation\<windows-10-record>.json `
  --evidence artifacts\manual-validation\<windows-11-record>.json
```

The validator rejects:

- a missing Windows 10 or Windows 11 record;
- mixed XCC versions;
- different archive hashes;
- absent required gates;
- any failed gate;
- malformed evidence.

## 12. Commit the final evidence state and verify CI

Evidence files may remain local if repository policy excludes `artifacts`; the release commit itself must contain all final code, assets, tests, and documentation.

Before tagging:

```powershell
git status
git log -1 --oneline
git rev-parse HEAD
git rev-parse origin/main
```

Required:

- working tree clean;
- branch `main`;
- `HEAD` equals `origin/main`;
- Windows CI green for the exact release commit.

## 13. Run the final readiness command

```powershell
python scripts\check_release_readiness.py `
  --archive artifacts\XCC-Context-Collector-v1.2.0-win64.zip `
  --checksum artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256 `
  --evidence artifacts\manual-validation\<windows-10-record>.json `
  --evidence artifacts\manual-validation\<windows-11-record>.json
```

Expected result:

```text
Release readiness passed for v1.2.0.
```

This command validates documents, version declarations, archive structure, checksum, evidence, branch, clean working tree, and `origin/main` synchronization.

## 14. Create the tag and draft GitHub Release

Only after the readiness command passes:

```powershell
git tag -a v1.2.0 -m "XCC Context Collector v1.2.0"
git push origin v1.2.0
```

Create a draft release with the final notes and assets:

```powershell
gh release create v1.2.0 `
  artifacts\XCC-Context-Collector-v1.2.0-win64.zip `
  artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256 `
  --title "XCC Context Collector v1.2.0" `
  --notes-file docs\releases\v1.2.0.md `
  --draft
```

Review the draft in GitHub before publishing. Confirm the tag, title, notes, ZIP, checksum, and displayed asset sizes are correct.

## 15. Post-publication verification

After publishing:

- download the ZIP and checksum from GitHub Releases;
- verify the downloaded checksum again;
- extract and start the downloaded build;
- confirm About and `VERSION.txt` show `1.2.0`;
- confirm the README release badge resolves to v1.2.0;
- confirm the GitHub Release page contains both assets;
- mark M6 and M10 complete in `docs/roadmap.md` in the post-release documentation commit only if all evidence is retained and verified.
