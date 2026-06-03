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

Status: DONE

* [x] config.json
* [x] save default mode
* [x] save max chars
* [x] save compact mode
* [x] save last source
* [x] load settings on GUI startup
* [x] validate config values
* [x] fallback to defaults on invalid config
* [x] manual persistence test
* [x] test suite pass
* [x] files mode restore guarded
* [x] startup save guard


## v0.7 Tray Mode

Status: DONE

* [x] tray icon
* [x] show/hide GUI
* [x] quit from tray
* [x] background GUI behavior
* [x] safe shutdown from tray
* [x] tray menu polish
* [x] first minimize notification
* [x] double click restore
* [x] maximized startup


## v0.8 Settings Expansion

Status: DONE

* [x] autostart with Windows
* [x] start minimized to tray
* [x] close to tray option
* [x] start maximized option
* [x] tray behavior settings
* [x] settings controls UI
* [x] persist new settings
* [x] validate new settings
* [x] manual settings test
* [x] test suite pass


## v0.9 Optimization

Status: DONE

* [x] code cleanup
* [x] remove unused imports
* [x] remove duplicate model definitions
* [x] remove unused placeholder helpers
* [x] normalize GUI helper naming
* [x] reduce duplicated settings layout code
* [x] improve settings page spacing
* [x] optimize startup flow
* [x] verify tray startup edge cases
* [x] verify start minimized behavior
* [x] verify close-to-tray behavior
* [x] verify invalid config recovery
* [x] improve error messages
* [x] update README for GUI usage
* [x] update roadmap before release
* [x] full manual app test
* [x] full pytest pass
* [x] measure idle CPU/RAM usage
* [x] verify no background scanning in tray mode
* [x] verify collect-only workload behavior


## v0.9.5 Settings/About Polish

Status: DONE

* [x] redesign Settings as control panel
* [x] separate behavior settings from read-only system info
* [x] replace checkbox cards with setting rows
* [x] simplify Settings visual hierarchy
* [x] redesign About page
* [x] add app identity block to About
* [x] add product badges to About
* [x] add config/startup path info to About
* [x] manual visual review
* [x] tune yellow accent to muted amber
* [x] reduce bright yellow usage in secondary UI
* [x] soften checkbox and radio checked color
* [x] soften card and row borders
* [x] manual color review


## v0.9.6 Integrated Restore Hotkey

Status: DONE

* [x] add GUI global hotkey listener
* [x] restore window with Ctrl+Alt+X
* [x] route hotkey callback through Qt signal
* [x] cleanup hotkey on app exit
* [x] keep legacy hotkey.py as dev-only mode
* [x] update README for integrated restore hotkey
* [x] manual hotkey test
* [x] test suite pass


## v1.0 Windows Release

Status: IN PROGRESS

* [x] define GUI as primary release entry point
* [x] exclude legacy scripts from primary release flow
* [x] Esc hides window to tray
* [x] add PyInstaller dependency
* [x] PyInstaller build
* [x] app icon
* [x] tray icon in packaged build
* [x] single-instance protection
* [x] second launch restores existing window
* [x] verify single-instance protection in exe
* [x] fix PyInstaller resource paths
* [x] packaged exe autostart target
* [x] verify autostart shortcut in exe mode
* [x] release build script
* [x] repeatable clean build
* [x] clean gitignore for build artifacts
* [x] README release update
* [ ] release folder
* [ ] basic install instructions
* [ ] manual release test
* [ ] release package


## v1.1 Post-Release Polish

Status: PLANNED

* [ ] add hotkey controls to Settings
* [ ] allow changing restore hotkey from GUI
* [ ] improve About page with release links
* [ ] optionally integrate collect action into hotkey workflow
* [ ] installer
* [ ] update system


## Future Improvements

Status: BACKLOG

* [ ] signed installer
* [ ] automatic update channel
* [ ] portable mode toggle
* [ ] export runtime history
* [ ] advanced include/exclude rules
