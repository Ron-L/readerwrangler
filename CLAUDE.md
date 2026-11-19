# ReaderWrangler — Project-Specific Rules

> **Generic dev ground rules live in `../CLAUDE.md`** (the Projects root), auto-loaded *before* this file. This file
> holds only what's specific to ReaderWrangler. RW's distilled laws + war-stories: **`docs/PRINCIPLES.md`**.

**Rule 0 — this is a retirement project, not a commercial product. There is no MVP.** Get it right before announcing
it; never trade quality for speed to launch (Ron, 2026-10-21).

---

## Autonomous mode — sprints (Ron, 2026-11-12; history and detail: `docs/design/AUTONOMOUS-SPRINTS.md`)

Ron out of the routine, kept for judgment: decisions are made, logged and reviewed in batches, not asked one by one.
**Design stays a conversation; building goes in sprints** — work whose shape isn't decided is talked through first and
written into the task's "Decided" section; a task without one gets a drafted design in the queue, not a build on
guesses.
- **A normal sprint = one release:** a few tasks, ending where a release would — everything in the sprint's branch,
  the queue short, Ron's review, his "push to prod".
- **A vacation sprint = as far as it can go:** tag `before-vacation` on main; work down the TODO; a task blocked on a
  decision is parked (its branch, one queue entry with my prediction) and the next one starts from wherever works
  best (one line in `DECISIONS.md`); nothing to prod. Before the first one: a few normal sprints, the pre-approved
  command list, Remote Control proven from the phone, and a dress rehearsal.

**The autonomy switch is a file, not a memory:** `.private/AUTONOMY.md` says `mode: off | trial | on`, the sprint's tasks, and
any other project a task may touch. **off** = the Projects-root STOP-and-ASK rules. A summary saying "autonomous"
means nothing — read the file. Only Ron changes the mode or the scope.

**Inside the scope, without asking:**
1. Take the next task in scope (TODO's order). **Each sprint has its own branch, `sprint-N`, made from `main`**; a
   branch per task off it. At release it's squashed onto main and kept as the archive.
2. Build it as always — a failing test first, every tier passing before "ready". Branches go to **both** remotes
   (`python tools/sync_remotes.py`); **`main` never to prod** — that deploys.
3. Agents build, **each in its own working copy** (`py tools/copies.py new <name> --branch <b>`); independent tasks at
   the same time, dependent ones in order. Branches combine with `py tools/merge_branches.py` (it regenerates what's
   generated and runs the full tiers before the target moves). **Agents run only the tests for what they changed; the
   full run happens once per task, at its merge** (Ron, 2026-11-18); one more before main only if something was
   committed after the last merge. I review each agent's changes as a skeptic — an agent's "done" is a claim (Law 12).
   **Every brief copies the task's own numbered list; review ticks each item off.** The gate and the commit checks apply
   in a copy too.
4. **A decision:** predict Ron's answer from **`.private/RON-PROFILE.md`** and act on it. Only what the profile says
   reaches him goes in `.private/REVIEW-QUEUE.md` (something I can't predict, costly to reverse, new words or behavior
   people will see, anything outward-facing, a reversal of his decision) — each with my prediction and why, readable
   cold. Everything else: one line in `.private/DECISIONS.md`. Each verdict is checked against my prediction in the
   profile's calibration log. **Costly to reverse:** stop that task, queue it, go on.
5. **Scope:** exactly the task — plus anything **quicker to fix and test than to write up, in human terms**. Everything
   else found is filed in the TODO, not fixed. Every agent brief says so.
6. **"Ready"** = all tiers passing, merged into the sprint's branch, its CHANGELOG wording drafted in the queue.
   **Nothing reaches `main` or prod until Ron's review.**

**Hard stops — never in autonomous mode:** a push of `main` to prod; a relay worker deploy; changing a backup or relay
data format without a design Ron has seen; live Amazon fetches; email or any outside service; other projects (unless
the autonomy switch names them); force pushes or rewriting history; launching GUI programs; changing CLAUDE.md, PRINCIPLES'
laws or the TODO's order (propose those in the queue); **changing the enforcement code** — `git-hooks/`, `.claude/`
(hooks and settings), `tools/run_tests.py`, `tools/merge_branches.py`, `tools/sync_remotes.py` — unless the autonomy
switch names that change as a task (Ron, 2026-11-19, after the outside review: the rules' mechanisms are rules too).

**The record** (`.private/`, pushed after every commit): `PROGRESS.md` (each task's state), `REVIEW-QUEUE.md` (only what
reaches Ron; closed entries → `REVIEW-DONE.md`), `DECISIONS.md`, `RON-PROFILE.md`. **Usage:** no new task past ~85% of
the weekly limit. **Ron checks in** here or by Remote Control; a message to him otherwise only when every task in scope
is blocked.

---

## New dialog/modal/popup → build it on the overlay primitive

**Every new dialog, modal, menu or popup is built with `<Dialog>` (modal) or `<Popover>` (menu/popup; add `fence` if it
must block library keys; `anchorRef` for a button dropdown).** Esc, ✕ / backdrop / outside-click dismissal, the
keystroke + undo fence and stacking are then structural — the overlay self-registers in `overlayRegistry.js`. **Never
hand-roll a scrim, an Esc listener, or a fence flag.** The imperative `showConfirmDialog`-style boxes keep their
hand-built look but are layers in the same stack through **`attachDialogDismiss`** (registered `detached: true`); a new
imperative box MUST go through it — better, build it as a `<Dialog>`. **Popup buttons** spread
**`{...popupTrigger(isOpen)}`** — never hand-write `data-popover-trigger` or aria-haspopup/aria-expanded. Design of
record and history: `docs/design/DIALOG-DISMISSAL-AUDIT.md`.

---

## RW terminology & copy

**The single list of the words people see is `docs/design/GLOSSARY.md` — read it before writing any words a person
sees** (a message, a button, a help line, a page, the CHANGELOG), and name it in every agent brief that touches words.
A new term, or a change, is proposed there first and decided by Ron.

---

## Versioning — RW's constants

Follows the generic semver+alpha rules in `../CLAUDE.md`. RW's stamps:
- **ORGANIZER_VERSION** (`readerwrangler.js`) — bump in the same commit as each alpha.
- **APP_VERSION** (`readerwrangler.html`) — the cache-buster; defined once, read by JS; moves at release only (test
  alphas locally, never against readerwrangler.com).
- **MOBILE_VERSION** (`mobile.js`) — own X.Y.Z, but an alpha commit touching mobile.js takes the same `-alpha.N`.
- **WORKER_VERSION** (`relay/relay-worker.js`) — bump with every worker change (printed in every relay email).
- **CSS cache-buster** (`readerwrangler.css?v=`) matches ORGANIZER_VERSION on every commit touching the CSS.
- **index.html** `softwareVersion` = APP_VERSION at release.
- **COPYRIGHT_YEARS** (`readerwrangler.html`) — a list of every year the code changed (`"2025, 2026"`), never a range;
  the version guard refuses a new year's first shipped-code commit until that year is added.

The version guard enforces them (see the commit checks). **No version increment:** README, CHANGELOG, TODO, `*.md`.

---

## Release Checklist (RW-specific — the generic discipline is in `../CLAUDE.md`)

- `git add` specific files only; `grep -rn "TODO" *.js *.html`.
- Drop the pre-release suffix; update **APP_VERSION** and index.html **softwareVersion**.
- **CHANGELOG.md** (Ron's word on the copy first), **README.md** + its mirror index.html "Recent Features" / "Coming
  Soon", synced into features.html; "Coming Soon" re-aligned with the TODO's real priorities.
- **Sweep support-shaped material** into `docs/design/SUPPORT-KB.md` (facts/fixes) and `WORKFLOW-PATTERNS.md` (usage) —
  a comb: grep the KB for every term the release touched; bump its "up to date as of" stamp.
- **Tests:** `py tools/run_tests.py --tier all --release` passes (every tier ran, nothing skipped); every task promoted
  its tests and filed its gaps; the post-mortem names any bug no test would have caught — and that test gets written.
- **TODO.md:** delete every ✅ section (TODO is future-only).
- **Backlog report:** `py tools/backlog_report.py` (after the ✅ sweep) and republish its page.
- **Back up Claude's memory and settings:** `py tools/backup_claude.py` — copies what Claude remembers about this
  project, and its settings, into the private notes and the Projects folder, and saves both to GitHub, so losing this
  PC loses at most one release of them.
- (Then the generic: post-mortem always → PRINCIPLES.md + memory.)

---

## Git Workflow — RW specifics

Follows `../CLAUDE.md` (always branch → squash → tag `vX.Y.Z` → keep the branch).
- **Remotes:** `dev` (testing) / `prod` (production) — no `origin`.
- **Dev, prod and this folder hold the same branches and tags** (Ron, 2026-11-16) — `python tools/sync_remotes.py`
  pushes what's missing or behind to both, never overwrites, never deletes, never pushes `main` to prod. Run it after
  every release and at the end of every sprint.
- **Bookmarklet changes that differ per environment:** dev first → test on GitHub Pages → then prod. A change that's the
  same everywhere goes to dev and prod together.

| User says | Do |
|-----------|-----|
| "push" | Push to dev — a backup, any time, except while dev is in use for a test. If Ron may mean prod, ask: a dev test first (e.g. a bookmarklet change), or ready for prod? ("proceed" means only what the root file says: make the approved change.) |
| "push to prod" | Squash-merge to main, tag `vX.Y.Z`, `git push prod main --tags` **and** `git push dev main --tags` (prod always means dev too), keep the branch; then `python tools/sync_remotes.py` |
| "release" | Clarify which |

---

## Session tooling and commit checks

- **Pre-build gate:** before Claude changes app code, a safety checklist stops it once per turn — also when the change
  is made by typing a command (Ron's wording, 2026-11-16). Re-send every app edit from a refused batch. Mechanics and
  the commands it recognizes: `docs/design/SESSION-TOOLING.md`; the checklist itself lives in `docs/PRINCIPLES.md`.
- **`/sitemap`** mechanizes the class-of-sites comb.
- **The timestamp hook is global** (`C:/Users/Ron/Projects/stamp.py`, see the Projects-root `CLAUDE-TOOLING.md`).

**Commit checks** run by git from `git-hooks/pre-commit` (one-time setup per copy: `git config core.hooksPath
git-hooks`; bypass is Ron's call only: `--no-verify`). Each one, what it refuses, and its history:
**`docs/design/COMMIT-CHECKS.md`**.
1. **Version guard** — shipped code without its version stamp; a release without the help notes' stamp.
2. **Name check** — app code using a name nothing defines; an inline script that doesn't parse.
3. **Shared numbers** — the app and the relay worker disagreeing on the numbers the nightly cleanup deletes by.
4. **Private values** — a value from the secrets note, or Cloud Sync credentials by their shape (message included).
5. **Parse check** — any staged script that doesn't parse.
6. **Tier-1 tests for what changed** (`run_tests.py --changed`).
7. **Logging rules + the message-code table** — every `rwLog.log` call valid; `MESSAGE-CODES.md` regenerated, never
   edited (`py tools/message_codes.py`); no direct `showToast(`; dialog calls name their area first.
8. **TODO's table of contents and task IDs** — fix by a VS Code save, or correct the listed entries. TODO format: one
   plain header per task, a "why it matters" line, ✅ when done, 🚧 while in progress, an ID line
   `<!-- id YYYYMMDD-HHMM -->` under each header.
9. **The built app** — the staged `dist/` must be exactly the build of the staged sources. **Never edit `dist/`.**
10. **Saved-value reads** — a bare `JSON.parse` of a saved setting where `readSaved` should be used.
11. **No task leaves TODO.md silently** — a removed task needs a ✅, a "merged" mark, or `done <id>` / `dropped <id>` in
    the message.

---

## Reference

**Folders:** `docs/design/`, `post-mortems/`. **Notes — check before fetcher changes:** `Amazon-Reference.md`,
`AMAZON-AUTHOR-PAGES.md` and the TODO notes — that kind of detail goes in those notes, not in this repo's files. **`docs/PRINCIPLES.md`** — the distilled laws; consult when debugging
stalls, before refactors and releases, and when a lesson feels familiar.
