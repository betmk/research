#!/bin/bash
# Inject load-bearing project rules into the session context as
# additionalContext on SessionStart. These are the constraints that have
# been violated recently and need maximum prominence so they aren't lost
# in the larger CLAUDE.md/MEMORY.md context noise.

set -u

# Resolve script's own location so we find CRITICAL.md even when invoked from
# a worktree cwd. The script lives at .claude/hooks/, so CRITICAL.md is one
# directory up.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CRITICAL_FILE="$SCRIPT_DIR/../CRITICAL.md"

# Fallback: hardcoded main-repo path (handles edge case where this hook
# is run from a worktree that hasn't pulled the latest yet).
if [ ! -f "$CRITICAL_FILE" ]; then
  CRITICAL_FILE="/Users/mikemadden/Desktop/Claude Projects/research/.claude/CRITICAL.md"
fi

if [ ! -f "$CRITICAL_FILE" ]; then
  exit 0
fi

# Use python3 for safe JSON escaping (file content may contain quotes,
# backslashes, special chars that would break naive shell JSON).
python3 - "$CRITICAL_FILE" <<'PYEOF'
import json
import sys

with open(sys.argv[1]) as f:
    rules = f.read()

prefix = (
    "CRITICAL PROJECT RULES — load-bearing constraints. "
    "Read these BEFORE any action. They override defaults and CLAUDE.md when in conflict. "
    "Source of truth: .claude/CRITICAL.md.\n\n"
)

output = {
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": prefix + rules,
    }
}

print(json.dumps(output))
PYEOF

exit 0
