[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$IncludeArtifacts,
    [switch]$IncludeLegacyReleaseArchives,
    [switch]$IncludeVirtualEnvironment
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$RemovedPaths = [System.Collections.Generic.List[string]]::new()

function Get-WorkspaceRelativePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FullPath
    )

    # Windows PowerShell 5.1 runs on .NET Framework, where
    # [System.IO.Path]::GetRelativePath() is unavailable. All cleanup targets
    # discovered here are descendants of $ProjectRoot, so a normalized,
    # case-insensitive prefix check gives a compatible relative path.
    $DirectorySeparator = [System.IO.Path]::DirectorySeparatorChar
    $AltDirectorySeparator = [System.IO.Path]::AltDirectorySeparatorChar
    $RootFullPath = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd(
        $DirectorySeparator,
        $AltDirectorySeparator
    )
    $CandidateFullPath = [System.IO.Path]::GetFullPath($FullPath)
    $RootPrefix = $RootFullPath + $DirectorySeparator

    if (-not $CandidateFullPath.StartsWith(
        $RootPrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Cleanup target is outside the project root: $CandidateFullPath"
    }

    return $CandidateFullPath.Substring($RootPrefix.Length)
}

function Remove-WorkspacePath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RelativePath
    )

    $FullPath = Join-Path $ProjectRoot $RelativePath
    if (-not (Test-Path -LiteralPath $FullPath)) {
        return
    }

    if ($DryRun) {
        Write-Host "[dry-run] remove $RelativePath" -ForegroundColor DarkGray
        return
    }

    Remove-Item -LiteralPath $FullPath -Recurse -Force -ErrorAction Stop
    $RemovedPaths.Add($RelativePath)
    Write-Host "Removed $RelativePath" -ForegroundColor DarkGray
}

$RunningPackagedProcess = @(
    Get-Process -Name "XCC Context Collector" -ErrorAction SilentlyContinue
)
if ($RunningPackagedProcess.Count -gt 0) {
    throw "A packaged XCC process is running. Quit it from the tray before cleaning the workspace."
}

Write-Host "Cleaning generated XCC workspace files..." -ForegroundColor Yellow

$GeneratedPaths = @(
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".nox",
    ".eggs",
    ".coverage",
    "coverage.xml",
    "htmlcov",
    "pip-wheel-metadata",
    "wheelhouse",
    "build",
    "dist",
    "XCC Context Collector.spec",
    "src\xcc_context_collector.egg-info",
    "xcc_context_collector.egg-info"
)

foreach ($RelativePath in $GeneratedPaths) {
    Remove-WorkspacePath $RelativePath
}

foreach ($SearchRoot in @("src", "tests", "scripts")) {
    $RootPath = Join-Path $ProjectRoot $SearchRoot
    if (-not (Test-Path -LiteralPath $RootPath)) {
        continue
    }

    $CacheDirectories = @(
        Get-ChildItem `
            -LiteralPath $RootPath `
            -Directory `
            -Recurse `
            -Force `
            -Filter "__pycache__" `
            -ErrorAction SilentlyContinue |
        Sort-Object { $_.FullName.Length } -Descending
    )

    foreach ($Directory in $CacheDirectories) {
        $RelativePath = Get-WorkspaceRelativePath $Directory.FullName
        Remove-WorkspacePath $RelativePath
    }
}

$RootWheelFiles = @(
    Get-ChildItem `
        -LiteralPath $ProjectRoot `
        -File `
        -Force `
        -Filter "*.whl" `
        -ErrorAction SilentlyContinue
)
foreach ($WheelFile in $RootWheelFiles) {
    Remove-WorkspacePath $WheelFile.Name
}

if ($IncludeArtifacts) {
    Remove-WorkspacePath "artifacts"
}
else {
    Write-Host "Preserved artifacts\ (current release-candidate outputs)." -ForegroundColor Cyan
}

if ($IncludeLegacyReleaseArchives) {
    Remove-WorkspacePath "release"
}
else {
    Write-Host "Preserved release\ (legacy local archives)." -ForegroundColor Cyan
}

if ($IncludeVirtualEnvironment) {
    Remove-WorkspacePath ".venv"
    Remove-WorkspacePath "venv"
}
else {
    Write-Host "Preserved local virtual environments." -ForegroundColor Cyan
}

if ($DryRun) {
    Write-Host "Dry run complete. No files were removed." -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Workspace cleanup complete." -ForegroundColor Green
Write-Host "Removed paths: $($RemovedPaths.Count)" -ForegroundColor Green
