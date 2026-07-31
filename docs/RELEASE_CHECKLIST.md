# XCC v1.3.0 Release Checklist

Use this checklist with [`M15_VALIDATION.md`](M15_VALIDATION.md). It intentionally contains no duplicated procedures.

Every checked item must refer to the same release commit and final ZIP SHA-256.

## A. Repository freeze

- [ ] C1–C4 cleanup changes are committed and pushed
- [ ] C5 documentation re-freeze is applied, source-tested, committed, and pushed
- [ ] canonical version is `1.3.0`
- [ ] README, changelog, architecture, UI reference, release notes, roadmap, and screenshots are final
- [ ] `docs/M10_VALIDATION.md` is absent
- [ ] `assets/original_icons/` is absent
- [ ] source gate passes
- [ ] branch is `main`
- [ ] working tree is clean
- [ ] local `main` equals `origin/main`
- [ ] CI is green for the release commit

Source gate:

```powershell
python -m compileall -q src tests scripts gui.py; python scripts\check_version_consistency.py; python -m pytest -q
```

## B. Source UI and workflow

- [ ] minimum, normal, maximized, 100%, 125%, and 150% layouts pass
- [ ] shell, Setup, Last Run, dialogs, Settings, History, and About pass
- [ ] mouse, keyboard, focus, disabled, long-path, mixed-location, and 100+ file states pass
- [ ] complete-sidebar wheel navigation and independent page scrolling pass
- [ ] Paste Paths and guarded `Ctrl+V` pass
- [ ] Selected Files Review is transactional
- [ ] all four collection modes pass
- [ ] source fidelity, Git separation, ignore rules, safety, budget, and cancellation pass
- [ ] tray, hotkey, autostart, config recovery, and single instance pass

Detailed cases: sections 2–4 of `M15_VALIDATION.md`.

## C. Automated candidate

- [ ] `validate_release_candidate.ps1 -ExpectedVersion 1.3.0` passes
- [ ] final ZIP exists
- [ ] checksum exists and matches the ZIP
- [ ] automated report declares `xcc_version: 1.3.0`
- [ ] automated report declares `passed: true`
- [ ] automated report binds the final filename and SHA-256

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

## D. Packaged build

- [ ] clean extraction contains executable, `_internal`, and `VERSION.txt`
- [ ] packaged application starts without Python
- [ ] version surfaces show `1.3.0`
- [ ] all required assets are present
- [ ] no console window appears
- [ ] source UI and workflow checks also pass in the package

## E. Release evidence and readiness

- [ ] Windows 10 evidence passes
- [ ] Windows 11 evidence passes
- [ ] both records reference the same final SHA-256
- [ ] final readiness passes
- [ ] evidence JSON remains private

Commands and required arguments: sections 7–8 of `M15_VALIDATION.md`.

## F. Publication

- [ ] annotated `v1.3.0` tag is pushed
- [ ] draft release uses `docs/releases/v1.3.0.md`
- [ ] only ZIP and checksum are attached
- [ ] release is published

## G. Public verification

- [ ] public ZIP and checksum are downloaded independently
- [ ] downloaded checksum passes
- [ ] downloaded package extracts and starts
- [ ] version, Paste Paths, one collection, and sidebar wheel/focus behavior pass
- [ ] release badge resolves to v1.3.0
- [ ] both public assets are present
- [ ] roadmap is marked `DONE — RELEASED`
- [ ] release announcement is published

