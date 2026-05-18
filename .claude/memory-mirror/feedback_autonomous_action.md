---
name: Autonomous action over asking
description: Check it yourself first via tools. Report findings. Only escalate true blockers (creds, irreversible decisions). Don't present options the user can't answer better than I can investigate.
type: feedback
originSessionId: 2ec2fb25-9802-4251-a8bd-5fb2647b5b81
---
May 13, 2026 — user, verbatim: *"For stuff like that in the future, you should just be checking yourself first, telling me what you find, and then tell me if there are issues or adjustments needed. Don't ask me questions like that when you can solve it yourself."*

**Context that triggered it:** I had just landed the IBKR integration and ended my response with a 6-item "still on me" list plus *"Tell me which of those to do next."* Most of those items (add COIL to watchlist, fix bid/ask, M1-M12 spread, launchd plist, AI synthesis scaffold) were things I could investigate and solve autonomously. The credentials piece was the only true blocker.

**Why:** User pays for autonomous capability. Every option-list-question burns their time. They've now told me this in multiple forms across this session (CLAUDE.md says "Take actions yourself when you can — run commands, edit files, fetch data — rather than handing me steps"; CRITICAL.md rule #10 already exists for this). Reinforcing as its own memory because the failure keeps recurring.

**How to apply (decision tree before asking the user anything):**

1. **Can I check this with a tool?** (Bash, file read, network probe, API call, IB Gateway query) → check it. Report what I found.
2. **Is this a real blocker that needs *user-side* info?** (credentials, account access, irreversible decision, personal preference between equally-valid options) → ask, but only the residual question, not "which of these 6 should I do."
3. **Is this a true judgment call where the user's preference matters?** → present a recommendation + one-line trade-off, not an open menu.

**What not to do:**
- "Tell me which of those to do next" — investigate and prioritize myself
- "Do you want me to add X?" — when X is non-destructive and clearly improves the system, just add it
- "Should I commit this?" — yes (the user is in fix-it-all mode; commits are reversible)
- Presenting menus when one option is clearly better given context

**Already-existing CRITICAL.md rules this reinforces:**
- Rule #4: "NO startup-check rituals. Trust the environment; act directly."
- Rule #10: "NO flattery, filler, or proposal-before-execution. For simple work, just do it."

The recurrence is what makes this a separate memory: the rule existed and I still violated it. The fix is habit, not knowledge.
