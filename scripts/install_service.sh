#!/bin/bash
# Install the research service as a launchd LaunchAgent.
# After install: service starts at login, restarts on crash, runs in background.
#
# Commands:
#   ./scripts/install_service.sh         # install (or update)
#   ./scripts/install_service.sh status  # show launchd status
#   ./scripts/install_service.sh stop    # stop + unload
#   ./scripts/install_service.sh start   # load + start

set -e

REPO_ROOT="/Users/mikemadden/Desktop/Claude Projects/research"
PLIST_SRC="$REPO_ROOT/launchd/com.research.research.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.research.research.plist"
LABEL="com.research.research"

cmd="${1:-install}"

case "$cmd" in
  install|update)
    mkdir -p "$HOME/Library/LaunchAgents"
    cp "$PLIST_SRC" "$PLIST_DST"
    # Unload first if already loaded (ignore errors)
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    launchctl load "$PLIST_DST"
    echo "Installed and loaded: $PLIST_DST"
    sleep 2
    launchctl list | grep "$LABEL" || echo "(not visible in launchctl yet — may need a few seconds)"
    ;;
  start)
    launchctl load "$PLIST_DST" 2>/dev/null || true
    launchctl start "$LABEL"
    echo "started: $LABEL"
    ;;
  stop)
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    echo "stopped: $LABEL"
    ;;
  status)
    launchctl list | grep "$LABEL" || echo "not loaded"
    ;;
  uninstall)
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    rm -f "$PLIST_DST"
    echo "uninstalled"
    ;;
  *)
    echo "usage: $0 [install|start|stop|status|uninstall]"
    exit 1
    ;;
esac
