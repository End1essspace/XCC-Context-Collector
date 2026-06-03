$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

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

Write-Host "Building XCC Context Collector..." -ForegroundColor Yellow

pyinstaller `
    --clean `
    --noconsole `
    --name "XCC Context Collector" `
    --icon "assets\xcc_app.ico" `
    --add-data "assets;assets" `
    --exclude-module PyQt5 `
    --exclude-module PyQt6 `
    --exclude-module PySide2 `
    --exclude-module PySide6.QtQml `
    --exclude-module PySide6.QtQuick `
    gui.py

Write-Host "Build complete." -ForegroundColor Green
Write-Host "Output: dist\XCC Context Collector\XCC Context Collector.exe" -ForegroundColor Green