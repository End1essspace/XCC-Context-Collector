<p align="center">
  <img src="assets/xcc_app.png" width="96" alt="XCC Context Collector logo">
</p>

<h1 align="center">XCC Context Collector</h1>

<p align="center">
  <strong>Turn your Windows project into clean, AI-ready context in seconds.</strong><br>
  Select exactly what an AI assistant needs — files, a folder, Git changes, or just the project tree — and copy one structured context block without manually assembling prompts.
</p>

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml"><img src="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml/badge.svg" alt="Windows CI"></a>
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><img src="https://img.shields.io/github/v/release/End1essspace/xcc-context-collector?display_name=tag" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-blue.svg" alt="GPL-3.0"></a>
</p>

<p align="center"><a href="#english">English</a> · <a href="#русский">Русский</a></p>

---

# English

Current version: **v1.4.0**

## Give AI the project context it actually needs

Coding assistants work best when they see the right source files, repository structure, and current Git state. Collecting that context by hand is slow, repetitive, and easy to get wrong.

**XCC Context Collector** turns that workflow into one local desktop action:

```text
Choose the relevant project context
        ↓
XCC collects and structures it
        ↓
One clipboard block is ready for your AI assistant
```

Use the whole folder when you need broad context, Git mode when you are debugging current changes, Project Tree when structure is enough, or Selected Files when you want precise control.

<p align="center">
  <img src="docs/screenshots/xcc-collect.png" alt="XCC Collect page" width="100%">
</p>

## Download

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><strong>⬇ Download XCC for Windows</strong></a>
  · <a href="docs/PORTABLE_ZIP.md">Portable guide</a>
  · <a href="docs/releases/v1.4.0.md">Release notes</a>
</p>

**Windows 10/11 x64 · Portable ZIP · No Python required**

Official v1.4.0 assets:

```text
XCC-Context-Collector-v1.4.0-win64.zip
XCC-Context-Collector-v1.4.0-win64.zip.sha256
```

Extract the complete `XCC Context Collector` directory and run `XCC Context Collector.exe`.

## What you can collect

| Mode | Best for | Result |
|---|---|---|
| **Selected Files** | Precise AI requests and focused debugging | Ordered files selected manually or imported from an AI response |
| **Full Folder** | Broad project understanding | Supported files under a project root, ignore rules, and a project tree |
| **Git Changed Files** | Reviewing or debugging current work | Changed files plus separate staged and unstaged Git diffs |
| **Project Tree** | Showing architecture without source contents | Repository structure only |

## Send original files back to AI

The **Attachments** page is a separate workflow for original filesystem files. It does not convert them into text context and does not apply the Collect extension allowlist.

```text
AI asks for exact files
        ↓
Paste Paths / Add Files
        ↓
Review ordered selection
        ↓
Copy Files
   or Send One-by-One
   or Create ZIP & Copy
```

- **Copy Files** publishes the whole ordered selection as Windows file objects.
- **Send One-by-One** is the compatibility path for targets that accept one file per paste event: XCC locks to one foreground window and dispatches one `Ctrl+V` per file without submitting the message.
- **Create ZIP & Copy** builds a ZIP64-capable bundle in `%USERPROFILE%\.xcc\attachment-bundles\`, preserves safe relative structure, then copies the completed archive as one file object.
- Original files are never rewritten, moved, or deleted.


### AI → XCC → AI workflow

When an assistant tells you which files it needs, you do not have to browse for them one by one:

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

## Local-first by design

XCC is built for source code and repository context, so privacy is part of the product boundary rather than an optional mode.

- **No account required.**
- **No cloud upload.** Collection and formatting happen locally on your machine.
- **No telemetry.** XCC does not send usage analytics.
- **Clipboard output is explicit.** Context is copied only when collection completes successfully.
- **Runtime History is persistent and metadata-only.** It survives restarts in `%USERPROFILE%\.xcc\history.json` while excluding collected source, Git diff bodies, detected secret values, attachment contents, and raw failure bodies.
- **Safety detection is warning-only.** Potentially sensitive material is surfaced instead of silently rewritten or redacted.

## Why XCC is reliable for code context

Generated context can include version metadata, collection statistics, safety-warning summaries, Git status and diffs, project tree, complete file sections, errors, and an explicit budget summary.

XCC keeps the important payload trustworthy:

- collected source payloads and Git diffs are not compacted, normalized, or rewritten;
- Compact mode affects only XCC-generated structure;
- files and Git diffs are not silently cut in the middle;
- omissions, summaries, warnings, errors, and truncation are explicit;
- cancellation never copies a partial result.

## v1.4.0 highlights

- New **Attachments** page for original-file handoff, separate from text-context collection.
- `Copy Files` publishes ordered Windows file objects without loading whole file bodies into XCC memory.
- **Send One-by-One** automates sequential paste for one-file-per-paste targets with foreground-window locking and fail-closed focus checks.
- **Create ZIP & Copy** provides a transactional ZIP64 fallback with safe relative archive paths and a 7-day XCC-managed bundle lifecycle.
- Configurable global shortcuts for Restore / Show, Collect & Copy, and optional Attachment Handoff.
- Persistent, exportable, metadata-only Runtime History with bounded retention and corruption recovery.
- Attachments, Settings, History, and About share the same responsive workbench geometry; no normal horizontal page scrolling.
- First-run defaults, Attachments table alignment/selection polish, About product composition, and QSS token rendering were refined for the v1.4.0 release.

## Windows integration

- Windows 10/11 x64;
- PySide6 desktop UI;
- portable ZIP package;
- tray, close-to-tray, `Esc` hide-to-tray;
- native `Ctrl+Alt+X` restore hotkey;
- single-instance restore behavior;
- optional Start with Windows;
- persistent local settings.

Settings:

```text
%USERPROFILE%\.xcc\config.json
```

## Install

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

History persists outcome, duration, sanitized source metadata, coverage, truncation, warnings, errors, and attachment-transfer metadata across restarts. It keeps the newest 200 records, can export the documented JSON schema, and never stores collected source bodies, Git diff bodies, detected secret values, attachment contents, or raw failure bodies.

## Documentation

| Document | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Runtime, UI, responsive, DPI, and release boundaries |
| [v1.4.0 UI reference](docs/UI_REFERENCE_v1.4.0.md) | Frozen visual and interaction contract |
| [v1.4.0 validation](docs/M17_VALIDATION.md) | Release-candidate and clean-host procedure |
| [Release checklist](docs/RELEASE_CHECKLIST.md) | Compact operational gate |
| [Portable ZIP guide](docs/PORTABLE_ZIP.md) | Checksum, extraction, updates, removal |
| [Bug-report diagnostics](docs/BUG_REPORTING.md) | Reproducible sanitized reports |
| [v1.4.0 release notes](docs/releases/v1.4.0.md) | User-visible release summary |
| [Roadmap](docs/XCC_ROADMAP_v1.4.0_UPDATED.md) | Release status and next steps |
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

Текущая версия: **v1.4.0**

## Дай AI именно тот контекст проекта, который ему нужен

AI-ассистент работает заметно лучше, когда видит нужные исходники, структуру проекта и текущее состояние Git. Собирать всё это вручную — медленно, однообразно и легко ошибиться.

**XCC Context Collector** превращает это в одно локальное действие:

```text
Выбираешь нужный контекст проекта
        ↓
XCC собирает и структурирует его
        ↓
Один готовый блок копируется для AI-ассистента
```

Нужен широкий обзор проекта — собирай папку. Нужно разобрать текущие изменения — используй Git mode. Нужна только архитектура — Project Tree. Нужен точный набор файлов — Selected Files.

<p align="center">
  <img src="docs/screenshots/xcc-collect.png" alt="XCC Collect page" width="100%">
</p>

## Скачать

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><strong>⬇ Скачать XCC для Windows</strong></a>
  · <a href="docs/PORTABLE_ZIP.md">Portable-инструкция</a>
  · <a href="docs/releases/v1.4.0.md">Описание релиза</a>
</p>

**Windows 10/11 x64 · Portable ZIP · Python не требуется**

Официальные файлы v1.4.0:

```text
XCC-Context-Collector-v1.4.0-win64.zip
XCC-Context-Collector-v1.4.0-win64.zip.sha256
```

Распакуй целиком папку `XCC Context Collector` и запусти `XCC Context Collector.exe`.

## Что можно собрать

| Режим | Когда использовать | Результат |
|---|---|---|
| **Selected Files** | Точный запрос AI или локальная отладка | Упорядоченный набор файлов, выбранных вручную или импортированных из ответа AI |
| **Full Folder** | Нужен широкий контекст проекта | Поддерживаемые файлы папки, ignore rules и дерево проекта |
| **Git Changed Files** | Нужно разобрать текущую работу | Изменённые файлы и раздельные staged/unstaged Git diff |
| **Project Tree** | Нужна структура без исходников | Только дерево репозитория |

## Отправка исходных файлов обратно в AI

Страница **Attachments** — отдельный workflow для оригинальных файлов. Она не превращает их в text context и не использует extension allowlist режима Collect.

```text
AI просит конкретные файлы
        ↓
Paste Paths / Add Files
        ↓
Проверяешь порядок
        ↓
Copy Files
   или Send One-by-One
   или Create ZIP & Copy
```

- **Copy Files** помещает весь упорядоченный набор в Windows clipboard как filesystem objects.
- **Send One-by-One** — compatibility workflow для целей, которые принимают только один файл на один paste event: XCC фиксирует одно foreground-окно и отправляет по одному `Ctrl+V` на файл, не отправляя само сообщение.
- **Create ZIP & Copy** создаёт ZIP64-capable bundle в `%USERPROFILE%\.xcc\attachment-bundles\`, сохраняет безопасную относительную структуру и копирует готовый ZIP как один файл.
- Оригинальные файлы не переписываются, не перемещаются и не удаляются.


### AI → XCC → AI

Если ассистент уже перечислил нужные файлы, не нужно искать каждый вручную:

```text
AI возвращает список файлов
        ↓
Paste Paths или Ctrl+V
        ↓
XCC разрешает пути относительно видимого project root
        ↓
Проверяешь итоговый порядок
        ↓
Collect & Copy
```

Paste Paths понимает обычные строки, Markdown-списки, кавычки, backticks и fenced code blocks. Выход по относительному пути за пределы выбранного root отклоняется. Нажатие на Source открывает транзакционный **Selected Files Review**.

## Local-first по умолчанию

XCC работает с исходным кодом и содержимым репозиториев, поэтому приватность заложена в саму границу продукта.

- **Аккаунт не нужен.**
- **Нет cloud upload.** Сбор и форматирование происходят локально на компьютере.
- **Нет telemetry.** XCC не отправляет аналитику использования.
- **Копирование в clipboard происходит явно.** Контекст копируется только после успешного завершения сбора.
- **Runtime History сохраняется между запусками и остаётся metadata-only.** `%USERPROFILE%\.xcc\history.json` не содержит исходники, тела Git diff, найденные secret values, содержимое attachments или raw failure bodies.
- **Safety detection только предупреждает.** Потенциально чувствительные данные не переписываются и не скрываются молча.

## Почему контексту XCC можно доверять

Сформированный блок может включать version metadata, статистику сбора, safety warnings, Git status и diff, project tree, полные file sections, errors и явный budget summary.

Основные гарантии:

- содержимое файлов и Git diff не compact-ится, не нормализуется и не переписывается;
- Compact mode влияет только на XCC-generated structure;
- files/diffs не обрываются молча посередине;
- warnings, errors, omissions и truncation отображаются явно;
- отмена не копирует частичный результат.

## Главное в v1.4.0

- новая страница **Attachments** для передачи оригинальных файлов отдельно от text-context workflow;
- `Copy Files` публикует упорядоченные Windows file objects без загрузки содержимого всех файлов в память;
- **Send One-by-One** автоматизирует последовательные paste events с фиксацией foreground window и fail-closed проверкой фокуса;
- **Create ZIP & Copy** даёт transactional ZIP64 fallback с безопасными относительными путями и 7-дневным lifecycle XCC-managed bundles;
- настраиваемые глобальные hotkeys для Restore / Show, Collect & Copy и optional Attachment Handoff;
- persistent/exportable metadata-only Runtime History с bounded retention и corruption recovery;
- Attachments, Settings, History и About используют общий responsive workbench;
- финальный polish таблицы Attachments, About, first-run defaults и QSS token renderer входит в v1.4.0.

## Windows integration

- Windows 10/11 x64;
- PySide6 desktop UI;
- portable ZIP;
- tray, close-to-tray, `Esc` hide-to-tray;
- native `Ctrl+Alt+X` restore hotkey;
- single-instance restore;
- optional Start with Windows;
- локальные persistent settings.

Настройки:

```text
%USERPROFILE%\.xcc\config.json
```

## Установка

Проверь SHA-256, распакуй всю папку и запусти `XCC Context Collector.exe`. `_internal` и `VERSION.txt` должны оставаться рядом с executable. Python для packaged build не нужен.

Подробности: [Portable ZIP Usage](docs/PORTABLE_ZIP.md).

## Запуск из исходников

Поддерживаемая development-среда: **CPython 3.13.x** на Windows 10/11 x64.

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

History сохраняет между запусками outcome, duration, sanitized source metadata, coverage, truncation, warnings, errors и attachment-transfer metadata. Хранятся максимум 200 newest records; доступен экспорт документированного JSON schema. Collected source bodies, Git diff bodies, detected secret values, attachment contents и raw failure bodies не сохраняются.

## Документация

| Документ | Назначение |
|---|---|
| [Архитектура](docs/ARCHITECTURE.md) | Runtime, UI, responsive, DPI и release boundaries |
| [UI-контракт v1.4.0](docs/UI_REFERENCE_v1.4.0.md) | Зафиксированный visual и interaction contract |
| [Validation v1.4.0](docs/M17_VALIDATION.md) | Release-candidate и clean-host procedure |
| [Release checklist](docs/RELEASE_CHECKLIST.md) | Компактный operational gate |
| [Portable ZIP](docs/PORTABLE_ZIP.md) | Checksum, extraction, updates и removal |
| [Диагностика bug reports](docs/BUG_REPORTING.md) | Воспроизводимые sanitized reports |
| [Release notes v1.4.0](docs/releases/v1.4.0.md) | User-visible release summary |
| [Roadmap](docs/XCC_ROADMAP_v1.4.0_UPDATED.md) | Статус релиза и следующие шаги |
| [Contributing](CONTRIBUTING.md) | Правила разработки |
| [Security](SECURITY.md) | Security model и reporting |

## Автор и лицензия

**End1essspace | RX** · [@End1essspace](https://t.me/End1essspace) · [GitHub](https://github.com/End1essspace)

XCC Context Collector распространяется по лицензии [GNU GPL v3.0](LICENSE).
