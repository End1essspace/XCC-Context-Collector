# XCC Roadmap

Last updated: 2026-08-17  
Current source version: `1.3.1`  
Current state: **v1.3.1 RELEASE CANDIDATE FREEZE**  
Supported runtime: `gui.py -> xcc.gui -> xcc.pipeline`

## Release overview

| Release | Status | Scope |
|---|---|---|
| v1.0.x | DONE | Desktop shell, tray, native hotkey, autostart, single instance |
| v1.1.x | DONE | Broader source coverage and Project Tree |
| v1.2.0 | DONE — RELEASED | Source fidelity, Git context, safety, background collection, reproducible release gates |
| v1.3.0 | DONE — RELEASED | Paste Paths, Selected Files Review, final product UI |
| **v1.3.1** | **IN PROGRESS — RC FREEZE** | Responsive, DPI, work-area reliability, Interface scale, X-SERIES footer |
| v1.4.0 | PLANNED | Windows workflow and distribution improvements |
| v1.5.0 | PLANNED | Advanced context rules and profiles |

Historical implementation detail lives in Git history and release notes. This file tracks release outcomes and the active path only.

# v1.3.1 — Responsive & DPI Reliability Patch

## M16.0 — Audit & baseline
**DONE** — Full HD reference, QHD/DPI failures, main-page/dialog/window risks recorded.

## M16.1 — Responsive contract
**DONE** — logical viewport breakpoints, independent height density, `920×620` minimum, hysteresis and regression anchors frozen.

## M16.2 — Central responsive foundation
**DONE** — shared page-width distribution and centered workbench behavior introduced without duplicating controls.

## M16.3 — Collect calibration
**DONE** — Full HD baseline preserved; wide-layout behavior calibrated from real visual evidence.

## M16.4 — Main pages
**DONE** — Settings, History and About made responsive; normal horizontal page scrolling removed.

## M16.5 — Dialogs
**DONE** — Paste Paths and Selected Files Review made work-area-aware with vertical overflow and long-path resilience.

## M16.6 — Window / DPI lifecycle
**DONE** — work-area clamp, restore behavior, screen changes, DPI-aware raster/SVG rerendering and teardown safety.

## M16.7 — Automated responsive regression
**DONE** — breakpoint `B-1/B/B+1`, height `H-1/H/H+1`, resize round-trip, widget/state preservation and responsive page invariants.

## M16.8 — Manual visual / DPI correction cycle
**DONE** — real display validation completed; fixes include progressive wide workbench, Interface scale, About scale integration, XCC-styled scale selector, content-aware selector width, and `X-SERIES` footer branding.

## M16.9 — Version / docs / release candidate
**CURRENT — DOCUMENTATION FREEZE**

Deliverables:

- canonical version `1.3.1`;
- current README/changelog/architecture/UI reference;
- `docs/M16_VALIDATION.md`;
- `docs/releases/v1.3.1.md`;
- v1.3.1 release tooling and evidence gates;
- source gate, commit, push, clean synchronized `main`.

## M16.10 — Build / tag / publish / verify
**PLANNED**

```text
release-candidate gate
→ final ZIP + SHA-256 + automated report
→ packaged/manual Windows 10 + 11 evidence
→ readiness gate
→ tag v1.3.1
→ GitHub Release
→ independently download/hash/extract/run public artifact
→ DONE — RELEASED
```

# Next releases

## v1.4.0 — Windows Workflow & Distribution

Planned: configurable hotkeys, installer/uninstall path, update availability, persistent/exportable history, and stronger installer/portable release gates.

## v1.5.0 — Advanced Context Rules

Planned: project profiles, advanced include/exclude rules, configurable tree/Git controls, output preview, context priorities, and provider-specific estimates.

# Development rule

A milestone is closed only after its change is validated, committed, and pushed. Release publication is complete only after the published artifact itself has been downloaded and verified.
