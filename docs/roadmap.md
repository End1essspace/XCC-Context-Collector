# XCC Roadmap

Last updated: 2026-07-31  
Current source version: `1.3.0`  
Current release state: **v1.3.0 RELEASE CANDIDATE PREPARATION — M15.10 IN PROGRESS**  
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

**Status: RELEASE CANDIDATE PREPARATION — M15.10 IN PROGRESS**  
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

**Status: IN PROGRESS — M15.10 DOCUMENTATION FREEZE AND RELEASE CANDIDATE**

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

**Status: DONE**

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
- [x] full Qt suite and visual behavior pass local Windows validation;
- [x] changes are committed and pushed.

### Intended commit

```text
feat: redesign collect setup workflow
```

---

## M15.6 — Last Run Metrics Redesign and Visual Calibration

**Status: DONE**

### Goal

Bring the real Collect page materially closer to the approved reference while
preserving the semantic improvements already made in M15.4 and M15.5.

### Approved shell calibration

- [x] keep the native Windows title bar;
- [x] remove the duplicate in-app app icon and product-title header;
- [x] move runtime and hotkey capsules into the Collect page header;
- [x] increase page-title and group-title hierarchy;
- [x] widen and strengthen the sidebar without restoring a bright gold block;
- [x] increase footer height and edge spacing;
- [x] use quieter card borders and subtle surface depth;
- [x] refine the primary action with a restrained gradient and copy icon;
- [x] add a Paste Paths icon without changing its workflow semantics.

### Target Structure

```text
Last Run                                  Completed · 17:36:36

Volume            Output            Coverage           Health
Files       51     Characters 356,647 Included     51   Outcome       Success
Lines   10,691     Tokens      89,161 Omitted       0   Duration       0.15 s
Source 349,675     Truncated       No Summary  0 / 0   Warnings / Errors 0 / 0
```

### Work

- [x] group metrics into four semantic columns;
- [x] add restrained group icons;
- [x] replace stacked label/value capsules with horizontal metric rows;
- [x] set the large-layout metric-row height to 58 px;
- [x] increase the Last Run card height to fit the metrics comfortably;
- [x] add subtle column separators;
- [x] align labels left and values right;
- [x] add consistent thousands separators;
- [x] use semantic result colors;
- [x] preserve a clear pre-run empty state;
- [x] keep `CollectionRunRecord` as the data source;
- [x] align Last Run and History outcome semantics;
- [x] add pure formatting/state policy tests;
- [x] add packaged SVG assets for card, group, and action icons.

### Semantic Colors

- Success — restrained green;
- With warnings — restrained amber;
- Cancelled — neutral gray;
- Failed — restrained red;
- Gold remains an interface accent, not a universal result color.

### Implementation Result

- `src/xcc/ui_metrics.py` owns integer formatting and metric semantic-state policy;
- `MetricCapsule` is now a 58 px horizontal row with aligned label and value;
- `PageHeader` supports right-aligned runtime actions;
- `IconTitle` provides reusable card and metric-group icon headers;
- the duplicate content-area app header is removed;
- Setup, Last Run, Paste Paths, and Collect & Copy use packaged SVG assets;
- Last Run and History share the same outcome-state mapping;
- the malformed `3,566,47` style is prevented by tested formatting helpers.

### M15.6.1 — Icon Rendering and Visual Polish

**Status: DONE**

- [x] official Lucide SVG files are tinted at runtime instead of relying on embedded black strokes or `currentColor`;
- [x] Setup, Last Run, Volume, Output, Coverage, Health, and Paste Paths use the semantic gold accent;
- [x] Collect & Copy keeps a deterministic dark icon on the gold primary surface;
- [x] source and packaged builds use the same SVG rendering path;
- [x] high-DPI 1× and 2× icon pixmaps are generated by the reusable component layer;
- [x] the selected sidebar item gains a restrained border without returning to a bright gold block;
- [x] the Last Run header title and state capsule are vertically calibrated;
- [x] the primary action gradient is reduced in brightness;
- [x] Qt regression tests inspect rendered icon pixels and reject black central icons.

### Acceptance Criteria

- [x] only the native Windows title bar displays persistent app identity;
- [x] runtime and hotkey capsules are aligned with the Collect page title;
- [x] all twelve metric rows are 58 px high in the large layout;
- [x] Last Run values use stable thousands separators;
- [x] empty metrics remain neutral and do not show misleading zeros;
- [x] outcome, truncation, coverage, and issue states are semantic;
- [x] no collection-domain module was changed;
- [x] full Qt suite and visual behavior pass local Windows validation;
- [x] changes are committed and pushed.

### Intended commit

```text
feat: redesign last run metrics
```

---

## M15.7 — Responsive Layout and Premium Visual Polish

**Status: DONE**

**M15.7.5 SIDEBAR BRAND SCALE POLISH — CLOSED**

### Goal

Make the approved interface work across the complete supported window range
without clipping, permanent scrollbars, delegate-driven sidebar defects, or
wasted vertical space. The same widgets, collection behavior, tab order,
accessible names, and domain boundaries remain intact.

### Width policy

Width arrangement is selected from the central **content viewport**, not from
the complete main-window width:

```text
Large content viewport:   1120 px and wider
Medium content viewport:   820–1119 px
Compact content viewport:  below 820 px
Supported window minimum:  920 × 620
```

### Height policy

Height density is calculated independently on every viewport resize:

```text
Tall:      viewport height ≥ 800 px
Standard:  viewport height 700–799 px
Short:     viewport height < 700 px
```

This prevents a width-only breakpoint from retaining stale geometry after a
height change.

### Stable responsive behavior

- [x] large layout keeps one-row Source actions and four metric groups;
- [x] medium layout moves Source actions below and uses a 2×2 metric grid;
- [x] compact layout uses 2×2 modes and metrics;
- [x] horizontal scrolling is always disabled;
- [x] helper text is removed only from compact density;
- [x] the same widget instances are moved between layouts;
- [x] signals are not duplicated.

### M15.7.1 — Maximized Geometry and Sidebar Rhythm

**Status: SUPERSEDED BY M15.7.2**

The first corrective patch increased card minimum heights and adjusted list
delegate geometry. Windows evidence showed that this did not solve the root
cause:

- maximized Collect still exposed a vertical scrollbar;
- the CTA could remain partially below the viewport;
- Setup and Last Run held excessive fixed minimum heights;
- Settings could still be clipped by `QListWidget` viewport/delegate rounding;
- sidebar composition remained top-heavy.

The replacement below removes those failure modes rather than adding another
fixed-height correction.

### M15.7.2 — Geometry Architecture Reset and Sidebar Rebuild

**Status: DONE**

#### Sidebar rebuild

- [x] remove the two `QListWidget` navigation surfaces;
- [x] remove delegate painting and manually calculated list heights;
- [x] add `src/xcc/ui_sidebar.py`;
- [x] use four real navigation buttons;
- [x] add a compact product identity anchor;
- [x] keep Collect, History, and Settings in the workspace zone;
- [x] keep About anchored below an expanding spacer;
- [x] use 50 px rows and 8 px inter-item gaps;
- [x] preserve exclusive selection;
- [x] preserve visible focus and accessible names;
- [x] support Up/Down navigation across all four actions;
- [x] guarantee that Settings cannot be clipped by item-view geometry.

#### Collect geometry reset

- [x] derive width mode from the actual content viewport;
- [x] derive height density independently;
- [x] recalculate height geometry inside one width mode;
- [x] keep the 42 px single-row title/subtitle/actions header;
- [x] elide the subtitle before runtime actions can be displaced;
- [x] make Setup a fixed content-driven card;
- [x] remove oversized 286 px / 332 px large-layout minimums;
- [x] make Last Run the expanding primary card;
- [x] preserve an explicit expanding Last Run geometry contract;
- [x] give Last Run layout stretch instead of static empty space;
- [x] cap Last Run expansion per density so extra height does not become a large empty lower zone;
- [x] allow metric rows to expand equally within minimum/preferred/maximum
  height ranges;
- [x] keep Collect & Copy fixed and fully visible in every scroll-free layout;
- [x] remove size-hint feedback from scrollbar decisions;
- [x] reset Collect content minimum height when the natural page fits;
- [x] enable vertical scrolling only when natural content exceeds viewport
  height;
- [x] continue recalculating after the Qt layout pass.

#### Pure policy and Qt coverage

- [x] test content-viewport breakpoints;
- [x] test Tall, Standard, and Short geometry;
- [x] test the maximized large natural height;
- [x] test compact minimum scrolling policy;
- [x] test real sidebar buttons and exclusive selection;
- [x] test keyboard movement from Settings to About;
- [x] add maximized and 920×620 GUI geometry tests;
- [x] keep all collection-domain modules unchanged.

### M15.7.3 — Mode Group and Sidebar Brand Composition

**Status: DONE**

Windows review confirmed that the geometry reset solved clipping and scrollbar
defects, but two composition problems remained: the four collection modes were
distributed across the complete Setup width, and the sidebar identity looked
like a detached card rather than one integrated brand lockup.

#### Mode composition

- [x] keep one compact left-aligned radio group;
- [x] remove equal column stretch between mode options;
- [x] cap the group width per responsive mode;
- [x] keep large and medium layouts on one row;
- [x] keep compact layout as a stable 2×2 group;
- [x] preserve the same four radio buttons, group ids, focus behavior, and
  source-reset semantics;
- [x] leave unused Setup width after the final option.

#### Sidebar identity composition

- [x] remove the detached identity-card treatment;
- [x] use one flat 68 px brand lockup;
- [x] place the app artwork inside a restrained 42 px mark;
- [x] align `XCC` and `Context Collector` as one tight text stack;
- [x] align the lockup with navigation content;
- [x] keep the workspace label, real navigation buttons, and bottom About
  placement unchanged;
- [x] preserve accessible identity and navigation names.

#### Coverage

- [x] add pure responsive-policy assertions for mode-group width and gaps;
- [x] add Qt coverage for compact left alignment and maximum width;
- [x] add Qt coverage for the final brand-lockup geometry;
- [x] register the composition contract in metadata and theme tests;
- [x] keep collection-domain modules and assets unchanged.

### M15.7.4 — Product Density and Branding Polish

**Status: DONE**

Windows review confirmed that M15.7.3 corrected mode distribution, but the final
page still had an uneven density profile: Setup was visually compressed, Last
Run was too open, and the 42 px framed logo treatment made the product identity
look smaller than the surrounding interface.

#### Product-scale sidebar identity

- [x] remove the square logo-mark container and its border treatment;
- [x] use the transparent application artwork directly at product scale;
- [x] use one product-scale 82 px brand lockup;
- [x] render the logo in a 56 px area with a 54 px smooth pixmap;
- [x] increase `XCC` to a 20 px high-weight title;
- [x] increase and clarify the `Context Collector` subtitle;
- [x] preserve navigation alignment, accessible identity, and bottom About
  placement.

#### balanced Setup and Last Run density

- [x] increase Setup card height and internal top/bottom padding;
- [x] increase semantic-row spacing without widening the mode group;
- [x] keep Source and Options helper text comfortably separated from controls;
- [x] reduce Last Run outer padding and header-to-grid spacing;
- [x] reduce metric-group and metric-row gaps;
- [x] lower Last Run maximum height so the card does not become an empty
  dashboard shell;
- [x] keep 54–60 px metric rows in the maximized large layout;
- [x] keep the natural maximized page height below the available viewport;
- [x] preserve conditional scrolling at short and compact sizes.

#### Coverage

- [x] update responsive policy assertions for the new density allocation;
- [x] add Qt geometry assertions for Setup padding and Last Run density;
- [x] verify the sidebar contains no framed logo-mark widget;
- [x] register the product-scale identity and balanced-density contract in
  metadata and theme tests;
- [x] keep assets, collection-domain modules, and Selected Files behavior
  unchanged.

### M15.7.5 — Sidebar Brand Scale Polish

**Status: DONE**

The M15.7.4 screenshot confirmed that removing the logo frame was correct, but
the 54 px rendered artwork dominated the sidebar and made the identity heavier
than the navigation. This micro-step keeps the same flat branding concept while
restoring a restrained product hierarchy.

#### Final sidebar brand scale

- [x] keep the transparent logo treatment without a square container;
- [x] reduce the identity zone from 82 px to 72 px;
- [x] reduce the logo area from 56 px to 44 px;
- [x] render the application artwork at 42 px with smooth scaling;
- [x] reduce the `XCC` title from 20 px to 18 px;
- [x] tighten logo-to-text spacing from 14 px to 11 px;
- [x] preserve subtitle readability, alignment, accessible identity, and all
  navigation behavior;
- [x] keep Setup, Last Run, responsive layout, assets, and collection behavior
  unchanged.

### Required Windows evidence

#### 1688×900 or maximized large window

- [ ] no vertical scrollbar;
- [ ] Collect & Copy is fully visible;
- [ ] Setup has no clipping and no oversized empty lower zone;
- [ ] Last Run uses the remaining height;
- [ ] all twelve metric rows have complete borders;
- [ ] all four sidebar actions are fully visible;
- [ ] Settings is not clipped;
- [ ] About is visually anchored at the bottom.

#### 1200 px width

- [ ] Source actions move below correctly;
- [ ] Last Run uses 2×2 groups;
- [ ] no horizontal clipping;
- [ ] vertical scrolling depends only on available height.

#### 920×620

- [ ] vertical scrolling is available;
- [ ] horizontal scrolling is absent;
- [ ] every mode, Source action, metric group, and CTA is reachable;
- [ ] sidebar remains usable without hiding labels.

### Intended commit

```text
fix: calibrate sidebar brand scale
```

---

## M15.8 — Dialog Visual Integration

**Status: DONE**

Completed:

- [x] Paste Paths matches the final theme, typography, spacing, and action hierarchy;
- [x] project-root input and Browse action are visually integrated;
- [x] path input readability and long-root tooltips are preserved;
- [x] validation summaries distinguish neutral, success, warning, and error states;
- [x] Add Files remains disabled when nothing can be applied;
- [x] Selected Files Review presents project root or `Mixed locations` clearly;
- [x] file-count badge, list rows, selection state, and action rows are calibrated;
- [x] multi-select, `Delete`, `Remove Selected`, `Clear All`, transactional `Cancel`, and explicit `Apply Changes` remain intact;
- [x] dedicated dialog tests cover validation states, large selections, root scope, and transactionality;
- [x] changes were validated, committed, and pushed.

### Commit

```text
feat: align selected files dialogs with new UI
```

---

## M15.9 — UI Regression, Accessibility, and Final Polish

**Status: DONE**

Completed:

- [x] mode-specific labels, Paste Paths visibility, Source summaries, clear behavior, and review opening are regression-covered;
- [x] collection-active disabled state and header/footer status separation are covered;
- [x] final hotkey display uses `Ctrl+Alt+X`;
- [x] footer status, version, Last Run state, primary action, and metric rows expose accessibility names;
- [x] long project roots and validation summaries expose useful tooltips and descriptions;
- [x] keyboard focus treatment was strengthened for primary actions, Source review, and clear actions;
- [x] disabled buttons, fields, radio buttons, and checkboxes remain legible;
- [x] real-window semantics cover long paths, `Mixed locations`, 100+ files, clearing, review, and active collection state;
- [x] final visual polish was validated, committed, and pushed.

### Commit

```text
fix: complete v1.3.0 interface polish
```

---

## M15.10 — Documentation Freeze and Release Candidate

**Status: IN PROGRESS — DOCUMENTATION FREEZE**

### Documentation freeze

- [x] README aligned with the final Selected Files workflow and interface;
- [x] changelog aligned with final v1.3.0 behavior;
- [x] architecture expanded to include presentation, responsive, accessibility, threading, fidelity, security, and packaging boundaries;
- [x] M15 validation procedure aligned with the final UI and release gate;
- [x] release checklist aligned with the final release-candidate process;
- [x] v1.3.0 release notes aligned with the final interface;
- [x] roadmap statuses updated through M15.9;
- [ ] replace `docs/screenshots/xcc-collect.png` with the final Collect screenshot;
- [ ] replace `docs/screenshots/xcc-history.png` with the final History screenshot;
- [ ] commit and push the documentation-and-screenshot freeze.

### Automated gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0
```

Required outputs:

```text
artifacts\XCC-Context-Collector-v1.3.0-win64.zip
artifacts\XCC-Context-Collector-v1.3.0-win64.zip.sha256
artifacts\XCC-v1.3.0-automated-gate.json
```

### Packaged validation

- [ ] final application shell, sidebar, Setup, Last Run, dialogs, and responsive behavior;
- [ ] correct v1.3.0 labels and complete packaged assets;
- [ ] Paste Paths, guarded `Ctrl+V`, and Selected Files Review;
- [ ] all four collection modes;
- [ ] source fidelity, Git separation, ignore rules, safety, budget, and cancellation;
- [ ] Last Run, History, tray, native hotkey, autostart, config recovery, and single instance;
- [ ] minimum, normal, maximized, 100%, 125%, and 150% interface checks.

### Release evidence

- [ ] automated report declares version `1.3.0`;
- [ ] automated report declares `passed: true`;
- [ ] clean-install validation passed;
- [ ] manual evidence references the exact final ZIP SHA-256;
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

Complete **M15.10 — Documentation Freeze and Release Candidate** in this order:

1. apply the documentation-freeze archive;
2. capture and replace the final Collect and History screenshots;
3. run the complete source gate;
4. commit and push the frozen documentation and screenshots;
5. run `scripts\validate_release_candidate.ps1 -ExpectedVersion 1.3.0`;
6. perform packaged validation and collect matching Windows evidence;
7. run final readiness.

After M15.10 passes for the final archive and release commit, continue with:

> **M15.11 — Tag, Publish, and Verify v1.3.0**

The `v1.3.0` tag remains blocked until final readiness passes.
