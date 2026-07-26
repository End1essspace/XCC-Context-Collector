# XCC Release Checklist

This checklist supplements `docs/roadmap.md`. A release is not complete until every applicable gate is evidenced.

## Repository gate

- [ ] Working tree is clean
- [ ] `main` is synchronized with `origin/main`
- [ ] Root `LICENSE`, `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `SECURITY.md` exist
- [ ] Version consistency check passes
- [ ] Windows CI is green

## Automated gate

- [ ] Compileall passes
- [ ] Full pytest suite passes
- [ ] Clean PyInstaller build passes
- [ ] Packaged executable startup smoke passes
- [ ] Portable ZIP validation passes
- [ ] SHA-256 verification passes

## Manual Windows gate

- [ ] Selected Files mode
- [ ] Full Folder mode
- [ ] Git Changed Files mode
- [ ] Project Tree mode
- [ ] Large-project responsiveness and cancellation
- [ ] Tray restore and Quit
- [ ] Native hotkey restore and conflict handling
- [ ] Autostart shortcut
- [ ] Invalid-config recovery
- [ ] Clean Windows 10 packaged smoke
- [ ] Clean Windows 11 packaged smoke

## Publication gate

- [ ] `src/xcc/__init__.py` version updated
- [ ] README version updated
- [ ] CHANGELOG release section finalized
- [ ] Release notes created
- [ ] Versioned ZIP and `.sha256` attached
- [ ] Archive checksum verified after upload
- [ ] Git tag matches the canonical version
- [ ] GitHub Release published
