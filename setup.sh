#!/usr/bin/env bash
# One-command setup for macOS / Linux.
#   Usage:  ./setup.sh
# Creates the backend venv, installs dependencies, installs frontend packages
# and seeds the database. Run ./run.sh afterwards to start both servers.

set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo
echo "=== GenAI Resource Allocation - setup ==="
echo

for tool in python3 npm; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "ERROR: '$tool' was not found on PATH."
    [ "$tool" = "python3" ] && echo "Install Python 3.10+ from https://www.python.org/downloads/"
    [ "$tool" = "npm" ] && echo "Install Node.js 18+ from https://nodejs.org/"
    exit 1
  fi
done

echo "[1/4] Creating the Python virtual environment..."
cd "$root/backend"
[ -d venv ] || python3 -m venv venv

echo "[2/4] Installing backend dependencies (this takes a couple of minutes)..."
./venv/bin/python -m pip install --upgrade pip --quiet
./venv/bin/python -m pip install -r requirements.txt --quiet

if [ ! -f .env ]; then
  cp .env.example .env
  echo
  echo "  Created backend/.env from the example."
  echo "  ACTION REQUIRED - open backend/.env and add your own API keys:"
  echo "    OPENROUTER_API_KEY  free key at https://openrouter.ai/keys"
  echo "    GEMINI_API_KEY      free key at https://aistudio.google.com/apikey"
  echo
  echo "  The app still runs without them - search falls back to keyword"
  echo "  matching - but AI summaries and semantic search need the keys."
  echo
fi

echo "[3/4] Installing frontend packages..."
cd "$root/frontend"
npm install --silent

echo "[4/4] Seeding the database with 15 sample employees..."
cd "$root/backend"
./venv/bin/python -m app.seed

echo
echo "=== Setup complete ==="
echo "Start everything with:  ./run.sh"
echo "Then open http://localhost:5173 and sign in with any email + password."
echo "  pm@company.com  -> Project Manager"
echo "  rm@company.com  -> Resource Manager (can upload resumes)"
echo
