#!/usr/bin/env bash
# Starts the backend and frontend together (macOS / Linux).
#   Usage:  ./run.sh
# Run ./setup.sh first if you have not already.

set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$root/backend/venv" ]; then
  echo "Backend venv missing - run ./setup.sh first."
  exit 1
fi

cleanup() {
  echo
  echo "Shutting down..."
  kill 0
}
trap cleanup EXIT INT TERM

echo "Starting backend on http://localhost:8000 ..."
(cd "$root/backend" && ./venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000) &

echo "Starting frontend on http://localhost:5173 ..."
(cd "$root/frontend" && npm run dev) &

echo
echo "Both servers are starting. Open http://localhost:5173 (give it ~10 seconds)."
echo "Press Ctrl+C to stop both."
echo
wait
