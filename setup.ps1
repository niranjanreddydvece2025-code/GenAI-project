# One-command setup for Windows (PowerShell).
#   Usage:  .\setup.ps1
# Creates the backend venv, installs dependencies, installs frontend packages
# and seeds the database. Run .\run.ps1 afterwards to start both servers.

$ErrorActionPreference = "Stop"
$root = $PSScriptRoot

Write-Host "`n=== GenAI Resource Allocation - setup ===`n" -ForegroundColor Cyan

# --- Prerequisite checks -----------------------------------------------------
foreach ($tool in @("python", "npm")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: '$tool' was not found on PATH." -ForegroundColor Red
        if ($tool -eq "python") { Write-Host "Install Python 3.10+ from https://www.python.org/downloads/" }
        else { Write-Host "Install Node.js 18+ from https://nodejs.org/" }
        exit 1
    }
}

# --- Backend -----------------------------------------------------------------
Write-Host "[1/4] Creating the Python virtual environment..." -ForegroundColor Yellow
Set-Location "$root\backend"
if (-not (Test-Path "venv")) { python -m venv venv }

Write-Host "[2/4] Installing backend dependencies (this takes a couple of minutes)..." -ForegroundColor Yellow
& "$root\backend\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
& "$root\backend\venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet

# --- Environment file --------------------------------------------------------
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "`n  Created backend\.env from the example." -ForegroundColor Green
    Write-Host "  ACTION REQUIRED - open backend\.env and add your own API keys:" -ForegroundColor Magenta
    Write-Host "    OPENROUTER_API_KEY  free key at https://openrouter.ai/keys"
    Write-Host "    GEMINI_API_KEY      free key at https://aistudio.google.com/apikey"
    Write-Host "`n  The app still runs without them - search falls back to keyword"
    Write-Host "  matching - but AI summaries and semantic search need the keys.`n"
}

# --- Frontend ----------------------------------------------------------------
Write-Host "[3/4] Installing frontend packages..." -ForegroundColor Yellow
Set-Location "$root\frontend"
npm install --silent

# --- Seed --------------------------------------------------------------------
Write-Host "[4/4] Seeding the database with 15 sample employees..." -ForegroundColor Yellow
Set-Location "$root\backend"
& "$root\backend\venv\Scripts\python.exe" -m app.seed

Set-Location $root
Write-Host "`n=== Setup complete ===" -ForegroundColor Green
Write-Host "Start everything with:  .\run.ps1"
Write-Host "Then open http://localhost:5173 and sign in with any email + password."
Write-Host "  pm@company.com  -> Project Manager"
Write-Host "  rm@company.com  -> Resource Manager (can upload resumes)`n"
