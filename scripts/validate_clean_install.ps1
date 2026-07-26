param(
    [string]$PythonLauncher = "py",
    [switch]$KeepEnvironment
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ValidationRoot = Join-Path $env:TEMP "xcc-m8-clean-$PID"
$VenvRoot = Join-Path $ValidationRoot ".venv"
$VenvPython = Join-Path $VenvRoot "Scripts\python.exe"
$InstallTarget = "$ProjectRoot[dev,build]"

try {
    New-Item -ItemType Directory -Path $ValidationRoot -Force | Out-Null

    & $PythonLauncher -3.13 -m venv $VenvRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Could not create a clean Python 3.13 virtual environment."
    }

    & $VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        throw "Could not upgrade pip in the clean environment."
    }

    & $VenvPython -m pip install -e $InstallTarget
    if ($LASTEXITCODE -ne 0) {
        throw "Could not install XCC with dev and build dependency groups."
    }

    & $VenvPython -m compileall -q (Join-Path $ProjectRoot "src") (Join-Path $ProjectRoot "tests")
    if ($LASTEXITCODE -ne 0) {
        throw "Source compilation failed in the clean environment."
    }

    & $VenvPython -m pytest -q (Join-Path $ProjectRoot "tests")
    if ($LASTEXITCODE -ne 0) {
        throw "Tests failed in the clean environment."
    }

    & $VenvPython -c "from importlib.metadata import version; import xcc; assert version('xcc-context-collector') == xcc.__version__; import xcc.gui; import xcc.qt_worker"
    if ($LASTEXITCODE -ne 0) {
        throw "Installed package metadata or GUI imports are invalid."
    }

    & $VenvPython -c "import importlib.util; assert importlib.util.find_spec('keyboard') is None, 'keyboard must remain optional'"
    if ($LASTEXITCODE -ne 0) {
        throw "The legacy keyboard dependency was installed unexpectedly."
    }

    Write-Host "M8 clean-install validation passed." -ForegroundColor Green
}
finally {
    if ($KeepEnvironment) {
        Write-Host "Validation environment retained at: $ValidationRoot" -ForegroundColor Yellow
    }
    elseif (Test-Path $ValidationRoot) {
        Remove-Item $ValidationRoot -Recurse -Force
    }
}
