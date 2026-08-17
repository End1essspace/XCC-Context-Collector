<p align="center">
  <img src="assets/xcc_app.png" width="96" alt="XCC Context Collector logo">
</p>

<h1 align="center">XCC Context Collector</h1>

<p align="center">
  <strong>AI-ready project context for Windows.</strong><br>
  Collect selected files, a folder, Git changes, or a project tree into one structured clipboard block.
</p>

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml"><img src="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml/badge.svg" alt="Windows CI"></a>
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><img src="https://img.shields.io/github/v/release/End1essspace/xcc-context-collector?display_name=tag" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-blue.svg" alt="GPL-3.0"></a>
</p>

<p align="center"><a href="#english">English</a> · <a href="#русский">Русский</a></p>

---

# English

Current version: **v1.3.1**

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><strong>Download XCC</strong></a>
  · <a href="docs/PORTABLE_ZIP.md">Portable guide</a>
  · <a href="docs/releases/v1.3.1.md">Release notes</a>
</p>

<p align="center">
  <img src="docs/screenshots/xcc-collect.png" alt="XCC Collect page" width="100%">
</p>

## What XCC does

| Mode | Result |
|---|---|
| **Selected Files** | Ordered files selected manually or imported from an AI response. |
| **Full Folder** | Supported files under a project root with ignore rules and a project tree. |
| **Git Changed Files** | Supported changed files plus separate staged and unstaged Git diffs. |
| **Project Tree** | Repository structure without file contents. |

Generated context can include version metadata, collection statistics, safety-warning summaries, Git status and diffs, project tree, complete file sections, errors, and an explicit budget summary.

## Selected Files workflow

```text
AI returns the files it needs
        ↓
Paste Paths or Ctrl+V
        ↓
Resolve relative paths under a visible project root
        ↓
Review the ordered selection
        ↓
Collect & Copy
```

Paste Paths accepts plain lines, Markdown lists, quotes, backticks, and fenced code blocks. Relative traversal outside the selected root is rejected. Clicking the Source summary opens transactional **Selected Files Review**.

## v1.3.1 highlights

- Responsive composition from the supported `920×620` minimum through Full HD, QHD, 4K-class and wide logical viewports.
- Independent width and height policies: reflow happens before controls are compressed.
- Progressive large-screen workbench instead of unlimited card stretching.
- Responsive Settings, History, About, Paste Paths, and Selected Files Review surfaces with no normal horizontal page scrolling.
- Work-area-aware maximize/restore and dialog sizing for multi-monitor Windows setups.
- DPI-aware raster and SVG rendering across screen changes.
- **Interface scale**: `Auto`, `90%`, `100%`, `110%`, `120%`, `125%`, or `150%`; changes apply after restart.
- XCC-styled scale selector and content-aware sizing for `Auto (recommended)`.
- Subtle `X-SERIES` footer wordmark included in source and packaged builds.
- Dedicated breakpoint, resize-round-trip, state-preservation, dialog, DPI, and responsive regression coverage.

v1.3.1 does not change collection semantics. The v1.3.0 Selected Files, source-fidelity, Git, safety, budget, background-work, tray, and hotkey contracts remain intact.

## Output guarantees

- collected source payloads and Git diffs are not compacted, normalized, or rewritten;
- Compact mode affects only XCC-generated structure;
- files and Git diffs are not silently cut in the middle;
- omissions, summaries, warnings, errors, and truncation are explicit;
- safety detection is warning-only and never silently redacts source;
- Runtime History is in-memory and metadata-only;
- cancellation never copies a partial result.

## Windows integration

- Windows 10/11 x64;
- PySide6 desktop UI;
- portable ZIP package;
- tray, close-to-tray, `Esc` hide-to-tray;
- native `Ctrl+Alt+X` restore hotkey;
- single-instance restore behavior;
- optional Start with Windows;
- persistent local settings;
- no account, cloud upload, or telemetry.

Settings:

```text
%USERPROFILE%\.xcc\config.json
```

## Install

Official v1.3.1 assets:

```text
XCC-Context-Collector-v1.3.1-win64.zip
XCC-Context-Collector-v1.3.1-win64.zip.sha256
```

Verify the checksum, extract the complete `XCC Context Collector` directory, and run `XCC Context Collector.exe`. Keep `_internal` and `VERSION.txt` beside the executable. Python is not required.

See [Portable ZIP Usage](docs/PORTABLE_ZIP.md).

## Run from source

Supported development runtime: **CPython 3.13.x** on Windows 10/11 x64.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m compileall -q src tests scripts gui.py
python scripts\check_version_consistency.py
python -m pytest -q
python gui.py
```

Installed entry point: `xcc-context-collector`.

## Runtime History

<p align="center">
  <img src="docs/screenshots/xcc-history.png" alt="XCC Runtime History page" width="100%">
</p>

History records outcome, duration, source, coverage, truncation, warnings, and errors for the current session. It never stores collected source, Git diffs, detected values, or failure-message bodies.

## Documentation

| Document | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Runtime, UI, responsive, DPI, and release boundaries |
| [v1.3.1 UI reference](docs/UI_REFERENCE_v1.3.1.md) | Frozen visual and interaction contract |
| [v1.3.1 validation](docs/M16_VALIDATION.md) | Release-candidate and clean-host procedure |
| [Release checklist](docs/RELEASE_CHECKLIST.md) | Compact operational gate |
| [Portable ZIP guide](docs/PORTABLE_ZIP.md) | Checksum, extraction, updates, removal |
| [Bug-report diagnostics](docs/BUG_REPORTING.md) | Reproducible sanitized reports |
| [v1.3.1 release notes](docs/releases/v1.3.1.md) | User-visible release summary |
| [Roadmap](docs/roadmap.md) | Release status and next steps |
| [Contributing](CONTRIBUTING.md) | Development rules |
| [Security](SECURITY.md) | Security model and reporting |

## Author

**End1essspace | RX**  
Telegram: [@End1essspace](https://t.me/End1essspace)  
GitHub: [End1essspace](https://github.com/End1essspace)

## License

XCC Context Collector is licensed under the [GNU General Public License v3.0](LICENSE).

Copyright (C) 2026 Rafael Xudoynazarov (End1essspace | RX)

---

# Русский

Текущая версия: **v1.3.1**

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><strong>Скачать XCC</strong></a>
  · <a href="docs/PORTABLE_ZIP.md">Portable-инструкция</a>
  · <a href="docs/releases/v1.3.1.md">Описание релиза</a>
</p>

**XCC Context Collector** собирает выбранные файлы, папку проекта, Git-изменения или только дерево репозитория в один структурированный блок для AI-ассистента.

## Режимы

| Режим | Результат |
|---|---|
| **Selected Files** | Упорядоченный набор файлов, выбранных вручную или импортированных из ответа AI. |
| **Full Folder** | Поддерживаемые файлы папки с ignore rules и деревом проекта. |
| **Git Changed Files** | Изменённые файлы и раздельные staged/unstaged Git diff. |
| **Project Tree** | Только структура проекта без содержимого файлов. |

## Главное в v1.3.1

- адаптивный интерфейс от `920×620` до больших logical viewport без бесконтрольного растягивания;
- отдельные width/height responsive policies и reflow без дублирования виджетов;
- адаптивные Settings, History, About и оба Selected Files диалога;
- корректный work-area restore/maximize и multi-monitor lifecycle;
- DPI-aware raster/SVG rendering при смене экрана;
- **Interface scale**: `Auto`, `90%`, `100%`, `110%`, `120%`, `125%`, `150%`, применяется после перезапуска;
- XCC-style selector масштаба без clipping;
- ненавязчивый `X-SERIES` wordmark в footer;
- отдельная regression-матрица для breakpoint, resize, state preservation, dialogs и DPI.

Семантика сбора не менялась: Paste Paths, Selected Files Review, source fidelity, Git, safety, budget, background collection, tray и `Ctrl+Alt+X` сохраняют контракты v1.3.0.

## Гарантии

- содержимое файлов и Git diff не переписывается;
- Compact mode влияет только на XCC-generated structure;
- files/diffs не обрываются молча посередине;
- warnings, errors, omissions и truncation отображаются явно;
- safety detection только предупреждает;
- Runtime History хранит только metadata текущей сессии;
- отмена не копирует частичный результат;
- нет аккаунта, cloud upload или telemetry.

## Установка

```text
XCC-Context-Collector-v1.3.1-win64.zip
XCC-Context-Collector-v1.3.1-win64.zip.sha256
```

Проверь SHA-256, распакуй всю папку и запусти `XCC Context Collector.exe`. `_internal` и `VERSION.txt` должны оставаться рядом с executable. Python для packaged build не нужен.

Подробности: [Portable ZIP Usage](docs/PORTABLE_ZIP.md).

## Запуск из исходников

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m compileall -q src tests scripts gui.py
python scripts\check_version_consistency.py
python -m pytest -q
python gui.py
```

## Документация

- [Архитектура](docs/ARCHITECTURE.md)
- [UI-контракт v1.3.1](docs/UI_REFERENCE_v1.3.1.md)
- [Validation v1.3.1](docs/M16_VALIDATION.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Portable ZIP](docs/PORTABLE_ZIP.md)
- [Диагностика bug reports](docs/BUG_REPORTING.md)
- [Release notes v1.3.1](docs/releases/v1.3.1.md)
- [Roadmap](docs/roadmap.md)
- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)

## Автор и лицензия

**End1essspace | RX** · [@End1essspace](https://t.me/End1essspace) · [GitHub](https://github.com/End1essspace)

XCC Context Collector распространяется по лицензии [GNU GPL v3.0](LICENSE).
