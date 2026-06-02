# XCC Roadmap

## v0.1 Core MVP

Status: DONE

* [x] project structure
* [x] data models
* [x] file collector
* [x] formatter
* [x] clipboard support
* [x] file picker
* [x] folder picker
* [x] recursive project scanner
* [x] basic config
* [x] root launcher
* [x] test suite stable
* [x] manual real-project test

## v0.2 Context Optimization

Status: DONE

* [x] compact mode
* [x] project tree in output
* [x] token/character budget
* [x] skip large files
* [x] output metadata
* [x] summarize oversized files
* [x] truncation status through model result
* [x] cache directories excluded

## v0.3 Git Context Mode

Status: DONE

* [x] detect git repository
* [x] collect modified files
* [x] collect untracked files
* [x] filter git files by allowed extensions
* [x] filter git files by excluded directories
* [x] include git diff
* [x] add mode metadata
* [x] test git diff extraction
* [x] git tests

## v0.4 Hotkey Mode

Status: DONE

* [x] global hotkey
* [x] safe hotkey selected: Ctrl+Alt+X
* [x] no conflict with XClip
* [x] background listener
* [x] background process
* [x] prevent concurrent runs
* [x] graceful Ctrl+C shutdown
* [x] hotkey launcher

## v0.5 PySide6 GUI

Status: DONE

* [x] PySide6 dependency
* [x] gui.py launcher
* [x] main window
* [x] black/yellow theme
* [x] header
* [x] sidebar navigation
* [x] Collect page
* [x] Settings placeholder
* [x] History placeholder
* [x] About placeholder
* [x] Select Source works
* [x] Full Folder mode works
* [x] Selected Files mode works
* [x] Git Changed Files mode works
* [x] Collect & Copy works
* [x] clipboard copy works
* [x] metrics update after run
* [x] success popup removed
* [x] inline success feedback
* [x] max chars validator
* [x] Setup layout alignment
* [x] Options row composition
* [x] dark strip behind Mode removed
* [x] Sidebar hover polish
* [x] Last Run visual hierarchy
* [x] History page runtime entries
* [x] History empty state
* [x] History newest-first ordering
* [x] History scroll area
* [x] History row height polish
* [x] Settings page basic controls
* [x] Settings tile layout
* [x] Settings runtime values refresh
* [x] Settings final polish
* [x] manual GUI test
* [x] test suite pass

## v0.6 Settings Persistence

Status: in progress

* [x] config.json
* [ ] save default mode
* [ ] save max chars
* [ ] save compact mode
* [ ] save last source
* [ ] load settings on GUI startup
* [x] validate config values
* [x] fallback to defaults on invalid config

## v0.7 Tray Mode

Status: PLANNED

* [ ] tray icon
* [ ] show/hide GUI
* [ ] quit from tray
* [ ] hotkey listener integration
* [ ] background GUI behavior
* [ ] safe shutdown from tray

## v1.0 Windows Release

Status: PLANNED

* [ ] PyInstaller build
* [ ] app icon
* [ ] release folder
* [ ] README update
* [ ] basic install instructions
* [ ] manual release test
* [ ] release package
