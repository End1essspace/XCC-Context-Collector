# XCC Context Collector

XCC is a small Windows desktop utility for collecting project code context and copying it to the clipboard for AI chats.

It is designed for workflows with ChatGPT, Codex, Claude, and other AI coding assistants where clean project context is needed quickly.

## Features

- PySide6 desktop GUI
- Select individual files
- Select full project folder
- Collect Git changed files
- Include Git diff in Git mode
- Compact output mode
- Project tree in output
- Character budget limit
- Large file summarization
- Clipboard copy
- Runtime history
- Persistent settings
- Windows tray mode
- Start minimized to tray
- Close to tray
- Start maximized option
- Optional Windows autostart
- Integrated restore hotkey: `Ctrl+Alt+X`

## Primary app mode

The primary application entry point is the GUI:

```bash
python gui.py
```

For the Windows release, the primary executable will be built from `gui.py`.

The GUI includes the main collection workflow, runtime history, settings, tray behavior, autostart behavior, and the restore hotkey.

## Restore hotkey

Default hotkey:

```text
Ctrl+Alt+X
```

When XCC is already running, the hotkey restores the main GUI window.

Expected behavior:

- if the window is hidden in tray, the hotkey restores it
- if the window is minimized or behind other windows, the hotkey brings it forward
- if the window is already visible, the hotkey raises it
- the hotkey does not run Collect & Copy automatically

This keeps the hotkey safe: it opens the app, but does not collect or copy project context without user action.

## Supported file types

XCC currently supports:

```text
.py
.pyw
.md
.txt
.json
.yaml
.yml
.toml
.ini
.cfg
```

## Excluded folders

XCC skips common cache/build/dependency folders:

```text
.git
.idea
.vscode
.venv
venv
__pycache__
.pytest_cache
.mypy_cache
.ruff_cache
node_modules
dist
build
bin
obj
```

## Output format

```text
# XCC Context

XCC Version: 0.9.0
Mode: Full Folder
Max Output Characters: 120000

Files: 12
Lines: 900
Characters: 42000

# Project Tree

src/main.py
src/utils.py

# Files

===== file: src/main.py =====

<content>
```

## Settings

Settings are stored locally in:

```text
%USERPROFILE%\.xcc\config.json
```

Current persistent settings include:

- default mode
- max chars
- compact mode
- last source
- start with Windows
- start minimized to tray
- close to tray
- start maximized
- tray notifications

## Windows autostart

When `Start with Windows` is enabled, XCC creates a shortcut in the Windows Startup folder:

```text
shell:startup
```

Disabling the option removes the shortcut.

## Legacy development modes

These scripts are kept for development and compatibility, but they are not the primary release flow.

### Legacy picker mode

```bash
python -m src.xcc.main
```

or:

```bash
python run.py
```

This opens the older tkinter-based picker workflow.

### Legacy hotkey listener

```bash
python hotkey.py
```

This starts the older standalone hotkey listener for the legacy picker workflow.

For the GUI release, use the integrated restore hotkey instead.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

## Requirements

Runtime/development dependencies are listed in `requirements.txt`:

```text
pyperclip
pytest
keyboard
PySide6
```

## Roadmap

Completed milestones:

- v0.1 Core MVP
- v0.2 Context Optimization
- v0.3 Git Context Mode
- v0.4 Hotkey Mode
- v0.5 PySide6 GUI
- v0.6 Settings Persistence
- v0.7 Tray Mode
- v0.8 Settings Expansion
- v0.9 Optimization
- v0.9.5 Settings/About Polish

Current milestone:

- v0.9.6 Integrated Restore Hotkey

Next milestone:

- v1.0 Windows Release
