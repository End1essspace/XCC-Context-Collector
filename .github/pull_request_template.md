## Summary

Describe the user-visible or repository-level change.

## Validation

- [ ] `python -m compileall -q src tests scripts gui.py run.py hotkey.py`
- [ ] `python -m pytest -q`
- [ ] `python scripts/check_version_consistency.py`
- [ ] Packaged build tested when build/release code changed
- [ ] Release archive validator tested when packaging code changed

## Safety and scope

- [ ] No credentials, private paths, collected project content, or generated binaries are committed
- [ ] Documentation and tests were updated where required
- [ ] The change stays within the current roadmap milestone
