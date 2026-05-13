---
name: Sparta podcast transcript via YouTube
description: When a Sparta "Trade with Conviction" episode transcript is needed, pull via YouTube auto-captions through Chrome DevTools MCP — this is the working path
type: feedback
originSessionId: ffab3716-767f-4057-9da9-1ec01fe922ca
---
For any Sparta "Trade with Conviction" episode transcript, use YouTube auto-captions via Chrome DevTools MCP. No need to evaluate other paths first.

**Why:** Confirmed working 2026-05-11 on Ep 92 (`MvhVU33cYk8`). The full 33-min audio extracted cleanly to 259 transcript segments / ~40K chars. This is the actionable Sparta audio content — chapter titles + written Deep Dives alone are not enough; the verbatim transcript surfaces explicit trade quotes that don't appear in any other Sparta-published format.

**How to apply:**

1. **YouTube channel anchors** (use these directly — don't search):
   - Channel handle: `@SpartaCommo` (NOT `@SpartaCommodities` — that one is dormant)
   - "Trade with Conviction" playlist: `https://www.youtube.com/playlist?list=PLI3dsnod9Rdj7KEMrCvibuZGxwFCw43Jv`

2. **Navigate to playlist via Chrome DevTools MCP**, then `evaluate_script`:
   ```js
   () => Array.from(document.querySelectorAll('ytd-playlist-video-renderer a#video-title'))
     .slice(0,5).map(a => ({ title: a.getAttribute('title'), href: a.href }))
   ```
   Episode N is at `index=1` in the playlist (newest first). Grab the `watch?v=` ID for the episode wanted.

3. **Navigate to the video URL** (`https://www.youtube.com/watch?v=<VIDEO_ID>`).

4. **Click "Show transcript"** — find the button via:
   ```js
   () => {
     const btn = Array.from(document.querySelectorAll('button, yt-button-shape, tp-yt-paper-button'))
       .find(b => /show transcript/i.test(b.textContent || '') || /show transcript/i.test(b.getAttribute('aria-label') || ''));
     if (btn) btn.click();
   }
   ```
   If not found, expand the description first (`#expand` button), then retry.

5. **Wait for the transcript panel** — it loads as `<ytd-engagement-panel-section-list-renderer target-id="PAmodern_transcript_view">`.

6. **Extract** — segments are `<transcript-segment-view-model>`; chapter headers are `<macro-markers-panel-item-view-model>`. Read `panel.innerText` for plain text in DOM order. Expect ~40K chars for a 30-min episode.

7. **Save key findings (paraphrased, not raw transcript) to `reports/hormuz/sources/ep<N>_key_findings.md`** — copyright rules say no raw transcript saved verbatim; extract explicit trade quotes (<15 words each), paraphrase the rest, attribute every claim to speaker + chapter timestamp.

**Format for key-findings file:** chapter map table (ch / start / title), explicit-trade-quote table (caller / time / trade / verbatim short quote in <15 words), then chapter-by-chapter paraphrased notes. This makes follow-up refreshes scan-friendly without re-pulling the transcript.

**Watch for:** YouTube's `transcript-segment-view-model` selector replaced the older `ytd-transcript-segment-renderer` — if the new selector returns 0, the UI has changed again; fall back to scanning all descendants of the engagement panel by tag-name frequency.
