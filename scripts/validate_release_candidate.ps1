param(
    [string]$PythonExecutable = "python",
    [string]$ExpectedVersion = "1.3.0",
    [string]$OutputDirectory = "artifacts",
    [switch]$SkipCleanInstall
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$AppVersion = (& $PythonExecutable -c "import sys; sys.path.insert(0, 'src'); from xcc import __version__; print(__version__)").Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AppVersion)) {
    throw "Could not read the canonical XCC version."
}
if ($AppVersion -ne $ExpectedVersion) {
    throw "Release candidate version mismatch: expected $ExpectedVersion, found $AppVersion"
}

$RunningPackagedProcess = @(Get-Process -Name "XCC Context Collector" -ErrorAction SilentlyContinue)
if ($RunningPackagedProcess.Count -gt 0) {
    throw "A packaged XCC process is running. Use the tray menu to Quit XCC before the release gate."
}

Write-Host "Running XCC v$AppVersion release-candidate gate..." -ForegroundColor Yellow

& $PythonExecutable -m compileall -q src tests scripts gui.py run.py hotkey.py
if ($LASTEXITCODE -ne 0) { throw "Compileall failed." }

& $PythonExecutable scripts\check_version_consistency.py
if ($LASTEXITCODE -ne 0) { throw "Version consistency failed." }

& $PythonExecutable -m pytest -q tests\test_path_list_parser.py tests\test_selected_files_importer.py tests\test_selected_files_review.py tests\test_selected_files_workflow.py
if ($LASTEXITCODE -ne 0) { throw "Selected Files regression tests failed." }

& $PythonExecutable -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Tests failed." }

if (-not $SkipCleanInstall) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File scripts\validate_clean_install.ps1
    if ($LASTEXITCODE -ne 0) { throw "Clean-install validation failed." }
}

& powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -PythonExecutable $PythonExecutable
if ($LASTEXITCODE -ne 0) { throw "Build failed." }

& powershell -NoProfile -ExecutionPolicy Bypass -File scripts\smoke_packaged_app.ps1
if ($LASTEXITCODE -ne 0) { throw "Packaged startup smoke failed." }

& powershell -NoProfile -ExecutionPolicy Bypass -File scripts\package_release.ps1 -PythonExecutable $PythonExecutable -OutputDirectory $OutputDirectory
if ($LASTEXITCODE -ne 0) { throw "Release packaging failed." }

$ResolvedOutputDirectory = (Resolve-Path $OutputDirectory).Path
$ArchiveName = "XCC-Context-Collector-v$AppVersion-win64.zip"
$ArchivePath = Join-Path $ResolvedOutputDirectory $ArchiveName
$ChecksumPath = "$ArchivePath.sha256"

& $PythonExecutable scripts\validate_release_archive.py --archive $ArchivePath --expected-version $AppVersion --checksum $ChecksumPath
if ($LASTEXITCODE -ne 0) { throw "Final archive validation failed." }

$ArchiveHash = (Get-FileHash $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
$PythonVersion = (& $PythonExecutable --version 2>&1).ToString().Trim()
$OsInfo = Get-CimInstance Win32_OperatingSystem
$ComputerInfo = Get-CimInstance Win32_ComputerSystem
$ReportPath = Join-Path $ResolvedOutputDirectory "XCC-v$AppVersion-automated-gate.json"

$Report = [ordered]@{
    schema_version = 1
    xcc_version = $AppVersion
    passed = $true
    completed_at_utc = [DateTime]::UtcNow.ToString("o")
    python = $PythonVersion
    os = [ordered]@{
        product_name = $OsInfo.Caption
        version = $OsInfo.Version
        build = $OsInfo.BuildNumber
        architecture = $OsInfo.OSArchitecture
        computer_name = $ComputerInfo.Name
    }
    archive = [ordered]@{
        filename = $ArchiveName
        sha256 = $ArchiveHash
        checksum_filename = (Split-Path $ChecksumPath -Leaf)
    }
    gates = [ordered]@{
        compileall = $true
        version_consistency = $true
        selected_files_regression = $true
        pytest = $true
        clean_install = (-not $SkipCleanInstall)
        pyinstaller_build = $true
        packaged_startup_smoke = $true
        archive_validation = $true
        checksum_validation = $true
    }
}

$Report | ConvertTo-Json -Depth 6 | Set-Content -Path $ReportPath -Encoding utf8

Write-Host "Release-candidate automated gate passed." -ForegroundColor Green
Write-Host "Version: $AppVersion" -ForegroundColor Green
Write-Host "Archive: $ArchivePath" -ForegroundColor Green
Write-Host "SHA-256: $ArchiveHash" -ForegroundColor Green
Write-Host "Report: $ReportPath" -ForegroundColor Green
