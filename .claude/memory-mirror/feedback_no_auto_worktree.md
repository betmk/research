---
name: Research project — no auto-worktrees (Claude Desktop launcher bypass)
description: Sessions in the research project should edit the main working tree directly, never an isolated worktree. Claude Desktop creates worktrees BEFORE settings load — the deny rule cannot prevent it. SessionStart hook is the active safeguard.
type: feedback
originSessionId: 6369ad43-bc71-4415-b755-5593523ae793
---
For the research project, sessions must edit the main working tree at `/Users/mikemadden/Desktop/Claude Projects/research/` directly. Auto-worktrees keep landing in `.claude/worktrees/<adjective-scientist>/` despite the project-level `permissions.deny: ["EnterWorktree"]` rule committed in `.claude/settings.json` on 2026-05-10.

**Why the deny rule doesn't work (verified 2026-05-12):**
Claude Desktop's launcher (entrypoint `"claude-desktop"` in session JSON at `~/.claude/sessions/<pid>.json`) creates the worktree out-of-band and sets the new process's cwd to the worktree path BEFORE Claude Code initializes. By the time `.claude/settings.json` is read, the cwd is already inside `.claude/worktrees/`. The permissions system can only block tool calls the model makes — there is no tool call here; the worktree exists at process start. The deferred-tool list in a session includes `ExitWorktree` but no `EnterWorktree`, so the permission key may not even match a real tool name.

**Why this matters:** the http.server on port 8530 serves from the MAIN repo path. When a session edits in the worktree, the user's browser keeps showing stale content from main, and any commits go to a throwaway `claude/<name>` branch instead of main. User hit this 2026-05-09 (caught it after several minutes of confusion) and again 2026-05-11.

**Active safeguard (2026-05-12):** SessionStart hook `.claude/hooks/warn-if-worktree.sh`, wired in `.claude/settings.json`. Fires when cwd matches `*/.claude/worktrees/*`, prints a warning to stderr AND emits `additionalContext` JSON so the model sees the alert at the top of its first turn. Hook is silent when cwd is the main repo.

**How to apply:**
1. If you see the SessionStart warning, surface it to the user immediately in your first response. Either: (a) ask the user to exit and re-launch outside Cowork's worktree-isolation mode, OR (b) make every file edit via the absolute path under `/Users/mikemadden/Desktop/Claude Projects/research/` (NOT under `.claude/worktrees/`). Same for any `git -C` commands.
2. The permanent fix is at the Claude Desktop app level — disable Cowork worktree-isolation for this project. The hook is a workaround, not a fix.
3. Verify the server's cwd if anything looks off: `lsof -p <pid> | grep cwd`. Server runs from main; if it doesn't, that's a separate problem.
4. After any analysis.html edit, the user may need to hard-refresh (Cmd+Shift+R) since the http.server doesn't send no-cache headers.
5. Never commit without explicit permission per global rules.

**Cleanup pattern for abandoned worktrees:** orphan branches and dirs accumulate when sessions end uncleanly. Periodic cleanup:
```
cd ~/Desktop/Claude\ Projects/research
git worktree list                    # see what's live
git worktree remove --force .claude/worktrees/<name>
git branch -D claude/<name>
git worktree prune
```
Cannot remove the worktree of the currently-running session; do this from another session or outside Claude.
