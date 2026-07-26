param(
    [string]$PythonExecutable = "python",
    [string]$DistRoot = "dist\XCC Context Collector",
    [string]$OutputDirectory = "artifacts"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$AppVersion = (& $PythonExecutable -c "import sys; sys.path.insert(0, 'src'); from xcc import __version__; print(__version__)").Trim()
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($AppVersion)) {
    throw "Could not read the canonical XCC version."
}

$ResolvedDistRoot = (Resolve-Path $DistRoot).Path
$ExecutablePath = Join-Path $ResolvedDistRoot "XCC Context Collector.exe"
$VersionPath = Join-Path $ResolvedDistRoot "VERSION.txt"

if (-not (Test-Path $ExecutablePath)) {
    throw "Packaged executable was not found: $ExecutablePath"
}
if (-not (Test-Path $VersionPath)) {
    throw "VERSION.txt was not found: $VersionPath"
}

$PackagedVersion = (Get-Content $VersionPath -Raw).Trim()
if ($PackagedVersion -ne $AppVersion) {
    throw "Packaged version mismatch: expected $AppVersion, found $PackagedVersion"
}

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$OutputDirectory = (Resolve-Path $OutputDirectory).Path

$ArchiveName = "XCC-Context-Collector-v$AppVersion-win64.zip"
$ArchivePath = Join-Path $OutputDirectory $ArchiveName
$ChecksumPath = "$ArchivePath.sha256"

Remove-Item $ArchivePath -Force -ErrorAction SilentlyContinue
Remove-Item $ChecksumPath -Force -ErrorAction SilentlyContinue

Compress-Archive -Path $ResolvedDistRoot -DestinationPath $ArchivePath -CompressionLevel Optimal

$Hash = (Get-FileHash $ArchivePath -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -Path $ChecksumPath -Value "$Hash  $ArchiveName" -Encoding ascii

& $PythonExecutable scripts\validate_release_archive.py `
    --archive $ArchivePath `
    --expected-version $AppVersion `
    --checksum $ChecksumPath

if ($LASTEXITCODE -ne 0) {
    throw "Release archive validation failed."
}

Write-Host "Portable release package created." -ForegroundColor Green
Write-Host "Archive: $ArchivePath" -ForegroundColor Green
Write-Host "SHA-256: $Hash" -ForegroundColor Green
Write-Host "Checksum: $ChecksumPath" -ForegroundColor Green
