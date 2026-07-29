# XCC Release Checklist

This checklist supplements `docs/roadmap.md`. A release is not complete until every applicable gate has evidence.

## Repository gate

- [ ] Working tree is clean
- [ ] Current branch is `main`
- [ ] `main` equals `origin/main`
- [ ] Root `LICENSE`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `SECURITY.md` exist
- [ ] Canonical version consistency passes
- [ ] Windows CI is green for the release commit

## Automated gate

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1
```

Verify:

- [ ] Compileall passes
- [ ] Full pytest suite passes
- [ ] Isolated clean-install gate passes
- [ ] Clean PyInstaller build passes
- [ ] Packaged executable startup smoke passes
- [ ] Portable ZIP validation passes
- [ ] SHA-256 verification passes
- [ ] Automated gate JSON reports version `1.2.0` and `passed: true`

## Manual Windows gate

Record evidence with `scripts\record_manual_validation.ps1`.

- [ ] Selected Files mode
- [ ] Full Folder mode
- [ ] Git Changed Files mode
- [ ] Project Tree mode
- [ ] Safety confirmation can be disabled, persists after restart, and does not disable warning detection
- [ ] Large-project GUI responsiveness
- [ ] Cooperative cancellation
- [ ] Second concurrent job is prevented
- [ ] Cancellation does not replace clipboard content
- [ ] Tray restore and Quit
- [ ] Native hotkey restore
- [ ] Hotkey conflict remains non-fatal
- [ ] Autostart shortcut creation/removal
- [ ] Invalid-config recovery
- [ ] Single-instance restore
- [ ] Clean Windows 10 packaged smoke evidence
- [ ] Clean Windows 11 packaged smoke evidence
- [ ] Combined evidence validator passes

## Publication gate

- [ ] `src/xcc/__init__.py` declares `1.2.0`
- [ ] README declares v1.2.0 in English and Russian
- [ ] CHANGELOG v1.2.0 section is finalized and dated
- [ ] `docs/releases/v1.2.0.md` is final
- [ ] `docs/roadmap.md` reflects the final gate state
- [ ] Versioned ZIP and `.sha256` are attached
- [ ] Archive checksum is verified after upload
- [ ] Local and remote tag are `v1.2.0`
- [ ] GitHub Release is reviewed and published

## Final readiness command

```powershell
python scripts\check_release_readiness.py `
  --archive artifacts\XCC-Context-Collector-v1.2.0-win64.zip `
  --checksum artifacts\XCC-Context-Collector-v1.2.0-win64.zip.sha256 `
  --evidence artifacts\manual-validation\<windows-10-record>.json `
  --evidence artifacts\manual-validation\<windows-11-record>.json
```
