[ENG]

📋 **XCC Context Collector**

**XCC Context Collector** is a Windows desktop utility for collecting clean project code context  
and copying it directly to the clipboard for AI coding workflows.

It is designed for developers working with **ChatGPT, Codex, Claude, and other AI assistants**,  
where sending structured project context quickly is more important than manually copying files one by one.

Unlike simple file-copy scripts, XCC focuses on a product-style workflow:
PySide6 GUI, Git changed-files mode, runtime history, persistent settings, system tray behavior,
restore hotkey, Windows autostart, and release-ready packaging.


🚀 **Core Features**

📂 **Flexible Context Collection**
- Select individual files
- Select a full project folder
- Collect Git changed files
- Include Git diff in Git mode
- Filter by supported file extensions
- Exclude cache/build/dependency folders

🧠 **AI-Ready Output Formatting**
- Structured output header
- Project tree included in context
- Per-file content sections
- Output metadata
- Source file statistics
- Clean format for AI chats

✂️ **Context Optimization**
- Compact mode
- Character budget limit
- Oversized file summarization
- Truncation status through model result
- Cache directories excluded by default

📋 **Clipboard Workflow**
- One-click Collect & Copy
- Output copied directly to clipboard
- No temporary manual file merging
- Designed for fast paste into AI chats

🧾 **Runtime History**
- Tracks recent collection runs
- Shows mode, source, file count, lines, characters, tokens, truncation, and errors
- Newest-first ordering
- Scrollable history view

⚙️ **Persistent Settings**
- Default mode
- Max output characters
- Compact mode
- Last selected source
- Start with Windows
- Start minimized to tray
- Close to tray
- Start maximized
- Tray notifications

🖥 **Windows Tray Integration**
- Background operation
- Show/hide from tray menu
- Quit from tray
- Close-to-tray behavior
- First minimize notification
- Double-click restore
- Tray-specific icon support

⌨️ **Integrated Restore Hotkey**
- Default hotkey: `Ctrl+Alt+X`
- Restores the main GUI window while XCC is running
- Works when hidden in tray or behind other windows
- Does not automatically run Collect & Copy
- Safe restore-only behavior

⌨️ **Esc Tray Hide**
- Press `Esc` to hide the main window to the system tray
- Keeps XCC running in the background
- Restore using tray icon or `Ctrl+Alt+X`

⚡ **Windows Autostart**
- Optional autostart from Settings
- Creates a shortcut in the Windows Startup folder
- Clean enable/disable behavior


🏗 **Architecture Overview**

Layered Python design:

```text
config      → constants and supported extensions
models      → typed collection result models
scanner     → project folder scanning
collector   → file reading and large-file handling
formatter   → AI-ready output formatting
optimizer   → compact output processing
budget      → character budget and truncation logic
git_utils   → Git repository detection, changed files, diff extraction
settings    → persistent config loading, validation, recovery
autostart   → Windows Startup shortcut integration
gui         → PySide6 GUI, tray, settings, history, hotkey restore
main        → legacy tkinter picker workflow
hotkey      → legacy standalone hotkey workflow
```

Designed for incremental growth without turning the app into a single script.


🗂 **Supported File Types**

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


🚫 **Excluded Folders**

XCC skips common cache, build, dependency, and IDE folders:

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


🗃 **Data Storage**

All settings are stored locally.

Default configuration path:

```text
%USERPROFILE%\.xcc\config.json
```

XCC does not require cloud storage or remote accounts.


🖥 **Primary App Mode**

Run the GUI:

```bash
python gui.py
```

For Windows release builds, the primary executable is built from:

```text
gui.py
```

Legacy scripts are kept for development and compatibility, but they are not the main release flow.


🧩 **Legacy Development Modes**

Legacy picker mode:

```bash
python -m src.xcc.main
```

or:

```bash
python run.py
```

Legacy standalone hotkey listener:

```bash
python hotkey.py
```

The release version uses the integrated GUI restore hotkey instead.


📦 **Build from Source**

Install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
pytest -q
```

Build Windows app with PyInstaller:

```bash
pyinstaller --clean --noconsole --name "XCC Context Collector" --icon assets\xcc_app.ico --add-data "assets;assets" --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick gui.py
```

Build output:

```text
dist\XCC Context Collector\XCC Context Collector.exe
```


🖥 **System Requirements**

* Windows 10 / 11 (64-bit)
* Python 3.13+ for source/development mode
* No Python installation required for packaged PyInstaller release


🔄 **Versioning**

Current version: **v0.9.0**

Current release stage: **v1.0 Windows Release preparation**


👨‍💻 **Author**

**XCON | RX**  
Telegram: [@End1essspace](https://t.me/End1essspace)  
GitHub: [End1essspace](https://github.com/End1essspace)


🧾 **License**

XCC Context Collector is licensed under the GNU General Public License v3.0 (GPL-3.0).

You are free to use, modify, and distribute this software under the terms of the GPL v3.
Any distributed modified versions must also be licensed under GPL v3 and include source code.


🧾 **Copyright**

Copyright (C) 2026 Rafael Xudoynazarov (XCON | RX)

-----------------------------

[RUS]

📋 **XCC Context Collector**

**XCC Context Collector** — это Windows-утилита для сбора чистого контекста кода проекта  
и копирования его напрямую в буфер обмена для работы с AI-инструментами.

Приложение рассчитано на разработчиков, которые работают с **ChatGPT, Codex, Claude и другими AI-ассистентами**,  
где важно быстро передать структурированный контекст проекта без ручного копирования десятков файлов.

В отличие от простого скрипта для копирования файлов, XCC развивается как небольшой Windows-продукт:
PySide6 GUI, режим Git changed files, runtime history, сохранение настроек, трей, hotkey восстановления,
автозапуск Windows и подготовка к релизной сборке.


🚀 **Основные возможности**

📂 **Гибкий сбор контекста**
- Выбор отдельных файлов
- Выбор полной папки проекта
- Сбор изменённых Git-файлов
- Добавление Git diff в Git-режиме
- Фильтрация по поддерживаемым расширениям
- Исключение cache/build/dependency папок

🧠 **AI-ready формат вывода**
- Структурированный заголовок
- Project tree внутри output
- Отдельные секции по каждому файлу
- Output metadata
- Статистика исходных файлов
- Чистый формат для вставки в AI-чаты

✂️ **Оптимизация контекста**
- Compact mode
- Лимит символов
- Summarize для слишком больших файлов
- Truncation status через модель результата
- Исключение cache-директорий по умолчанию

📋 **Clipboard workflow**
- One-click Collect & Copy
- Готовый output сразу копируется в буфер обмена
- Не нужно вручную объединять файлы
- Быстрая вставка в AI-чат

🧾 **Runtime History**
- История последних сборов
- Mode, source, files, lines, characters, tokens, truncation, errors
- Newest-first ordering
- Scrollable history view

⚙️ **Сохраняемые настройки**
- Default mode
- Max output characters
- Compact mode
- Last selected source
- Start with Windows
- Start minimized to tray
- Close to tray
- Start maximized
- Tray notifications

🖥 **Интеграция с системным треем**
- Работа в фоне
- Show/hide через tray menu
- Quit from tray
- Close-to-tray поведение
- First minimize notification
- Double-click restore
- Отдельная tray icon

⌨️ **Встроенный hotkey восстановления**
- Hotkey по умолчанию: `Ctrl+Alt+X`
- Восстанавливает главное окно, пока XCC запущен
- Работает, если окно скрыто в трее или находится за другими окнами
- Не запускает Collect & Copy автоматически
- Безопасное restore-only поведение

⌨️ **Скрытие в трей через Esc**
- `Esc` скрывает главное окно в системный трей
- XCC продолжает работать в фоне
- Восстановление через tray icon или `Ctrl+Alt+X`

⚡ **Автозапуск Windows**
- Опциональный автозапуск из Settings
- Создание shortcut в Windows Startup folder
- Чистое включение/отключение


🏗 **Архитектура**

Слоистая Python-структура:

```text
config      → константы и поддерживаемые расширения
models      → typed модели результата
scanner     → сканирование папки проекта
collector   → чтение файлов и обработка больших файлов
formatter   → AI-ready форматирование
optimizer   → compact output
budget      → лимит символов и truncation
git_utils   → Git repository detection, changed files, diff extraction
settings    → загрузка, валидация и recovery настроек
autostart   → Windows Startup shortcut integration
gui         → PySide6 GUI, tray, settings, history, hotkey restore
main        → legacy tkinter picker workflow
hotkey      → legacy standalone hotkey workflow
```

Архитектура рассчитана на постепенное развитие без превращения проекта в один большой скрипт.


🗂 **Поддерживаемые типы файлов**

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


🚫 **Исключаемые папки**

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


🗃 **Хранение данных**

Все настройки хранятся локально.

Путь по умолчанию:

```text
%USERPROFILE%\.xcc\config.json
```

XCC не требует облачного хранилища или удалённых аккаунтов.


🖥 **Основной режим запуска**

Запуск GUI:

```bash
python gui.py
```

Для Windows release основной executable собирается из:

```text
gui.py
```

Legacy-скрипты сохранены для разработки и совместимости, но не являются основным release flow.


🧩 **Legacy development modes**

Legacy picker mode:

```bash
python -m src.xcc.main
```

или:

```bash
python run.py
```

Legacy standalone hotkey listener:

```bash
python hotkey.py
```

Релизная версия использует встроенный GUI restore hotkey.


📦 **Сборка из исходников**

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Запуск тестов:

```bash
pytest -q
```

Сборка Windows-приложения через PyInstaller:

```bash
pyinstaller --clean --noconsole --name "XCC Context Collector" --icon assets\xcc_app.ico --add-data "assets;assets" --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 --exclude-module PySide6.QtQml --exclude-module PySide6.QtQuick gui.py
```

Результат сборки:

```text
dist\XCC Context Collector\XCC Context Collector.exe
```


🖥 **Системные требования**

* Windows 10 / 11 (64-bit)
* Python 3.13+ для запуска из исходников
* Для packaged PyInstaller release установка Python не требуется


🔄 **Версионирование**

Текущая версия: **v0.9.0**

Текущий этап: **подготовка v1.0 Windows Release**


👨‍💻 **Автор**

**XCON | RX**  
TG: [@End1essspace](https://t.me/End1essspace)  
GitHub: [End1essspace](https://github.com/End1essspace)


🧾 **Лицензия**

XCC Context Collector распространяется под лицензией GNU General Public License v3.0 (GPL-3.0).

Вы имеете право использовать, изменять и распространять данное программное обеспечение в соответствии с условиями GPL v3.
Любые распространяемые модифицированные версии также должны быть лицензированы по GPL v3 и сопровождаться исходным кодом.


🧾 **Copyright**

Copyright (C) 2026 Rafael Xudoynazarov (XCON | RX)
