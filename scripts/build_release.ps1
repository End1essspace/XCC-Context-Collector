param(
    [string]$PythonExecutable = "python"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$VersionInfoPath = Join-Path $env:TEMP "xcc-version-info-$PID.txt"

try {
    $AppVersion = (& $PythonExecutable -c "import sys; sys.path.insert(0, 'src'); from xcc import __version__; print(__version__)").Trim()
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AppVersion)) {
        throw "Could not read the canonical XCC version."
    }

    Write-Host "Building XCC Context Collector v$AppVersion..." -ForegroundColor Yellow

    & $PythonExecutable "scripts\generate_version_info.py" --output $VersionInfoPath | Out-Null
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $VersionInfoPath)) {
        throw "Could not generate Windows version metadata."
    }

    Write-Host "Cleaning previous build artifacts..." -ForegroundColor Yellow

    if (Test-Path "build") {
        Remove-Item "build" -Recurse -Force
    }

    if (Test-Path "dist") {
        Remove-Item "dist" -Recurse -Force
    }

    if (Test-Path "XCC Context Collector.spec") {
        Remove-Item "XCC Context Collector.spec" -Force
    }

    & $PythonExecutable -m PyInstaller `
        --clean `
        --noconsole `
        --name "XCC Context Collector" `
        --paths "src" `
        --icon "assets\xcc_app.ico" `
        --add-data "assets;assets" `
        --version-file $VersionInfoPath `
        --exclude-module PyQt5 `
        --exclude-module PyQt6 `
        --exclude-module PySide2 `
        --exclude-module PySide6.QtQml `
        --exclude-module PySide6.QtQuick `
        gui.py

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed."
    }

    $DistRoot = "dist\XCC Context Collector"
    Set-Content -Path (Join-Path $DistRoot "VERSION.txt") -Value $AppVersion -Encoding ascii

    Write-Host "Build complete." -ForegroundColor Green
    Write-Host "Version: $AppVersion" -ForegroundColor Green
    Write-Host "Output: $DistRoot\XCC Context Collector.exe" -ForegroundColor Green
}
finally {
    if (Test-Path $VersionInfoPath) {
        Remove-Item $VersionInfoPath -Force
    }
}
