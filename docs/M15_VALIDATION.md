# M15 — v1.3.0 Validation and Release Procedure

M15 is the release blocker for XCC v1.3.0. The release must validate the v1.2.0 reliability baseline, the Selected Files Paste Paths workflow, and the final responsive PySide6 interface.

## Release rule

Do not create or push `v1.3.0` until the documentation freeze, final screenshots, automated release-candidate gate, packaged manual checks, archive validation, clean-host evidence, and repository-readiness checks pass for the same release commit and archive.

## 1. Documentation and repository preflight

Run from the repository root:

```powershell
git status --short; git branch --show-current; git fetch origin --tags; python scripts\check_version_consistency.py
```

Required state:

- branch is `main`;
- documentation and final screenshots are frozen;
- working tree is clean after the M15.10 release-candidate commit;
- local `main` equals `origin/main`;
- canonical version is `1.3.0`;
- `docs/releases/v1.3.0.md` exists;
- `docs/screenshots/xcc-collect.png` and `docs/screenshots/xcc-history.png` show the final interface.

## 2. Source regression gate

```powershell
python -m compileall -q src tests scripts gui.py run.py hotkey.py; python -m pytest -q
```

The full suite must pass. Coverage includes parser, importer, review, end-to-end Selected Files workflow, responsive geometry, dialogs, accessibility semantics, status roles, and release tooling.

## 3. Final interface gate

Verify the source application and packaged application at the supported minimum, normal window size, and maximized size:

- final sidebar brand scale and navigation density;
- Collect page title, runtime state, hotkey capsule, Setup, Last Run, and primary action;
- large, medium, compact, tall, standard, and short responsive behavior;
- no horizontal scrolling;
- vertical scrolling only when natural content cannot fit;
- keyboard-only sidebar and form navigation;
- visible focus, hover, pressed, and disabled states;
- long folder path, `Mixed locations`, and 100+ selected files;
- Windows scaling at 100%, 125%, and 150%;
- accessible names on actions, metrics, statuses, Source review, and dialogs;
- header runtime state remains separate from footer event guidance;
- `Ctrl+Alt+X` is displayed consistently.

## 4. Selected Files packaged behavior gate

Verify:

- `Paste Paths` appears only in Selected Files mode;
- guarded `Ctrl+V` does not replace text inside editable fields;
- plain, Markdown, quoted, backtick, and fenced lists are recognized;
- relative paths require a valid visible project root;
- absolute paths can be imported without a root;
- duplicate imports do not add files again;
- missing, directory, unsupported, invalid, outside-root, and external states are reported correctly;
- stale remembered roots trigger root selection again;
- separate repositories display `Mixed locations`;
- clicking Source opens Selected Files Review;
- `Delete`, `Remove Selected`, `Clear All`, `Cancel`, and `Apply Changes` behave transactionally;
- final output contains stable relative file headers.

## 5. Existing four-mode regression gate

Verify Selected Files, Full Folder, Git Changed Files, and Project Tree. Confirm source fidelity, staged/unstaged Git separation, rename/copy/delete handling, ignore rules, safety warnings, character-budget behavior, cancellation, Last Run metrics, metadata-only History, tray, native hotkey, autostart, config recovery, and single-instance behavior.

## 6. Automated release-candidate gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

The JSON report must declare `xcc_version: 1.3.0`, `passed: true`, and `gates.selected_files_regression: true`.

## 7. Manual Windows evidence

Use the evidence recorder for the exact final archive. Windows 10 and Windows 11 records must reference the same SHA-256. The v1.3.0 records include Paste Paths, root-boundary, issue-reporting, stale-root, mixed-location, review-transactionality, and relative-output gates in addition to the existing product baseline.

```powershell
python scripts\validate_release_evidence.py --expected-version 1.3.0 --expected-archive-sha256 <FINAL_SHA256> --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Evidence JSON is private validation material and must not be uploaded as a public release asset.

## 8. Final readiness

```powershell
python scripts\check_release_readiness.py --archive artifacts\XCC-Context-Collector-v1.3.0-win64.zip --checksum artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --automated-report artifacts\XCC-v1.3.0-automated-gate.json --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Final readiness validates the canonical version, release documents, archive structure, checksum, automated-gate report, explicit v1.3.0 manual gates, clean `main`, and synchronization with `origin/main`.

Expected result:

```text
Release readiness passed for v1.3.0.
```

## 9. Tag and draft release

Only after final readiness passes:

```powershell
git tag -a v1.3.0 -m "XCC Context Collector v1.3.0"; git push origin v1.3.0
```

```powershell
gh release create v1.3.0 artifacts\XCC-Context-Collector-v1.3.0-win64.zip artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --title "XCC Context Collector v1.3.0" --notes-file docs\releases\v1.3.0.md --draft
```

## 10. Post-publication verification

- download both public assets;
- verify the ZIP against the published SHA-256;
- extract and start the downloaded package;
- confirm About and `VERSION.txt` show `1.3.0`;
- repeat one Paste Paths collection;
- confirm the release badge resolves to v1.3.0;
- mark the roadmap `DONE — RELEASED` only after downloaded-asset verification.
