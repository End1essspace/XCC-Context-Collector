# Portable ZIP Usage

XCC is distributed as a Windows x64 portable ZIP. It does not require an installer or a Python installation.

## Release files

For v1.2.0, download both files from the official GitHub Release:

```text
XCC-Context-Collector-v1.2.0-win64.zip
XCC-Context-Collector-v1.2.0-win64.zip.sha256
```

Do not download executables or repackaged archives from third-party mirrors.

## Verify SHA-256

Place the ZIP and checksum file in the same folder, then run:

```powershell
$Zip = "XCC-Context-Collector-v1.2.0-win64.zip"
$Expected = ((Get-Content "$Zip.sha256" -Raw).Trim() -split "\s+")[0]
$Actual = (Get-FileHash $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Actual -ne $Expected.ToLowerInvariant()) { throw "Checksum mismatch" }
"Checksum verified: $Actual"
```

A checksum mismatch means the archive must not be used.

## Extract and run

1. Extract the complete ZIP to a writable folder.
2. Keep the entire `XCC Context Collector` directory together.
3. Start `XCC Context Collector.exe`.
4. Do not run the executable directly from inside the ZIP.
5. Do not move the executable away from `_internal` and `VERSION.txt`.

Expected structure:

```text
XCC Context Collector/
├── XCC Context Collector.exe
├── VERSION.txt
└── _internal/
```

`VERSION.txt` must contain `1.2.0` for the v1.2.0 package.

## Windows reputation warning

v1.2.0 binaries are not code-signed. Windows may therefore display a reputation or SmartScreen warning even when the archive is unchanged.

Before proceeding:

- confirm the download came from the official repository;
- verify the SHA-256 checksum;
- confirm `VERSION.txt` matches the release tag.

Do not bypass a warning for an archive with an unknown origin or mismatched checksum.

## Settings and portability boundary

The application is portable in the distribution sense: no installer is required and the extracted application directory can be moved as a unit.

Settings are not stored beside the executable. They remain under:

```text
%USERPROFILE%\.xcc\config.json
```

Runtime history is in-memory and is cleared when XCC exits. A fully self-contained settings mode is outside the v1.2.0 scope.

## Update XCC

1. Quit XCC from the tray.
2. Download and verify the new versioned ZIP and checksum.
3. Extract it into a new folder instead of overwriting files while XCC is running.
4. Start the new executable and verify the About-page version.
5. Delete the old extracted folder after confirming the new build works.

Existing `%USERPROFILE%\.xcc\config.json` settings are reused when compatible.

## Remove XCC

1. Quit XCC from the tray.
2. Delete the extracted `XCC Context Collector` folder.
3. Optionally delete `%USERPROFILE%\.xcc` to remove saved settings.
4. If **Start with Windows** was enabled, disable it before removal or delete the XCC shortcut from `shell:startup`.

## Troubleshooting

### The application appears to remain open

XCC may be hidden in the Windows notification area. Open the tray overflow menu and use **Quit** from the XCC tray menu.

### A second launch does not open another window

XCC is single-instance. The second launch asks the existing instance to restore.

### `Ctrl+Alt+X` does not restore the window

Another application may own the hotkey. XCC treats this as non-fatal and displays the hotkey state in Settings.

### The tray icon is not visible

Check the Windows notification-area overflow menu. If no XCC entry exists, restart the packaged application and report the issue using `docs/BUG_REPORTING.md`.
