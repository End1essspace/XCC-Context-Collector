param(
    [string]$PythonExecutable = "python",
    [string]$ArchivePath = "",
    [string]$OutputDirectory = "artifacts\manual-validation"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$AppVersion = (& $PythonExecutable -c "import sys; sys.path.insert(0, 'src'); from xcc import __version__; print(__version__)").Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AppVersion)) {
    throw "Could not read the canonical XCC version."
}

if ([string]::IsNullOrWhiteSpace($ArchivePath)) {
    $ArchivePath = "artifacts\XCC-Context-Collector-v$AppVersion-win64.zip"
}
$ResolvedArchive = (Resolve-Path $ArchivePath).Path
$ArchiveHash = (Get-FileHash $ResolvedArchive -Algorithm SHA256).Hash.ToLowerInvariant()

$OsInfo = Get-CimInstance Win32_OperatingSystem
$ComputerInfo = Get-CimInstance Win32_ComputerSystem
$BuildNumber = [int]$OsInfo.BuildNumber
$ReleaseLabel = if ($BuildNumber -ge 22000) { "Windows 11" } else { "Windows 10" }

function Read-GateResult([string]$Label) {
    $Answer = Read-Host "$Label [y/N]"
    return $Answer.Trim().ToLowerInvariant() -in @("y", "yes")
}

$Operator = Read-Host "Operator name or alias [$env:USERNAME]"
if ([string]::IsNullOrWhiteSpace($Operator)) {
    $Operator = $env:USERNAME
}

Write-Host "Record results for packaged XCC v$AppVersion on $ReleaseLabel." -ForegroundColor Yellow

$Gates = [ordered]@{
    packaged_startup = (Read-GateResult "Packaged application starts cleanly")
    application_icons = (Read-GateResult "Window, header, About, taskbar, and tray icons render correctly")
    selected_files_mode = (Read-GateResult "Selected Files mode passes")
    full_folder_mode = (Read-GateResult "Full Folder mode passes")
    git_changed_files_mode = (Read-GateResult "Git Changed Files mode passes")
    project_tree_mode = (Read-GateResult "Project Tree mode passes")
    large_project_responsiveness = (Read-GateResult "Large-project GUI remains responsive")
    cooperative_cancellation = (Read-GateResult "Cooperative cancellation passes")
    second_job_prevented = (Read-GateResult "Second concurrent collection is prevented")
    clipboard_unchanged_after_cancel = (Read-GateResult "Cancellation leaves clipboard unchanged")
    tray_restore = (Read-GateResult "Tray restore passes")
    tray_quit = (Read-GateResult "Tray Quit passes")
    native_hotkey_restore = (Read-GateResult "Ctrl+Alt+X restore passes")
    hotkey_conflict_non_fatal = (Read-GateResult "Hotkey conflict remains non-fatal")
    autostart_shortcut = (Read-GateResult "Autostart shortcut creation/removal passes")
    invalid_config_recovery = (Read-GateResult "Invalid-config recovery passes")
    single_instance_restore = (Read-GateResult "Second launch restores existing instance")
}

$Notes = Read-Host "Optional notes"
$AllPassed = -not ($Gates.Values -contains $false)

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$ResolvedOutputDirectory = (Resolve-Path $OutputDirectory).Path
$Timestamp = [DateTime]::UtcNow.ToString("yyyyMMdd-HHmmss")
$SafeRelease = $ReleaseLabel.Replace(" ", "-")
$EvidencePath = Join-Path $ResolvedOutputDirectory "XCC-v$AppVersion-$SafeRelease-$Timestamp.json"

$Evidence = [ordered]@{
    schema_version = 1
    xcc_version = $AppVersion
    archive_sha256 = $ArchiveHash
    recorded_at_utc = [DateTime]::UtcNow.ToString("o")
    operator = $Operator
    os = [ordered]@{
        release = $ReleaseLabel
        product_name = $OsInfo.Caption
        version = $OsInfo.Version
        build = $OsInfo.BuildNumber
        architecture = $OsInfo.OSArchitecture
        computer_name = $ComputerInfo.Name
    }
    gates = $Gates
    all_passed = $AllPassed
    notes = $Notes
}

$Evidence | ConvertTo-Json -Depth 6 | Set-Content -Path $EvidencePath -Encoding utf8

if (-not $AllPassed) {
    Write-Warning "Manual validation record contains failed or unconfirmed gates."
}
Write-Host "Manual validation evidence written: $EvidencePath" -ForegroundColor Green
Write-Host "Archive SHA-256: $ArchiveHash" -ForegroundColor Green
