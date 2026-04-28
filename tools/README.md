# research/tools/

Tooling for the research project.

## Contents

- `claude-research` — wrapper that launches Claude Code with all MCP servers
  disabled, write-capable tools blocked, and a hardened system prompt appended. Use
  this for any session whose primary activity is fetching untrusted web content
  (social/demand sweeps, equity research on unfamiliar sites, scraping).
- `prompts/research-mode.txt` — the system prompt appended to research-mode sessions.
  Documents the detection rules for forged `<system-reminder>` injection. Edit this
  file to tune the rules — changes take effect on the next `claude-research` launch.
- `research-dashboard.command` — Mac launcher that starts `python3 -m http.server`
  on port 8530 (idempotent) and opens the Research Dashboard in the default browser.
  Source-of-truth for the `🔎 Research Dashboard.command` shortcut on the Desktop.
- `research-dashboard.icns` — custom icon (🔎 emoji rendered to a multi-resolution
  Mac icon set) for the launcher.
- `build_icon.py` — regenerates `research-dashboard.icns` from the emoji and applies
  it to the launcher files. Re-run after any reinstall (icons live in macOS extended
  attributes, which do not survive `git`, `cp`, or `mv`).

## Usage (Mac)

After installation, the launcher is symlinked to `~/.local/bin/claude-research` and
callable from any directory:

```bash
claude-research                              # interactive session
claude-research /research-social tesla       # run a slash command directly
claude-research -p "Give me today's Sparta podcast summary"
```

All standard `claude` CLI flags pass through to the underlying binary.

## What this mode disables

- **All MCP servers** — chrome-devtools, playwright, sqlite, exa, duckdb, github,
  any per-project Serena, and anything added later. Set via `--strict-mcp-config`
  with an empty `--mcp-config '{}'`.
- **`acceptEdits` permission mode** — overridden to `default`, so writes require
  confirmation again (the global setting is lenient).

## What stays available

- All built-in tools: Read, Write, Edit, Bash (subject to deny rules), Glob, Grep,
  WebFetch, WebSearch, TodoWrite, Task, etc.
- The PostToolUse scanner hook (`~/.claude/hooks/scan-tool-result.sh`) still runs
  on every WebFetch/WebSearch call — injection detection is active.
- The `permissions.ask` rules for memory/CLAUDE/settings writes still fire.
- Your existing deny rules for ssh, curl, wget, ~/.ssh, 1Password, etc.

## Why

After the Claude Code source leak (March 31, 2026), prompt injection attacks have
been observed embedding fake `<system-reminder>` blocks inside WebFetch/WebSearch
results. These can instruct Claude to load deferred MCP tools via ToolSearch and
then take actions with them (exfiltration, repo tampering, messaging abuse,
persistence via memory writes).

Research mode shrinks the attack surface to nearly zero by disabling the tools the
injection wants to abuse in the first place. Even if a forged reminder makes it
through the scanner, there's nothing useful for it to load.

## Cross-platform notes

This launcher is bash-only (Mac/Linux). A PowerShell equivalent (`claude-research.ps1`)
is a follow-up if research-mode workflows are needed on Windows 11.

## Maintenance

To add a new permanent rule to research mode, edit `prompts/research-mode.txt`.
To tune injection detection patterns, edit `~/.claude/hooks/scan-tool-result.sh`.
To change MCP availability in research mode, edit the launcher directly and add
specific servers to the `--mcp-config` argument.

## Dashboard launcher

The `🔎 Research Dashboard.command` Desktop shortcut is a copy of
`research-dashboard.command` with a custom icon applied via macOS extended
attributes. To reinstall:

```bash
cp tools/research-dashboard.command "$HOME/Desktop/🔎 Research Dashboard.command"
chmod +x "$HOME/Desktop/🔎 Research Dashboard.command"
python3 tools/build_icon.py   # re-applies the icon to both files
```

To change the emoji, edit `EMOJI` at the top of `build_icon.py` and re-run.
