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

Status: DONE

* [x] define GUI as primary release entry point
* [x] exclude legacy scripts from primary release flow
* [x] Esc hides window to tray
* [x] PyInstaller dependency
* [x] PyInstaller build
* [x] release build script
* [x] repeatable clean build
* [x] app icon
* [x] tray icon
* [x] PyInstaller resource paths
* [x] packaged exe resource loading
* [x] single-instance protection
* [x] second launch restores existing window
* [x] verify single-instance protection in exe
* [x] packaged exe autostart target
* [x] verify autostart shortcut in exe mode
* [x] clean gitignore for build artifacts
* [x] release folder
* [x] README release update
* [x] basic install instructions
* [x] manual release test
* [x] release zip package
* [x] verify ZIP contains exe and _internal folder
* [x] final v1.0 package smoke test


## v1.0.1 Hotkey Reliability Patch

Status: DONE

* [x] replace GUI `keyboard` listener with native Windows `RegisterHotKey` restore hotkey
* [x] route `WM_HOTKEY` through Qt native event filter
* [x] keep legacy `hotkey.py` as development-only workflow
* [x] show hotkey unavailable status in UI/tray/settings
* [x] acquire single-instance lock before creating the main window
* [x] register restore hotkey only after single-instance server is ready
* [x] add native hotkey parser tests


## v1.1 Source Coverage Expansion

Status: DONE

* [x] expand supported source file extensions
* [x] add filename-based allowlist
* [x] support Dockerfile, Makefile, package/config files
* [x] avoid sensitive defaults like .env, .pem, .key
* [x] update scanner and collector filtering
* [x] update tests
* [x] update README supported file types


## v1.1.1 Context Filtering Patch

Status: DONE

* [x] centralize context file allowlist logic in `config.py`
* [x] generate GUI file picker filters from supported context file definitions
* [x] update Selected Files mode to use the expanded extension list
* [x] update legacy picker file filters
* [x] apply filename-based allowlist support to Git Changed Files mode
* [x] remove duplicated file allowlist checks from scanner and collector
* [x] add tests for allowed extensions, allowed filenames, and sensitive file exclusion
* [x] add tests for GUI/Tk file filter generation
* [x] add tests for Dockerfile support in scanner, collector, and Git mode
* [x] verify expanded source coverage works consistently across files, folder, and git modes


## v1.1.2 Project Tree Mode Patch

Status: DONE

* [x] add Project Tree collection mode to GUI
* [x] persist Project Tree as a valid settings mode
* [x] add tree-only formatter output
* [x] build full project directory tree without reading file contents
* [x] include both files and directories in Project Tree mode
* [x] exclude cache, build, dependency, IDE, and VCS folders from Project Tree mode
* [x] remove Project Tree from Selected Files output
* [x] keep Project Tree in Full Folder and Git Changed Files modes
* [x] add tests for directory tree builder
* [x] add tests for tree-only formatter output
* [x] add settings validation test for Project Tree mode
* [x] verify Project Tree output does not include file content sections


## v1.2 Post-Release Polish

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
