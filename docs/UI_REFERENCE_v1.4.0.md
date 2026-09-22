# XCC v1.4.0 UI Reference Contract

Target: `v1.4.0`  
Status: **RELEASE CANDIDATE**

This document extends the v1.3.1 responsive/DPI contract with the Attachments workflow, persistent History, configurable hotkeys, current About composition, and v1.4.0 polish.

## 1. Product identity

- dark neutral surfaces;
- restrained gold accent for selected/action states;
- Segoe UI system typography;
- no decorative animation;
- X-SERIES footer mark remains a low-contrast, non-interactive signature.

Base logical metrics remain compatible with v1.3.1:

```text
window title bar: 48
footer: 36
large sidebar: 228
window control width: 52
normal control height: 40
primary action: ~52–54
minimum window: 920×620
```

## 2. Navigation

```text
Collect
Attachments
History
Settings
About
```

All five are real exclusive navigation buttons. Keyboard/wheel navigation keeps the existing focus and one-page-per-event rules.

## 3. Shared responsive surface

Responsive decisions use Qt logical viewport geometry.

```text
COMPACT: < 820
MEDIUM:  820–1119
LARGE:   >= 1120

SHORT:    < 700 high
STANDARD: 700–799
TALL:     >= 800
```

Collect uses the established progressive workbench. Attachments, History, Settings, and About share the same outer progressive page-surface width/insets. About no longer has a separate 1320 px fixed cap.

Normal page-level horizontal scrolling is disabled.

## 4. Attachments

Large composition:

```text
Attachments
Source
Selection | Transfer
```

Constrained composition stacks Transfer below Selection without recreating the business widgets.

Selection contract:

- ordered explicit files;
- visible root / Mixed locations;
- visible file count and aggregate bytes;
- File column stretches;
- Size column is compact/fixed and its header + values are centered;
- selected row has one left-edge gold indicator, not one per cell.

Transfer actions:

- Copy Files;
- Send One-by-One;
- Create ZIP & Copy;
- Open bundle location when applicable.

The page must clearly communicate file handoff, not text-context generation.

## 5. Automated Attachment Handoff

`Send One-by-One` is explicitly user-armed.

Visual states include:

- 3-second countdown for button start;
- visible `N/total` progress;
- cancellation;
- completed/failed state.

The UI must not imply that `sent` means third-party upload completion. It means XCC prepared the file and dispatched the paste action to the locked foreground target.

## 6. History

History is persistent metadata, not a source-code database.

- restart persistence;
- Clear History;
- Export JSON;
- collection + attachment-transfer records;
- long metadata wraps;
- no horizontal history scrollbar.

## 7. Settings / first-run defaults

First-run product defaults:

```text
Default mode:             Selected Files
Compact mode:             Disabled
Max output chars:         3,000,000
Start with Windows:       On
Start minimized to tray:  On
Start maximized:          On
Close to tray:            On
Tray notifications:       Off
Safety confirmation:      Off
Interface scale:          110%
Restore / Show:           On   Ctrl+Alt+X
Collect & Copy:           Off  Ctrl+Alt+C
Attachment Handoff:       Off  Ctrl+Alt+V
```

The very first visible launch must not disappear unexpectedly into the tray merely because the persisted startup default is enabled.

## 8. About

About is a full product page using the shared outer page width:

- hero / version / positioning;
- What XCC does;
- Privacy & guarantees;
- Runtime & paths;
- live hotkey/startup state;
- responsive `2 columns -> 1`;
- badges `4 -> 2` when constrained.

## 9. QSS / semantic tokens

Application styles are built from semantic palette tokens. Replacement must resolve longer token names before shorter prefix tokens so values such as `@accent_hover` cannot be partially rendered as invalid colors.

Clean startup must not emit `QCssParser::parseHexColor` warnings caused by XCC stylesheets.

## 10. DPI / work-area lifecycle

The v1.3.1 contract remains:

- Qt logical geometry drives composition;
- raster/SVG presentation assets rerender for active DPR;
- maximize uses current `availableGeometry()`;
- normal geometry is clamped to the current work area;
- tray/hotkey restore preserves intended window state;
- unsupported hardware/manual cases are recorded as NOT TESTED, never inferred as PASS.

## 11. Accessibility / interaction

- primary controls and status surfaces retain accessible names;
- keyboard-only operation remains viable;
- disabled/hover/pressed/focus/selected states remain distinct;
- page reflow reuses the same business widgets/signals.

## 12. Required release validation

Automated:

- width/height breakpoints;
- progressive workbench distribution;
- Attachments/Settings/About reflow;
- Size-column alignment and single selection accent;
- resize round-trip/state preservation;
- no horizontal page scrolling;
- hotkey conflict/rollback;
- Handoff order/focus/cancel/failure;
- persistent History schema/retention/corruption;
- QSS token rendering.

Manual/package:

- minimum window and Full HD;
- available DPI/interface-scale cases;
- real Copy Files to Explorer;
- real one-file-per-paste Handoff target;
- focus-change stop;
- ZIP create/cancel/extract/hash;
- persistent History restart/export/clear/corruption;
- tray/hotkey restore and startup behavior.
