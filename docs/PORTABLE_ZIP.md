# Portable ZIP Usage

XCC is distributed as a Windows x64 portable ZIP. No installer or Python runtime is required.

## Download

Official v1.3.1 files:

```text
XCC-Context-Collector-v1.3.1-win64.zip
XCC-Context-Collector-v1.3.1-win64.zip.sha256
```

Download only from the official GitHub Release.

## Verify SHA-256

Place both files together and run:

```powershell
$Zip="XCC-Context-Collector-v1.3.1-win64.zip"; $Expected=((Get-Content "$Zip.sha256" -Raw).Trim() -split "\s+")[0]; $Actual=(Get-FileHash $Zip -Algorithm SHA256).Hash.ToLowerInvariant(); if ($Actual -ne $Expected.ToLowerInvariant()) { throw "Checksum mismatch" }; "Checksum verified: $Actual"
```

Do not use an archive with a mismatched checksum.

## Extract and run

Extract the complete directory and start `XCC Context Collector.exe`.

```text
XCC Context Collector/
├── XCC Context Collector.exe
├── VERSION.txt
└── _internal/
```

Do not run the executable from inside the ZIP or move it away from `_internal` and `VERSION.txt`. `VERSION.txt` must contain `1.3.1`.

## Windows reputation warning

The binaries are not code-signed. Before proceeding through a SmartScreen/reputation warning, confirm the official download source, verify SHA-256, and confirm `VERSION.txt` matches the release tag.

## Settings boundary

The app directory is portable; settings are user-local:

```text
%USERPROFILE%\.xcc\config.json
```

This includes behavior settings and **Interface scale**. An explicit Interface scale is applied at process startup, so restart XCC after changing it.

Runtime History is in-memory and clears when XCC exits.

## Update

1. Quit XCC from the tray.
2. Download and verify the new ZIP/checksum.
3. Extract to a new folder.
4. Launch the new build and confirm About/`VERSION.txt`.
5. Delete the old extracted folder after validation.

Compatible saved settings are reused automatically.

## Remove

1. Quit XCC from the tray.
2. Delete the extracted application folder.
3. Optionally delete `%USERPROFILE%\.xcc`.
4. If Start with Windows was enabled, disable it first or remove the XCC shortcut from `shell:startup`.

## Troubleshooting

**Window disappeared:** check the notification-area overflow; XCC may be hidden to tray.  
**Second launch opens no second window:** XCC is single-instance and restores the existing process.  
**`Ctrl+Alt+X` unavailable:** another app may own the hotkey; XCC treats that as non-fatal.  
**Scale looks wrong:** set Settings → Interface scale to `Auto`, fully Quit from tray, and restart before reporting a DPI issue.
