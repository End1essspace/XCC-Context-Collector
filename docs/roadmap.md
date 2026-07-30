# XCC Roadmap

Last updated: 2026-07-30  
Current source version: `1.3.0`  
Current release state: **v1.3.0 IN DEVELOPMENT — UI FINALIZATION AND RELEASE VALIDATION**  
Supported product boundary: `gui.py -> xcc.gui -> xcc.pipeline`

---

## 1. Product Direction

XCC Context Collector is a local-first Windows desktop utility that converts project files, folders, Git changes, or a project tree into one structured context block for AI coding assistants.

The roadmap follows four product principles:

1. **Context integrity** — collected source and Git payloads must not be silently rewritten or cut.
2. **Workflow speed** — repeated AI coding workflows should require as little manual file handling as possible.
3. **Operational transparency** — omissions, warnings, errors, truncation, and runtime state must be explicit.
4. **Release discipline** — every completed milestone must pass automated and manual validation, then be committed and pushed before the next milestone begins.

The supported release application is the PySide6 desktop GUI. Legacy Tkinter and standalone hotkey entry points remain development-only compatibility paths and do not receive new product features.

---

## 2. Current Status Summary

| Release / milestone | Status | Result |
|---|---|---|
| v1.0.x Windows release foundation | DONE | Packaged PySide6 app, tray, native hotkey, autostart, single instance |
| v1.1.x Source coverage | DONE | Expanded language/config support and centralized allowlist |
| v1.1.2 Project Tree patch | DONE | Standalone structure-only collection mode |
| v1.2.0 Context Integrity & Reliability | DONE — RELEASED | Fidelity, Git completeness, safety visibility, background worker, release gates |
| M11 Paste Paths Core | DONE | AI path lists can be parsed, validated, and imported |
| M12 Selected Files Review | DONE | Selected files can be reviewed and edited transactionally |
| M13 Workflow Regression & UX Polish | DONE | Edge cases and end-to-end workflow coverage completed |
| M14 Documentation & Version Integration | DONE | Source and release documentation moved to v1.3.0 |
| M15 v1.3.0 Validation and Release | IN PROGRESS | Release hardening, final interface redesign, packaged validation, publication |
| v1.4.0 Windows Workflow & Distribution | PLANNED | Installer, editable hotkeys, persistent history, update availability |
| v1.5.0 Advanced Context Rules | PLANNED | Profiles, rule editor, preview, advanced output controls |

---

# Completed Releases

## v0.1–v0.4 Core Foundation

**Status: DONE**

Completed foundations:

- project structure and typed data models;
- file and folder collection;
- formatter and clipboard output;
- recursive scanner;
- compact generated output;
- character budget;
- Git changed-file collection and diff support;
- background hotkey workflow;
- baseline automated tests.

These releases established the functional prototype that later moved into the supported PySide6 application.

---

## v0.5–v0.9.6 PySide6 Desktop Foundation

**Status: DONE**

Completed:

- PySide6 main window;
- black and gold interface identity;
- header, sidebar, Collect, History, Settings, and About pages;
- Selected Files, Full Folder, and Git Changed Files modes;
- Last Run metrics;
- in-memory runtime history;
- persistent settings;
- system tray integration;
- close-to-tray and `Esc` hide behavior;
- native `Ctrl+Alt+X` restore path;
- autostart support;
- GUI-focused regression coverage.

---

## v1.0.0 Windows Release

**Status: DONE — RELEASED**

Completed:

- supported GUI entry point;
- PyInstaller build pipeline;
- packaged icon and resource loading;
- single-instance protection;
- second-launch restore;
- packaged autostart target;
- repeatable clean build;
- portable release directory and ZIP;
- packaged smoke validation.

---

## v1.0.1 Hotkey Reliability Patch

**Status: DONE — RELEASED**

Completed:

- native Windows `RegisterHotKey`;
- Qt native event filter;
- safe GUI-thread restore scheduling;
- conflict/error visibility;
- native hotkey parsing tests;
- release-path cleanup.

---

## v1.1.0–v1.1.1 Source Coverage Expansion

**Status: DONE — RELEASED**

Completed:

- broader source-language support;
- frontend, backend, system, scripting, database, and documentation types;
- exact filename support for common project files;
- centralized context-file allowlist;
- consistent filtering in picker, scanner, collector, and Git mode;
- sensitive file types kept excluded by default.

---

## v1.1.2 Project Tree Mode

**Status: DONE — RELEASED**

Completed:

- standalone Project Tree mode;
- metadata-only structure output;
- folders and files rendered in one clean tree;
- standard cache, build, dependency, IDE, and Git exclusions;
- Selected Files no longer receives an incorrect project tree section.

---

# v1.2.0 Context Integrity & Reliability

**Status: DONE — RELEASED**

## Release Goal

Turn XCC from a useful utility into a dependable context-collection tool whose output, Git state, safety signals, and release artifacts can be trusted.

## M1 — Source Content Fidelity

**Status: DONE**

- [x] preserve collected source payloads verbatim;
- [x] restrict compacting to XCC-generated structural text;
- [x] avoid whitespace, newline, comment, or content normalization;
- [x] add fidelity regression tests.

## M2 — Complete Git Context

**Status: DONE**

- [x] null-delimited porcelain parsing;
- [x] typed staged and unstaged state;
- [x] untracked, renamed, copied, and deleted semantics;
- [x] staged and unstaged diff separation;
- [x] literal pathspec handling;
- [x] spaces and Unicode path coverage.

## M3 — Stable File Identity

**Status: DONE**

- [x] stable display paths;
- [x] duplicate basename disambiguation;
- [x] cross-root selection support;
- [x] no ambiguous filename-only collapse.

## M4 — Structure-Aware Character Budget

**Status: DONE**

- [x] hard output limit;
- [x] complete-section planning;
- [x] explicit included and omitted counts;
- [x] budget summary;
- [x] no silent mid-file or mid-diff cuts;
- [x] partial source-file inclusion disabled by default.

## M5 — Ignore Rules and Safety Visibility

**Status: DONE**

- [x] `.xccignore`;
- [x] root `.gitignore` integration where applicable;
- [x] built-in exclusions remain authoritative;
- [x] sensitive filename detection;
- [x] private-key, token, credential, and connection-string heuristics;
- [x] warning-only behavior without silent redaction;
- [x] optional modal confirmation without disabling detection metadata.

## M6 — Background Collection Pipeline

**Status: DONE**

- [x] worker-thread collection;
- [x] progress reporting;
- [x] cooperative cancellation;
- [x] single active job;
- [x] partial results never copied after cancellation;
- [x] safe deferred close and quit behavior.

## M7 — Result Health and Runtime History

**Status: DONE**

- [x] `SUCCESS`;
- [x] `SUCCESS_WITH_WARNINGS`;
- [x] `CANCELLED`;
- [x] `FAILED`;
- [x] Last Run coverage and health metrics;
- [x] metadata-only in-memory history;
- [x] no source contents, diff payloads, detected values, or failure bodies stored in history.

## M8–M9 — Repository and Release Maturity

**Status: DONE**

- [x] package metadata;
- [x] Windows CI;
- [x] clean workspace tooling;
- [x] clean-install validation;
- [x] packaged startup and asset smoke tests;
- [x] portable ZIP and SHA-256 generation;
- [x] archive validation;
- [x] release evidence schema;
- [x] release-readiness validation;
- [x] architecture, security, contribution, diagnostics, and release documentation.

## M10 — v1.2.0 Validation and Release Gate

**Status: DONE — RELEASED**

- [x] final automated release gate;
- [x] clean-host Windows validation;
- [x] release archive and checksum validation;
- [x] GitHub tag and release publication;
- [x] downloaded-asset verification;
- [x] stable v1.2.0 baseline.

---

# v1.3.0 Selected Files Workflow and Final Interface

**Status: IN DEVELOPMENT — M15 IN PROGRESS**  
Selected Files Workflow Status: IMPLEMENTED — M15 RELEASE VALIDATION PENDING

## Release Goal

Complete the direct AI-to-XCC workflow:

```text
AI returns a path list
        ↓
Copy once
        ↓
Paste Paths or Ctrl+V
        ↓
Resolve and validate paths
        ↓
Review the final ordered selection
        ↓
Collect & Copy
```

v1.3.0 also completes a release-quality visual redesign of the supported PySide6 application before the final release candidate is built.

## Scope Freeze

The following are in scope for v1.3.0:

- Paste Paths;
- Selected Files Review;
- edge-case hardening;
- final Collect-page and application-shell redesign;
- responsive layout;
- dialog visual integration;
- UI regression coverage;
- packaged validation;
- release publication.

The following remain outside v1.3.0:

- installer;
- automatic updater;
- editable global hotkey;
- persistent runtime history;
- advanced rule editor;
- full output preview editor;
- per-project profiles.

No additional feature work should enter v1.3.0 unless it fixes a release-blocking defect or is explicitly included below.

---

## M11 — Paste Paths Core

**Status: DONE**

- [x] ordered path-list parser;
- [x] plain line lists;
- [x] Markdown bullets and numbering;
- [x] quoted and backtick-wrapped paths;
- [x] fenced code block extraction;
- [x] relative and absolute Windows paths;
- [x] visible project-root resolution;
- [x] path existence validation;
- [x] file/directory validation;
- [x] supported-type validation;
- [x] traversal protection;
- [x] canonical Windows-aware deduplication;
- [x] manual-selection merge;
- [x] `Paste Paths` button;
- [x] guarded `Ctrl+V`;
- [x] parser and importer tests.

### Release Guarantee

Pasted text is treated only as path input. It is never executed as code or shell content.

---

## M12 — Selected Files Review

**Status: DONE**

- [x] clickable Source summary;
- [x] relative path display;
- [x] effective project-root display;
- [x] `Mixed locations`;
- [x] absolute-path tooltip;
- [x] extended multi-selection;
- [x] `Remove Selected`;
- [x] `Delete` shortcut;
- [x] `Clear All`;
- [x] transactional `Cancel`;
- [x] explicit `Apply Changes`;
- [x] order preservation;
- [x] root recalculation;
- [x] review-model tests.

---

## M13 — Workflow Regression and UX Polish

**Status: DONE**

- [x] stale or deleted root recovery;
- [x] absolute external files remain importable;
- [x] outside-root paths rejected;
- [x] separate repositories produce `Mixed locations`;
- [x] repository roots preferred in monorepository layouts;
- [x] external-path count visibility;
- [x] duplicate-only imports remain non-modal;
- [x] detailed issue reports;
- [x] inactive clear/apply controls disabled;
- [x] end-to-end import → review → collection coverage;
- [x] real multi-file AI-list regression scenario.

---

## M14 — Documentation and Version Integration

**Status: DONE**

- [x] canonical source version set to `1.3.0`;
- [x] bilingual README updated;
- [x] changelog updated;
- [x] parser/importer/review architecture documented;
- [x] security boundary documented;
- [x] v1.3.0 release notes created;
- [x] M15 validation procedure created;
- [x] portable and release documentation moved to v1.3.0;
- [x] issue template updated;
- [x] version and documentation regression tests updated;
- [x] M14 changes validated, committed, and pushed.

---

# M15 — v1.3.0 Validation and Release

**Status: IN PROGRESS — CURRENT MILESTONE**

M15 is the release blocker. The `v1.3.0` tag must not be created until all M15 sub-milestones pass for the same final commit and archive.

---

## M15.1 — Release Gate Hardening

**Status: DONE**

### Goal

Ensure final readiness cannot pass without the complete automated report, clean-install result, Selected Files regression gate, manual evidence, and exact final archive hash.

### Planned / prepared work

- [x] define the Selected Files regression gate;
- [x] require automated-gate JSON in final readiness;
- [x] validate report schema and XCC version;
- [x] require every automated gate to pass;
- [x] require canonical clean-install validation;
- [x] bind readiness to the final ZIP name and SHA-256;
- [x] extend Windows evidence questions for Paste Paths and Review;
- [x] preserve compatibility with historical v1.2.0 evidence;
- [x] apply the M15 hardening archive to the repository;
- [x] run complete local tests;
- [x] inspect generated reports;
- [x] commit and push the hardening changes.

### Intended commit

```text
build: harden v1.3.0 release gates
```

---

## M15.2 — Final UI Reference Contract

**Status: DONE**

### Goal

Freeze the visual and behavioral contract before changing implementation code.

### Reference Direction

The final interface keeps the current XCC product identity:

- dark Windows desktop utility;
- black and charcoal surfaces;
- restrained gold accent;
- dense but calm commercial layout;
- clear runtime state;
- four collection modes;
- Setup and Last Run as the primary page structure.

The generated reference is a visual direction, not a literal specification. The implementation must correct its semantic and responsive weaknesses.

### Required corrections to the reference

- [x] Selected Files Source displays `Project · N files selected` or `N files selected · Mixed locations`;
- [x] Selected Files action is `Select Files`;
- [x] folder and tree actions are `Select Folder`;
- [x] Git action is `Select Repository`;
- [x] Source remains clickable for review;
- [x] clear affordance remains available;
- [x] `Paste Paths` is visible only in Selected Files;
- [x] Compact mode description states that source contents remain unchanged;
- [x] number formatting is consistent;
- [x] header and footer statuses have different roles;
- [x] primary button and active sidebar use restrained emphasis;
- [x] layout works from 920×620 through maximized 2K displays.

### Deliverable

```text
docs/UI_REFERENCE_v1.3.0.md
```

- [x] authoritative UI contract created
- [x] responsive breakpoints frozen
- [x] mode-specific Source semantics frozen
- [x] accessibility and behavioral invariants documented
- [x] project metadata regression test added

### Intended commit

```text
docs: define v1.3.0 interface reference
```

---

## M15.3 — Theme and Reusable UI Foundation

**Status: DONE**

### Goal

Reduce visual logic inside the monolithic `src/xcc/gui.py` before major layout changes.

### Planned modules

```text
src/xcc/ui_theme.py
src/xcc/ui_components.py
tests/test_ui_theme.py
tests/test_ui_components.py
```

### Work

- [x] extract color tokens;
- [x] extract spacing and radius constants;
- [x] extract typography sizes and weights;
- [x] extract shared QSS;
- [x] add reusable section/card headers;
- [x] add reusable status capsules;
- [x] add reusable metric rows;
- [x] add primary and secondary button variants;
- [x] add helper-text component;
- [x] preserve all existing behavior;
- [x] verify source and packaged resource loading.

### Implementation Result

- shared semantic palette and geometry tokens live in `src/xcc/ui_theme.py`;
- application and tray stylesheets are no longer embedded in `XccMainWindow`;
- reusable component factories and metric/status widgets live in `src/xcc/ui_components.py`;
- `src/xcc/gui.py` delegates shared visual construction without changing collection-domain behavior;
- dedicated theme and component tests cover the new boundary.

### Acceptance Criteria


- no collection behavior changes;
- all current tests pass;
- current GUI remains functional;
- reusable styles no longer depend on one page;
- no Qt widget is duplicated solely for responsive layouts.

### Intended commit

```text
refactor: extract reusable UI foundation
```

---

## M15.4 — Application Shell Redesign

**Status: DONE**

### Header

- [x] refine logo and title alignment;
- [x] add restrained runtime-state capsule with semantic indicator;
- [x] keep separate lower-emphasis hotkey capsule;
- [x] enforce the Ready, Working, Cancelling, Copied, Warnings, Failed, and Cancelled vocabulary;
- [x] keep the header limited to short runtime state.

### Sidebar

- [x] reduce active-state visual weight;
- [x] add a slim gold accent line;
- [x] use a quiet dark selected surface;
- [x] keep selected text light and the icon gold;
- [x] preserve hover, focus, arrow-key, and activation behavior;
- [x] add accessible navigation names;
- [x] keep About anchored at the bottom.

### Footer

- [x] use the footer for current event, progress, or next-action guidance;
- [x] keep version on the right;
- [x] remove duplicate header/footer `Ready` semantics;
- [x] add a semantic status indicator;
- [x] support detailed collection progress and issue summaries;
- [x] restore useful idle guidance after transient tray/hotkey events.

### Implementation Result

- `RuntimeState` in `src/xcc/ui_shell.py` freezes the supported header vocabulary and semantic states;
- the runtime capsule now uses a small colored indicator instead of a bright filled block;
- arbitrary event sentences no longer leak into the header;
- footer guidance distinguishes an empty source, a selected folder, and selected-file counts;
- the selected sidebar item uses a quiet dark-gold surface and slim indicator rather than black text on a large gold block;
- shell policy has dedicated non-Qt tests and reusable Qt component coverage.

### Acceptance Criteria

- [x] runtime state is understandable at a glance;
- [x] header and footer have distinct responsibilities;
- [x] sidebar no longer overpowers the working area;
- [x] no custom frameless title bar was introduced;
- [x] tray, hotkey, single-instance, and window behavior pass local Windows validation;
- [x] minimum-size and maximized shell behavior is reviewed.

### Intended commit

```text
feat: redesign application shell
```

---

## M15.5 — Collect Setup Redesign

**Status: IMPLEMENTED — LOCAL VALIDATION, COMMIT, AND PUSH PENDING**

### Page Header

```text
Collect Context
Configure what to collect and generate an AI-ready context snapshot.
```

- [x] add the final page title and subtitle;
- [x] expose the subtitle as a reusable component for later responsive hiding;
- [x] keep the page header visually subordinate to the application shell.

### Mode Row

- [x] preserve all four modes;
- [x] improve radio control spacing, hover, focus, and accessible names;
- [x] preserve standard radio-group keyboard behavior;
- [x] preserve source-reset semantics when the mode changes;
- [x] keep adaptive wrapping assigned to M15.7 rather than duplicating widgets here.

### Source Row Semantics

#### Selected Files

```text
XCC · 14 files selected
Paste Paths
Select Files
```

or:

```text
14 files selected · Mixed locations
Paste Paths
Select Files
```

#### Full Folder

```text
D:\projects\GitHub\XCC
Select Folder
```

#### Git Changed Files

```text
D:\projects\GitHub\XCC
Select Repository
```

#### Project Tree

```text
D:\projects\GitHub\XCC
Select Folder
```

### Work

- [x] remove the generic `Select Source` action;
- [x] add mode-specific `Select Files`, `Select Folder`, and `Select Repository` actions;
- [x] keep `Paste Paths` visible only in Selected Files;
- [x] place `Paste Paths` before the mode-specific selection action;
- [x] retain clickable and keyboard-activatable Selected Files review;
- [x] retain the clear action;
- [x] visually mark populated Selected Files Source as reviewable;
- [x] preserve full folder/repository paths in tooltips;
- [x] add mode-specific Source helper text;
- [x] clarify Compact mode without claiming source modification;
- [x] keep Max chars aligned, validated, and accessible;
- [x] disable collection controls while a job is active;
- [x] preserve manual selection, Paste Paths, and mode-switch behavior.

### Compact Mode Contract

```text
Reduce XCC-generated structural whitespace.
Source file contents remain unchanged.
```

The same product guarantee is now used in the Collect page tooltip/helper and the Settings description.

### Implementation Result

- `src/xcc/ui_collect.py` owns the frozen Collect copy and mode-specific presentation policy;
- `PageHeader` in `src/xcc/ui_components.py` provides a reusable title/subtitle boundary;
- `src/xcc/gui.py` now renders explicit mode actions and the corrected Source summaries;
- Source helper text changes with the selected mode;
- Selected Files Source exposes a calm reviewable state without becoming a bright action block;
- Source action and helper controls have meaningful accessible names;
- `src/xcc/ui_theme.py` contains dedicated Setup selectors rather than relying only on generic button rules;
- pure policy tests and Qt component tests cover the new boundary.

### Acceptance Criteria

- [x] no user-facing `Select Source` label remains;
- [x] Selected Files shows `Paste Paths` and `Select Files`;
- [x] Full Folder and Project Tree show `Select Folder`;
- [x] Git Changed Files shows `Select Repository`;
- [x] Source summaries retain singular/plural and `Mixed locations` semantics;
- [x] Compact mode explicitly preserves source contents;
- [x] no collection-domain module was changed;
- [ ] full Qt suite and visual behavior pass local Windows validation;
- [ ] changes are committed and pushed.

### Intended commit

```text
feat: redesign collect setup workflow
```

---

## M15.6 — Last Run Metrics Redesign

**Status: PLANNED**

### Target Structure

```text
Last Run                                  Completed · 17:36:36

Volume            Output            Coverage           Health
Files             Characters        Included           Outcome
Lines             Tokens            Omitted            Duration
Source chars      Truncated         Summary / Partial  Warnings / Errors
```

### Work

- [ ] group metrics into four semantic columns;
- [ ] add restrained group icons;
- [ ] replace heavy independent capsules with lighter metric rows;
- [ ] add subtle column separators;
- [ ] align labels and values;
- [ ] add consistent thousands separators;
- [ ] use semantic result colors;
- [ ] preserve a clear pre-run empty state;
- [ ] keep `CollectionRunRecord` as the data source;
- [ ] align Last Run and History outcome semantics.

### Semantic Colors

- Success — restrained green;
- With warnings — restrained amber;
- Cancelled — neutral gray;
- Failed — restrained red;
- Gold remains an interface accent, not a universal result color.

### Intended commit

```text
feat: redesign last run metrics
```

---

## M15.7 — Responsive Layout

**Status: PLANNED — HIGH RISK**

### Goal

Make the reference-quality design work in the real supported window range instead of only one screenshot size.

### Breakpoints

#### Large: 1350 px and wider

- [ ] one-row Source controls;
- [ ] four metric columns;
- [ ] full page subtitle;
- [ ] standard page margins and spacing.

#### Medium: 1050–1349 px

- [ ] Source actions may wrap;
- [ ] metrics switch to a 2×2 grid;
- [ ] reduced card spacing;
- [ ] full sidebar remains available.

#### Compact: 920–1049 px

- [ ] Source actions move below the input;
- [ ] metrics remain 2×2 or use a compact vertical arrangement;
- [ ] page margins and gaps reduce safely;
- [ ] no horizontal clipping or scrollbar;
- [ ] all primary actions remain visible.

### Validation Matrix

- [ ] minimum window 920×620;
- [ ] 1920×1080 at 100%;
- [ ] 1920×1080 at 125%;
- [ ] 1920×1080 at 150%;
- [ ] 2560×1440;
- [ ] maximized;
- [ ] resize transitions without layout jitter.

### Implementation Constraints

- reuse the same widget instances;
- avoid duplicate signal connections;
- avoid rebuilding the entire page on every resize event;
- debounce or guard layout switching;
- preserve accessibility and tab order.

### Intended commit

```text
feat: add responsive collect layouts
```

---

## M15.8 — Dialog Visual Integration

**Status: PLANNED**

### Paste Paths Dialog

- [ ] match final theme and typography;
- [ ] refine project-root selector;
- [ ] improve path input readability;
- [ ] distinguish valid, warning, and error summaries;
- [ ] keep disabled-state clarity;
- [ ] preserve live validation.

### Selected Files Review

- [ ] refine project-root or Mixed locations presentation;
- [ ] improve file-count badge;
- [ ] use a calmer selected-row state;
- [ ] preserve multi-select and `Delete`;
- [ ] preserve `Remove Selected`;
- [ ] preserve transactional `Cancel`;
- [ ] preserve explicit `Apply Changes`;
- [ ] handle long paths without layout breakage.

### Acceptance Criteria

- dialogs visually belong to the same product;
- actions remain understandable without documentation;
- no visual change weakens the existing workflow guarantees.

### Intended commit

```text
feat: align selected files dialogs with new UI
```

---

## M15.9 — UI Regression, Accessibility, and Final Polish

**Status: PLANNED**

### Automated Coverage

Planned tests:

```text
tests/test_gui_semantics.py
tests/test_gui_responsive_layout.py
tests/test_ui_components.py
```

Required checks:

- [ ] mode-specific action labels;
- [ ] Paste Paths visibility;
- [ ] Source summary and Mixed locations;
- [ ] clear behavior;
- [ ] review opening;
- [ ] responsive breakpoint switching;
- [ ] metric number formatting;
- [ ] collection-active disabled state;
- [ ] header/footer status separation;
- [ ] version labels;
- [ ] keyboard accessibility;
- [ ] no regression in existing Selected Files workflow tests.

### Manual UI Checklist

- [ ] hover, pressed, disabled, and focus states;
- [ ] keyboard-only navigation;
- [ ] long folder path;
- [ ] one selected file;
- [ ] 100+ selected files;
- [ ] mixed repositories;
- [ ] warning result;
- [ ] failure result;
- [ ] truncated result;
- [ ] cancellation;
- [ ] no-history state;
- [ ] minimum window;
- [ ] maximized window;
- [ ] Windows scaling 100%, 125%, and 150%.

### Final Visual Review

- [ ] spacing;
- [ ] alignment;
- [ ] typography;
- [ ] icon sizing;
- [ ] divider lengths;
- [ ] active sidebar weight;
- [ ] primary button saturation;
- [ ] Source affordance;
- [ ] Last Run density;
- [ ] screenshot parity with the approved design direction.

### Intended commit

```text
fix: complete v1.3.0 interface polish
```

---

## M15.10 — Documentation Freeze and Release Candidate

**Status: PLANNED**

### Documentation

Update after the final GUI is approved:

```text
README.md
CHANGELOG.md
docs/ARCHITECTURE.md
docs/M15_VALIDATION.md
docs/RELEASE_CHECKLIST.md
docs/releases/v1.3.0.md
docs/roadmap.md
docs/screenshots/xcc-collect.png
docs/screenshots/xcc-history.png
```

### Automated Gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

### Packaged Validation

- [ ] correct header, sidebar, footer, cards, and responsive layout;
- [ ] correct v1.3.0 labels;
- [ ] Paste Paths;
- [ ] guarded `Ctrl+V`;
- [ ] Selected Files Review;
- [ ] all four collection modes;
- [ ] source fidelity;
- [ ] staged and unstaged Git separation;
- [ ] ignore rules;
- [ ] safety warnings;
- [ ] character budget;
- [ ] cancellation;
- [ ] Last Run and History;
- [ ] tray;
- [ ] native restore hotkey;
- [ ] autostart;
- [ ] config recovery;
- [ ] single instance;
- [ ] application and tray icons.

### Release Evidence

- [ ] automated report declares version `1.3.0`;
- [ ] automated report declares `passed: true`;
- [ ] manual evidence references the final ZIP SHA-256;
- [ ] final readiness validation passes;
- [ ] repository is clean;
- [ ] local `main` equals `origin/main`;
- [ ] CI is green for the release commit.

### Intended commit

```text
docs: freeze v1.3.0 release candidate
```

---

## M15.11 — Tag, Publish, and Verify v1.3.0

**Status: PLANNED**

- [ ] create annotated `v1.3.0` tag;
- [ ] push the tag;
- [ ] create GitHub draft release;
- [ ] attach ZIP and checksum;
- [ ] review final release notes;
- [ ] publish release;
- [ ] download published assets;
- [ ] verify downloaded SHA-256;
- [ ] extract and run the downloaded build;
- [ ] confirm About and `VERSION.txt`;
- [ ] confirm release badge;
- [ ] confirm both assets are present;
- [ ] update roadmap status to `DONE — RELEASED`;
- [ ] publish Telegram release announcement.

### Release Completion Rule

v1.3.0 is complete only after the published downloadable artifact has been independently verified.

---

# v1.4.0 Windows Workflow & Distribution

**Status: PLANNED**

## Goal

Improve installation, maintenance, and long-term Windows use without weakening the portable release path.

### Planned Scope

- [ ] editable restore hotkey;
- [ ] conflict validation before saving;
- [ ] reset-to-default hotkey;
- [ ] optional Collect & Copy hotkey;
- [ ] repository and release links in About;
- [ ] Windows installer;
- [ ] clean uninstall;
- [ ] explicit settings preservation/removal behavior;
- [ ] explicit portable mode;
- [ ] update-availability check;
- [ ] open release page from the app;
- [ ] persistent runtime history;
- [ ] history export;
- [ ] installer and portable validation gates.

An update-availability check is preferred to a full self-updater. A self-updater requires stronger signature, rollback, atomic replacement, and failure-recovery guarantees.

---

# v1.5.0 Advanced Context Rules

**Status: PLANNED**

## Goal

Provide advanced control for large or specialized repositories without complicating the default workflow.

### Planned Scope

- [ ] per-project presets;
- [ ] reusable collection profiles;
- [ ] advanced include/exclude editor;
- [ ] extension-specific file size rules;
- [ ] context priority rules;
- [ ] selected-directory scopes;
- [ ] generated-code exclusion profiles;
- [ ] configurable project-tree depth;
- [ ] optional output preview;
- [ ] optional partial-file strategies;
- [ ] advanced tree and diff controls;
- [ ] configurable safety categories;
- [ ] opt-in secret redaction;
- [ ] custom output templates;
- [ ] provider-specific token estimation.

---

# Development and Validation Rules

## Milestone Rule

Every milestone must be completed in this order:

1. implement one focused change set;
2. provide only the changed files in a ZIP with repository-relative paths;
3. extract into the repository root;
4. run compile checks;
5. run targeted tests;
6. run the full test suite;
7. perform the required manual GUI checks;
8. inspect `git status`;
9. commit the completed milestone;
10. pull with rebase;
11. push;
12. continue only after the pushed milestone is confirmed.

## Standard Local Gate

```powershell
python -m compileall -q src tests scripts gui.py run.py hotkey.py; python scripts\check_version_consistency.py; python -m pytest -q
```

## Repository Synchronization

```powershell
git status --short; git pull --rebase; git push
```

## Scope Rule

Before each implementation stage, request only the exact files required for that stage. Do not request the complete project when a local subset is sufficient.

## PowerShell Rule

Every PowerShell command in project instructions must be written on one physical line without backtick continuations.

---

# Immediate Next Step

Apply and validate **M15.5 — Collect Setup Redesign**, including the full test suite and manual checks for every mode-specific action, Source summary, helper text, review affordance, clear action, Compact mode guarantee, and active-collection disabled states.

After M15.5 is committed and pushed, continue with:

> **M15.6 — Last Run Metrics Redesign**

The v1.3.0 tag and public release remain blocked until M15.11 is complete.
