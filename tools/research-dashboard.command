#!/bin/bash
# Research Dashboard launcher
# Starts a local HTTP server in research/ if not already running, then opens the dashboard in the default browser.

REPO="/Users/mikemadden/Desktop/Claude Projects/research"
PORT=8530
URL="http://localhost:${PORT}/"

if [ ! -d "$REPO" ]; then
  echo "Research repo not found at: $REPO"
  echo "If you moved it, edit this script and update REPO=."
  read -p "Press Enter to close..."
  exit 1
fi

cd "$REPO"

if ! command -v python3 > /dev/null 2>&1; then
  echo "python3 not found in PATH."
  read -p "Press Enter to close..."
  exit 1
fi

if ! lsof -i ":${PORT}" -sTCP:LISTEN > /dev/null 2>&1; then
  nohup python3 -m http.server "$PORT" > /dev/null 2>&1 &
  sleep 0.5
fi

open "$URL"
