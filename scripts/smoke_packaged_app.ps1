param(
    [string]$ExecutablePath = "dist\XCC Context Collector\XCC Context Collector.exe",
    [int]$StartupSeconds = 6
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$ResolvedExecutable = (Resolve-Path $ExecutablePath).Path
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
