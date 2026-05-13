---
name: Cowork sessions ignore local MCP settings
description: Claude Desktop's Cowork launcher passes --settings {} on fresh sessions, wiping user/project mcpServers config; only its hardcoded MCP whitelist (chrome-devtools, computer-use, Claude_in_Chrome, Claude_Preview, ccd_*, mcp-registry, scheduled-tasks) loads. User's playwright/sqlite/exa/duckdb/serena from settings.json are silently dropped.
type: feedback
originSessionId: 52fd3ac4-8f32-4278-a089-660e991061fb
---
## The rule

Claude Desktop Cowork sessions launched fresh (no `--resume`) pass `--settings {}` on the claude command line, which overrides the user's `~/.claude/settings.json` and the project's `.claude/settings.json`. Result: the `mcpServers` block in either of those files is NOT loaded into the running session.

Cowork uses its own hardcoded MCP whitelist that always loads regardless of local config:
- `chrome-devtools` (started via `npm exec chrome-devtools-mcp@latest` — NOT the user's pinned version)
- `computer-use`
- `Claude_in_Chrome`
- `Claude_Preview`
- `ccd_directory`, `ccd_session`, `ccd_session_mgmt`
- `mcp-registry`
- `scheduled-tasks`

User-configured MCPs that get silently dropped in Cowork:
- `playwright` (`@playwright/mcp@0.0.70`)
- `sqlite` (`mcp-server-sqlite`)
- `exa` (HTTP at mcp.exa.ai/mcp)
- `duckdb` (motherduck)
- `serena` (project-level — `uvx --from git+https://github.com/oraios/serena`)

## Why

**Why:** Verified May 13 2026 in this research session. `ps` shows my fresh Cowork session (no `--resume`) has `--settings {}` in argv; investing-dash session (`--resume e7f0410e`) does NOT have `--settings {}` and has serena running. The merged settings file at `/tmp/claude-settings-<hash>.json` showed an empty object `{}` for my session. Local settings.json fully populated with 5 MCPs. Chrome-devtools running but at `@latest`, not the `@0.21.0` from local config — confirms Cowork has its own MCP source.

This is the same class of issue as the worktree auto-spawn (see `feedback_no_auto_worktree.md`): Claude Desktop's Cowork launcher overrides local Claude Code config in ways that can't be intercepted from inside a session.

## How to apply

- **Don't promise local MCPs will work in Cowork sessions** — verify by running `cat /tmp/claude-settings-*.json | jq '.mcpServers // "missing"'` at session start.
- **Resumed sessions retain their original MCP config** — so if user has an old session with serena/exa running, that session is fine; new sessions launched after the --settings {} change won't get those MCPs.
- **Three separate MCP registries** to keep straight:
  1. Local `~/.claude/settings.json` mcpServers — used by vanilla Claude Code CLI; ignored by Cowork
  2. Cowork hardcoded whitelist — not user-customizable from any local file
  3. claude.ai/customize/connectors — used by claude.ai chat AND remote scheduled-agent routines
- **For remote scheduled agents**: attach MCPs via `mcp_connections` field on `RemoteTrigger` create body. Connector must first exist at claude.ai/customize/connectors.
- **Local-only MCPs can't go cloud:** chrome-devtools, playwright, sqlite require local processes / browsers / files. Only network-API MCPs (exa, hosted databases) can be added as cloud connectors.
- **Cannot fix mid-session.** MCPs are attached at session launch. To get a user MCP loaded, the session must restart with appropriate launch flags (and Cowork doesn't currently expose that).
- **Permanent fix is at the Claude Desktop app level** — same as the worktree issue. I have no visibility into Cowork UI from a session.

## Open question

Where does Cowork's hardcoded MCP whitelist live? Not in user settings.json. Possibly in the Claude.app bundle or in cloud-side per-account config. Worth investigating if user ever needs to add a custom MCP to a Cowork session.
