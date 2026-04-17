$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Python 3.10 virtual environment not found at $pythonExe"
}

Set-Location $projectRoot

Write-Host "Using interpreter:" $pythonExe
& $pythonExe -c "import sys; print(sys.executable)"
& $pythonExe app.py
