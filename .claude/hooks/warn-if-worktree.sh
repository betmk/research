#!/bin/bash
# Detect if Claude Desktop / Cowork launched this session inside a worktree
# under .claude/worktrees/ and surface a loud warning to both the user and
# the model. The project-level permissions.deny: ["EnterWorktree"] rule does
# NOT prevent this because Claude Desktop creates the worktree out-of-band
# before settings.json is loaded — it is a structural bypass at the launcher
# layer, not a tool-call that permissions can intercept.
#
# This hook fires at SessionStart and is the only practical countermeasure
# until Anthropic surfaces a Cowork-level "don't isolate this project" flag.

set -u

CWD="$(pwd)"

case "$CWD" in
  */.claude/worktrees/*)
    MAIN_REPO="${CWD%%/.claude/worktrees/*}"
    WORKTREE_NAME="${CWD#*/.claude/worktrees/}"
    WORKTREE_NAME="${WORKTREE_NAME%%/*}"

    # macOS notification — visible regardless of whether stderr is captured
    # by the harness. Fires asynchronously so it doesn't delay session start.
    if command -v osascript >/dev/null 2>&1; then
      osascript -e "display notification \"Session launched in worktree $WORKTREE_NAME. Switch to Code mode (not Cowork) for clean sessions.\" with title \"Claude Code — Worktree Detected\" sound name \"Sosumi\"" >/dev/null 2>&1 &
    fi

    # Visible warning to the user (stderr is shown in Claude Code transcripts
    # for many hook events; harmless if not).
    cat <<EOF >&2
=====================================================================
WARNING: This session was launched inside a git worktree.

  Worktree: $CWD
  Main repo: $MAIN_REPO
  Worktree branch: claude/$WORKTREE_NAME

The http.server on port 8530 serves files from the MAIN repo, so any
edit made here will NOT appear in the user's live preview. Edits made
here also commit to a throwaway branch (claude/$WORKTREE_NAME), not main.

Root cause: Claude Desktop / Cowork's launcher creates the worktree
before .claude/settings.json is loaded. The permissions.deny rule
("EnterWorktree") in settings.json cannot intercept this — there is
no tool call to deny; the worktree exists at process start.

To fix permanently: disable Cowork's worktree-isolation for this project
in the Claude Desktop app settings. Until then, edit files in the main
repo via absolute paths starting with: $MAIN_REPO/
=====================================================================
EOF

    # Structured output for the model (additionalContext field, used by
    # Claude Code's SessionStart hook spec to inject system context).
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "WORKTREE ALERT: cwd is $CWD, which is a worktree, not the main repo. The live preview http.server on port 8530 serves from $MAIN_REPO. Any file edit must use absolute paths starting with $MAIN_REPO/ — otherwise edits go to a throwaway branch and the user's browser shows stale content. This is the documented 'Claude Desktop launcher worktree bypass' (.claude/settings.json comment). Surface this to the user at the top of your first response."
  }
}
EOF
    ;;
  *)
    # Not in a worktree — nothing to do. Exit silently.
    :
    ;;
esac

exit 0
