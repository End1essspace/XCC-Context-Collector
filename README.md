# XCC Context Collector

XCC is a small Windows utility for collecting project code context and copying it to clipboard for AI chats.

## MVP

Current MVP supports:

- selecting multiple `.py` files
- reading files with encoding fallback
- formatting files into one AI-ready context block
- copying the result to clipboard
- showing basic collection statistics

## Output format

```text
# XCC Context

Files: 2
Lines: 120
Characters: 4200

===== file: main.py =====

<content>

===== file: utils.py =====

<content>
```

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m src.xcc.main
```

## Roadmap

* folder picker
* recursive project scan
* smart excludes
* compact context mode
* git diff mode
* global hotkey
* Windows tray app
* `.exe` build with PyInstaller

````
