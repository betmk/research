#!/bin/bash
# Sync auto-memory files into the repo mirror so they survive a project nuke.
# Idempotent: cp -u only copies files where source is newer than destination.
# Designed to run as a Stop hook (fires after each Claude response) with
# negligible overhead when nothing has changed.

set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/mikemadden/Desktop/Claude Projects/research}"
MEMORY_SRC="$HOME/.claude/projects/-Users-mikemadden-Desktop-Claude-Projects-research/memory"
MEMORY_DST="$PROJECT_DIR/.claude/memory-mirror"

# Bail silently if memory dir doesn't exist yet (fresh clone, no session yet)
[ -d "$MEMORY_SRC" ] || exit 0

# Ensure mirror dir exists
[ -d "$MEMORY_DST" ] || mkdir -p "$MEMORY_DST"

# -u = update only if source newer than dest; -p = preserve timestamps.
# Suppress noise; we don't want to slow down stop events.
cp -up "$MEMORY_SRC"/*.md "$MEMORY_DST/" 2>/dev/null
cp -up "$MEMORY_SRC"/commits.log "$MEMORY_DST/" 2>/dev/null

exit 0
