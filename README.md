<p align="center">
  <img src="assets/xcc_app.png" width="96" alt="XCC Context Collector logo">
</p>

<h1 align="center">XCC Context Collector</h1>

<p align="center">
  <strong>Move the right project context — or the exact files — between your Windows project and AI in seconds.</strong><br>
  XCC turns repetitive context gathering and file hunting into a fast, local workflow.
</p>

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml"><img src="https://github.com/End1essspace/xcc-context-collector/actions/workflows/ci.yml/badge.svg" alt="Windows CI"></a>
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><img src="https://img.shields.io/github/v/release/End1essspace/xcc-context-collector?display_name=tag" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-blue.svg" alt="GPL-3.0"></a>
</p>

<p align="center">
  <a href="#what-xcc-does">What XCC does</a> ·
  <a href="#attachments">Attachments</a> ·
  <a href="#collect">Collect</a> ·
  <a href="#download">Download</a> ·
  <a href="README.ru.md">Русский</a>
</p>

---

## What XCC does

XCC is a local Windows desktop tool built around two AI-assisted development workflows:

| Workflow | Use it when | Result |
|---|---|---|
| **Collect** | The AI needs source context, Git state, or project structure | One structured text block copied to the clipboard |
| **Attachments** | The AI asks for exact project files | Original files, a ZIP bundle, or sequential file paste |

```text
AI asks for context                      AI asks for files
        ↓                                      ↓
      Collect                              Attachments
        ↓                                      ↓
structured clipboard block      Copy Files / Send One-by-One / ZIP
        ↓                                      ↓
             continue working with the AI
```

No manual prompt assembly. No hunting through Explorer for every requested file.

<p align="center">
  <img src="docs/screenshots/xcc-collect.png" alt="XCC Collect page" width="100%">
</p>

## Download

<p align="center">
  <a href="https://github.com/End1essspace/xcc-context-collector/releases"><strong>⬇ Download XCC for Windows</strong></a>
  · <a href="docs/PORTABLE_ZIP.md">Portable guide</a>
  · <a href="docs/releases/v1.4.0.md">v1.4.0 release notes</a>
</p>

**Current version: v1.4.0**  
**Windows 10/11 x64 · Portable ZIP · No Python required**

Official release assets:

```text
XCC-Context-Collector-v1.4.0-win64.zip
XCC-Context-Collector-v1.4.0-win64.zip.sha256
```

### Quick start

1. Download the ZIP from GitHub Releases.
2. Verify the SHA-256 checksum.
3. Extract the complete `XCC Context Collector` directory.
4. Run `XCC Context Collector.exe`.
5. Paste an AI-requested path list into XCC, then either collect context or send the requested files.

Keep `_internal` and `VERSION.txt` beside the executable.

---

## Attachments

Use **Attachments** when an AI assistant asks for the actual project files rather than text context.

```text
AI asks for exact files
        ↓
Paste Paths / Add Files
        ↓
resolve + validate
        ↓
review ordered selection
        ↓
Copy Files / Send One-by-One / Create ZIP & Copy
```

Attachments is intentionally separate from Collect. It works with original filesystem files and does not apply the Collect extension allowlist.

That means explicitly selected project artifacts can be handed off even when they are not text files — for example images, Unity assets, archives, binaries, databases, or unknown extensions.

<p align="center">
  <img src="docs/screenshots/xcc-attachments.png" alt="XCC Attachments page" width="100%">
</p>

### Copy Files

Publishes the selected files to the Windows clipboard as filesystem objects.

Use it when the receiving application accepts file objects from the clipboard.

### Send One-by-One

Automates sequential paste for targets that accept one file per paste event.

XCC:

- waits through a short countdown;
- captures one foreground target window;
- prepares one selected file at a time;
- verifies that focus has not changed;
- sends one `Ctrl+V` per file;
- stops if the target window changes;
- never presses Enter or submits the message.

This is a Windows input workflow, not browser DOM automation and not a provider API integration.

### Create ZIP & Copy

Builds a ZIP64-capable bundle and copies the completed archive as one file object.

The bundle:

- preserves safe project-relative structure where possible;
- preserves original file bytes;
- rejects unsafe archive paths;
- is published only after successful completion;
- is stored under `%USERPROFILE%\.xcc\attachment-bundles\`.

For large selections or targets with weak clipboard support, this is the most predictable handoff path.

> **Browser note:** XCC guarantees the local clipboard/file preparation step. The receiving application controls how pasted files are interpreted. If filename or directory fidelity matters, use **Create ZIP & Copy**.

---

## Collect

Use **Collect** when the AI needs readable project context rather than original file objects.

### Collection modes

| Mode | Best for | Result |
|---|---|---|
| **Selected Files** | Precise AI requests and focused debugging | Ordered files selected manually or imported from an AI response |
| **Full Folder** | Broad project understanding | Supported files under a project root, ignore rules, and a project tree |
| **Git Changed Files** | Reviewing or debugging current work | Changed files plus separate staged and unstaged Git diffs |
| **Project Tree** | Showing architecture without source contents | Repository structure only |

### AI → XCC → AI

When an assistant returns a list of files it wants to inspect:

```text
AI returns requested paths
        ↓
Paste Paths / Ctrl+V
        ↓
resolve under a visible project root
        ↓
review the ordered selection
        ↓
Collect & Copy
        ↓
structured context back to the AI
```

**Paste Paths** accepts plain lines, Markdown lists, quotes, backticks, and fenced code blocks.

Relative traversal outside the selected project root is rejected. The final selection can be reviewed before collection.

### Context fidelity

XCC treats collected source as payload, not as text to silently rewrite.

- collected source bodies and Git diffs are not normalized or rewritten;
- Compact mode affects XCC-generated structure, not source payload;
- files and diffs are not silently cut in the middle;
- warnings, omissions, errors, summaries, and truncation are explicit;
- cancellation never publishes a partial result.

Generated context can include version metadata, collection statistics, safety-warning summaries, Git status and diffs, project tree, complete file sections, errors, and an explicit budget summary.

---

## v1.4.0 highlights

v1.4.0 expands XCC from a context collector into a broader AI project handoff tool.

- **Attachments workspace** for original-file transfer.
- **Copy Files** for direct Windows file-object clipboard publication.
- **Send One-by-One** for controlled sequential file paste.
- **Create ZIP & Copy** with safe relative paths and ZIP64 support.
- **Configurable global hotkeys** for Restore / Show, Collect & Copy, and optional Attachment Handoff.
- **Persistent, exportable Runtime History** with metadata-only storage.
- Shared responsive workbench behavior across Attachments, Settings, History, and About.
- Release hardening across DPI behavior, first-run defaults, safety, project traversal, packaging, and regression coverage.

---

## Local-first by design

XCC works with source code and project files, so privacy is part of the product boundary.

- **No account required.**
- **No telemetry.**
- **No cloud upload performed by XCC.**
- Collection and formatting happen locally.
- Clipboard publication is explicit.
- Original attachment files are never rewritten, moved, or deleted.
- Safety detection warns instead of silently editing or redacting source.
- Runtime History stores metadata, not project contents.

Runtime History is stored at:

```text
%USERPROFILE%\.xcc\history.json
```

It excludes collected source bodies, Git diff bodies, detected secret values, attachment contents, and raw failure bodies.

---

## Runtime History

<p align="center">
  <img src="docs/screenshots/xcc-history.png" alt="XCC Runtime History page" width="100%">
</p>

Runtime History persists operational outcomes across restarts, including duration, sanitized source metadata, coverage, truncation, warnings, errors, and attachment-transfer metadata.

It keeps the newest **200 records**, supports export through the documented JSON format, and remains metadata-only.

---

## Windows integration

- Windows 10/11 x64;
- PySide6 desktop UI;
- portable ZIP distribution;
- tray and close-to-tray behavior;
- `Esc` hide-to-tray;
- configurable native global hotkeys;
- single-instance restore behavior;
- optional Start with Windows;
- persistent local settings.

Settings are stored at:

```text
%USERPROFILE%\.xcc\config.json
```

---

## Install

See [Portable ZIP Usage](docs/PORTABLE_ZIP.md) for checksum verification, extraction, updates, and removal.

Python is not required for the packaged build.

---

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

```text
xcc-context-collector
```

---

## Documentation

| Document | Purpose |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | Runtime, UI, responsive, DPI, and release boundaries |
| [v1.4.0 UI reference](docs/UI_REFERENCE_v1.4.0.md) | Frozen visual and interaction contract |
| [v1.4.0 validation](docs/M17_VALIDATION.md) | Release-candidate and clean-host procedure |
| [Release checklist](docs/RELEASE_CHECKLIST.md) | Compact operational release gate |
| [Portable ZIP guide](docs/PORTABLE_ZIP.md) | Checksum, extraction, updates, and removal |
| [Bug-report diagnostics](docs/BUG_REPORTING.md) | Reproducible sanitized bug reports |
| [v1.4.0 release notes](docs/releases/v1.4.0.md) | User-visible release summary |
| [Roadmap](docs/XCC_ROADMAP_v1.4.0_UPDATED.md) | Release status and next steps |
| [Contributing](CONTRIBUTING.md) | Development rules |
| [Security](SECURITY.md) | Security model and reporting |

---

## Author

**End1essspace | RX**  
Telegram: [@End1essspace](https://t.me/End1essspace)  
GitHub: [End1essspace](https://github.com/End1essspace)

## License

XCC Context Collector is licensed under the [GNU General Public License v3.0](LICENSE).

Copyright (C) 2026 Rafael Xudoynazarov (End1essspace | RX)
