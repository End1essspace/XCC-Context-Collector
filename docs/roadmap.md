# XCC Roadmap

## v0.1 Core MVP

**Status: DONE**

- [x] project structure
- [x] data models
- [x] file collector
- [x] formatter
- [x] clipboard support
- [x] file picker
- [x] folder picker
- [x] recursive project scanner
- [x] basic config
- [x] root launcher
- [x] test suite stable
- [x] manual real-project test


## v0.2 Context Optimization

**Status: DONE**

- [x] compact mode
- [x] project tree in output
- [x] token/character budget
- [x] skip large files
- [x] output metadata
- [x] summarize oversized files
- [x] truncation status through model result
- [x] cache directories excluded


## v0.3 Git Context Mode

**Status: DONE**

- [x] detect git repository
- [x] collect modified files
- [x] collect untracked files
- [x] filter git files by allowed extensions
- [x] filter git files by excluded directories
- [x] include git diff
- [x] add mode metadata
- [x] test git diff extraction
- [x] git tests


## v0.4 Hotkey Mode

**Status: DONE**

- [x] global hotkey
- [x] safe hotkey selected: Ctrl+Alt+X
- [x] no conflict with XClip
- [x] background listener
- [x] background process
- [x] prevent concurrent runs
- [x] graceful Ctrl+C shutdown
- [x] hotkey launcher


## v0.5 PySide6 GUI

**Status: DONE**

- [x] PySide6 dependency
- [x] gui.py launcher
- [x] main window
- [x] black/yellow theme
- [x] header
- [x] sidebar navigation
- [x] Collect page
- [x] Settings placeholder
- [x] History placeholder
- [x] About placeholder
- [x] Select Source works
- [x] Full Folder mode works
- [x] Selected Files mode works
- [x] Git Changed Files mode works
- [x] Collect & Copy works
- [x] clipboard copy works
- [x] metrics update after run
- [x] success popup removed
- [x] inline success feedback
- [x] max chars validator
- [x] Setup layout alignment
- [x] Options row composition
- [x] dark strip behind Mode removed
- [x] Sidebar hover polish
- [x] Last Run visual hierarchy
- [x] History page runtime entries
- [x] History empty state
- [x] History newest-first ordering
- [x] History scroll area
- [x] History row height polish
- [x] Settings page basic controls
- [x] Settings tile layout
- [x] Settings runtime values refresh
- [x] Settings final polish
- [x] manual GUI test
- [x] test suite pass


## v0.6 Settings Persistence

**Status: DONE**

- [x] config.json
- [x] save default mode
- [x] save max chars
- [x] save compact mode
- [x] save last source
- [x] load settings on GUI startup
- [x] validate config values
- [x] fallback to defaults on invalid config
- [x] manual persistence test
- [x] test suite pass
- [x] files mode restore guarded
- [x] startup save guard


## v0.7 Tray Mode

**Status: DONE**

- [x] tray icon
- [x] show/hide GUI
- [x] quit from tray
- [x] background GUI behavior
- [x] safe shutdown from tray
- [x] tray menu polish
- [x] first minimize notification
- [x] double click restore
- [x] maximized startup


## v0.8 Settings Expansion

**Status: DONE**

- [x] autostart with Windows
- [x] start minimized to tray
- [x] close to tray option
- [x] start maximized option
- [x] tray behavior settings
- [x] settings controls UI
- [x] persist new settings
- [x] validate new settings
- [x] manual settings test
- [x] test suite pass


## v0.9 Optimization

**Status: DONE**

- [x] code cleanup
- [x] remove unused imports
- [x] remove duplicate model definitions
- [x] remove unused placeholder helpers
- [x] normalize GUI helper naming
- [x] reduce duplicated settings layout code
- [x] improve settings page spacing
- [x] optimize startup flow
- [x] verify tray startup edge cases
- [x] verify start minimized behavior
- [x] verify close-to-tray behavior
- [x] verify invalid config recovery
- [x] improve error messages
- [x] update README for GUI usage
- [x] update roadmap before release
- [x] full manual app test
- [x] full pytest pass
- [x] measure idle CPU/RAM usage
- [x] verify no background scanning in tray mode
- [x] verify collect-only workload behavior


## v0.9.5 Settings/About Polish

**Status: DONE**

- [x] redesign Settings as control panel
- [x] separate behavior settings from read-only system info
- [x] replace checkbox cards with setting rows
- [x] simplify Settings visual hierarchy
- [x] redesign About page
- [x] add app identity block to About
- [x] add product badges to About
- [x] add config/startup path info to About
- [x] manual visual review
- [x] tune yellow accent to muted amber
- [x] reduce bright yellow usage in secondary UI
- [x] soften checkbox and radio checked color
- [x] soften card and row borders
- [x] manual color review


## v0.9.6 Integrated Restore Hotkey

**Status: DONE**

- [x] add GUI global hotkey listener
- [x] restore window with Ctrl+Alt+X
- [x] route hotkey callback through Qt signal
- [x] cleanup hotkey on app exit
- [x] keep legacy hotkey.py as dev-only mode
- [x] update README for integrated restore hotkey
- [x] manual hotkey test
- [x] test suite pass


## v1.0 Windows Release

**Status: DONE**

- [x] define GUI as primary release entry point
- [x] exclude legacy scripts from primary release flow
- [x] Esc hides window to tray
- [x] PyInstaller dependency
- [x] PyInstaller build
- [x] release build script
- [x] repeatable clean build
- [x] app icon
- [x] tray icon
- [x] PyInstaller resource paths
- [x] packaged exe resource loading
- [x] single-instance protection
- [x] second launch restores existing window
- [x] verify single-instance protection in exe
- [x] packaged exe autostart target
- [x] verify autostart shortcut in exe mode
- [x] clean gitignore for build artifacts
- [x] release folder
- [x] README release update
- [x] basic install instructions
- [x] manual release test
- [x] release zip package
- [x] verify ZIP contains exe and _internal folder
- [x] final v1.0 package smoke test


## v1.0.1 Hotkey Reliability Patch

**Status: DONE**

- [x] replace GUI `keyboard` listener with native Windows `RegisterHotKey` restore hotkey
- [x] route `WM_HOTKEY` through Qt native event filter
- [x] keep legacy `hotkey.py` as development-only workflow
- [x] show hotkey unavailable status in UI/tray/settings
- [x] acquire single-instance lock before creating the main window
- [x] register restore hotkey only after single-instance server is ready
- [x] add native hotkey parser tests


## v1.1 Source Coverage Expansion

**Status: DONE**

- [x] expand supported source file extensions
- [x] add filename-based allowlist
- [x] support Dockerfile, Makefile, package/config files
- [x] avoid sensitive defaults like .env, .pem, .key
- [x] update scanner and collector filtering
- [x] update tests
- [x] update README supported file types


## v1.1.1 Context Filtering Patch

**Status: DONE**

- [x] centralize context file allowlist logic in `config.py`
- [x] generate GUI file picker filters from supported context file definitions
- [x] update Selected Files mode to use the expanded extension list
- [x] update legacy picker file filters
- [x] apply filename-based allowlist support to Git Changed Files mode
- [x] remove duplicated file allowlist checks from scanner and collector
- [x] add tests for allowed extensions, allowed filenames, and sensitive file exclusion
- [x] add tests for GUI/Tk file filter generation
- [x] add tests for Dockerfile support in scanner, collector, and Git mode
- [x] verify expanded source coverage works consistently across files, folder, and git modes


## v1.1.2 Project Tree Mode Patch

**Status: DONE**

- [x] add Project Tree collection mode to GUI
- [x] persist Project Tree as a valid settings mode
- [x] add tree-only formatter output
- [x] build full project directory tree without reading file contents
- [x] include both files and directories in Project Tree mode
- [x] exclude cache, build, dependency, IDE, and VCS folders from Project Tree mode
- [x] remove Project Tree from Selected Files output
- [x] keep Project Tree in Full Folder and Git Changed Files modes
- [x] add tests for directory tree builder
- [x] add tests for tree-only formatter output
- [x] add settings validation test for Project Tree mode
- [x] verify Project Tree output does not include file content sections

## v1.2.0 Context Integrity & Reliability

**Status: RELEASE CANDIDATE PREPARED — FINAL VALIDATION PENDING**

### Release Goal

Make XCC safe and reliable for everyday use across real-world repositories.

The release must guarantee that:

- source content is not modified during formatting;
- Git mode correctly represents staged and unstaged changes;
- selected files retain distinguishable project paths;
- character limits do not silently cut arbitrary source code;
- large collections do not freeze the main window;
- potentially sensitive context is surfaced before copying;
- public builds are validated through repeatable CI and release checks.

---

### M1 — Source Content Fidelity

**Status: DONE**

**Priority: CRITICAL**

- [x] stop applying global compact processing to source file contents
- [x] preserve repeated empty lines inside collected files
- [x] preserve trailing spaces inside collected files
- [x] preserve final blank lines where they are part of file content
- [x] remove destructive `rstrip()` processing from file content formatting
- [x] apply compact mode only to XCC-generated metadata and separators
- [x] separate structural output formatting from source content rendering
- [x] guarantee that compact and non-compact modes contain identical source content
- [x] add regression tests for multiline strings
- [x] add regression tests for Markdown whitespace
- [x] add regression tests for YAML block content
- [x] add regression tests for trailing spaces
- [x] add regression tests for repeated blank lines
- [x] add source-content fidelity test using exact string comparison

#### Acceptance Criteria

```text
input FileContent.content == content extracted from final XCC file section
```

The only permitted differences are XCC section delimiters surrounding the file.

Compact mode must never rewrite collected file content.

Completed in the first v1.2.0 implementation batch.

---

### M2 — Git Context Correctness

**Status: DONE**

**Priority: CRITICAL**

- [x] replace line-based `git status --porcelain` parsing with null-delimited parsing
- [x] use `git status --porcelain=v1 -z`
- [x] introduce a typed Git change model
- [x] represent working-tree and index status separately
- [x] support unstaged modified files
- [x] support staged modified files
- [x] support staged added files
- [x] support untracked files
- [x] support renamed files
- [x] support copied files
- [x] support deleted files
- [x] handle paths containing spaces
- [x] handle quoted paths
- [x] handle non-ASCII paths
- [x] remove duplicate paths from combined Git results
- [x] collect unstaged diff
- [x] collect staged diff with `git diff --cached`
- [x] combine staged and unstaged diff into clearly labelled sections
- [x] represent untracked files through full file content
- [x] represent deleted files through status and diff without attempting file reads
- [x] include old and new paths for renamed files
- [x] expose Git command failures instead of silently returning an empty result
- [x] distinguish a clean repository from a failed Git command
- [x] add tests for all supported Git statuses
- [x] add tests for staged-only changes
- [x] add tests for mixed staged and unstaged changes
- [x] add tests for rename and delete scenarios
- [x] add tests for paths containing spaces and Unicode

#### Proposed Output Structure

```text
# Git Changes

- [ M] src/main.py
- [A ] tests/test_new_feature.py
- [R ] src/old_name.py -> src/new_name.py
- [D ] docs/obsolete.md
- [??] notes.md

# Git Diff — Staged

...

## Git Diff — Unstaged

...
```

#### Acceptance Criteria

A repository containing modified, staged, renamed, deleted, and untracked files must produce complete and deterministic context without silently losing any supported change.

Completed in the fourth v1.2.0 implementation batch.

---

### M3 — Stable File Identity and Relative Paths

**Status: DONE**

**Priority: HIGH**

- [x] calculate a common source root for Selected Files mode
- [x] preserve relative directory paths where possible
- [x] prevent different files from receiving the same display path
- [x] support selected files from different directories
- [x] support selected files from different drives
- [x] add a safe fallback when no common project root exists
- [x] avoid exposing unnecessary absolute user-profile paths
- [x] add stable path normalization for Windows
- [x] use forward slashes in generated AI context
- [x] add tests for duplicate filenames
- [x] add tests for nested selected files
- [x] add tests for cross-root selections
- [x] add tests for non-ASCII directory names

#### Example

Instead of:

```text
===== file: config.py =====
===== file: config.py =====
```

XCC must produce distinguishable paths:

```text
===== file: backend/config.py =====
===== file: frontend/config.py =====
```

Completed in the second v1.2.0 implementation batch.

---

### M4 — Structure-Aware Character Budget

**Status: DONE**

**Priority: CRITICAL**

- [x] replace arbitrary whole-text slicing with section-aware budgeting
- [x] calculate budget before adding each output section
- [x] reserve space for truncation metadata
- [x] keep XCC header complete whenever the configured budget can hold mandatory metadata
- [x] emit a bounded budget-too-small notice for extremely small limits
- [x] keep file section headers complete
- [x] avoid cutting source files in the middle by default
- [x] avoid cutting Git diff lines in the middle
- [x] add complete files until the remaining budget is insufficient
- [x] keep partial-file inclusion disabled by default and report `Partial files: 0`
- [x] list files omitted because of the output budget
- [x] distinguish oversized-file summaries from budget omissions
- [x] track included file count
- [x] track omitted file count
- [x] track partially included file count
- [x] track summarized file count
- [x] expose budget usage in result statistics
- [x] preserve deterministic file ordering
- [x] add tests for very small budgets
- [x] add tests for exact-boundary budgets
- [x] add tests for file omission order
- [x] add tests proving that output never exceeds the configured limit

#### Proposed Budget Summary

```text
## XCC Budget Summary

Limit: 120000
Used: 118742
Included files: 14
Omitted files: 6
Partial files: 0

Omitted:
- tests/large_fixture.py
- docs/reference.md
- src/generated/schema.py
```

#### Acceptance Criteria

The final output must never exceed the configured limit and must never silently end in the middle of an unmarked source file.

---

Completed in the third v1.2.0 implementation batch.

---

### M5 — Context Safety Guardrails

**Status: DONE**

**Priority: HIGH**

- [x] add `.xccignore` support
- [x] define documented `.xccignore` pattern semantics
- [x] optionally respect `.gitignore` in Full Folder mode
- [x] allow built-in exclusions and project exclusions to work together
- [x] add suspicious filename detection
- [x] warn about credential and secret configuration files
- [x] add lightweight secret-pattern warnings
- [x] detect common private key headers
- [x] detect likely API tokens and access keys
- [x] detect likely password and connection-string assignments
- [x] never write detected secret values to logs or history
- [x] report only filename, line number, and warning category
- [x] show a warning summary before clipboard copy when findings exist
- [x] allow the user to cancel collection after a warning
- [x] clearly state that detection is heuristic and not a security guarantee
- [x] add tests for obvious secret patterns
- [x] add false-positive regression tests
- [x] update README security wording

#### Scope Boundary

v1.2.0 should provide **warnings**, not automatic redaction.

Silent redaction could corrupt code and produce misleading context. Automatic redaction may be considered later as an explicit opt-in mode.

Completed in the fifth v1.2.0 implementation batch. Safety scanning covers current file payloads, staged and unstaged Git diffs, and sensitive filenames in Project Tree mode. Warning output never includes detected secret values.

---

### M6 — Responsive Collection Pipeline

**Status: RELEASE CANDIDATE — FINAL WINDOWS VALIDATION PENDING**

**Priority: HIGH**

- [x] move scanning and collection out of the Qt main thread
- [x] introduce a dedicated collection worker
- [x] keep clipboard interaction on the GUI thread
- [x] expose worker progress through Qt signals
- [x] show current collection phase
- [x] show scanned and processed file counts
- [x] disable conflicting controls while collection is running
- [x] prevent multiple simultaneous collection jobs
- [x] add a Cancel action
- [x] implement cooperative cancellation between files
- [x] restore UI state after success
- [x] restore UI state after failure
- [x] restore UI state after cancellation
- [x] prevent closing or mode switching from leaving an orphan worker
- [x] preserve single-instance and tray behavior during collection
- [x] add worker and pipeline unit tests
- [x] add automated cancellation and progress regression tests
- [ ] complete final Windows manual large-project responsiveness validation

#### Collection Phases

```text
Preparing
Scanning
Reading files
Inspecting Git changes
Inspecting context
Formatting
Applying budget
Copying
Completed
```

#### Acceptance Criteria

During collection of a large repository:

- the window remains responsive;
- the user can move or minimize it;
- the operation can be cancelled;
- no second collection can start concurrently;
- partial results are not copied after cancellation.

Implementation completed in the sixth v1.2.0 batch. The milestone remains open only for the final packaged Windows manual responsiveness check.

---


### M7 — Result Model and Runtime History Upgrade

**Status: DONE**

**Priority: MEDIUM**

- [x] expand `CollectionStats`
- [x] add included file count
- [x] add omitted file count
- [x] add summarized file count
- [x] add partial file count
- [x] add warning count
- [x] add collection duration
- [x] add collection outcome enum
- [x] distinguish errors from warnings
- [x] distinguish cancellation from failure
- [x] update Last Run metrics
- [x] update runtime history entries
- [x] add clear health status for completed-with-warnings
- [x] keep history free of file contents and detected secret values
- [x] add tests for result statistics

#### Suggested Outcomes

```text
SUCCESS
SUCCESS_WITH_WARNINGS
CANCELLED
FAILED
```


Completed in the seventh v1.2.0 implementation batch. `CollectionOutcome` now distinguishes successful, warning-bearing, cancelled, and failed runs. Last Run and Runtime History use typed metadata-only records with duration, coverage, warning, and error statistics. Cancellation after a safety warning is recorded as `CANCELLED`, while fatal worker or clipboard failures are recorded as `FAILED`.

---

### M8 — Dependency and Project Structure Cleanup

**Status: DONE**

**Priority: MEDIUM**

- [x] add `pyproject.toml`
- [x] define project metadata in one canonical location
- [x] define supported Python version
- [x] separate runtime dependencies from development dependencies
- [x] separate build dependencies from runtime dependencies
- [x] make legacy `keyboard` dependency optional
- [x] pin compatible dependency ranges
- [x] document reproducible source setup
- [x] remove version duplication where possible
- [x] ensure packaged build reads the canonical version
- [x] evaluate removal of legacy Tkinter entry points
- [x] clearly mark retained legacy modules as unsupported development tools
- [x] update architecture documentation
- [x] verify clean installation in a new virtual environment

#### Dependency Groups

```text
runtime:
- PySide6 >=6.8,<6.12
- pyperclip >=1.9,<2

dev:
- pytest >=8.3,<10
- pytest-cov >=6,<8

build:
- pyinstaller >=6.11,<7

legacy:
- keyboard ==0.13.5
```

Implementation completed in the eighth v1.2.0 batch. The repository now uses a standard installable `src` layout with import package `xcc`, canonical PEP 621 metadata in `pyproject.toml`, dynamic version metadata sourced from `xcc.__version__`, separated optional dependency groups, and version-aware PyInstaller resources. Legacy Tkinter and `keyboard` workflows are retained only as unsupported development compatibility tools. Clean-install validation covers a fresh Windows CPython 3.13 virtual environment, editable package installation, canonical version verification, the full regression suite, GUI import checks, and confirmation that the optional legacy `keyboard` dependency is absent from the normal runtime install.

---

### M9 — GitHub Repository Maturity

**Status: DONE**

**Priority: HIGH**

- [x] add Windows GitHub Actions test workflow
- [x] run tests on supported Python versions
- [x] add source compilation check
- [x] add packaged build smoke check
- [x] cache Python dependencies safely
- [x] add `CHANGELOG.md`
- [x] add `CONTRIBUTING.md`
- [x] add `SECURITY.md`
- [x] verify repository contains a root `LICENSE`
- [x] add issue templates
- [x] add pull request template
- [x] document bug-report diagnostics
- [x] add CI status badge to README
- [x] add release link to README
- [x] add screenshots to README
- [x] document portable ZIP usage
- [x] generate SHA-256 checksum for release archives
- [x] verify release archive contents automatically
- [x] add release checklist
- [x] ensure version consistency across code, README, and release notes

#### CI Minimum Gate

```text
pytest
compileall
clean PyInstaller build
packaged executable startup smoke test
release archive structure validation
```

Implementation completed in the ninth v1.2.0 batch. The repository now has a Windows-only Python 3.13 CI gate, safe pip caching through `setup-python`, deterministic source compilation and tests, canonical version checks, clean PyInstaller packaging, offscreen packaged startup smoke validation, portable ZIP generation, SHA-256 checksums, and archive-structure validation. Governance and support documentation now includes changelog, contribution, security, diagnostics, issue/PR templates, portable usage, release checklist, release links, CI badge, and current UI previews.

The M9 local compile, regression, build, packaged-smoke, portable-archive, and checksum gates passed, and the committed Windows CI workflow completed successfully on the GitHub-hosted `windows-latest` runner. Later v1.2.0 work extended the same repository gate with packaged artwork checks, optional Safety confirmation coverage, workspace cleanup, and final documentation consistency.

---

### M10 — v1.2.0 Validation and Release Gate

**Status: DONE — RELEASED**

- [x] complete automated release-candidate gate
- [x] canonical version and package validation
- [x] source fidelity, Git, budget, ignore, safety, worker, and history regression coverage
- [x] clean-install and packaged startup validation
- [x] portable ZIP and SHA-256 validation
- [x] Windows release evidence and publication workflow
- [x] annotated v1.2.0 release baseline

v1.2.0 is the completed Context Integrity & Reliability baseline used by all later releases.

---

## v1.3.0 Selected Files Workflow

**Status: IMPLEMENTED — M15 RELEASE VALIDATION PENDING**

### Release goal

Reduce the repeated AI coding workflow from manual file-by-file selection to one copied path list, one validated import, one review step, and one normal Collect & Copy run.

### M11 — Paste Paths Core

**Status: DONE**

- [x] add ordered path-list parser
- [x] support plain lines, Markdown bullets, numbering, quotes, backticks, and fenced blocks
- [x] support relative and absolute Windows paths
- [x] add explicit project-root resolution
- [x] validate existence, file type, directory state, and root traversal
- [x] preserve order and deduplicate canonically
- [x] merge pasted paths with manual Selected Files state
- [x] add Paste Paths button and guarded Ctrl+V workflow
- [x] add parser and importer tests

### M12 — Selected Files Review

**Status: DONE**

- [x] make Source summary open review
- [x] display relative paths and effective project root
- [x] support mixed locations
- [x] support multi-select removal and Clear All
- [x] keep Cancel transactional
- [x] apply reviewed changes explicitly
- [x] preserve remaining order
- [x] add review-model tests

### M13 — Workflow Regression and UX Polish

**Status: DONE**

- [x] recover from stale or deleted roots
- [x] keep absolute external files importable
- [x] distinguish separate repositories from one common project
- [x] prefer repository roots in monorepository layouts
- [x] expose external and issue counts
- [x] keep duplicate-only imports non-modal
- [x] disable inactive clear/apply controls
- [x] add Delete shortcut and accessibility metadata
- [x] add end-to-end import-review-collection regression coverage

### M14 — Documentation and Version Integration

**Status: DONE**

- [x] bump canonical version to 1.3.0
- [x] update bilingual README
- [x] update changelog and comparison links
- [x] document parser/importer/review architecture and security boundary
- [x] create v1.3.0 release notes
- [x] create M15 validation procedure
- [x] update portable, security, issue-template, and release-checklist version references
- [x] update release-candidate default version
- [x] update repository version/document regression tests
- [x] run the complete local test suite after applying the M14 archive
- [x] manually inspect the updated About/version labels
- [x] commit and push M14

### M15 — v1.3.0 Validation and Release

**Status: IN PROGRESS — RELEASE GATE HARDENING**

- [x] require an explicit Selected Files regression sub-gate in the automated report
- [x] require explicit v1.3.0 Paste Paths and review gates in Windows evidence
- [x] bind final readiness to the automated report filename, version, pass state, and archive SHA-256
- [ ] run complete compileall and pytest gates
- [ ] validate all four source collection modes
- [ ] validate Paste Paths and Selected Files Review in the packaged executable
- [ ] build the clean PyInstaller package
- [ ] validate portable ZIP and SHA-256
- [ ] complete Windows 10/11 evidence for the same archive hash
- [ ] run final readiness validation
- [ ] create annotated v1.3.0 tag
- [ ] create and review GitHub draft release
- [ ] publish and verify downloaded assets
- [ ] mark v1.3.0 released in the roadmap

See `docs/M15_VALIDATION.md`.

---

## v1.4.0 Windows Workflow & Distribution

**Status: PLANNED**

- [ ] editable restore hotkey with conflict validation
- [ ] optional Collect & Copy hotkey
- [ ] repository and release links in About
- [ ] installer and clean uninstall
- [ ] explicit settings preservation/removal behavior
- [ ] portable mode
- [ ] update-availability check
- [ ] persistent runtime history and export
- [ ] installer and portable validation gates

An update-availability check is preferred to a full automatic self-updater at this stage.

---

## v1.5.0 Advanced Context Rules

**Status: PLANNED**

- [ ] per-project presets
- [ ] richer include/exclude profiles
- [ ] preview editor
- [ ] optional partial-file strategies
- [ ] advanced tree and diff controls
- [ ] configurable safety categories

---

## Immediate Next Step

Apply and validate the M15 release-gate hardening patch, commit and push it, then run the canonical automated gate against that exact commit. No additional feature work should enter v1.3.0 unless it fixes a release-blocking defect.
