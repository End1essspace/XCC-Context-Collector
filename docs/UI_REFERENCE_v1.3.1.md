# XCC v1.3.1 UI Reference Contract

Target: `v1.3.1`  
Status: **FROZEN — RELEASE CANDIDATE**

This document defines the visual/interaction contract added by the Responsive & DPI Reliability Patch. Collection semantics remain governed by the existing product contracts.

## 1. Product identity

- dark neutral surfaces;
- restrained gold accent for selected/action states;
- Segoe UI system typography;
- no decorative animation;
- X-SERIES footer mark is a low-contrast signature, not a primary control.

Core metrics at the base logical scale:

```text
window title bar: 48
footer: 36
large sidebar: 228
window control width: 52
normal control height: 40
primary action: ~52–54
minimum window: 920×620
```

## 2. Shell

The frameless shell contains:

```text
sidebar brand + navigation | title bar + active page
---------------------------------------------------
footer event/status                                X-SERIES
```

Window controls remain edge-aligned. The close target cannot extend invisibly outside the real button rectangle.

Header status is short runtime state. Footer text is progress/event guidance. These roles stay separate.

## 3. Responsive model

Responsive decisions use Qt **logical viewport geometry**.

```text
COMPACT: < 820
MEDIUM:  820–1119
LARGE:   >= 1120

SHORT:    < 700 high
STANDARD: 700–799
TALL:     >= 800
```

Width and height are independent. Reflow happens before controls are compressed. Business widgets are reused; responsive changes do not create duplicate controls or duplicate signal connections.

Normal utility/settings pages must not require horizontal scrolling.

## 4. Wide-screen workbench

Full HD @100% is the composition reference, not a resolution-specific mode.

```text
reference useful width: 1692 logical px
extra-width admission: 75%
outer breathing room: 25%
hard useful-width ceiling: 3200
```

No production branch may test for QHD, 4K, 125%, or 150% as named resolutions/scales. Windows/Qt already exposes scaled logical geometry.

## 5. Collect

Large state keeps:

- 4 mode choices in one compact row;
- Source and action inline;
- 4 Last Run metric groups;
- visible subtitle/helpers;
- full-width primary CTA inside the useful workbench.

Medium/Compact may move Source actions below and use 2-column metric reflow. Vertical scrolling appears only when natural content cannot fit the available height.

## 6. Settings / History / About

**Settings:** two columns at large width; one stacked column when constrained. Rows are content-aware, not fixed-height clipping surfaces.

**History:** follows the progressive workbench; long source/metadata wraps; no horizontal history scrollbar.

**About:** readability-oriented bounded surface. Its base cap is `1320` logical px and is multiplied only by an explicit XCC Interface scale override. Badge layout is 4 columns at normal width and 2×2 when compact.

## 7. Dialogs

Paste Paths and Selected Files Review:

- use the current screen `availableGeometry()`;
- retain a 24 px logical work-area edge margin where possible;
- never rely on normal horizontal scrolling;
- allow vertical overflow;
- keep footer actions reachable;
- tolerate long paths and large selections.

## 8. Interface scale

Settings → Interface scale:

```text
Auto (recommended)
90%
100%
110%
120%
125%
150%
```

`Auto` follows Windows/Qt. Explicit values are Qt global multipliers applied before `QApplication` exists. A restart is required.

The selector must:

- keep its arrow inside the control;
- show the XCC gold selected-state indicator;
- size itself so `Auto (recommended)` is not clipped;
- remain compact rather than stretching across the Settings row.

## 9. DPI assets

Raster and SVG presentation assets must rerender for the active DPR after screen/DPI changes. Logical icon sizes remain stable; only raster density changes.

Covered surfaces include app branding, About branding, card icons, window controls, and the footer X-SERIES wordmark.

## 10. Window lifecycle

- maximize uses the current screen work area;
- restore geometry is clamped to that work area;
- minimize → restore, tray → restore, and hotkey → restore preserve the intended window mode;
- screen/work-area changes refit only when necessary;
- unavailable hardware cases are recorded as `NOT TESTED`, never inferred as PASS.

## 11. Accessibility / interaction

- primary controls and status surfaces keep accessible names;
- keyboard navigation remains usable;
- disabled/hover/pressed/focus/selected states remain distinct;
- sidebar wheel navigation changes at most one page per event and transfers focus to the active button.

## 12. Release validation matrix

Required automated coverage:

- `B-1/B/B+1` width boundaries;
- `H-1/H/H+1` height boundaries;
- wide-workbench distribution;
- Settings/About reflow;
- dialog sizing;
- resize round-trip and state/widget preservation;
- no horizontal page scrolling;
- work-area restore;
- DPR-aware asset rerendering.

Required manual review includes minimum window, Full HD baseline, QHD scaling cases where available, Interface scale, dialogs, About, restore lifecycle, and available multi-monitor/DPI cases.

Only release-blocking corrections may change this contract after M16.9 freeze.
