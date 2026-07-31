# M15 — v1.3.0 Validation and Release Procedure

Status: **ACTIVE — DOCUMENTATION AND SCREENSHOTS FROZEN; RELEASE-CANDIDATE GATE NEXT**

This procedure applies to the exact commit and archive that will become XCC v1.3.0.

## Release rule

Do not tag or publish v1.3.0 until the source gate, packaged gate, Windows evidence, final readiness, repository synchronization, and CI all pass for the same release candidate.

## 1. Documentation and repository preflight

Required public files:

```text
README.md
CHANGELOG.md
docs/ARCHITECTURE.md
docs/BUG_REPORTING.md
docs/M15_VALIDATION.md
docs/PORTABLE_ZIP.md
docs/RELEASE_CHECKLIST.md
docs/UI_REFERENCE_v1.3.0.md
docs/releases/v1.3.0.md
docs/roadmap.md
docs/screenshots/xcc-collect.png
docs/screenshots/xcc-history.png
```

Confirm:

- version markers are `1.3.0`;
- release notes contain `## Summary` and `## Validation`;
- screenshots show the final interface;
- screenshots contain no credentials, user-profile names, private repositories, client data, or unrelated clipboard content;
- a deliberate path to a public demonstration repository is acceptable;
- documentation describes wheel navigation, focus synchronization, responsive behavior, Selected Files import/review, source fidelity, safety, and release artifacts;
- the branch is `main`;
- the working tree is clean after the documentation commit;
- local `main` equals `origin/main`.

Source gate:

```powershell
python -m compileall -q src tests scripts gui.py; python scripts\check_version_consistency.py; python -m pytest -q
```

## 2. Final interface gate

Validate the source build at:

```text
920×620
normal desktop window
maximized 2K
Windows scaling 100%, 125%, 150%
```

Confirm:

- native title bar remains intact;
- sidebar brand, WORKSPACE label, upper navigation, anchored About, and footer align correctly;
- no navigation label or icon is clipped;
- Setup and Last Run remain balanced;
- Collect & Copy remains visible;
- dialogs share the final design system;
- long paths, `Mixed locations`, 100+ files, and disabled controls remain readable;
- header runtime state and footer event guidance remain distinct;
- `Ctrl+Alt+X` is displayed consistently;
- keyboard focus is visible;
- no stale secondary active/focus state remains after page navigation.

### Sidebar wheel navigation

Verify over the logo, brand text, section label, every navigation button, separators, and empty sidebar space:

- wheel down moves to the next page;
- wheel up moves to the previous page;
- one input event changes at most one page;
- partial touchpad/high-resolution deltas accumulate;
- reversing direction clears the partial accumulator;
- navigation stops at Collect and About;
- no visible sidebar scrollbar or `QScrollArea` appears;
- the newly active button receives focus;
- wheel input over the page content continues to scroll page content instead of changing tabs.

## 3. Selected Files packaged behavior gate

Verify:

- Paste Paths appears only in Selected Files mode;
- guarded `Ctrl+V` does not replace text inside editable fields;
- plain, Markdown, numbered, quoted, backtick, and fenced lists are recognized;
- relative paths require a valid visible project root;
- canonical traversal outside the root is rejected;
- absolute files can be imported without a root;
- duplicates are not added again;
- missing, directory, unsupported, invalid, outside-root, and external states are reported;
- stale remembered roots trigger root selection again;
- separate repositories display `Mixed locations`;
- Source opens Selected Files Review by mouse and keyboard;
- extended selection, `Delete`, Remove Selected, Clear All, Cancel, and Apply Changes work transactionally;
- final output uses stable relative headers.

## 4. Existing four-mode regression gate

Verify:

- Selected Files;
- Full Folder;
- Git Changed Files;
- Project Tree.

For the four modes, confirm:

- exact source fidelity;
- staged/unstaged Git separation;
- rename/copy/delete/untracked handling;
- spaces and Unicode paths;
- `.gitignore`, `.xccignore`, and built-in exclusions;
- safety warnings and optional confirmation;
- character-budget summaries;
- cancellation without partial clipboard output;
- Last Run and metadata-only Runtime History;
- tray, native hotkey, autostart, config recovery, and single instance.

## 5. Automated release-candidate gate

Run from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

The automated report must declare:

```text
xcc_version: 1.3.0
passed: true
gates.selected_files_regression: true
```

It must bind the report to the exact archive filename and SHA-256.

## 6. Packaged application gate

Extract the generated archive to a clean writable folder and verify:

- `XCC Context Collector.exe` starts without Python installed;
- `_internal` and `VERSION.txt` are present;
- About and footer show `1.3.0`;
- application, tray, navigation, card, metric, dialog, and action assets are present;
- no console window appears during normal GUI startup;
- second launch restores the existing instance;
- close-to-tray, tray restore, tray quit, `Esc`, and `Ctrl+Alt+X` work;
- Start with Windows can be enabled and removed;
- all UI and workflow checks from sections 2–4 pass in the packaged build.

## 7. Manual Windows evidence

Create evidence for the exact final archive on Windows 10 and Windows 11. Both records must reference the same archive SHA-256 and contain every explicit v1.3.0 manual gate.

Validate the records:

```powershell
python scripts\validate_release_evidence.py --expected-version 1.3.0 --expected-archive-sha256 <FINAL_SHA256> --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Evidence JSON is private release material. Do not publish it as a GitHub Release asset.

## 8. Final readiness

Run:

```powershell
python scripts\check_release_readiness.py --archive artifacts\XCC-Context-Collector-v1.3.0-win64.zip --checksum artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --automated-report artifacts\XCC-v1.3.0-automated-gate.json --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Expected result:

```text
Release readiness passed for v1.3.0.
```

Final readiness must confirm:

- canonical version and dated changelog entry;
- release-note markers;
- safe archive structure;
- checksum match;
- automated report match;
- Windows 10/11 evidence match;
- clean `main`;
- local `main == origin/main`.

Confirm Windows CI is green for the same release commit.

## 9. Tag and draft release

Only after final readiness passes:

```powershell
git tag -a v1.3.0 -m "XCC Context Collector v1.3.0"
```

```powershell
git push origin v1.3.0
```

```powershell
gh release create v1.3.0 artifacts\XCC-Context-Collector-v1.3.0-win64.zip artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --title "XCC Context Collector v1.3.0" --notes-file docs\releases\v1.3.0.md --draft
```

Do not upload automated or manual evidence JSON as public assets.

## 10. Post-publication verification

After publication:

- download the public ZIP and checksum;
- verify the downloaded ZIP against the published checksum;
- extract and start the downloaded package;
- confirm About, footer, and `VERSION.txt` show `1.3.0`;
- repeat one Paste Paths collection;
- confirm sidebar wheel and focus behavior;
- confirm the release badge resolves to v1.3.0;
- confirm both public assets are present;
- mark the roadmap `DONE — RELEASED`;
- publish the release announcement.

v1.3.0 is complete only after the downloadable public artifact has been independently verified.
