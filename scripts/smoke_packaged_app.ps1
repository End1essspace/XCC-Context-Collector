param(
    [string]$ExecutablePath = "dist\XCC Context Collector\XCC Context Collector.exe",
    [int]$StartupSeconds = 6
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ResolvedExecutable = (Resolve-Path $ExecutablePath).Path
$DistRoot = Split-Path -Parent $ResolvedExecutable
$CandidateAssetRoots = @(
    (Join-Path $DistRoot "_internal\assets"),
    (Join-Path $DistRoot "assets")
)
$AssetRoot = $CandidateAssetRoots | Where-Object { Test-Path $_ } | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($AssetRoot)) {
    throw "Packaged assets directory was not found beside the executable."
}

$RequiredAssets = @(
    "xcc_app.ico",
    "xcc_app.png",
    "xcc_tray.ico",
    "xcc_tray.png",
    "x-series.png",
    "nav-collect.svg",
    "nav-history.svg",
    "nav-settings.svg",
    "nav-about.svg",
    "ui-setup.svg",
    "ui-last-run.svg",
    "ui-volume.svg",
    "ui-output.svg",
    "ui-coverage.svg",
    "ui-health.svg",
    "ui-paste-paths.svg",
    "ui-collect-copy.svg",
    "window-minimize.svg",
    "window-maximize.svg",
    "window-restore.svg",
    "window-close.svg"
)
$MissingAssets = @(
    $RequiredAssets | Where-Object { -not (Test-Path (Join-Path $AssetRoot $_)) }
)
if ($MissingAssets.Count -gt 0) {
    throw "Packaged UI assets are missing: $($MissingAssets -join ', ')"
}

$Process = $null
$PreviousQtPlatform = $env:QT_QPA_PLATFORM

try {
    # Offscreen mode avoids depending on an interactive desktop in CI while
    # still exercising Python, Qt plugin, assets, settings, and window startup.
    $env:QT_QPA_PLATFORM = "offscreen"
    $Process = Start-Process -FilePath $ResolvedExecutable -PassThru

    Start-Sleep -Seconds $StartupSeconds
    $Process.Refresh()

    if ($Process.HasExited) {
        throw "Packaged executable exited during startup smoke test with code $($Process.ExitCode)."
    }

    Write-Host "Packaged UI assets found: $AssetRoot" -ForegroundColor Green
    Write-Host "Packaged executable startup smoke test passed." -ForegroundColor Green
}
finally {
    if ($null -ne $Process) {
        try {
            $Process.Refresh()
            if (-not $Process.HasExited) {
                Stop-Process -Id $Process.Id -Force
                Wait-Process -Id $Process.Id -ErrorAction SilentlyContinue
            }
        }
        catch {
            Write-Warning "Could not clean up smoke-test process: $($_.Exception.Message)"
        }
    }

    if ($null -eq $PreviousQtPlatform) {
        Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
    }
    else {
        $env:QT_QPA_PLATFORM = $PreviousQtPlatform
    }
}
