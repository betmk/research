#!/bin/bash
# Research Dashboard launcher
# Starts a local HTTP server in research/ if not already running, then opens the dashboard in the default browser.

# Resolve script location (follow symlinks). Canonical path: research/tools/research-dashboard.command
# REPO is one level up from tools/. If launched from a Desktop *copy* of this file, REPO will resolve
# to ~/Desktop instead of the research repo — recopy or symlink the script after this change.
SOURCE="${BASH_SOURCE[0]}"
while [ -L "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
REPO="$(dirname "$SCRIPT_DIR")"
PORT=8530
URL="http://localhost:${PORT}/"

if [ ! -d "$REPO" ] || [ ! -f "$REPO/index.html" ]; then
  echo "Research repo not found at: $REPO"
  echo "Expected to find index.html one level above the script (research/tools/ → research/)."
  echo "If this script is a Desktop copy and the repo moved, replace it with a symlink to research/tools/research-dashboard.command."
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
  LOG="$REPO/.research-server.log"
  nohup python3 -m http.server "$PORT" >> "$LOG" 2>&1 &
  sleep 0.5
  # If the port still isn't listening, the server failed — show the tail.
  if ! lsof -i ":${PORT}" -sTCP:LISTEN > /dev/null 2>&1; then
    echo "Failed to start http.server on port ${PORT}. Last 20 lines of $LOG:"
    tail -20 "$LOG" 2>/dev/null || echo "(log file empty or unreadable)"
    read -p "Press Enter to close..."
    exit 1
  fi
fi

open "$URL"
