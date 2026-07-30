# M15 — v1.3.0 Validation and Release Procedure

M15 is the release blocker for XCC v1.3.0. The release must validate both the established v1.2.0 reliability baseline and the new Selected Files Paste Paths workflow.

## Release rule

Do not create or push `v1.3.0` until the canonical automated gate, packaged manual checks, archive validation, and final repository readiness checks pass for the same commit and archive.

## 1. Preflight

Run from the repository root:

```powershell
git status --short; git branch --show-current; git fetch origin --tags; python scripts\check_version_consistency.py
```

Required state:

- branch is `main`;
- working tree is clean after the M14 commit;
- local `main` is synchronized with `origin/main`;
- canonical version is `1.3.0`;
- `docs/releases/v1.3.0.md` exists.

## 2. Source regression gate

```powershell
python -m compileall -q src tests scripts gui.py run.py hotkey.py; python -m pytest -q
```

The full suite must pass. Selected Files coverage must include parser, importer, review, and end-to-end workflow tests.

## 3. Selected Files packaged behavior gate

In the packaged application verify:

- `Paste Paths` appears only in Selected Files mode;
- `Ctrl+V` imports paths only when focus is not inside an editable field;
- plain, Markdown, quoted, backtick, and fenced lists are recognized;
- relative paths require a valid visible project root;
- absolute paths can be imported without a root;
- duplicate imports do not add files again;
- missing, directory, unsupported, invalid, outside-root, and external states are reported correctly;
- stale remembered roots trigger root selection again;
- separate repositories display `Mixed locations`;
- clicking Source opens Selected Files Review;
- `Delete`, `Remove Selected`, `Clear All`, `Cancel`, and `Apply Changes` behave transactionally;
- final collection output contains the expected stable relative file headers.

## 4. Existing four-mode regression gate

Verify Selected Files, Full Folder, Git Changed Files, and Project Tree. Confirm source fidelity, staged/unstaged Git separation, ignore rules, safety warnings, character-budget behavior, cancellation, Last Run metrics, and metadata-only history.

## 5. Automated release-candidate gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

The JSON report must declare `version: 1.3.0` and `passed: true`.

## 6. Manual Windows evidence

Use the existing evidence recorder for the final archive. Windows 10 and Windows 11 records must reference the same SHA-256.

```powershell
python scripts\validate_release_evidence.py --expected-version 1.3.0 --expected-archive-sha256 <FINAL_SHA256> --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Do not publish evidence JSON as a public release asset.

## 7. Final readiness

```powershell
python scripts\check_release_readiness.py --archive artifacts\XCC-Context-Collector-v1.3.0-win64.zip --checksum artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --evidence artifacts\manual-validation\<windows-10-record>.json --evidence artifacts\manual-validation\<windows-11-record>.json
```

Expected result:

```text
Release readiness passed for v1.3.0.
```

## 8. Commit, tag, and draft release

The M14 documentation/version commit must already be pushed before the release gate. After readiness passes:

```powershell
git tag -a v1.3.0 -m "XCC Context Collector v1.3.0"; git push origin v1.3.0
```

```powershell
gh release create v1.3.0 artifacts\XCC-Context-Collector-v1.3.0-win64.zip artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256 --title "XCC Context Collector v1.3.0" --notes-file docs\releases\v1.3.0.md --draft
```

## 9. Post-publication verification

- download both public assets;
- verify the ZIP against the published SHA-256;
- start the downloaded package;
- confirm About and `VERSION.txt` show `1.3.0`;
- repeat one Paste Paths collection from the downloaded package;
- confirm the release badge resolves to v1.3.0;
- update the roadmap from release candidate to released only after verification.
