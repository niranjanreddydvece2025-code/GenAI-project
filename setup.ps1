# One-command setup for Windows (PowerShell).
#   Usage:  .\setup.ps1
# Creates the backend venv, installs dependencies, installs frontend packages
# and seeds the database. Run .\run.ps1 afterwards to start both servers.

$root = $PSScriptRoot
$python = "$root\backend\venv\Scripts\python.exe"

# Windows PowerShell turns anything a native command writes to stderr into an error
# record. Python writes deprecation warnings there, so "Stop" would abort the script
# on harmless output. Exit codes are checked explicitly instead.
$ErrorActionPreference = "Continue"
$env:PYTHONWARNINGS = "ignore::FutureWarning"

function Invoke-Step {
    param([string]$Description, [scriptblock]$Action)
    Write-Host $Description -ForegroundColor Yellow
    & $Action
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`nFAILED: $Description (exit code $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
}

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
Set-Location "$root\backend"

if (-not (Test-Path $python)) {
    Invoke-Step "[1/4] Creating the Python virtual environment..." { python -m venv venv }
} else {
    Write-Host "[1/4] Virtual environment already exists, skipping." -ForegroundColor Yellow
}

Invoke-Step "[2/4] Installing backend dependencies (this takes a couple of minutes)..." {
    & $python -m pip install --upgrade pip --quiet
    & $python -m pip install -r requirements.txt --quiet
}

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
Set-Location "$root\frontend"
Invoke-Step "[3/4] Installing frontend packages..." { npm install --silent }

# --- Seed --------------------------------------------------------------------
Set-Location "$root\backend"
Invoke-Step "[4/4] Seeding the database with 15 sample employees..." { & $python -m app.seed }

Set-Location $root
Write-Host "`n=== Setup complete ===" -ForegroundColor Green
Write-Host "Start everything with:  .\run.ps1"
Write-Host "Then open http://localhost:5173 and sign in with any email + password."
Write-Host "  pm@company.com  -> Project Manager"
Write-Host "  rm@company.com  -> Resource Manager (can upload resumes)`n"
