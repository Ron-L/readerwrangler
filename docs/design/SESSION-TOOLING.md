# RW Session Tooling & the single-source hook pattern

_ReaderWrangler's project-**local** Claude Code tooling (`.claude/`, saved in the repo; only `settings.local.json` is
gitignored) and the reusable
**pattern** behind it. Global tooling (e.g. the per-turn timestamp stamp) lives at the Projects root —
see `CLAUDE-TOOLING.md` there. Established 2026-09-30._

## The pattern (worth considering for any project)

**A hook is a thin mechanism; the human-readable content it enforces lives in a versioned single source,
and the hook PULLS it at run time.** And **a hook that can't reach its source must fail LOUD** — announce
the break — never silently degrade, because a silent fallback lets the mechanism rot unnoticed.

Why: content duplicated between a hook and the docs *drifts*. Earned 7.18.0 — the pre-build checklist had
drifted across three copies (the hook, the PRINCIPLES intro, and each Law's enforcement line). We made
`docs/PRINCIPLES.md` the one source (a `GATE-CHECKLIST` block) and turned the hook into a dumb printer that
pulls that block; edit the checklist once and the gate auto-syncs. If the block/file/markers break, the
gate prints a loud `SOURCE MISSING` alarm instead of a stale checklist.

## RW's session hooks (`.claude/hooks/`, saved in git; wired in `.claude/settings.json`)

- **`gate-check.py`** (PreToolUse) — the **pre-build gate**. On the first edit of shipped code (any shipped
  `.js` — `is_app_source()` asks `git-hooks/shipped_paths.py`, the one "is this shipped?" rule shared with the version
  guard and the style build, so `logkit/` and `relay/` are covered and `dist/` never is; widened 2026-10-08, shared
  2026-11-11) each turn it prints the checklist and refuses that batch's app edits; re-sending them (the next batch) proceeds.
  **Whole-batch refusal — a three-state switch moved by real signals** (2026-10-19, Ron + Claude): **ARMED** (set by
  `gate-reset.py` at each turn's end / session start) → the first app edit flips it to **REFUSING** and gets the
  checklist; **every** app edit while REFUSING is refused, however the batch streams or is timed → **`gate-batch-end.py`
  on PostToolBatch** (fires once a whole batch has finished, before the next model call — probed 2026-10-19) flips it
  to **CLEAR**, so the re-send (the next batch) goes through. The reset also clears a leftover REFUSING. Why: refusing
  only the first edit let the rest of a batch land (alpha.62; twice on 7.21.2). Two earlier fixes GUESSED where a batch
  ends — a 5-second timer, then the session transcript's message ids — and both failed (7.23.0-alpha.2, 7.22.1-alpha.3)
  because edits stream in and are written with unpredictable timing; that guessing code is deleted. A hook can't
  "hold" an edit while Claude thinks (Claude only sees a hook's message in a call's result), so the checklist must
  arrive by refusing — the switch makes the refusal whole. The
  checklist is **not** in the hook — it's pulled from the `GATE-CHECKLIST` block in `docs/PRINCIPLES.md`
  (single source). Unreadable → loud `CHECKLIST SOURCE MISSING` alarm + a minimal core.
  **In a working copy too** (2026-11-16, below): a file is judged by the working copy that HOLDS it — the nearest folder
  above it with a `.git` and `git-hooks/shipped_paths.py` — not by the session's folder. Before, an edit to
  `readerwrangler.js` in a copy counted as "outside this repo" and went through while the gate was armed (seen live).
  The hooks are wired in `.claude/settings.json` by `$CLAUDE_PROJECT_DIR`, so a session started in the main folder runs
  the main folder's hooks for every copy's files, and a session started in a copy runs the copy's. Tests: `GATE-001`.
- **`gate-batch-end.py`** (PostToolBatch) — REFUSING → CLEAR once the refused batch is over (2026-10-19).
- **`gate-reset.py`** (Stop/SessionStart) — re-arms the gate's per-turn flag (a temp-dir file keyed by
  session id) so the checklist lands exactly once, at the planning→build boundary.
- **`survey-check.py`** (UserPromptSubmit; Ron, 2026-11-03) — tools for Claude (skills, plugins, tool servers) appear
  faster than Claude's training data keeps up with, so the survey of what RW should use (`docs/design/TOOL-SURVEY.md`)
  is re-run **every 4 weeks**. **The report IS the state** — its `Next due:` line: once reached, the hook asks Claude to
  raise the refresh at a natural break and offer **`/tool-survey`** (`.claude/commands/tool-survey.md`, which holds the
  research brief so every run asks the same questions and reports what changed). "Not now" = Claude moves the `Next
  due` line (the edit is the snooze), so it doesn't nag every message. A missing report or an unreadable line is
  reported loudly.
- **`relay-check.py`** (UserPromptSubmit; Ron, 2026-10-30) — the relay mails its daily summaries at 23:55 UTC. On any
  prompt where the newest nightly (yesterday, UTC) isn't yet in **the relay trend file** (kept with the TODO notes), it tells Claude to read
  the missing nights, add one row per relay per night, and report (one line if healthy; details + the trend if not).
  **The trend file IS the state** (its last `run=nightly` date) — so the reminder repeats until the rows are really
  added, and can't be "done" by being shown once. Days away from RW are caught up whenever Ron is next here (up to 31
  nights; beyond that the note says so). On-demand rows don't count. A missing trend file is reported loudly. Claude
  reads through the ONE Gmail filter Ron allowed (`from:alerts@readerwrangler.com subject:"Daily usage summary"`,
  memory `feedback_gmail_relay_only`); the hook only reminds. Why a hook: "remember to check each evening" doesn't
  survive a compaction. A dedicated inbox later (TODO "Relay worker: one release…", item 8) changes only the filter.
- **`/sitemap`** (`.claude/commands/`) — mechanizes the class-of-sites comb (two independent pivots).

## RW's commit checks (`git-hooks/` — run BY GIT, saved in the repo)

Moved 2026-10-15 from `.git/hooks/` (git never saves its own hooks folder) + `.claude/hooks/` (gitignored): before
that, losing this PC — or a fresh clone — silently lost every commit check. **One-time setup per copy of the project:
`git config core.hooksPath git-hooks`.** `git-hooks/pre-commit` is the thin wiring; each check is its own script.
Bypass (Ron's call): `git commit --no-verify`.

- **`version-guard.py`** — refuses a commit that stages
  shipped code without moving its version stamp: `readerwrangler.js`→`ORGANIZER_VERSION`,
  `mobile.js`→`MOBILE_VERSION`, `relay/relay-worker.js`→`WORKER_VERSION` (shown in the relay's emails), and the
  module `.js` files + `readerwrangler.css` → their `?v=` cache-buster in `readerwrangler.html`. **A release sweeps the
  help notes** (2026-10-20): a commit that moves `APP_VERSION` is refused unless `docs/design/SUPPORT-KB.md`'s stamp says
  "through release <that version>" — the stamp used to be a promise nothing checked (7.21.3 went unswept for 4 days).
- **`check-toc.js`** (when `TODO.md` is staged; checks the STAGED copy) — refuses a
  `TODO.md` whose table of contents (between `<!-- TOC -->` markers, built by the VS Code extension "Auto Markdown
  TOC" on save) doesn't match its headers by text and depth. Link targets aren't compared (the extension owns them).
  Earned 2026-10-14 when the TODO became one header per task: edits that don't go through a VS Code save leave it stale.
  **Since 2026-10-21 it also refuses a task without its ID line** (`<!-- id YYYYMMDD-HHMM -->` right under the header;
  `; merged …` on a task that absorbed others) **or a repeated ID** — `tools/backlog_report.py` follows tasks through
  the TODO's git history by these IDs to chart the backlog's hump (arrivals vs completions, the launch burn-down).
- **`check-names.js`** (when any `.js`/`.html` is staged) — Babel scope analysis of
  `readerwrangler.js` + `mobile.js`: refuses any identifier that is neither bound in scope, a browser/CDN global, nor
  defined by `readerwrangler.html` (its inline scripts + every local `<script src>`, derived automatically). Also
  refuses an inline script that doesn't parse. Earned 2026-10-06: an edit joined `const shareBtnRef = …` into a `//`
  comment — it parsed, then crashed the book details window; the first run also found a `readerwrangler.html` inline
  script broken since 7.4.0 (raw line break in a string — the load-error capture had never run). Needs
  `npm i --no-save @babel/core @babel/preset-react`; exits 2 (loud) if missing.

## Working copies and merging branches (`tools/copies.py`, `tools/merge_branches.py`; 2026-11-16)

TODO "Faster sprints", items 3–4 (working copies: Ron's idea). One agent builds in one copy while Claude reviews and tests
in another; independent tasks build at once, each on its own branch, and a script merges them.

- **`py tools/copies.py new <name> [--branch <b>] [--from <ref>]`** — a git worktree at
  `C:\Users\Ron\Projects\ReaderWrangler-copies\<name>` (beside the main folder) on branch `<b>` (default: the name; a new
  branch starts at `<ref>`, default HEAD; an existing one is checked out). It **links** what git doesn't hold — `.venv`,
  `node_modules` (the commit checks' Babel), `tools/build/node_modules`, `relay/node_modules` — each a Windows directory
  junction to the main folder's (nothing copied), checks the **pytools submodule** out from the main folder's copy (no
  network; a link can't work there — its `.git` file points at `../.git/modules` by a relative path, and git then fails
  on every command), then runs **tier 1 in the copy**: READY only if it passes. Without the links, tier 1 fails in a
  copy (proven 2026-11-16: the build tests, the parse and saved-reads checks, the runner's screen-test rows) and tier 2
  can't start at all; serve.py won't start without pytools.
- **`py tools/copies.py remove <name> [--force]`** — refuses while the copy has anything uncommitted, or while its branch
  has commits no other branch, tag or remote has; `--force` removes it anyway. **The branch is always kept.** Every link
  in the copy is removed FIRST, by itself: `git worktree remove` deletes THROUGH a junction (tried on a throwaway: the
  linked folder's files were gone). Afterwards it checks each of the main folder's linked folders still holds what it
  held, and says so loudly if not. **Every folder in the copy must be looked into first** (2026-11-16): one it can't
  read might hold a link it would miss, so it refuses — even with `--force` — naming each such folder, before anything is
  removed. Tests: `COPY-001`–`006`.
- **`py tools/copies.py list`** (also a double-click) — each copy, its branch and commit, anything uncommitted, and its
  test stamp (`run_tests.py --stamp` run there: each copy keeps its own run records).
- **What works inside a copy** (checked 2026-11-16): the pre-build gate (above); the commit checks — `core.hooksPath
  git-hooks` is shared config and relative, so git runs the COPY's `git-hooks/` from the copy's root (seen: the version
  guard refused, the name check and the build check ran, all on the copy's files); serve.py and the test runner use the
  copy's own `dist/`; screenshots go to `%TEMP%\rw-test-artifacts-<name>` (the main folder's stay in
  `rw-test-artifacts`); the private-values check reads the main folder's `.private/` notes (a copy has none, and it
  silently checked credential shapes only).
- **serve.py's rebuild while another server reads the file:** Windows refuses to swap a new `dist/` copy in over a file
  another program is reading. `tools/build.py` retries for ~2 s; still refused, serve.py serves the copy that's there and
  logs `REBUILD NOT SWAPPED IN` (the next request tries again) — before, the request died. Tests: `BUILD-010`,
  `SERVE-001`.
- **`py tools/merge_branches.py <branch> … [--into main-prime] [--no-squash] [--no-test]`** — run in a folder ON the
  target branch, clean. On a scratch branch `merging/<target>`, each branch in turn is squash-merged as one commit (the
  sprints' way into `main-prime`; `--no-squash`: a merge commit). Never hand-merged — settled by the script, after every
  branch, even when git merged them cleanly: **`dist/`** (rebuilt by `tools/build.py`), **`docs/design/MESSAGE-CODES.md`**
  (`tools/message_codes.py`), **TODO.md's table of contents** (only the table, rebuilt from the headers with the
  extension's link rule — the tasks are real content), and **the version stamps**: every stamp a branch moved
  (`ORGANIZER_VERSION`, `MOBILE_VERSION`'s `-alpha.N`, each `?v=`) becomes a fresh alpha above the highest
  `ORGANIZER_VERSION` among the target and every branch given; ORGANIZER_VERSION moves with them. One alpha per commit, so
  the last commit's version is above everything merged. A file whose only conflict is a stamp line is merged again with
  the stamps hidden. **Any other conflict stops the run**, naming each file, the merge left in place: resolve, `git
  add`, then `--continue` (or `--abort`: back on the target exactly as it was). Every commit goes through the commit
  checks. Then **tier 1 and tier 2 in full on the merged result**, committed on the scratch branch, so `run_tests.py
  --stamp` must say PROVEN for exactly the commit that lands; only then is the target fast-forwarded and the scratch
  branch deleted. A failure leaves the target untouched (fix and commit on the scratch branch, then `--continue`).
  `--no-test` lands and prints `NOTHING WAS PROVEN`. Tests: `MERGE-001`–`004` (real git in throwaway repositories).

## Related
- The gate's checklist content + the debugging law it now carries: `docs/PRINCIPLES.md` (Laws + the
  `GATE-CHECKLIST` block).
- Global (cross-project) tooling: `CLAUDE-TOOLING.md` at the Projects root.
