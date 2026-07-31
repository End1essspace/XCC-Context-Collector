<p align="center">
  <img src="assets/xcc_app.png" width="96" alt="XCC Context Collector logo">
</p>

<h1 align="center">XCC Context Collector</h1>

<p align="center">
  <strong>AI-ready project context for Windows.</strong><br>
  Collect files, folders, Git changes, or a project tree into one structured clipboard block.
</p>

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml"><img src="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml/badge.svg" alt="Windows CI"></a>
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><img src="https://img.shields.io/github/v/release/End1essspace/xcc-context-collector?display_name=tag" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-blue.svg" alt="GPL-3.0"></a>
</p>

<p align="center">
  <a href="#english">English</a> · <a href="#русский">Русский</a>
</p>

---

# English

Current version: **v1.3.0**

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><strong>Download XCC</strong></a>
  ·
  <a href="docs/PORTABLE_ZIP.md">Portable guide</a>
  ·
  <a href="docs/releases/v1.3.0.md">Release notes</a>
</p>

<p align="center">
  <img src="docs/screenshots/xcc-collect.png" alt="XCC Collect page" width="100%">
</p>

<p align="center"><sub>Collect a real repository, inspect coverage and result health, then copy the generated context in one action.</sub></p>

## What XCC does

XCC turns project material into one structured context block for ChatGPT, Codex, Claude, and other coding assistants.

| Mode | Result |
|---|---|
| **Selected Files** | A reviewed, ordered set of files selected manually or imported from an AI response. |
| **Full Folder** | Supported files from a project folder, with ignore rules and a project tree. |
| **Git Changed Files** | Supported changed files plus separate staged and unstaged Git diffs. |
| **Project Tree** | Repository structure without file contents. |

The generated block can include version metadata, collection statistics, safety-warning summaries, typed Git status, staged/unstaged diffs, a project tree, complete file sections, errors, and an explicit budget summary.

## Selected Files AI workflow

```text
AI returns the files it needs
        ↓
Copy the path list
        ↓
Paste Paths or Ctrl+V
        ↓
Resolve relative paths against a visible project root
        ↓
Review the ordered selection
        ↓
Collect & Copy
```

The importer accepts plain lines, Markdown bullets, numbered lists, quotes, backticks, and fenced code blocks. It preserves order, applies Windows-aware deduplication, validates supported files, rejects traversal outside the chosen root, and reports missing, unsupported, external, or invalid paths.

Click the Source summary to open **Selected Files Review**. Changes remain transactional until **Apply Changes** is pressed.

## v1.3.0 highlights

- **Paste Paths** and guarded `Ctrl+V` for direct AI-to-XCC file selection.
- **Selected Files Review** with project-root visibility, `Mixed locations`, multi-select removal, `Delete`, `Clear All`, `Cancel`, and `Apply Changes`.
- A final PySide6 design system across the shell, Collect page, dialogs, metrics, settings, history, and tray menu.
- Responsive layouts from the supported `920×620` minimum through maximized 2K displays.
- Keyboard navigation with visible focus states and accessible names for primary controls and status surfaces.
- Fast wheel navigation across the complete sidebar: one wheel step changes one page, high-resolution touchpad deltas are accumulated, navigation stops at the first and last page, and focus follows the active tab.
- Product-formatted `Ctrl+Alt+X` display without changing native hotkey registration.

## Output guarantees

XCC is built around explicit boundaries:

- collected source payloads and Git diffs are not trimmed, compacted, normalized, or rewritten;
- Compact mode affects only XCC-generated structural text;
- source files and Git diffs are not silently cut in the middle;
- omissions, summaries, warnings, errors, and truncation are reported;
- safety detection is warning-only and never silently redacts source;
- runtime history is in-memory and stores metadata only;
- collection runs outside the Qt main thread and cancellation never copies a partial result.

## Windows integration

- Windows 10/11 x64
- PySide6 desktop interface
- portable ZIP package
- system tray and close-to-tray
- native `Ctrl+Alt+X` restore hotkey
- `Esc` to hide to tray
- single-instance restore behavior
- optional Start with Windows
- persistent local settings
- no account, cloud upload, or telemetry

Settings are stored at:

```text
%USERPROFILE%\.xcc\config.json
```

## Supported source types

XCC supports common Python, JavaScript/TypeScript, frontend, backend, systems, data, documentation, configuration, and scripting formats, plus project files such as `Dockerfile`, `Makefile`, `CMakeLists.txt`, `pyproject.toml`, `package.json`, `.gitignore`, and `.xccignore`.

Real `.env` files, private keys, certificates, databases, logs, archives, and binaries are excluded by default.

Folder and tree modes respect root `.gitignore` and `.xccignore`. Git mode uses Git status plus `.xccignore`. Selected Files treats explicit user selection as intentional.

## Install

Official v1.3.0 assets:

```text
XCC-Context-Collector-v1.3.0-win64.zip
XCC-Context-Collector-v1.3.0-win64.zip.sha256
```

Verify the checksum, extract the complete `XCC Context Collector` directory, and run:

```text
XCC Context Collector.exe
```

Keep `_internal` and `VERSION.txt` beside the executable. Python is not required.

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

Installed entry point:

```powershell
xcc-context-collector
```

## Runtime History

<p align="center">
  <img src="docs/screenshots/xcc-history.png" alt="XCC Runtime History page" width="100%">
</p>

Runtime History records outcome, duration, source, coverage, truncation, warnings, and errors for the current session. It does not store collected source, Git diffs, detected values, or failure-message bodies.

## Documentation

| Document | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Runtime layers and product boundaries |
| [Final UI contract](docs/UI_REFERENCE_v1.3.0.md) | Frozen visual and interaction baseline |
| [Portable ZIP guide](docs/PORTABLE_ZIP.md) | Checksum, extraction, updates, removal |
| [Bug-report diagnostics](docs/BUG_REPORTING.md) | Reproducible and sanitized reports |
| [v1.3.0 validation](docs/M15_VALIDATION.md) | Release-candidate and clean-host procedure |
| [Release checklist](docs/RELEASE_CHECKLIST.md) | Operational publication gate |
| [v1.3.0 release notes](docs/releases/v1.3.0.md) | User-visible release summary |
| [Roadmap](docs/roadmap.md) | Completed and planned milestones |
| [Contributing](CONTRIBUTING.md) | Development and validation rules |
| [Security policy](SECURITY.md) | Vulnerability reporting and security model |

## Author

**XCON | RX**  
Telegram: [@End1essspace](https://t.me/End1essspace)  
GitHub: [End1essspace](https://github.com/End1essspace)

## License

XCC Context Collector is licensed under the [GNU General Public License v3.0](LICENSE).

Copyright (C) 2026 Rafael Xudoynazarov (XCON | RX)

---

# Русский

Текущая версия: **v1.3.0**

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><strong>Скачать XCC</strong></a>
  ·
  <a href="docs/PORTABLE_ZIP.md">Portable-инструкция</a>
  ·
  <a href="docs/releases/v1.3.0.md">Описание релиза</a>
</p>

**XCC Context Collector** собирает файлы проекта, папку, Git-изменения или только дерево репозитория в один структурированный блок для AI-ассистента.

## Режимы

| Режим | Результат |
|---|---|
| **Selected Files** | Проверенный упорядоченный набор файлов, выбранных вручную или импортированных из ответа AI. |
| **Full Folder** | Поддерживаемые файлы папки с ignore rules и деревом проекта. |
| **Git Changed Files** | Изменённые файлы и раздельные staged/unstaged Git diff. |
| **Project Tree** | Только структура проекта без содержимого файлов. |

## AI-workflow для Selected Files

```text
AI сообщает нужные файлы
        ↓
Копирование списка путей
        ↓
Paste Paths или Ctrl+V
        ↓
Разрешение относительных путей через project root
        ↓
Проверка итогового списка
        ↓
Collect & Copy
```

Импорт понимает обычные строки, Markdown-списки, нумерацию, кавычки, backticks и fenced code blocks. Порядок сохраняется, дубликаты удаляются по Windows-семантике, выход за выбранный root блокируется, а проблемные пути отображаются явно.

Нажатие на Source открывает **Selected Files Review**. Изменения применяются только через **Apply Changes**.

## Главное в v1.3.0

- Paste Paths и безопасный `Ctrl+V` для прямого импорта списков из ответов AI.
- Selected Files Review с project root, `Mixed locations`, множественным удалением, `Delete`, `Clear All`, `Cancel` и транзакционным применением.
- Финальная единая тёмная UI-система для shell, Collect, диалогов, метрик, Settings, History и tray menu.
- Адаптация от `920×620` до maximized 2K без дублирования виджетов и изменения логики.
- Keyboard navigation, видимый focus и accessibility names.
- Быстрое переключение вкладок колёсиком по всей области sidebar: один шаг — одна вкладка, touchpad-delta накапливается, переходы останавливаются на краях, focus следует за активной вкладкой.
- Единое отображение `Ctrl+Alt+X` при сохранении прежней native registration.

## Гарантии

- содержимое файлов и Git diff не переписывается и не уплотняется;
- Compact mode влияет только на структуру, которую генерирует XCC;
- файлы и diff не обрываются молча посередине;
- пропуски, warnings, errors и truncation отображаются явно;
- safety detection только предупреждает и не редактирует код;
- Runtime History хранит только metadata текущей сессии;
- сбор выполняется вне Qt main thread, а отмена не копирует частичный результат;
- XCC не требует аккаунта, не загружает данные в облако и не содержит telemetry.

## Установка

Скачай оба файла релиза:

```text
XCC-Context-Collector-v1.3.0-win64.zip
XCC-Context-Collector-v1.3.0-win64.zip.sha256
```

Проверь SHA-256, распакуй всю папку и запусти:

```text
XCC Context Collector.exe
```

`_internal` и `VERSION.txt` должны оставаться рядом с executable. Python для packaged build не нужен.

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
- [Финальный UI-контракт](docs/UI_REFERENCE_v1.3.0.md)
- [Portable ZIP](docs/PORTABLE_ZIP.md)
- [Диагностика bug reports](docs/BUG_REPORTING.md)
- [Validation v1.3.0](docs/M15_VALIDATION.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [Release notes v1.3.0](docs/releases/v1.3.0.md)
- [Roadmap](docs/roadmap.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)

## Автор и лицензия

**XCON | RX** · [@End1essspace](https://t.me/End1essspace) · [GitHub](https://github.com/End1essspace)

XCC Context Collector распространяется по лицензии [GNU GPL v3.0](LICENSE).
