---
description: Re-run the 4-weekly survey of tools for Claude (skills, plugins, tool servers) that ReaderWrangler should use, and report what changed
---

Re-run the tool survey (Ron, 2026-11-03). The 4-weekly reminder hook (`.claude/hooks/survey-check.py`) reads the report's
`Next due:` line; this command refreshes the report.

1. Read the current report, `docs/design/TOOL-SURVEY.md` (the last run's verdicts are the baseline).
2. Launch ONE background research agent (general-purpose) with the brief below, writing its draft to the scratchpad as
   `tool-survey-<today>.md`. Do not duplicate its work while it runs.
3. When it finishes, VERIFY before trusting: spot-check every USE NOW / USE WHEN entry against the tool's own repo or
   docs (version, license, whether data leaves the PC). Correct or mark UNVERIFIED anything that doesn't hold.
4. Rewrite `docs/design/TOOL-SURVEY.md`: first lines `Surveyed: <today>` and `Next due: <today + 28 days>`, then a
   **"Changed since <last date>"** section (new tools, new versions, verdicts that moved, tools gone), then the report.
5. Tell Ron the top changes in a few lines and ask before acting on any USE NOW (installing anything is his call; read
   and pin an exact version first, per our outside-code rules). Commit the report only with his OK (docs-only, no bump).

**The brief for the agent** (keep it in step with the report's categories):

> Survey the current ecosystem of tools that extend Claude / Claude Code — skills, plugins, MCP servers, CLI tools built
> for coding agents — for ReaderWrangler: a solo-developer web app (plain HTML + React 18, Tailwind, IndexedDB, a
> Cloudflare Worker relay with end-to-end-encrypted sync, bookmarklets on amazon.com, a phone web view; GitHub Pages;
> Windows 11, VS Code + Claude Code, Edge/Chrome; Python preferred for scripts; exact-version pinning; nothing sends the
> user's data off the PC without consent). Your training data is out of date: rely on web searches (extended mode where
> thin) and the tools' own pages. Categories: (1) browser automation/testing an agent can drive, incl. video recording;
> (2) video assembly and sound for a short promo reel (Remotion, FFmpeg toolkits, Earshot, transcription, licensed
> music/sfx); (3) accessibility checking; (4) screenshots/docs generation; (5) code quality on a 20k-line single JS file
> (refactoring, use-before-declare, dead code); (6) Cloudflare Workers and browser extensions/bookmarklets;
> (7) official Anthropic skills/plugins a solo developer might miss. Per tool: name + URL, what it does, maturity (first
> release, latest version, activity, stars), license, WHETHER ANY DATA LEAVES THE PC, Windows install footprint, verdict
> USE NOW / USE WHEN (task) / WATCH / SKIP with one line why. At most ~25 entries; mark anything not confirmed from a
> primary source UNVERIFIED; be skeptical of hype. Compare against the previous report (given) and list what changed.
> Write Markdown to the scratchpad path given; do not install anything, modify other files, or visit amazon.com.
