# XCC Roadmap

Last updated: 2026-07-31  
Current source version: `1.3.0`  
Current state: **PRE-RC CLEANUP — C4 PREPARED, LOCAL VALIDATION PENDING**  
Supported runtime: `gui.py -> xcc.gui -> xcc.pipeline`

---

## Product direction

XCC Context Collector is a local-first Windows utility that converts selected files, a project folder, Git changes, or a project tree into one structured clipboard block for AI coding assistants.

Release work follows four rules:

1. preserve collected source and Git payloads exactly;
2. make omissions, warnings, failures, and truncation explicit;
3. keep the supported runtime and release surface small;
4. validate, commit, and push each completed milestone before continuing.

---

## Release overview

| Release | Status | Scope |
|---|---|---|
| v1.0.x | DONE | PySide6 desktop application, tray, native hotkey, autostart, single instance |
| v1.1.x | DONE | Broader source coverage and Project Tree mode |
| v1.2.0 | DONE — RELEASED | Source fidelity, complete Git context, safety visibility, background collection, reproducible release gates |
| v1.3.0 | IN PROGRESS | Paste Paths, Selected Files Review, final responsive interface, repository cleanup, release candidate |
| v1.4.0 | PLANNED | Windows distribution and daily workflow improvements |
| v1.5.0 | PLANNED | Advanced project rules, profiles, preview, and output controls |

Historical implementation detail remains available in Git history and release notes. This roadmap records product-level outcomes and the active release path only.

---

# v1.2.0 — Context Integrity & Reliability

**Status: DONE — RELEASED**

Delivered:

- exact source-payload preservation;
- typed staged and unstaged Git context;
- stable file identity for Selected Files;
- structure-aware output budgeting;
- `.gitignore` and `.xccignore` support;
- warning-only sensitive-context detection;
- background collection with cooperative cancellation;
- typed outcomes, Last Run, and metadata-only Runtime History;
- tray, native restore hotkey, autostart, and single-instance behavior;
- Windows CI, clean-install validation, packaged smoke, ZIP/checksum validation, and release evidence.

Historical validation record: [`docs/releases/v1.2.0-validation.md`](releases/v1.2.0-validation.md).

---

# v1.3.0 — Selected Files Workflow & Final Interface

**Status: IN PROGRESS — RELEASE CANDIDATE PREPARATION**

## M11 — Paste Paths Core

**Status: DONE**

- parse plain, Markdown, quoted, backtick, and fenced path lists;
- resolve relative paths against an explicit project root;
- reject canonical traversal outside that root;
- preserve order and Windows-aware deduplication;
- report missing, unsupported, invalid, external, and duplicate paths;
- expose guarded `Ctrl+V` and Paste Paths in Selected Files mode.

## M12 — Selected Files Review

**Status: DONE**

- display project root or `Mixed locations`;
- review stable relative paths;
- support extended selection, `Delete`, Remove Selected, and Clear All;
- keep Cancel transactional;
- enable Apply Changes only after a real selection change.

## M13 — Workflow Regression & UX Polish

**Status: DONE**

- cover stale roots, monorepositories, absolute external files, duplicate basenames, mixed drives, and large selections;
- verify final Selected Files output and source summaries;
- preserve existing collection, fidelity, safety, budget, and cancellation behavior.

## M14 — Documentation & Version Integration

**Status: DONE**

- move canonical source and release metadata to `1.3.0`;
- document the new Selected Files workflow;
- align release scripts, evidence schema, and readiness checks.

## M15 — Validation, Final UI & Release

**Status: IN PROGRESS — M15.10**

Completed:

- release-gate hardening;
- final UI reference contract;
- reusable theme and component foundation;
- redesigned shell, Collect Setup, Last Run, dialogs, Settings, History, and About;
- responsive behavior from `920×620` through maximized 2K;
- keyboard, focus, accessibility, and semantic-state regression coverage;
- sidebar wheel navigation across the complete sidebar surface;
- focus synchronization after wheel navigation;
- final Collect and History screenshots;
- documentation freeze baseline.

### M15.10 — Documentation Freeze & Release Candidate

**Status: PAUSED FOR PRE-RC CLEANUP**

Cleanup sequence:

| Step | Status | Result |
|---|---|---|
| C1 — Remove unsupported legacy workflows | DONE | Tkinter path, standalone `keyboard` listener, launchers, dependency, and tests removed |
| C2 — Remove obsolete compatibility APIs | DONE | compatibility wrappers and dead symbols removed |
| C3 — Replace brittle repository tests | DONE | prose/snippet assertions replaced with stable behavioral and repository contracts |
| C4 — Consolidate documentation and archival assets | PREPARED | compact roadmap, separated historical validation, lean current checklist, unused icon copies removed after local application |
| C5 — Re-freeze and run RC | NEXT | final documentation sync, complete automated gate, packaged validation, evidence, CI |

C4 is complete only after the archive is applied, the archival files are removed, the full test suite passes, and the change is committed and pushed.

### C5 release-candidate outputs

Run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

Required artifacts:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

The same final ZIP SHA-256 must be referenced by Windows 10 and Windows 11 manual evidence. Final readiness also requires a clean synchronized `main` branch and green CI for the release commit.

## M15.11 — Tag, Publish & Verify

**Status: PLANNED**

- create and push annotated `v1.3.0` tag;
- create the GitHub release with ZIP and checksum only;
- publish final release notes;
- download the public assets independently;
- verify checksum, extraction, startup, version, Paste Paths, and sidebar behavior;
- confirm the release badge and both public assets;
- mark v1.3.0 released and publish the announcement.

v1.3.0 is complete only after the published downloadable artifact has been independently verified.

---

# v1.4.0 — Windows Workflow & Distribution

**Status: PLANNED**

Planned scope:

- editable restore hotkey with conflict validation and reset;
- optional Collect & Copy hotkey;
- repository and release links in About;
- Windows installer and clean uninstall;
- explicit portable-settings behavior;
- update-availability check;
- persistent Runtime History and export;
- installer and portable release gates.

A release-page availability check is preferred to a self-updater until signing, rollback, atomic replacement, and recovery guarantees are defined.

---

# v1.5.0 — Advanced Context Rules

**Status: PLANNED**

Planned scope:

- per-project presets and reusable profiles;
- advanced include/exclude rules;
- extension-specific size limits and context priorities;
- selected-directory scopes and generated-code profiles;
- configurable tree depth and Git controls;
- optional output preview and partial-file strategies;
- configurable safety categories and opt-in redaction;
- custom templates and provider-specific token estimates.

---

# Development rules

## Focused milestone flow

1. change one coherent area;
2. deliver only changed files in a repository-relative ZIP;
3. apply the ZIP at repository root;
4. run compile, version, targeted, and full tests;
5. perform required manual checks;
6. commit and push before the next milestone.

## Standard local gate

```powershell
python -m compileall -q src tests scripts gui.py; python scripts\check_version_consistency.py; python -m pytest -q
```

## Scope and command rules

- request only the folders and files required for the next stage;
- keep PowerShell commands on one physical line without backtick continuations;
- use simple Git commands after a verified milestone: `git add .`, `git commit -m "..."`, `git push`.

---

# Immediate next step

Apply and validate **C4 — Documentation and Asset Consolidation**, remove the two obsolete paths listed by the C4 instructions, commit and push, then start C5.
