$ErrorActionPreference = "Stop"

$frontendRoot = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "frontend"

if (-not (Test-Path (Join-Path $frontendRoot "package.json"))) {
    throw "Frontend package.json not found at $frontendRoot"
}

Set-Location $frontendRoot
npm run dev -- --host 127.0.0.1 --port 5173
