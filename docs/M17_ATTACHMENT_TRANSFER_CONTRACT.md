# M17 Attachment Transfer Contract

Status: v1.4.0 release contract — implemented baseline for original-file transfer, automated Attachment Handoff, ZIP fallback, lifecycle and safety

## Product boundary

`Collect` and `Attachments` are separate workflows.

- `Collect` reads supported source-like files and produces text context.
- `Attachments` transfers explicitly selected original filesystem files without converting, compacting, normalizing, or rewriting their contents.
- Attachment selection does not use the Collect extension allowlist.
- XCC prepares clipboard file objects; the receiving application decides whether it accepts them.

## M17.0 clipboard contract

The preferred implementation uses `QMimeData` + local `QUrl` values on the Qt GUI thread.

Before publishing the clipboard payload XCC revalidates the complete selection. It rejects an empty selection, missing paths, directories, and inaccessible/non-regular files. File contents are not loaded into XCC memory.

A native `CF_HDROP` backend is intentionally not introduced without Windows compatibility evidence proving that Qt's native platform mapping is insufficient.

### Manual Windows compatibility gate

Validate the packaged build on Windows 10 and Windows 11 against:

1. Windows Explorer: `Copy Files`, then paste into a normal folder.
2. A representative browser file-attachment surface where clipboard file paste is supported.
3. At least one supported desktop AI client where practical.
4. Multiple files in a known order.
5. A stale/deleted file immediately before copy.

Record which targets accept multi-file clipboard objects. A target rejecting one multi-file paste is not an XCC source-fidelity failure; Attachment Handoff or ZIP is the compatibility fallback.

## M17.1 selection contract

Path list input remains data-only and reuses `path_list_parser`.

Relative paths require an explicit project root. Relative traversal outside that root is rejected. Absolute external files are valid. Direct file-picker selection accepts any existing regular file regardless of extension. Windows-style path de-duplication preserves first-seen order. Selection metadata contains file count and aggregate byte size without reading file bodies.

The UI reports `Mixed locations` when the current attachment set cannot be represented as one project-root-contained selection.

## M17.2 page contract

Navigation order:

```text
Collect
Attachments
History
Settings
About
```

Attachments uses the existing XCC shell but a distinct handoff composition:

```text
Attachments
  Source
  Selection | Transfer
```

On narrower logical viewports the Transfer surface moves below Selection. Horizontal page scrolling remains disabled. `Ctrl+V` is page-local and must not steal ordinary paste from editable text controls.

## M17.3 Copy Original Files

`Copy Files` publishes references to existing local files as file-system clipboard objects. It does not upload files to an AI service.

Implementation rules:

- the complete selection is revalidated immediately before publication;
- multiple files preserve selection order;
- source bytes are not loaded into XCC memory;
- stale, missing, inaccessible, and non-regular files fail explicitly;
- the operation is initiated only by an explicit Attachments action and never replaces a successful Collect text clipboard implicitly;
- the GUI shows a clear copied/failed state;
- Runtime History receives metadata only: transfer type, outcome, file count, aggregate bytes, duration, warning count, and optional generated bundle filename;
- raw attachment contents and absolute source paths are not written to history.

## M17.3A Automated Attachment Handoff

`Send One-by-One` is a compatibility workflow for web/AI targets that accept one file per paste event even when Windows can represent the complete selection on the clipboard.

Unlike `Copy Files`, this mode intentionally automates the repetitive paste gesture. XCC snapshots the ordered selection, publishes exactly one file at a time through the existing Qt/Windows file clipboard backend, and emits one synthetic `Ctrl+V` for each file into one user-chosen foreground window. It does not automate a browser DOM, call a provider API, click upload controls, or submit the chat/message.

### Start modes

- **Attachments button:** `Send One-by-One` arms a 3-second countdown. The user switches to the destination application before the countdown reaches zero. XCC captures that foreground HWND and locks the sequence to it.
- **Optional global hotkey:** when enabled, the Attachment Handoff hotkey captures the application that is already foreground and starts the sequence after a short modifier-release delay. Pressing the same hotkey while a handoff is active cancels it.

Implementation rules:

- snapshot the current ordered attachment selection when the handoff starts;
- lock attachment selection/root mutation until the sequence completes, fails, or is cancelled;
- publish exactly one file per step through the same Qt/Windows file-object backend used by `Copy Files`;
- revalidate each file immediately before its clipboard publication;
- preserve selection order exactly;
- wait briefly for the clipboard to settle, then send exactly one synthetic `Ctrl+V`;
- use Win32 `SendInput` only; never force focus with `SetForegroundWindow`;
- capture one target HWND and verify that it remains the foreground window before every clipboard/paste step;
- if focus changes, stop before sending input to the newly focused window;
- never synthesize Enter, click Send, submit a message, or interact with provider/browser DOM APIs;
- stop immediately if a later file becomes missing, inaccessible, or non-regular;
- cancellation/failure does not clear the last successfully prepared clipboard item;
- record one metadata-only Runtime History event for the overall sequence outcome;
- never store attachment bodies, absolute attachment source paths, target window titles, or target process metadata in history.

The success boundary is **paste-action dispatch**, not third-party upload completion. `N/N sent` means XCC successfully prepared each selected file and dispatched one `Ctrl+V` to the same foreground target in order. The receiving application still decides whether each attachment is accepted, uploaded, rejected, or retained.

Development validation on 2026-09-22 demonstrated the motivating case: the tested ChatGPT Web composer accepted multiple image attachments when the same files were pasted in separate paste actions, while one multi-file paste attached only one image. This observation is target/version-specific evidence, not a permanent ChatGPT product guarantee.

## M17.4 ZIP Bundle Engine

`Create ZIP & Copy` creates one standard ZIP archive with ZIP64 enabled and publishes the completed ZIP only after successful creation.

Implementation rules:

- streaming 1 MiB chunks; no whole-bundle RAM load;
- progress reports both file count and bytes;
- cooperative cancellation;
- partial archives use a private `.partial` filename and are removed on cancellation/failure;
- source files are revalidated before use and checked again after streaming;
- size/mtime changes during bundling fail the operation;
- project-contained selections preserve project-relative structure;
- mixed selections use deterministic `location-NN/` namespaces instead of absolute local paths;
- archive members are sanitized and may not be absolute or contain `..` traversal;
- case-insensitive archive-name collisions receive deterministic numeric suffixes;
- source files are never moved, deleted, normalized, or rewritten;
- only the successfully completed ZIP is sent to the clipboard.

Bundle naming uses:

```text
XCC-Attachments-YYYYMMDD-HHMMSS.zip
```

with deterministic numeric collision suffixes when required.

## M17.5 Bundle lifecycle, safety and scale

Managed bundle directory:

```text
%USERPROFILE%\.xcc\attachment-bundles\
```

Retention policy: **7 days**. Cleanup only targets XCC-managed `XCC-Attachments-*.zip` files older than the retention threshold. The current/active bundle is excluded. Cleanup failures are non-destructive and surfaced when relevant.

The Transfer surface exposes `Open bundle location`. Closing XCC does not delete a successfully created bundle, so an existing clipboard file reference remains valid.

Safety rules:

- attachment safety warnings are filename/path based only;
- binary/original attachment contents are not silently scanned;
- relative root escape remains rejected;
- direct transfer never recursively expands directories;
- symlink paths resolve to a regular target file and remain subject to normal root/regular-file validation;
- generated ZIPs contain only selected source files and no XCC telemetry, credentials, manifests, or hidden metadata payloads;
- Runtime History stores attachment metadata only and avoids absolute source paths.

Scale wording:

> No XCC-imposed file-count limit.

Practical limits still come from Windows/filesystem behavior, disk space, ZIP tooling, and the target application's own upload/attachment limits.
