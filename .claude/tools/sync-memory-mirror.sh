#!/bin/bash
# Sync auto-memory files into the repo mirror so they survive a project nuke.
# Uses rsync --update because macOS BSD cp does not support -u.
# Designed to run as a Stop hook (fires after each Claude response) with
# negligible overhead when nothing has changed.

set -u

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-/Users/mikemadden/Desktop/Claude Projects/research}"
MEMORY_SRC="$HOME/.claude/projects/-Users-mikemadden-Desktop-Claude-Projects-research/memory"
MEMORY_DST="$PROJECT_DIR/.claude/memory-mirror"

# Resolve the mirror destination via script-relative path if PROJECT_DIR
# would point at a worktree without the memory-mirror dir.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_RELATIVE_MIRROR="$SCRIPT_DIR/../memory-mirror"
if [ ! -d "$MEMORY_DST" ] && [ -d "$SCRIPT_RELATIVE_MIRROR" ]; then
  MEMORY_DST="$SCRIPT_RELATIVE_MIRROR"
fi
# Hardcoded fallback for the main repo
if [ ! -d "$MEMORY_DST" ]; then
  MEMORY_DST="/Users/mikemadden/Desktop/Claude Projects/research/.claude/memory-mirror"
fi

# Bail silently if memory dir doesn't exist yet (fresh clone, no session yet)
[ -d "$MEMORY_SRC" ] || exit 0

# Ensure mirror dir exists
[ -d "$MEMORY_DST" ] || mkdir -p "$MEMORY_DST"

# rsync --update copies only files where source mtime is newer than dest,
# or where dest is missing. -a preserves perms/times. Suppress noise so
# this doesn't slow down Stop events.
rsync -a --update "$MEMORY_SRC"/*.md "$MEMORY_DST/" 2>/dev/null
[ -f "$MEMORY_SRC/commits.log" ] && rsync -a --update "$MEMORY_SRC/commits.log" "$MEMORY_DST/" 2>/dev/null

exit 0
