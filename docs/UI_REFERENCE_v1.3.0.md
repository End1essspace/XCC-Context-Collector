# XCC v1.3.0 Final UI Reference Contract

Version: 1.0  
Target release: `v1.3.0`  
Status: **FROZEN FOR IMPLEMENTATION**  
Applies to: supported PySide6 application (`gui.py -> xcc.gui -> xcc.pipeline`)  
Minimum supported window: `920 × 620`

---

## 1. Purpose

This document is the authoritative visual and behavioral contract for the final XCC v1.3.0 interface redesign.

The approved generated mockup defines the intended product direction: a premium dark Windows utility with restrained gold accents, clear hierarchy, compact operational information, and a calm commercial finish. The mockup is not a literal implementation specification. Where the image conflicts with real XCC behavior, accessibility, or responsive constraints, this document takes precedence.

The redesign must improve presentation without changing collection semantics, source-content fidelity, safety behavior, history privacy, tray behavior, native hotkey behavior, or the Selected Files workflow completed in M11–M13.

---

## 2. Product Experience Goals

The final interface must feel:

- professional rather than experimental;
- dense but calm;
- immediately understandable without a tutorial;
- consistent across Collect, History, Settings, About, Paste Paths, and Selected Files Review;
- stable from the minimum window through maximized 2K displays;
- clearly Windows-native in interaction even though it uses a custom dark visual system.

The user should understand the main workflow within a few seconds:

```text
Choose mode -> choose or paste source -> adjust options -> Collect & Copy -> review result health
```

---

## 3. Non-Goals

The v1.3.0 redesign must not introduce:

- a custom frameless title bar;
- animated backgrounds, decorative particles, or heavy glow;
- a collapsible or icon-only sidebar;
- installer or updater controls;
- editable global hotkeys;
- persistent history;
- an output editor or preview page;
- new collection behavior;
- any transformation of collected source payloads.

Visual restructuring must remain separate from collection-domain logic.

---

## 4. Visual System

### 4.1 Color roles

The exact values may receive minor final calibration from real screenshots, but the semantic roles are fixed.

| Role | Target value | Usage |
|---|---:|---|
| Window background | `#0E0F11` | Main application background |
| Header / footer | `#141517` | Persistent shell surfaces |
| Sidebar | `#111214` | Navigation surface |
| Card | `#17181A` | Primary content cards |
| Raised row | `#1B1C1F` | Metric rows, settings rows, list rows |
| Input | `#101113` | Text inputs and read-only source fields |
| Quiet border | `#302D26` | Low-emphasis separation |
| Accent border | `#57471F` | Focused or important controls |
| Gold accent | `#D2A533` | Active navigation, primary action, key emphasis |
| Gold hover | `#E0B440` | Hover and focused accent state |
| Primary text | `#F2F3F4` | Titles and primary values |
| Secondary text | `#ADB1B7` | Labels and descriptions |
| Muted text | `#7F848C` | Helper text and inactive metadata |
| Success | `#69B985` | Successful runtime/result state |
| Warning | `#D5A13B` | Warning state |
| Error | `#D86C6C` | Failure state |
| Cancelled / neutral | `#90959D` | Cancelled or neutral state |

Gold is an interface accent. It must not be used as the universal color for every metric or outcome.

### 4.2 Typography

- Primary family: `Segoe UI`.
- Monospace family: `Consolas` for file paths and pasted path lists.
- Page title: 22–24 px equivalent, bold.
- Card title: 13–14 px equivalent, bold.
- Body: 12–13 px equivalent.
- Helper text: 11–12 px equivalent.
- Metric value: 14–16 px equivalent, semibold or bold.
- Avoid all-uppercase labels except established technical values.

Text must remain readable at Windows scaling values of 100%, 125%, and 150%.

### 4.3 Spacing and geometry

Use one consistent spacing scale:

```text
4, 8, 12, 16, 20, 24, 28 px
```

Preferred geometry:

- controls: 40 px standard height;
- primary action: 48–52 px height;
- header: 56 px height;
- footer: 32 px height;
- sidebar: approximately 184–192 px;
- card radius: 12–14 px;
- control radius: 8–10 px;
- capsule radius: 8–10 px.

Borders must remain subtle. Glow is permitted only as a very weak hover/focus effect and must never reduce text clarity.

### 4.4 Interaction states

Every interactive control must define:

- default;
- hover;
- pressed;
- keyboard focus;
- disabled.

Focus must be visible without relying only on color. Disabled controls must remain legible and must not look active.

---

## 5. Application Shell

### 5.1 Header

The header contains:

```text
[App icon] XCC Context Collector                      [Runtime state] [Hotkey]
```

Requirements:

- app icon remains 28 px and aligned with the title;
- title remains visually primary but not oversized;
- runtime state uses a restrained capsule;
- hotkey uses a separate lower-emphasis capsule;
- compact layouts may reduce capsule padding but must not remove the runtime state;
- the header must not display a verbose activity sentence.

Runtime-state vocabulary:

```text
Ready
Working
Cancelling
Copied
Warnings
Failed
Cancelled
```

The header owns **runtime state**. It does not own detailed progress or user guidance.

### 5.2 Sidebar

Navigation remains:

```text
Collect
History
Settings
About
```

Requirements:

- Collect, History, and Settings remain in the upper navigation zone;
- About remains anchored in the lower zone;
- selected navigation uses a quiet dark-gold surface plus a slim gold indicator;
- selected text and icon remain light/gold, not black on a large bright block;
- hover is visible but weaker than selected state;
- icon size and text baselines remain consistent;
- keyboard navigation and accessible names remain intact.

The sidebar must never visually overpower the Collect page.

### 5.3 Footer

The footer contains:

```text
[Current event, progress, or next action]                            v1.3.0
```

Examples:

```text
Ready · Select a source to begin
14 files selected
Collecting files: 9/14
Copied to clipboard
2 paths need review
```

The footer owns **event detail and progress**. It must not duplicate the header runtime capsule word-for-word unless no more useful message exists.

---

## 6. Collect Page Contract

### 6.1 Page header

Required copy:

```text
Collect Context
Configure what to collect and generate an AI-ready context snapshot.
```

The subtitle may be hidden only in the compact breakpoint when required to preserve core controls above the fold.

### 6.2 Primary structure

The page order is fixed:

```text
Page header
Setup card
Last Run card
Collect & Copy
```

The primary action stays visible without horizontal scrolling.

### 6.3 Setup card

The Setup card contains three semantic rows:

```text
Mode
Source
Options
```

The label column must align across all rows. The card title and row labels must not compete visually.

### 6.4 Mode row

The four modes remain:

```text
Selected Files
Full Folder
Git Changed Files
Project Tree
```

Requirements:

- radio controls use consistent spacing and focus behavior;
- the selected state is clear without a bright filled strip;
- controls may wrap only at medium or compact widths;
- changing mode preserves the existing source-reset semantics.

### 6.5 Source row: mode-specific semantics

The generic label `Select Source` is prohibited in the final interface. The action label must describe the real operation.

| Mode | Source summary | Primary source action | Secondary action |
|---|---|---|---|
| Selected Files | `Project · N files selected` | `Select Files` | `Paste Paths` |
| Selected Files, mixed roots | `N files selected · Mixed locations` | `Select Files` | `Paste Paths` |
| Full Folder | selected folder path | `Select Folder` | none |
| Git Changed Files | selected repository path | `Select Repository` | none |
| Project Tree | selected folder path | `Select Folder` | none |

Selected Files requirements:

- clicking Source opens Selected Files Review;
- keyboard `Enter`, `Return`, or `Space` opens review when the field is focused;
- the clear affordance remains visible when files exist;
- `Paste Paths` is visible only in Selected Files;
- the Source field visually communicates that it is reviewable;
- one file uses singular wording; all other counts use plural wording.

Folder/repository requirements:

- Source behaves as a read-only path display;
- tooltip exposes the complete path when the visible value is elided;
- clear removes the selected folder/repository.

### 6.6 Source helper text

Use mode-specific helper text:

| Mode | Helper text |
|---|---|
| Selected Files | `Choose files manually or paste paths returned by an AI assistant.` |
| Full Folder | `Collect supported files while respecting project ignore rules.` |
| Git Changed Files | `Collect supported changed files with staged and unstaged Git diffs.` |
| Project Tree | `Collect project structure without file contents.` |

Helper text is secondary. It must not increase the card height unnecessarily in compact mode.

### 6.7 Options row

Controls remain:

```text
Compact mode
Max chars
```

The Compact mode contract is exact:

```text
Reduce XCC-generated structural whitespace.
Source file contents remain unchanged.
```

The interface must never claim that Compact mode removes comments, rewrites source, or modifies file payloads.

`Max chars` remains a validated positive integer field and must stay aligned with the compact control.

### 6.8 Primary action

Required label:

```text
Collect & Copy
```

Requirements:

- full-width within the content column;
- 48–52 px height;
- restrained gold fill without strong glow;
- hover may increase brightness slightly;
- active collection changes the label to `Cancel`;
- cancellation state uses `Cancelling…` and disables repeated activation;
- success feedback may briefly use `Copied!` before restoring the normal label.

---

## 7. Last Run Contract

### 7.1 Header

The card header contains:

```text
Last Run                                      [Outcome · time]
```

Before the first run:

```text
No collection yet
```

The timestamp/outcome capsule is low emphasis and must not compete with the page title.

### 7.2 Metric groups

The data model remains divided into four groups:

| Volume | Output | Coverage | Health |
|---|---|---|---|
| Files | Output Characters | Included | Outcome |
| Lines | Output Tokens | Omitted | Duration |
| Source Characters | Truncated | Summarized / Partial | Warnings / Errors |

Requirements:

- use lighter metric rows rather than twelve visually heavy independent cards;
- values align consistently within each group;
- group separation is visible through spacing or subtle dividers;
- labels remain readable at the compact breakpoint;
- the card must support an empty state without misleading zeros.

### 7.3 Number formatting

Integer counts greater than or equal to 1,000 use a consistent thousands separator:

```text
10,691
349,675
356,647
89,161
```

The malformed format `3,566,47` is prohibited.

### 7.4 Outcome semantics

| Outcome | Label | Semantic color |
|---|---|---|
| `SUCCESS` | `Success` | success green |
| `SUCCESS_WITH_WARNINGS` | `With warnings` | warning amber |
| `CANCELLED` | `Cancelled` | neutral gray |
| `FAILED` | `Failed` | error red |

Color supplements the text label; it never replaces it.

Last Run and History must use the same outcome vocabulary.

---

## 8. Responsive Layout Contract

Responsive behavior is mandatory. A screenshot-perfect layout that breaks at 920×620 does not satisfy the contract.

### 8.1 Large breakpoint: 1350 px and wider

- standard page margins;
- Source field and actions remain on one row;
- four Last Run columns appear in one row;
- full subtitle and helper text remain visible;
- sidebar uses standard width.

### 8.2 Medium breakpoint: 1050–1349 px

- page margins and gaps reduce moderately;
- Source actions may move to a secondary row when needed;
- Last Run becomes a 2×2 group grid;
- full navigation labels remain visible;
- no horizontal scrollbar appears.

### 8.3 Compact breakpoint: 920–1049 px

- Source actions move below the Source field;
- Last Run uses a 2×2 grid or compact vertical group arrangement;
- page margins and card padding reduce;
- subtitle or non-critical helper text may be hidden;
- all modes, Source controls, Max chars, and Collect & Copy remain reachable;
- no overlap, clipping, or horizontal scrollbar is allowed.

### 8.4 Implementation constraints

- reuse the same widget instances across breakpoints;
- do not duplicate signal connections;
- do not rebuild the complete page on every resize event;
- switch layouts only when crossing a breakpoint;
- preserve tab order and accessible names;
- avoid visible resize jitter.

### 8.5 Validation matrix

The final implementation must be checked at:

```text
920 × 620
1920 × 1080 at 100%
1920 × 1080 at 125%
1920 × 1080 at 150%
2560 × 1440
maximized window
```

---

## 9. Dialog Contract

### 9.1 Paste File Paths

The dialog retains:

- title and concise explanation;
- visible project-root selector;
- Browse action;
- editable pasted path list;
- live validation summary;
- Cancel;
- `Add N Files` primary action.

Visual requirements:

- use the same card, input, typography, and button system as the main window;
- paths remain monospace;
- valid, warning, and error states are distinguishable by text and semantic accent;
- disabled primary action remains clearly disabled;
- long paths do not force horizontal window growth.

Behavioral guarantees remain unchanged:

- pasted text is never executed;
- relative paths require a visible valid root;
- traversal outside the root is rejected;
- duplicates and external paths remain explicitly reported.

### 9.2 Selected Files Review

The dialog retains:

- file count;
- project root or `Mixed locations`;
- ordered path list;
- multiple selection;
- `Delete` shortcut;
- Remove Selected;
- Clear All;
- Cancel;
- Apply Changes.

Visual requirements:

- selected rows use a calm dark accent, not a full bright-gold fill;
- absolute paths remain available in tooltips;
- long paths are elided safely;
- Apply Changes activates only after a real change;
- the dialog remains usable at 700×480 and above.

Transactional behavior is non-negotiable: Cancel must leave the original selection unchanged.

---

## 10. Accessibility and Keyboard Contract

- every interactive control has a meaningful accessible name;
- keyboard focus is visible;
- tab order follows visual order;
- radio controls support standard arrow-key behavior;
- Source review supports keyboard activation;
- `Delete` removes selected review rows;
- `Esc` keeps its existing application hide-to-tray behavior outside modal dialogs;
- dialog Escape cancels the dialog rather than mutating state;
- status and outcome are always expressed in text, not only color;
- controls remain usable at Windows 150% scaling.

---

## 11. Behavioral Invariants

The redesign must preserve all of the following:

- source payloads remain verbatim;
- Compact mode touches only XCC-generated structural text;
- staged and unstaged Git diffs remain separate;
- character-budget behavior remains structure-aware;
- safety detection and optional confirmation remain unchanged;
- only one collection job can run;
- cancellation never copies partial output;
- runtime history remains in-memory and metadata-only;
- native `Ctrl+Alt+X`, tray behavior, autostart, and single-instance behavior remain intact;
- Paste Paths and Selected Files Review retain M11–M13 semantics.

A visual change that weakens any invariant is a regression.

---

## 12. Implementation Boundaries

The redesign should be implemented through reusable UI modules rather than adding more unrelated styling to the monolithic GUI file.

Planned ownership:

```text
src/xcc/ui_theme.py       color, spacing, typography, and shared QSS tokens
src/xcc/ui_components.py  reusable presentational widgets and formatting helpers
src/xcc/gui.py            page composition, signals, and application state integration
```

Domain modules such as `pipeline.py`, `formatter.py`, `collector.py`, and `git_utils.py` must not be changed solely to support visual styling.

---

## 13. Acceptance Checklist

The UI reference contract is satisfied only when:

- [ ] the application shell matches the defined hierarchy;
- [ ] header and footer have distinct semantic roles;
- [ ] Selected Files uses `Select Files` and correct Source summaries;
- [ ] Full Folder and Project Tree use `Select Folder`;
- [ ] Git Changed Files uses `Select Repository`;
- [ ] Paste Paths appears only in Selected Files;
- [ ] Source review and clear affordances remain available;
- [ ] Compact mode wording preserves the source-fidelity guarantee;
- [ ] Last Run uses four semantic groups and consistent number formatting;
- [ ] outcome colors are semantic and accompanied by text;
- [ ] primary action and active sidebar emphasis remain restrained;
- [ ] dialogs match the final visual system;
- [ ] keyboard and accessibility behavior passes;
- [ ] 920×620 has no clipping or horizontal scrolling;
- [ ] 100%, 125%, and 150% Windows scaling passes;
- [ ] all existing automated tests pass;
- [ ] packaged executable matches source behavior and visual structure.

---

## 14. Approval and Change Control

This contract is frozen for the v1.3.0 implementation cycle.

Changes are allowed only when:

1. a requirement is technically impossible in supported PySide6/Windows constraints;
2. a real screenshot exposes a usability or accessibility defect;
3. an existing product invariant would otherwise be weakened;
4. the change is documented in this file and reflected in `docs/roadmap.md` before release freeze.

The final screenshot is evidence of implementation quality, but this document remains the source of truth for semantics and responsive behavior.
