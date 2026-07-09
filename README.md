[ENG]

📋 **XCC Context Collector**

**XCC Context Collector** is a Windows desktop utility for collecting clean project code context  
and copying it directly to the clipboard for AI coding workflows.

It is designed for developers working with **ChatGPT, Codex, Claude, and other AI assistants**,  
where structured project context needs to be prepared quickly and consistently.

AI chats often have limits on file uploads, attached files, and context size. Manually sending many project files is slow, repetitive, and often impossible in one message. XCC solves this by turning selected files, full project folders, Git changes, or a project tree into one structured AI-ready context block that can be pasted directly into an AI chat.


🚀 **Core Features**

📂 **Project Context Collection**
- Select individual files
- Select a full project folder
- Collect Git changed files
- Copy project tree only, without file contents
- Include Git diff in Git mode
- Filter supported source, documentation, configuration, script, API, and database text files
- Skip cache, build, dependency, and IDE folders

🧠 **AI-Ready Output**
- Structured output header
- Project tree included for folder/Git modes
- Standalone Project Tree mode for structure-only context
- Per-file content sections
- Source/output statistics
- Compact mode for cleaner prompts
- Character budget with truncation status
- Oversized file summarization

📋 **Fast Clipboard Workflow**
- One-click **Collect & Copy**
- Output copied directly to clipboard
- Runtime history for recent collection runs
- Last selected source and settings are restored between launches

🖥 **Windows Desktop Integration**
- PySide6 desktop GUI
- System tray mode
- `Ctrl+Alt+X` restores the app window through a native Windows hotkey
- `Esc` hides the window to tray
- Close-to-tray behavior
- Single-instance protection
- Optional Windows autostart


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

The GUI is the primary release mode. Legacy scripts remain for development and compatibility.


🗂 **Supported File Types**

XCC supports common source, documentation, configuration, script, API, and database text files.

```text
Python:
.py
.pyw

JavaScript / TypeScript / frontend:
.js
.jsx
.ts
.tsx
.mjs
.cjs
.html
.css
.scss
.sass
.less
.vue
.svelte

Backend / system languages:
.java
.kt
.kts
.cs
.go
.rs
.c
.h
.cpp
.hpp
.cc
.cxx
.php
.rb
.swift

Data / API / database:
.sql
.graphql
.gql

Documentation:
.md
.mdx
.rst
.txt

Configuration:
.json
.jsonc
.yaml
.yml
.toml
.ini
.cfg
.conf
.properties
.xml

Scripts:
.sh
.bash
.zsh
.ps1
.bat
.cmd
```

XCC also supports common project filenames without relying only on extensions.

```text
Dockerfile
Containerfile
Makefile
CMakeLists.txt
requirements.txt
pyproject.toml
setup.py
setup.cfg
package.json
tsconfig.json
vite.config.js
vite.config.ts
next.config.js
next.config.ts
.gitignore
.dockerignore
.gitattributes
.editorconfig
.env.example
.env.template
.env.sample
```

Sensitive files such as `.env`, private keys, certificates, databases, logs, archives, and binaries are not included by default.


🚫 **Excluded Folders**

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

Run the GUI from source:

```bash
python gui.py
```

For Windows release builds, the primary executable is built from:

```text
gui.py
```


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

Build Windows app:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
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

Current version: **v1.1.2**


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
где важно быстро и стабильно подготовить структурированный контекст проекта.

У AI-чатов часто есть лимиты на загрузку файлов, количество attachments и общий размер контекста. Ручная отправка множества файлов проекта занимает время, повторяется каждый раз и часто не помещается в одно сообщение. XCC решает эту проблему: превращает выбранные файлы, папку проекта, Git-изменения или дерево проекта в один структурированный AI-ready context block для вставки в AI-чат.


🚀 **Основные возможности**

📂 **Сбор контекста проекта**
- Выбор отдельных файлов
- Выбор полной папки проекта
- Сбор изменённых Git-файлов
- Копирование только дерева проекта без содержимого файлов
- Добавление Git diff в Git-режиме
- Фильтрация поддерживаемых файлов исходного кода, документации, конфигурации, скриптов, API и баз данных
- Исключение cache, build, dependency и IDE-папок

🧠 **AI-ready output**
- Структурированный заголовок
- Project tree для folder/Git режимов
- Отдельный Project Tree mode для context только по структуре проекта
- Отдельные секции по каждому файлу
- Статистика source/output
- Compact mode для более чистого prompt
- Лимит символов с truncation status
- Summarize для слишком больших файлов

📋 **Быстрый clipboard workflow**
- One-click **Collect & Copy**
- Готовый output сразу копируется в буфер обмена
- Runtime history последних сборов
- Last selected source и настройки восстанавливаются между запусками

🖥 **Интеграция с Windows**
- PySide6 desktop GUI
- System tray mode
- `Ctrl+Alt+X` восстанавливает окно приложения через нативный Windows hotkey
- `Esc` скрывает окно в трей
- Close-to-tray поведение
- Защита от двойного запуска
- Опциональный Windows autostart


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

GUI является основным release mode. Legacy-скрипты сохранены для разработки и совместимости.


🗂 **Поддерживаемые типы файлов**

XCC поддерживает распространённые текстовые файлы исходного кода, документации, конфигурации, скриптов, API и баз данных.

```text
Python:
.py
.pyw

JavaScript / TypeScript / frontend:
.js
.jsx
.ts
.tsx
.mjs
.cjs
.html
.css
.scss
.sass
.less
.vue
.svelte

Backend / system languages:
.java
.kt
.kts
.cs
.go
.rs
.c
.h
.cpp
.hpp
.cc
.cxx
.php
.rb
.swift

Data / API / database:
.sql
.graphql
.gql

Документация:
.md
.mdx
.rst
.txt

Конфигурация:
.json
.jsonc
.yaml
.yml
.toml
.ini
.cfg
.conf
.properties
.xml

Скрипты:
.sh
.bash
.zsh
.ps1
.bat
.cmd
```

XCC также поддерживает распространённые проектные файлы по имени, а не только по расширению.

```text
Dockerfile
Containerfile
Makefile
CMakeLists.txt
requirements.txt
pyproject.toml
setup.py
setup.cfg
package.json
tsconfig.json
vite.config.js
vite.config.ts
next.config.js
next.config.ts
.gitignore
.dockerignore
.gitattributes
.editorconfig
.env.example
.env.template
.env.sample
```

Чувствительные файлы вроде `.env`, приватных ключей, сертификатов, баз данных, логов, архивов и бинарных файлов не включаются по умолчанию.


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

Запуск GUI из исходников:

```bash
python gui.py
```

Для Windows release основной executable собирается из:

```text
gui.py
```


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

Сборка Windows-приложения:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_release.ps1
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

Текущая версия: **v1.1.2**


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
