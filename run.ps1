# Starts the backend and frontend together (Windows / PowerShell).
#   Usage:  .\run.ps1
# Run .\setup.ps1 first if you have not already.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

if (-not (Test-Path "$root\backend\venv")) {
    Write-Host "Backend venv missing - run .\setup.ps1 first." -ForegroundColor Red
    exit 1
}

Write-Host "Starting backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process -FilePath "$root\backend\venv\Scripts\python.exe" `
    -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
    -WorkingDirectory "$root\backend"

Write-Host "Starting frontend on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory "$root\frontend"

Write-Host "`nBoth servers are starting in separate windows." -ForegroundColor Green
Write-Host "Open http://localhost:5173 (give it ~10 seconds).`n"
