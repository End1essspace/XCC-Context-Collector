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
    selected_files_paste_paths_visibility = (Read-GateResult "Paste Paths is visible only in Selected Files mode")
    selected_files_ctrl_v_guard = (Read-GateResult "Guarded Ctrl+V imports paths without intercepting editable fields")
    selected_files_parser_formats = (Read-GateResult "Plain, Markdown, quoted, backtick, and fenced path lists pass")
    selected_files_root_boundary = (Read-GateResult "Relative root resolution, absolute paths, and outside-root blocking pass")
    selected_files_issue_reporting = (Read-GateResult "Duplicate, missing, directory, unsupported, invalid, and external reporting passes")
    selected_files_stale_root_recovery = (Read-GateResult "Stale remembered project root recovery passes")
    selected_files_mixed_locations = (Read-GateResult "Separate repositories display Mixed locations")
    selected_files_review_transactionality = (Read-GateResult "Selected Files Review remove, Delete, Clear, Cancel, and Apply pass")
    selected_files_relative_output = (Read-GateResult "Collected output uses the expected stable relative file headers")
    responsive_minimum_window = (Read-GateResult "920x620 minimum window remains usable with no horizontal page scrolling")
    responsive_full_hd_baseline = (Read-GateResult "Full HD baseline composition passes")
    responsive_qhd_scaling = (Read-GateResult "QHD Windows scaling cases available on this host pass")
    interface_scale_persistence_restart = (Read-GateResult "Interface scale persists and applies after a full restart")
    settings_history_about_responsive = (Read-GateResult "Settings, History, and About responsive layouts pass")
    responsive_dialogs = (Read-GateResult "Paste Paths and Selected Files Review fit the work area")
    work_area_restore = (Read-GateResult "Maximize/restore, minimize/restore, and tray/hotkey restore stay inside the work area")
    dpi_asset_rerender = (Read-GateResult "Raster/SVG branding and window controls remain sharp after DPI/screen changes")
    footer_x_series_brand = (Read-GateResult "X-SERIES footer wordmark renders correctly and remains non-intrusive")
    full_folder_mode = (Read-GateResult "Full Folder mode passes")
    git_changed_files_mode = (Read-GateResult "Git Changed Files mode passes")
    project_tree_mode = (Read-GateResult "Project Tree mode passes")
    safety_confirmation_setting = (Read-GateResult "Safety confirmation can be disabled and remains disabled after restart")
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
