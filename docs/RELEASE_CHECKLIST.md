# XCC v1.3.1 Release Checklist

Use with [`M16_VALIDATION.md`](M16_VALIDATION.md). Every checked item must refer to the same release commit and final ZIP SHA-256.

## A. Freeze

- [ ] canonical version is `1.3.1`
- [ ] README, changelog, architecture, UI reference, validation, release notes, roadmap are final
- [ ] `python -m compileall -q src tests scripts gui.py` passes
- [ ] `python scripts\check_version_consistency.py` passes
- [ ] `python -m pytest -q` passes
- [ ] branch is `main`, working tree clean, local `main == origin/main`
- [ ] CI is green for the release commit

## B. v1.3.1 UI / DPI gate

- [ ] `920×620` minimum window passes
- [ ] Full HD baseline passes
- [ ] QHD Windows scaling `100% / 125% / 150%` passes where available
- [ ] Interface scale Auto/manual persistence + restart behavior passes
- [ ] Collect responsive width/height behavior passes
- [ ] Settings two-column → one-column reflow passes
- [ ] History long metadata/path wrapping passes
- [ ] About scale/badge reflow passes
- [ ] Paste Paths and Selected Files Review fit the current work area
- [ ] no normal horizontal page scrollbars
- [ ] maximize/restore, minimize/restore, tray/hotkey restore pass
- [ ] DPI-aware logo/SVG/window controls/X-SERIES footer render correctly
- [ ] mixed-DPI/secondary monitor is PASS or explicitly NOT TESTED

## C. Existing product regression

- [ ] Paste Paths + guarded `Ctrl+V`
- [ ] Selected Files Review transactionality
- [ ] all four collection modes
- [ ] source fidelity and Git staged/unstaged separation
- [ ] ignore rules, safety, budget, cancellation
- [ ] Last Run / Runtime History
- [ ] tray, native hotkey, autostart, config recovery, single instance

## D. Automated candidate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.1
```

- [ ] `XCC-Context-Collector-v1.3.1-win64.zip` exists
- [ ] checksum exists and matches
- [ ] automated report declares `xcc_version: 1.3.1`, `passed: true`
- [ ] automated report includes `responsive_regression: true`
- [ ] packaged asset smoke includes `x-series.png`

## E. Clean-host evidence / readiness

- [ ] Windows 10 evidence passes
- [ ] Windows 11 evidence passes
- [ ] both records reference the same final SHA-256
- [ ] responsive/DPI/interface-scale manual gates are present
- [ ] final readiness command passes
- [ ] evidence JSON remains private

## F. Publish

- [ ] annotated `v1.3.1` tag pushed
- [ ] release uses `docs/releases/v1.3.1.md`
- [ ] only ZIP and checksum attached
- [ ] release published

## G. Public verification

- [ ] public ZIP/checksum downloaded independently
- [ ] downloaded SHA-256 passes
- [ ] package extracts and starts
- [ ] About and `VERSION.txt` show `1.3.1`
- [ ] Interface scale, one collection, tray/hotkey restore pass
- [ ] release badge resolves to v1.3.1
- [ ] roadmap marked `DONE — RELEASED`
