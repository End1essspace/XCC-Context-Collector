param(
    [string]$PythonExecutable = "python"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$VersionInfoPath = Join-Path $env:TEMP "xcc-version-info-$PID.txt"
$SpecPath = Join-Path $ProjectRoot "XCC Context Collector.spec"

function Remove-DirectoryWithRetry([string]$Path) {
    if (-not (Test-Path $Path)) {
        return
    }

    for ($Attempt = 1; $Attempt -le 3; $Attempt++) {
        try {
            Remove-Item $Path -Recurse -Force -ErrorAction Stop
            return
        }
        catch {
            if ($Attempt -eq 3) {
                throw "Could not clean $Path. Close every packaged XCC process, including tray instances, and retry. $($_.Exception.Message)"
            }
            Start-Sleep -Milliseconds 500
        }
    }
}

$RunningPackagedProcess = @(Get-Process -Name "XCC Context Collector" -ErrorAction SilentlyContinue)
if ($RunningPackagedProcess.Count -gt 0) {
    throw "A packaged XCC process is running. Use the tray menu to Quit XCC before building."
}

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

    Remove-DirectoryWithRetry "build"
    Remove-DirectoryWithRetry "dist"

    if (Test-Path $SpecPath) {
        Remove-Item $SpecPath -Force
    }

    & $PythonExecutable -m PyInstaller `
        --clean `
        --noconsole `
        --name "XCC Context Collector" `
        --paths "src" `
        --icon "assets\xcc_app.ico" `
        --add-data "assets\xcc_app.ico;assets" `
        --add-data "assets\xcc_app.png;assets" `
        --add-data "assets\xcc_tray.ico;assets" `
        --add-data "assets\xcc_tray.png;assets" `
        --add-data "assets\x-series.png;assets" `
        --add-data "assets\nav-collect.svg;assets" `
        --add-data "assets\nav-history.svg;assets" `
        --add-data "assets\nav-settings.svg;assets" `
        --add-data "assets\nav-about.svg;assets" `
        --add-data "assets\ui-setup.svg;assets" `
        --add-data "assets\ui-last-run.svg;assets" `
        --add-data "assets\ui-volume.svg;assets" `
        --add-data "assets\ui-output.svg;assets" `
        --add-data "assets\ui-coverage.svg;assets" `
        --add-data "assets\ui-health.svg;assets" `
        --add-data "assets\ui-paste-paths.svg;assets" `
        --add-data "assets\ui-collect-copy.svg;assets" `
        --add-data "assets\window-minimize.svg;assets" `
        --add-data "assets\window-maximize.svg;assets" `
        --add-data "assets\window-restore.svg;assets" `
        --add-data "assets\window-close.svg;assets" `
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

    Remove-DirectoryWithRetry "build"

    Write-Host "Build complete." -ForegroundColor Green
    Write-Host "Version: $AppVersion" -ForegroundColor Green
    Write-Host "Output: $DistRoot\XCC Context Collector.exe" -ForegroundColor Green
}
finally {
    if (Test-Path $VersionInfoPath) {
        Remove-Item $VersionInfoPath -Force
    }

    if (Test-Path $SpecPath) {
        Remove-Item $SpecPath -Force
    }
}
