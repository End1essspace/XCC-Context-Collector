## Summary

Describe the user-visible or repository-level change and the problem it solves.

## Scope

- Affected area:
- Related issue or roadmap milestone:
- Out of scope:

## Validation

- [ ] `python -m compileall -q src tests scripts gui.py run.py hotkey.py`
- [ ] `python scripts/check_version_consistency.py`
- [ ] `python -m pytest -q`
- [ ] Regression tests were added or updated for behavior changes
- [ ] Packaged build and startup smoke were run when packaging, assets, tray, startup, or release code changed
- [ ] Portable ZIP and checksum validation were run when release packaging changed
- [ ] UI was checked at relevant Windows display scaling when visual code or artwork changed

Exact commands and results:

```text

```

## Documentation and compatibility

- [ ] README and relevant docs match the implemented behavior
- [ ] Current version and release-note markers remain consistent
- [ ] Screenshots were updated only when they represent the release UI
- [ ] Supported PySide6 product behavior remains primary
- [ ] Unsupported legacy workflows were not expanded unintentionally

## Safety and repository hygiene

- [ ] No credentials, tokens, private keys, connection strings, or secret values are committed
- [ ] No private paths, collected project context, proprietary source, or confidential Git diff is committed
- [ ] No `build`, `dist`, `artifacts`, `release`, cache, `*.egg-info`, generated executable, or local `.xcc` data is committed
- [ ] Safety-warning metadata remains sanitized
- [ ] The change stays focused on one coherent defect, milestone, or documentation update

## Visual evidence

Add sanitized before/after screenshots or a short recording when the interface changed.
