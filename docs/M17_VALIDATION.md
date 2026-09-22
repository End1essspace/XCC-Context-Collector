# XCC v1.4.0 / M17 Validation

Target version: `1.4.0`  
Status: **RELEASE CANDIDATE GATE**

This document is the canonical validation plan for the v1.4.0 Attachments & Windows Workflow release.

## 1. Source gate

```powershell
python -m compileall -q src tests scripts gui.py
python scripts\check_version_consistency.py
python -m pytest -q
```

All commands must pass from a clean checkout on the release commit.

Large-project traversal must also verify that built-in excluded directories such as `.git`, `.venv`, `node_modules`, `build`, and `dist` are pruned before descent, while `.gitignore` / `.xccignore` negation semantics remain intact for non-built-in paths.

## 2. Version gate

Verify:

- `xcc.__version__ == "1.4.0"`;
- README English/Russian markers show v1.4.0;
- `CHANGELOG.md` contains `[1.4.0]`;
- `docs/releases/v1.4.0.md` declares `Version: 1.4.0`;
- `docs/UI_REFERENCE_v1.4.0.md` and this file exist;
- packaged `VERSION.txt` and Windows version resource match 1.4.0.

## 3. Attachments selection

Cover:

- empty / one / 100+ files;
- duplicate case/slash variants;
- Unicode, spaces and long paths;
- missing/stale/inaccessible files;
- absolute external files and mixed locations;
- duplicate basenames;
- project-root traversal attempts;
- directory input rejection;
- extensions unsupported by Collect but valid as explicit attachments.

## 4. Direct clipboard transfer

Packaged Windows validation:

1. select multiple known files;
2. Copy Files;
3. verify Windows clipboard/explorer receives the full ordered file list;
4. paste to a normal folder;
5. verify file hashes match originals;
6. delete/stale one source just before Copy Files and confirm explicit failure.

XCC guarantees clipboard preparation, not acceptance by every third-party target.

## 5. Automated Attachment Handoff

Use a target that accepts the same files as separate paste events.

Verify:

- button-start countdown;
- exact file order;
- one clipboard file + one `Ctrl+V` per step;
- `N/total` progress;
- same target HWND for the sequence;
- switch focus mid-sequence: XCC stops before pasting into the new window;
- cancel restores normal controls;
- stale later file stops without skipping;
- hotkey start/cancel when enabled;
- no Enter/message submission;
- History contains metadata only.

## 6. ZIP bundle

Verify:

- one file and large multi-file selections;
- ZIP64-capable path;
- streaming progress;
- cancellation removes `.partial` output and publishes nothing;
- safe relative paths;
- mixed-location namespaces;
- collision suffixes;
- no absolute / `..` members;
- source change/disappearance during bundling fails;
- extracted hashes match originals;
- completed ZIP copies as one file object;
- Open bundle location works;
- retention cleanup touches only stale XCC-managed bundles.

## 7. Persistent Runtime History

Verify:

- collection event survives restart;
- Copy Files / Handoff / ZIP metadata survives restart;
- newest-200 retention;
- metadata-only export schema;
- absolute paths sanitized;
- bundle path reduced to filename;
- Clear History survives restart;
- malformed top-level store preserved as `history.corrupt-*.json`;
- malformed individual records skipped;
- no collected source, Git diff, secret value, attachment content, target-window identity, or raw failure body stored.

## 8. Configurable hotkeys

Verify:

- Restore / Show default;
- persistence after edit/restart;
- occupied shortcut rejection with rollback;
- reset;
- optional Collect & Copy;
- optional Attachment Handoff;
- duplicate enabled-shortcut conflict rejection.

## 9. Responsive / DPI / polish

Validate:

- `920×620`;
- Full HD baseline;
- available Windows scaling/interface-scale cases;
- Attachments 2-column -> stacked;
- Settings 2-column -> 1;
- shared outer width for Attachments/History/Settings/About;
- centered Size column;
- single selected-row indicator;
- About 2-column -> 1 and badge reflow;
- no normal horizontal page scrolling;
- maximize/restore/tray/hotkey lifecycle;
- clean startup with no XCC QSS parser warnings.

## 10. Portable release candidate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.4.0
```

Required output:

```text
XCC-Context-Collector-v1.4.0-win64.zip
XCC-Context-Collector-v1.4.0-win64.zip.sha256
```

The archive/checksum, automated evidence and manual evidence must refer to the same release commit and SHA-256.

The automated gate report must include `selected_files_regression`, `global_hotkey_regression`, `attachments_regression`, `persistent_history_regression`, and `responsive_regression`. Manual evidence for v1.4.0 must include the M17 Attachment/Handoff/ZIP/History/UI gates defined by `scripts/validate_release_evidence.py`.

## 11. Publication completion

v1.4.0 is complete only after the public ZIP/checksum are independently downloaded and verified, then the extracted public build passes:

- startup/version check;
- one normal Collect workflow;
- Copy Files;
- Send One-by-One;
- Create ZIP & Copy;
- persistent History restart;
- tray/hotkey restore.
