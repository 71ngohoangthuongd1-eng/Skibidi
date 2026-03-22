param(
    [string]$Python = "python",
    [switch]$SkipMigrations
)

$ErrorActionPreference = "Stop"

Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".venv")) {
    & $Python -m venv .venv
}

$venvPython = Join-Path ".venv\Scripts" "python.exe"

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements-prod.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Fill your real values before starting the bot."
}

New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "data" | Out-Null

if (-not $SkipMigrations) {
    & $venvPython -m alembic upgrade head
}

Write-Host ""
Write-Host "Setup complete."
Write-Host "Start the bot with:"
Write-Host ".\.venv\Scripts\python.exe run.py"
