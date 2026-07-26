# Portable ZIP Usage

XCC is distributed as a Windows x64 portable ZIP. It does not require an installer.

## Verify the download

Each official archive has a matching `.sha256` file.

```powershell
$Zip = "XCC-Context-Collector-v1.2.0-win64.zip"
$Expected = ((Get-Content "$Zip.sha256" -Raw).Trim() -split "\s+")[0]
$Actual = (Get-FileHash $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Actual -ne $Expected.ToLowerInvariant()) { throw "Checksum mismatch" }
"Checksum verified: $Actual"
```

## Run XCC

1. Extract the complete ZIP to a writable folder.
2. Keep the entire `XCC Context Collector` directory together.
3. Start `XCC Context Collector.exe`.
4. Do not run the executable directly from inside the ZIP.
5. `VERSION.txt` identifies the packaged version.

The package is portable in the distribution sense, but application settings remain under:

```text
%USERPROFILE%\.xcc\config.json
```

A self-contained settings mode is outside the v1.2.0 scope.

## Remove XCC

Quit XCC from the tray, delete the extracted folder, and optionally remove `%USERPROFILE%\.xcc` if saved settings are no longer needed.
