# XCC v1.3.0 Release Checklist

Operational companion to `docs/M15_VALIDATION.md`.

Every completed item must refer to the same release commit and final archive SHA-256.

## 1. Documentation and screenshots

- [x] `src/xcc/__init__.py` declares `1.3.0`
- [x] README contains English and Russian v1.3.0 markers
- [x] README uses the final Collect and History screenshots
- [x] README describes Selected Files import/review and sidebar wheel navigation
- [x] `CHANGELOG.md` contains dated `[1.3.0]`
- [x] `docs/releases/v1.3.0.md` is final and user-facing
- [x] `docs/ARCHITECTURE.md` matches the implemented product boundary
- [x] `docs/UI_REFERENCE_v1.3.0.md` matches final geometry and interactions
- [x] `docs/roadmap.md` reports M11–M15.9 accurately
- [x] final screenshots contain no credentials, user-profile names, private repositories, client data, or unrelated clipboard content
- [x] deliberate public repository paths are documented as acceptable demonstration content
- [x] documentation and screenshots are ready for the release-candidate commit

Source verification:

```powershell
python -m compileall -q src tests scripts gui.py; python scripts\check_version_consistency.py; python -m pytest -q
```

## 2. Repository state

- [ ] branch is `main`
- [ ] documentation-and-screenshot freeze commit is pushed
- [ ] working tree is clean
- [ ] local `main` equals `origin/main`
- [ ] Windows CI is green for the release commit

```powershell
git status --short
```

```powershell
git branch --show-current
```

```powershell
git rev-parse HEAD
```

```powershell
git rev-parse origin/main
```

## 3. Final interface

- [ ] sidebar brand scale and navigation density match the final screenshots
- [ ] Setup and Last Run density are balanced
- [ ] dialogs belong to the same design system
- [ ] `920×620`, normal, and maximized 2K layouts pass
- [ ] Windows scaling 100%, 125%, and 150% passes
- [ ] keyboard-only navigation passes
- [ ] focus, hover, pressed, selected, and disabled states remain distinct
- [ ] long paths, `Mixed locations`, and 100+ files do not break layout
- [ ] header runtime state and footer event status remain distinct
- [ ] hotkey displays as `Ctrl+Alt+X`
- [ ] screenshots were captured from the final build

### Sidebar wheel navigation

- [ ] the complete sidebar surface accepts wheel input
- [ ] wheel down selects the next page
- [ ] wheel up selects the previous page
- [ ] one input event changes at most one page
- [ ] partial touchpad/high-resolution deltas accumulate correctly
- [ ] reversing direction resets the partial accumulator
- [ ] navigation stops at Collect and About
- [ ] no sidebar scrollbar or `QScrollArea` is present
- [ ] focus follows the active tab
- [ ] page-content scrolling remains independent

## 4. Selected Files workflow

- [ ] Paste Paths appears only in Selected Files
- [ ] guarded `Ctrl+V` works
- [ ] plain and Markdown path lists work
- [ ] relative paths resolve under a visible project root
- [ ] canonical traversal outside the root is rejected
- [ ] absolute paths work without a root
- [ ] duplicates are skipped
- [ ] missing, directory, unsupported, invalid, outside-root, and external paths are reported
- [ ] stale root recovery works
- [ ] mixed repositories show `Mixed locations`
- [ ] Source opens Selected Files Review by mouse and keyboard
- [ ] extended selection and `Delete` work
- [ ] Remove Selected, Clear All, Cancel, and Apply Changes behave transactionally
- [ ] final output has stable relative headers

## 5. Existing behavior and Windows integration

- [ ] all four collection modes pass
- [ ] source-fidelity and budget contracts pass
- [ ] staged/unstaged Git separation passes
- [ ] rename/copy/delete/untracked, spaces, and Unicode paths pass
- [ ] `.gitignore`, `.xccignore`, and built-in exclusions pass
- [ ] safety detection and optional confirmation pass
- [ ] cancellation never copies partial output
- [ ] Last Run and metadata-only Runtime History pass
- [ ] tray, hotkey, autostart, config recovery, and single instance pass
- [ ] packaged application starts without Python installed
- [ ] all runtime assets are present

## 6. Automated release-candidate gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

- [ ] compileall passes
- [ ] version consistency passes
- [ ] Selected Files regression gate passes
- [ ] full pytest passes
- [ ] clean-install validation passes
- [ ] PyInstaller build passes
- [ ] packaged startup and asset smoke passes
- [ ] portable ZIP is generated
- [ ] SHA-256 file is generated
- [ ] archive validation passes
- [ ] checksum validation passes
- [ ] automated report declares `xcc_version: 1.3.0`
- [ ] automated report declares `passed: true`
- [ ] automated report binds the exact archive filename and SHA-256

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

## 7. Packaged build

- [ ] `XCC Context Collector.exe` starts
- [ ] `_internal` exists
- [ ] `VERSION.txt` contains `1.3.0`
- [ ] About and footer show `1.3.0`
- [ ] no console window appears
- [ ] second launch restores the existing instance
- [ ] close-to-tray works
- [ ] tray restore and tray quit work
- [ ] `Esc` hides to tray
- [ ] `Ctrl+Alt+X` restores the window
- [ ] Start with Windows can be enabled and removed
- [ ] sections 3–5 pass in the packaged build

## 8. Clean-host evidence

- [ ] Windows 10 record exists
- [ ] Windows 11 record exists
- [ ] both declare XCC `1.3.0`
- [ ] both reference the same archive SHA-256
- [ ] both contain every explicit v1.3.0 manual gate
- [ ] combined evidence validator passes

```powershell
python scripts\validate_release_evidence.py --expected-version 1.3.0 --expected-archive-sha256 <FINAL_SHA256> --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

## 9. Final readiness

```powershell
python scripts\check_release_readiness.py --archive artifacts\XCC-Context-Collector-v1.3.0-win64.zip --checksum artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --automated-report artifacts\XCC-v1.3.0-automated-gate.json --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

- [ ] command prints `Release readiness passed for v1.3.0.`
- [ ] working tree remains clean
- [ ] local `main` still equals `origin/main`
- [ ] Windows CI is green

## 10. Tag and draft release

```powershell
git tag -a v1.3.0 -m "XCC Context Collector v1.3.0"
```

```powershell
git push origin v1.3.0
```

```powershell
gh release create v1.3.0 artifacts\XCC-Context-Collector-v1.3.0-win64.zip artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --title "XCC Context Collector v1.3.0" --notes-file docs\releases\v1.3.0.md --draft
```

- [ ] annotated tag points to the release commit
- [ ] draft title and notes are correct
- [ ] ZIP and checksum are attached
- [ ] evidence JSON is not public

## 11. Post-publication

- [ ] downloaded ZIP matches the published checksum
- [ ] downloaded application starts
- [ ] About, footer, and `VERSION.txt` show `1.3.0`
- [ ] Paste Paths works in the downloaded build
- [ ] sidebar wheel and focus behavior work in the downloaded build
- [ ] release badge resolves to v1.3.0
- [ ] both public assets are present
- [ ] roadmap is marked `DONE — RELEASED`
- [ ] release announcement is published
