# XCC v1.3.0 Release Checklist

This checklist is the operational companion to `docs/M15_VALIDATION.md`. A release is complete only when every applicable item has objective evidence.

## 1. Documentation and version freeze

- [ ] `src/xcc/__init__.py` declares `1.3.0`
- [ ] README contains both current-version markers for v1.3.0
- [ ] `CHANGELOG.md` contains a dated `[1.3.0]` section
- [ ] `docs/releases/v1.3.0.md` is final and user-facing
- [ ] `docs/roadmap.md` reports M11–M14 accurately
- [ ] `docs/ARCHITECTURE.md` documents parser, importer, review, and security boundaries
- [ ] `docs/M15_VALIDATION.md` matches implemented release tooling
- [ ] no private paths, secrets, temporary hashes, or local-only evidence appear in public docs

```powershell
python scripts\check_version_consistency.py; python -m pytest tests\test_project_metadata.py tests\test_repository_maturity.py tests\test_m10_release_candidate.py -q
```

## 2. Repository state

- [ ] branch is `main`
- [ ] working tree is clean
- [ ] `main` equals `origin/main`
- [ ] final M14 commit is pushed
- [ ] Windows CI is green for that commit

```powershell
git status --short; git branch --show-current; git rev-parse HEAD; git rev-parse origin/main
```

## 3. Automated gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

- [ ] compileall passes
- [ ] full pytest passes
- [ ] clean-install validation passes
- [ ] PyInstaller build passes
- [ ] packaged startup and required-asset smoke passes
- [ ] portable ZIP and SHA-256 are generated
- [ ] archive validation passes
- [ ] automated report declares `xcc_version: 1.3.0`, `passed: true`, and `selected_files_regression: true`

Expected outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

## 4. Selected Files workflow

- [ ] Paste Paths appears only in Selected Files
- [ ] guarded `Ctrl+V` works
- [ ] plain and Markdown path lists work
- [ ] relative paths resolve under a visible project root
- [ ] absolute paths work without a root
- [ ] duplicates are skipped
- [ ] missing, directories, unsupported, invalid, outside-root, and external paths are reported
- [ ] stale root recovery works
- [ ] mixed repositories show `Mixed locations`
- [ ] Source opens Selected Files Review
- [ ] `Delete`, removal, clear, cancel, and apply behave correctly
- [ ] final output has stable relative headers

## 5. Existing behavior and Windows integration

- [ ] all four modes pass
- [ ] source fidelity and budget contracts pass
- [ ] Git staged/unstaged and rename/copy/delete behavior pass
- [ ] safety detection and optional confirmation pass
- [ ] cancellation never copies partial output
- [ ] tray, hotkey, autostart, config recovery, and single instance pass
- [ ] packaged app starts without Python installed
- [ ] final UI and screenshots are reviewed

## 6. Clean-host evidence

- [ ] Windows 10 record exists
- [ ] Windows 11 record exists
- [ ] both declare XCC 1.3.0
- [ ] both reference the same archive SHA-256
- [ ] both contain every explicit v1.3.0 Selected Files manual gate
- [ ] combined evidence validator passes

```powershell
python scripts\validate_release_evidence.py --expected-version 1.3.0 --expected-archive-sha256 <FINAL_SHA256> --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

## 7. Final readiness

```powershell
python scripts\check_release_readiness.py --archive artifacts\XCC-Context-Collector-v1.3.0-win64.zip --checksum artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --automated-report artifacts\XCC-v1.3.0-automated-gate.json --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

- [ ] command prints `Release readiness passed for v1.3.0.`
- [ ] working tree remains clean
- [ ] archive name is exact
- [ ] checksum file is present
- [ ] automated report matches the final archive filename and SHA-256

## 8. Tag and draft release

```powershell
git tag -a v1.3.0 -m "XCC Context Collector v1.3.0"; git push origin v1.3.0
```

```powershell
gh release create v1.3.0 artifacts\XCC-Context-Collector-v1.3.0-win64.zip artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --title "XCC Context Collector v1.3.0" --notes-file docs\releases\v1.3.0.md --draft
```

- [ ] annotated tag points to the release commit
- [ ] draft title and notes are correct
- [ ] ZIP and checksum are attached
- [ ] evidence JSON is not public

## 9. Post-publication

- [ ] downloaded ZIP matches the checksum
- [ ] downloaded application starts
- [ ] About and `VERSION.txt` show 1.3.0
- [ ] Paste Paths works in the downloaded build
- [ ] release badge resolves to v1.3.0
- [ ] roadmap is marked released after verification
