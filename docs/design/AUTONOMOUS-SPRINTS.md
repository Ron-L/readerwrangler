# Autonomous sprints — the history and the detail

_The rules themselves are in `CLAUDE.md` ("Autonomous mode — sprints"). This file holds only what CLAUDE.md doesn't:
why the method exists, where each rule came from, and the longer detail behind its short lines (moved from CLAUDE.md
2026-11-19, the rule trim). If a rule here and in CLAUDE.md ever differ, CLAUDE.md wins — fix this file._

## Why

Most of the asking was routine yeses that cost Ron hours of waiting and gave nothing back; his real value is taste,
truth-checking against real use, and real-device testing. So: Ron out of the routine, kept for judgment. Not just for a
vacation — if it speeds the work up, it's how we build all the time. The first trial (7.28.1, 2026-11-12): 35
decisions, 0 reversed — done the old way they'd have cost half a day more; but 36 questions reached Ron in one day,
which was too many — hence `RON-PROFILE.md` and the rule that only what it says reaches him is queued (Ron: "the vast
majority I don't feel I needed to review").

## Sprints

- **Design stays a conversation; building goes in sprints.** Tasks with a written "Decided" section make the best
  sprint material.
- **A normal sprint** is one to three tasks, ending where a release would.
- **A vacation sprint** (Ron, 2026-11-12) tags `before-vacation` on main as the rollback point. When a task blocks on a
  decision it's parked and work goes on **"branching wherever works best"** (Ron: "not meant to be a limitation"):
  usually the sprint's branch as it stood before the parked task started, so the next task carries none of its
  half-done work; from the parked branch when the next task builds on what's there; or any similar arrangement — my
  call, one line in `DECISIONS.md`. It stops only when every remaining task depends on a decision, a prompt needs an
  answer, or the session can't resume after a usage limit. **Before the first one:** a few days of normal sprints to
  tune the method, the pre-approved command list, Remote Control proven from the phone (answering a permission prompt
  included), and a dress rehearsal — a normal sprint with Ron home but not answering.

## The autonomy switch

`.private/AUTONOMY.md` — `mode: off | trial | on`, the sprint's tasks, and any other project a task may touch. Its
"why a file": a summary saying "autonomous" means nothing — only the file does; and only Ron changes it.

## Where the numbered rules came from

1. **One branch per sprint** (Ron, 2026-11-16) replaced the long-lived `main-prime` (kept as an archive): each sprint's
   branch is made from main, squashed onto main at release and kept; the next sprint starts fresh, so nothing is ever
   merged back. Later tasks build on earlier ones because each task's branch comes off the sprint's branch.
2. **Branches to both remotes** (2026-11-16) — `python tools/sync_remotes.py`; it never pushes `main` to prod, which
   deploys (2026-11-12).
3. **Working copies** — `py tools/copies.py new <name> --branch <b>` makes a git worktree in `..\ReaderWrangler-copies\`
   with the tools that aren't in git linked in; `remove` takes the links out first (git's worktree removal deletes
   through links) and keeps the copy's run records and time report. Independent tasks build at the same time —
   `readerwrangler.js` included. `py tools/merge_branches.py` restamps the version, regenerates `dist/`, the message
   codes table and TODO's contents, and runs the full tiers on the merged result before the target moves. The testing
   cadence is Ron's (2026-11-18: "1 full regression after each task").
4. **Decisions** — the profile holds how Ron decides (his rules, his patterns, what he always wants to see); each
   verdict is checked against my prediction in its calibration log and the profile corrected where it missed. Queue
   entries are written to be read cold, hours later: the task, the question with its context, my prediction and why,
   how to reverse it and what that costs.
5. **Scope** (Ron, 2026-11-12) — the example: "a `>` that should have been `>=`" is quicker to fix than to write up.
6. **"Ready"** includes the task's version in the sprint's branch and its CHANGELOG wording drafted in the queue; after
   Ron's review the sprint goes to main as one squash, tagged, and pushed (prod + dev).

## The record — each file's detail

- `PROGRESS.md` — each task's state: queued → building → ready (in the sprint's branch) | blocked-on-Ron → released; its
  branch, last alpha, last test run.
- `REVIEW-QUEUE.md` — only what reaches Ron; closed entries move to `REVIEW-DONE.md`. **Two measures:** how few
  questions reach him, and how rarely he reverses a prediction.
- `DECISIONS.md` — everything decided without asking, one line each (what, why, how to reverse): his to skim or ignore.
- `RON-PROFILE.md` — read before every decision; corrected by every verdict.

## Usage and checking in

- No new task once ~85% of the weekly limit is used (Ron, 2026-11-12: "about right — we'll see"). The five-hour window
  resets and the session resumes itself (`autoContinueAtUsageLimit`, three times in a row; any message from Ron —
  Remote Control from his phone included — starts the count over).
- Ron checks in here or by Remote Control (`/remote-control` in this session).
