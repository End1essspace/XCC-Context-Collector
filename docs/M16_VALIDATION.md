# XCC v1.3.1 Release Validation

Status: **ACTIVE — RELEASE CANDIDATE**

This is the canonical validation procedure for the exact commit/archive that will become v1.3.1. Use [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md) as the compact operator checklist.

## Release invariant

Do not tag or publish until source, automated report, packaged validation, Windows evidence, archive/checksum, Git state, and CI all refer to the same final release commit and ZIP SHA-256.

## 1. Source freeze

Required current surfaces:

```text
README.md
CHANGELOG.md
docs/ARCHITECTURE.md
docs/BUG_REPORTING.md
docs/M16_VALIDATION.md
docs/PORTABLE_ZIP.md
docs/RELEASE_CHECKLIST.md
docs/UI_REFERENCE_v1.3.1.md
docs/releases/v1.3.1.md
docs/roadmap.md
```

Run:

```powershell
python -m compileall -q src tests scripts gui.py
```

```powershell
python scripts\check_version_consistency.py
```

```powershell
python -m pytest -q
```

Required result: every gate passes; a PASS followed by a teardown exception is a failure.

## 2. Responsive / DPI source gate

Run the dedicated matrix:

```powershell
python -m pytest -q tests\test_ui_responsive.py tests\test_responsive_regression_matrix.py tests\test_gui_responsive_regression.py tests\test_gui_geometry.py tests\test_ui_dialogs.py tests\test_ui_components.py
```

It must cover breakpoint boundaries, height boundaries, progressive workbench behavior, page reflow, state/widget preservation, dialog sizing, work-area restore, and DPI-aware assets.

## 3. Manual UI gate

Validate actual available environments; mark unavailable hardware `NOT TESTED`.

Minimum required:

```text
920×620
Full HD baseline
QHD at available Windows 100% / 125% / 150% cases
Interface scale Auto + at least one manual override
```

Check Collect, Settings, History, About, Paste Paths, Selected Files Review, title/footer, tray/hotkey restore and maximize/restore.

Pass conditions:

- no normal horizontal page scrolling;
- no clipping/overlap/duplicate controls;
- constrained layouts reflow instead of uniformly shrinking;
- long paths/metadata remain readable;
- Interface scale persists and applies after full restart;
- scale selector and X-SERIES footer match the XCC style;
- window remains inside the current work area;
- raster/SVG assets remain sharp after DPI/screen changes.

## 4. Automated release candidate

Quit every packaged/tray XCC process first.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.1
```

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.1-win64.zip
artifacts\XCC-Context-Collector-v1.3.1-win64.zip.sha256
artifacts\XCC-v1.3.1-automated-gate.json
```

The automated report must declare `passed: true` and include `responsive_regression: true`.

## 5. Packaged validation

From a clean extraction confirm:

- executable starts without Python;
- About and `VERSION.txt` show `1.3.1`;
- all runtime assets exist, including `x-series.png`;
- all four collection modes and v1.3.0 Selected Files workflows still pass;
- responsive/DPI/interface-scale behavior matches source mode;
- tray, hotkey, single-instance, config recovery, autostart and cancellation pass.

## 6. Windows evidence

Record one complete packaged validation on Windows 10 x64 and one on Windows 11 x64, both against the same final ZIP SHA-256:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\record_manual_validation.ps1
```

Evidence JSON is private release material. For v1.3.1 it must include the responsive/DPI/interface-scale gates defined by `validate_release_evidence.py`.

Validate:

```powershell
python scripts\validate_release_evidence.py --expected-version 1.3.1 --expected-archive-sha256 <FINAL_SHA256> --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

## 7. Final readiness

```powershell
python scripts\check_release_readiness.py --archive artifacts\XCC-Context-Collector-v1.3.1-win64.zip --checksum artifacts\XCC-Context-Collector-v1.3.1-win64.zip.sha256 --automated-report artifacts\XCC-v1.3.1-automated-gate.json --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Required final state:

- branch `main`;
- working tree clean;
- local `main == origin/main`;
- CI green for the release commit;
- final readiness prints `Release readiness passed for v1.3.1.`

## 8. Tag / draft / publish

```powershell
git tag -a v1.3.1 -m "XCC Context Collector v1.3.1"
```

```powershell
git push origin v1.3.1
```

```powershell
gh release create v1.3.1 artifacts\XCC-Context-Collector-v1.3.1-win64.zip artifacts\XCC-Context-Collector-v1.3.1-win64.zip.sha256 --title "XCC Context Collector v1.3.1" --notes-file docs\releases\v1.3.1.md --draft
```

Publish only the ZIP and checksum.

## 9. Public artifact verification

After publication, independently download the public ZIP/checksum, verify SHA-256, extract, launch, confirm `1.3.1`, run one collection, test Interface scale restart and tray/hotkey restore, then mark the roadmap `DONE — RELEASED`.

The release is incomplete until the published artifact itself passes this verification.
