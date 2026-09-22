# XCC v1.4.0 Release Checklist

Use with [`M17_VALIDATION.md`](M17_VALIDATION.md). Every checked item must refer to the same release commit and final ZIP SHA-256.

## A. Freeze

- [ ] canonical version is `1.4.0`
- [ ] README, changelog, architecture, UI reference, validation, release notes, roadmap are synchronized
- [ ] `python -m compileall -q src tests scripts gui.py` passes
- [ ] `python scripts\check_version_consistency.py` passes
- [ ] `python -m pytest -q` passes
- [ ] branch is `main`, working tree clean, local `main == origin/main`
- [ ] CI is green for the release commit

## B. Collect regression

- [ ] Paste Paths + guarded `Ctrl+V`
- [ ] Selected Files Review transactionality
- [ ] all four collection modes
- [ ] source fidelity and Git staged/unstaged separation
- [ ] ignore rules, safety, budget, cancellation
- [ ] built-in excluded directories are pruned before descent without breaking `.gitignore` / `.xccignore` negation semantics
- [ ] Last Run rendering
- [ ] tray, Restore / Show hotkey, autostart, config recovery, single instance

## C. Attachments

- [ ] Add Files and Paste Paths accept ordered explicit regular files
- [ ] traversal/missing/directory/duplicate handling passes
- [ ] file count and aggregate byte size are correct
- [ ] Size values align under the Size header
- [ ] Copy Files publishes the full ordered selection to Explorer
- [ ] stale file immediately before copy fails explicitly
- [ ] Send One-by-One preserves order
- [ ] changing foreground focus mid-handoff stops before input reaches the new window
- [ ] cancellation restores normal Attachments controls
- [ ] no Enter/message submission occurs
- [ ] Create ZIP & Copy produces a valid archive
- [ ] extracted hashes match original files
- [ ] archive paths are safe/relative and mixed-location collisions are deterministic
- [ ] cancellation/failure never publishes a partial ZIP
- [ ] Open bundle location works
- [ ] 7-day managed-bundle cleanup does not touch source files

## D. Hotkeys

- [ ] Restore / Show defaults to enabled `Ctrl+Alt+X`
- [ ] changed Restore / Show shortcut persists after restart
- [ ] occupied/conflicting shortcut is rejected with previous registration preserved
- [ ] Collect & Copy enable/disable/reset works
- [ ] Attachment Handoff hotkey enable/disable/reset works
- [ ] duplicate enabled shortcuts are rejected

## E. Persistent Runtime History

- [ ] collection event survives restart
- [ ] Copy Files / ZIP / Handoff metadata survives restart
- [ ] newest-200 retention passes
- [ ] absolute collection/attachment paths are sanitized
- [ ] Export JSON matches `xcc-runtime-history` schema v1
- [ ] Clear History persists across restart
- [ ] malformed top-level JSON is preserved as `history.corrupt-*.json`
- [ ] malformed records are skipped while valid records survive
- [ ] no source body, Git diff body, secret value, attachment body, target-window identity, or raw failure body is serialized

## F. UI / responsive / DPI

- [ ] `920×620` minimum window passes
- [ ] Full HD baseline passes
- [ ] supported Windows/interface-scale cases pass
- [ ] Attachments `2 columns -> stacked` reflow passes
- [ ] Settings `2 columns -> 1` reflow passes
- [ ] History, Settings, Attachments, and About share the page-surface width contract
- [ ] About product composition/badges/runtime rows reflow correctly
- [ ] no normal horizontal page scrollbars
- [ ] maximize/restore and tray/hotkey restore pass
- [ ] QSS startup is free of token/color parser warnings

## G. Portable candidate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.4.0
```

- [ ] `XCC-Context-Collector-v1.4.0-win64.zip` exists
- [ ] checksum exists and matches
- [ ] packaged `VERSION.txt` is `1.4.0`
- [ ] executable version resource is `1.4.0`
- [ ] packaged assets required by Collect and Attachments are present
- [ ] packaged startup smoke passes
- [ ] packaged build contains every Attachments navigation/action asset

## H. Publish

- [ ] annotated `v1.4.0` tag pushed
- [ ] release uses `docs/releases/v1.4.0.md`
- [ ] ZIP and checksum attached
- [ ] release published

## I. Public verification

- [ ] public ZIP/checksum downloaded independently
- [ ] SHA-256 passes
- [ ] package extracts and starts
- [ ] About and `VERSION.txt` show `1.4.0`
- [ ] one normal Collect workflow passes
- [ ] one Copy Files workflow passes
- [ ] one Send One-by-One workflow passes
- [ ] one Create ZIP & Copy workflow passes
- [ ] persistent History survives restart
- [ ] release badge resolves to v1.4.0
- [ ] roadmap marked `DONE — RELEASED`
