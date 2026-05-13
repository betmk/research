---
name: Session efficiency threshold
description: User has signaled willingness to nuke and restart if session-startup overhead doesn't improve — prioritize ruthless efficiency, no warm-up dance
type: feedback
originSessionId: 2ec2fb25-9802-4251-a8bd-5fb2647b5b81
---
May 13, 2026 — user said verbatim: *"We're getting close to the point where I'm just going to have to delete all this and just restart from scratch because it seems like it's so inefficient. Please take note of that and try to make it so that this process survives somehow."*

Project is on the brink of abandonment over Cowork-induced startup overhead. Pattern observed across May 9–13: every session burns 5–15 minutes on worktree-spawn + MCP-wipe diagnosis + cleanup ritual before any actual research work begins.

**Why:** The recurring failure modes are well-documented but the harness keeps re-creating them. User has watched the same dance multiple sessions. The threshold has shifted from "annoying" to "I'm considering nuking the whole project."

**How to apply:**

1. **First minute matters.** Run startup checks (`pwd`, worktree list, MCP check) in ONE parallel batch. If problems found, surface them concisely and propose action — do NOT enumerate every memory file, chain 10 verification commands, or re-explain the Cowork root cause that the user already knows.

2. **Always use main-repo absolute paths for writes** (`/Users/mikemadden/Desktop/Claude Projects/research/...`) regardless of cwd. Never rely on cwd being correct. This eliminates the worktree-mismatch class of bugs entirely.

3. **Don't lecture about Cowork.** User knows. Surface state → propose action → execute → move on.

4. **If a chronic problem can't be solved this session, name it once and move on.** Don't re-explain.

5. **Recovery package is at repo root:** `RECOVERY.md` + `.claude/memory-mirror/` (mirror of this dir). If user nukes and re-clones, those files restore them to the current state. Keep the mirror in sync at session end.

6. **Sync command for memory mirror** (run at session end if memory changed this session):
```bash
cp ~/.claude/projects/-Users-mikemadden-Desktop-Claude-Projects-research/memory/*.md \
   ~/.claude/projects/-Users-mikemadden-Desktop-Claude-Projects-research/memory/commits.log \
   "/Users/mikemadden/Desktop/Claude Projects/research/.claude/memory-mirror/" 2>/dev/null
```

7. **Permanent fix (NOT in my power):** disable Cowork worktree-isolation in Claude Desktop UI for this project. Same toggle handles both worktree-spawn and `--settings {}` MCP wipe. User to action this — escalate to Anthropic support if not in UI.
