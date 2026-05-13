#!/bin/bash
# Dev runner — install deps + start the FastAPI service on port 8530.
# Usage:
#   ./scripts/run_dev.sh
#
# For production / always-on, install the launchd plist (TBD: launchd/com.research.research.plist).

set -e

REPO_ROOT="/Users/mikemadden/Desktop/Claude Projects/research"
cd "$REPO_ROOT"

# Create venv if missing
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

# Install requirements
.venv/bin/pip install -q -r requirements.txt 2>&1 | grep -v "already satisfied" || true

# Initialize DB (idempotent)
.venv/bin/python -c "from app.db import init_db; init_db(); print('db ok')"

# Start FastAPI with auto-reload during dev
exec .venv/bin/uvicorn app.main:app \
  --host 127.0.0.1 \
  --port 8530 \
  --reload
