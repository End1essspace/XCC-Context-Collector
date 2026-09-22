# XCC Roadmap

Last updated: 2026-09-22  
Current source version: `1.4.0`  
Current state: **v1.4.0 RELEASE CANDIDATE PREPARATION**  
Supported runtime: `gui.py -> xcc.gui -> xcc.pipeline`

## Release overview

| Release | Status | Scope |
|---|---|---|
| v1.0.x | DONE | Desktop shell, tray, native hotkey, autostart, single instance |
| v1.1.x | DONE | Broader source coverage and Project Tree |
| v1.2.0 | RELEASED | Source fidelity, Git context, safety, background collection, reproducible release gates |
| v1.3.0 | RELEASED | Paste Paths, Selected Files Review, product UI |
| v1.3.1 | BASELINE | Responsive/DPI/work-area reliability and Interface scale |
| **v1.4.0** | **RC PREPARATION** | Attachments, automated handoff, ZIP fallback, configurable hotkeys, persistent history, release polish |
| v1.5.0 | PLANNED | Advanced context rules/profiles and deferred distribution work |

Historical implementation detail belongs in Git history and release notes. This file records current release outcomes and the active path.

---

# v1.4.0 — Attachments & Windows Workflow

## Release goal

Reduce the manual work between an AI assistant asking for project files and the user delivering those files back, without weakening the existing text-context collector.

Two product paths are intentionally separate:

```text
CONTEXT
AI request -> source selection -> Collect -> structured text -> clipboard

ATTACHMENTS
AI file request -> Paste Paths/Add Files -> ordered review
-> Copy Files / Send One-by-One / Create ZIP & Copy
```

## Product invariants

1. Local-first: no account, cloud upload, or telemetry.
2. Collect preserves source/Git payload fidelity.
3. Attachments never rewrite original files.
4. Sharing is explicit and user-armed.
5. Failures/cancellation are visible.
6. Generated context/ZIP is never published as successful when incomplete.
7. Persistent History remains metadata-only.
8. Attachment Handoff may dispatch `Ctrl+V`, but never submits a message or automates provider DOM/API behavior.
9. Portable ZIP remains the supported distribution for v1.4.0.
10. Third-party attachment acceptance is outside XCC's guarantee.

---

# M17 — v1.4.0 implementation status

## M17.0 — Transfer contract / compatibility spike
**DONE**

- Qt `QMimeData` + local `QUrl` validated as Windows file-object clipboard publication.
- Explorer receives the full multi-file selection.
- Browser/client acceptance is treated as a target capability, not an XCC source-fidelity guarantee.
- Native `CF_HDROP` fallback is not required by current Windows evidence.

## M17.1 — Attachment selection core
**DONE**

- dedicated attachment importer;
- explicit regular-file selection without Collect's extension allowlist;
- path-list parsing/project-root resolution;
- traversal rejection;
- Windows-aware de-duplication;
- ordered selection, file count, aggregate bytes, mixed/external locations.

## M17.2 — Attachments page
**DONE**

- real sidebar page;
- Add Files / Paste Paths;
- ordered review, remove/clear;
- visible root/count/size;
- responsive `Selection | Transfer -> stacked` behavior;
- centered Size column and single selected-row accent.

## M17.3 — Copy original files
**DONE**

- ordered filesystem clipboard objects;
- final selection revalidation;
- no whole-file body load;
- metadata-only history.

### M17.3A — Automated Attachment Handoff
**DONE — TARGET-SPECIFIC VALIDATION CONTINUES**

- button-start countdown;
- optional global hotkey;
- exact target HWND lock;
- one file + one `Ctrl+V` per step;
- focus-change fail-closed behavior;
- cancellation/progress;
- no Enter/submit/DOM/provider API automation;
- metadata-only history.

The tested motivating workflow showed that separate paste events can succeed where one multi-file paste is accepted incompletely. This remains target/version-specific compatibility evidence.

## M17.4 — ZIP bundle engine
**DONE**

- ZIP64-capable standard archive;
- streaming reads and progress;
- cooperative cancellation;
- `.partial` transactional finalization;
- safe project-relative/mixed-location member mapping;
- deterministic collision handling;
- completed ZIP copied as one file object.

## M17.5 — Bundle lifecycle / safety / scale
**DONE**

- `%USERPROFILE%\.xcc\attachment-bundles\`;
- 7-day XCC-managed retention;
- `Open bundle location`;
- path-only attachment safety warnings;
- no recursive directory attachment;
- no XCC-imposed file-count limit.

## M17.6 — Configurable global hotkeys
**DONE**

- Restore / Show;
- optional Collect & Copy;
- optional Attachment Handoff;
- normalized validation;
- conflict rejection;
- transactional replacement/rollback;
- persistent settings and reset.

## M17.7 — Persistent/exportable Runtime History
**DONE**

- `%USERPROFILE%\.xcc\history.json`;
- `xcc-runtime-history` schema v1;
- newest 200 records;
- metadata-only collection + attachment records;
- clear/export;
- corruption backup/recovery;
- sanitized absolute paths.

## M17.8 — Installer / update availability
**DEFERRED — NOT PART OF v1.4.0**

The implemented v1.4.0 release remains portable-ZIP-first. Installer/uninstall and update-availability work was not implemented in the current source and is therefore not claimed by v1.4.0 documentation or release notes.

Candidate future scope:
- installer/uninstall;
- installed-vs-portable parity;
- preserve/remove `%USERPROFILE%\.xcc` decision;
- release-availability check;
- no silent self-update.

## M17.9 — Regression / docs / release
**CURRENT — RELEASE BLOCKER**

Required before publication:

- canonical source version `1.4.0`;
- README / changelog / architecture / UI reference / validation / release notes synchronized;
- `python -m compileall -q src tests scripts gui.py`;
- `python scripts\check_version_consistency.py`;
- full `python -m pytest -q`;
- packaged Attachments/clipboard/ZIP/Handoff validation;
- persistent History restart/export/clear/corruption validation;
- responsive/DPI/interface-scale regression;
- portable ZIP build + archive/checksum validation;
- Windows packaged smoke;
- clean synchronized `main` and green CI;
- public ZIP/checksum independently downloaded, verified, extracted, launched, and smoke-tested.

---

# v1.5.0 — Advanced Context & Distribution

Planned candidates:

- per-project presets and reusable collection profiles;
- advanced include/exclude editor;
- extension/file-size/context-priority rules;
- selected-directory scopes;
- project-tree depth and output preview controls;
- optional redaction/templates/provider estimates;
- Windows installer/uninstall;
- update-availability surface.

The exact v1.5.0 scope is frozen only after v1.4.0 is published and independently verified.
