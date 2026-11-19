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

- **`gate-check.py`** (PreToolUse: Edit, Write, Bash, PowerShell) — the **pre-build gate**. On the first edit of shipped code (any shipped
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
  **Terminal commands too** (2026-11-16, TODO tooling task item 1 — decided Ron): the gate is wired for the Bash and
  PowerShell tools as well as Edit / Write, because twice in one week an agent moved version stamps with `sed` — the
  gate never saw it, and the brief saying "don't" failed both times. **`command_writes.py`** reads the command's TEXT
  for the files it writes; each is judged by the same `is_app_source()` as an edit, and a hit joins the same state
  machine (one ARMED flag per turn; an Edit and a `sed -i` in one batch see one checklist and are both refused; the
  re-sent batch passes). It reads: redirects (`>`, `>>`, `>|`, `&>`, `2>` — not `2>&1`, not `/dev/null`), `sed -i` /
  `--in-place`, `perl -i`, `awk -i inplace`, `tee`, `cp` / `mv` (incl. `-t DIR` and a folder as the destination), `dd
  of=`; PowerShell `Set-Content` / `Add-Content` / `Out-File` / `Tee-Object` / `New-Item` / `Copy-Item` / `Move-Item`
  (and their aliases), `>` and `[IO.File]::WriteAll…`; python / py / node one-liners and heredocs (`open(…, 'w'|'a'|'x')`,
  `Path(…).write_text`, `shutil.copy`/`move`, `os.replace`, `fs.writeFileSync` …); `bash -c` / `powershell -Command`
  read the same way; an earlier `cd` / `Set-Location` and Git Bash's `/c/…` paths are followed; wildcards are matched
  against the files there. Heredoc bodies are data (a `>` in a commit message is not a redirect); git's own commands
  (`checkout`, `mv`, `rm`) never trip it — but a redirect of git's output onto shipped code does (`git show X >
  storage.js` is a write). **It never guesses**: a target it can't tell passes — a path in a variable (`$f`, `$p`), a
  loop, `xargs` / `find -exec`, a script run from a file, `patch` / `git apply`; and a deletion (`rm`, `Remove-Item`)
  isn't an edit. Like the Edit gate, only shipped `.js` counts (pages and styles don't). Tests: `GATE-002`–`009`
  (`GATE-009`: settings.json's matcher really covers Edit, Write, Bash and PowerShell).
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
- **`setup-check.py`** (SessionStart, beside `gate-reset.py`; sprint 9, 2026-11-18 — TODO "Working-process safety net"
  item 1) — when the session's copy of the project isn't set up for the commit checks (below), a message Ron sees at once
  (framed in `!`) and a note telling Claude to say it first thing, with the fix: `git config core.hooksPath git-hooks`.
  Set up → silent. The rule and wording are `tools/setup_check.py`'s (serve.py prints the same at start-up); if that
  can't be loaded the hook says so (fail loud). Tests: `SETUP-001`–`004`.
- **`prod-guard.py`** (PreToolUse: Bash, PowerShell; sprint 10, 2026-11-19 — TODO "Remove the test-runner parts…",
  Decided item 7) — while the autonomy switch is on (the main folder's `.private/AUTONOMY.md` says `on` or `trial`,
  found from a working copy too), a push of main to prod (it deploys) is refused unless **Ron's newest typed message**
  in the conversation record says "push to prod" — the switch is usually on even while Ron releases, so his word lets it
  through. Only a push that reaches prod's main counts (`main`, `…:main`, `--all`, `--mirror`, no branch named, a bare
  `git push` — main's own remote is prod; `-C <path>` and longer command lines too); dev pushes and prod pushes of
  other branches pass. Switch off or missing → no say (the "ask" rule in settings still applies). When unsure — a switch
  file it can't read, no readable record, no message of Ron's — it refuses (it guards a deploy); a command that isn't a
  prod push is never stopped. Tests: `PROD-001`–`008`.
- **`/sitemap`** (`.claude/commands/`) — mechanizes the class-of-sites comb (two independent pivots).

## RW's commit checks (`git-hooks/` — run BY GIT, saved in the repo)

Moved 2026-10-15 from `.git/hooks/` (git never saves its own hooks folder) + `.claude/hooks/` (gitignored): before
that, losing this PC — or a fresh clone — silently lost every commit check. **One-time setup per copy of the project:
`git config core.hooksPath git-hooks`.** `git-hooks/pre-commit` is the thin wiring; each check is its own script.
Bypass (Ron's call): `git commit --no-verify`.

**A copy that isn't set up is warned LOUDLY** (sprint 9, 2026-11-18; TODO "Working-process safety net" item 1 —
decided Ron + UX 2026-10-22): the setting is local to git and a clone never brings it, so a fresh copy committed with no
checks at all and nothing said so. Now **`serve.py`** (every contributor runs it to test locally — Claude Code or not;
Ron at logon) prints a warning framed in `!` lines, in red where the console can, as the FIRST thing it prints — and
Claude's session start does the same (`setup-check.py`, above). Both say the one command that fixes it. One rule
(`hooks_path_problem`: set, and exactly `git-hooks`) and one wording, in **`tools/setup_check.py`**. A working copy
(`tools/copies.py`) is its own clone since 2026-11-19: `copies.py new` sets the copy's own `core.hooksPath git-hooks`
(an older worktree copy shares the main folder's). Tests: `SETUP-001`–`004`, `SERVE-002`, `COPY-001`.

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

- **What a copy is — its own clone** (since 2026-11-19; TODO "Working copies that can't break each other", item 1 — Ron:
  "Yes to belt and suspenders"). Until then a copy was a git worktree: another folder on ONE shared repository, so git's
  settings and history were shared — and on 2026-11-18 a test that set that repository to "bare" stopped git in every
  copy and the main folder for 13 minutes. Now each copy is a **local clone** of the main folder's repository: its own
  git settings, its own history, so a mistake damages only that copy. On the same drive git shares the stored history
  through **file links** (`git clone --local`), so a copy costs almost no disk (the repository is ~113 MB). The clone
  calls the main folder's repository **`main-folder`** (its remote) — that's how a copy finds the main folder
  (`copies.main_folder`, used by `backup_claude.py` and `shortcuts.py`; the private-values check reads the same remote).
  A clone brings no settings, so `new` gives it the main folder's own: `core.hooksPath git-hooks` (the commit checks
  on), `user.name` / `user.email`, and the main folder's ignore list (`.git\info\exclude` — `.private/` among it).
  **Stays shared, on purpose:** the test-slot folder (all copies together stay under the PC's browser limit) and the
  records' archive (below) — our own files, which our tools guard directly. Copies made before 2026-11-19 are
  worktrees: `list` and `remove` handle both kinds (`COPY-014`). Tests: `COPY-001`, `COPY-005`, `COPY-013` (a copy set
  to bare leaves the main folder's repository as it was).
- **Getting the work back:** an agent's commits live in its copy until **`merge_branches.py`** (run in the main folder)
  fetches each branch it merges from the copy that has it — fast-forward only; a branch that moved on both sides stops
  the merge, nothing touched (`copies.fetch_from_copies`, `MERGE-006`). One place, at the one moment the work is
  needed — nothing pushes into the main folder's repository behind its back. Until then the branch isn't in the main
  folder (so `sync_remotes.py` can't back it up yet); to look at an agent's work, run git in the copy
  (`git -C ..\ReaderWrangler-copies\<name> log` / `diff main-folder/sprint-N...`), or fetch it by hand: `git fetch
  ..\ReaderWrangler-copies\<name> <branch>:<branch>`.
- **`py tools/copies.py new <name> [--branch <b>] [--from <ref>]`** — a clone at
  `C:\Users\Ron\Projects\ReaderWrangler-copies\<name>` (beside the main folder) on branch `<b>` (default: the name; a new
  branch starts at `<ref>`, default HEAD, and lives in the copy; an existing one is checked out) — its only branch. **One
  copy per branch:** a branch the main folder or another copy is on is refused (a worktree had that from git). It
  **links** what git doesn't hold — `.venv`,
  `node_modules` (the commit checks' Babel), `tools/build/node_modules`, `relay/node_modules` — each a Windows directory
  junction to the main folder's (nothing copied), checks the **pytools submodule** out from the main folder's copy (no
  network; a link can't work there — its `.git` file points at `../.git/modules` by a relative path, and git then fails
  on every command), then runs **tier 1 in the copy**: READY only if it passes. Without the links, tier 1 fails in a
  copy (proven 2026-11-16: the build tests, the parse and saved-reads checks, the runner's screen-test rows) and tier 2
  can't start at all; serve.py won't start without pytools.
- **`py tools/copies.py remove <name> [--force]`** — refuses while the copy has anything uncommitted, or while it holds
  commits the main folder's repository doesn't have — on any of its branches or a detached HEAD (it fetches the main
  folder's branches and tags into the copy to compare; nothing in the main folder changes). The refusal names the merge
  that fetches them. `--force` removes it anyway — and says how many commits it threw away with it. (An older worktree
  copy: commits no other branch, tag or remote has; its branch is kept, as before.) Every link in the copy is removed
  FIRST, by itself: `git worktree remove` deletes THROUGH a junction (tried on a throwaway: the linked folder's files
  were gone). A clone is first renamed aside (`.removing-<name>-<when>`): Windows refuses that while a program has a
  file open there, so a busy copy is left whole — "nothing was touched" — never half-deleted; then its links come out
  and the folder is deleted. Afterwards it checks each of the main folder's linked folders still holds what it held,
  and says so loudly if not. **Every folder in the copy must be looked into first** (2026-11-16): one it can't read
  might hold a link it would miss, so it refuses — even with `--force` — naming each such folder, before anything is
  removed. Tests: `COPY-001`–`006`, `COPY-014`.
- **A removed copy keeps its test-run records and says where its time went** (2026-11-18, TODO tooling item 11.6; Ron:
  "Should the agents record where their time goes … so we can analyze that?"). A copy's records live in its own git
  folder (a clone's `.git\rw-test-results`; an older worktree's `.git\worktrees\<name>\rw-test-results`), which goes with
  the copy — so before anything is taken
  out, `remove` copies them (the `.json` records AND the failed files' kept outputs) into the main folder's records, in
  their own archive folder: **`.git\rw-test-results\copies\<name>-<YYYYMMDD-HHMM removed>\`**. The runner never reads
  it (`read_records` reads only its folder's own `.json` files — the stamp and the longest-first estimates never see a
  copy's runs) and its pruning (the newest 300) never deletes it (`COPIES_ARCHIVE` in run_tests.py). If they can't be
  kept, **nothing is removed, even with `--force`**, and it says where they still are. `new` notes when it made the copy
  (and the commit it started at, and when its tier 1 made it ready) in `rw-copy.json` in the copy's git folder — gone
  with the copy, its content kept in the archive's `time.json`; a copy made before that note existed gets git's own
  folder time, marked "estimated". Beside the records, `time.json` + `time.txt` (also printed at removal): made →
  removed (wall time); its test runs — how many, the minutes they covered (overlapping runs counted once), full or
  narrow (`--changed`, `--id`, `--tag`, `RW_CELLS` — since 2026-11-18 every narrowed run, the commit hook's `--changed`
  included, leaves its record on the copy's quick shelf, `rw-test-results\quick\`, archived with the rest and labelled
  `quick: <what narrowed it>`, COPY-010), passed / failed, files
  rerun alone after the machine's trouble, which full tier 1 was `new`'s own readiness run — each run on a line; its
  commits since it was made; and **everything else** = wall − test minutes: building, reading, thinking, waiting (the
  records can't tell these apart, and it doesn't pretend to).
  **The archive is kept bounded** (2026-11-18, TODO tooling 13.5 — it grew forever): after each removal, the newest
  `ARCHIVE_KEEP` (100) copies' folders are kept, and every one removed less than `ARCHIVE_MIN_DAYS` (30) days ago however
  many; the older rest is deleted, said (`· the archive trimmed: N older copies' records deleted …`). A folder's age is
  its `time.json`'s "removed", else the folder's own time (COPY-012).
- **`copies.py new`'s words** (2026-11-18, TODO tooling 13.12): a tier 1 that ended NOT PROVEN (exit 3 — no test failed,
  the machine too busy) is `NOT READY — tier 1 not proven … — the machine was too busy`, never "tier 1 failed" (COPY-011).
- **`py tools/copies.py report [--since YYYY-MM-DD]`** — for a sprint's post-mortem: one row per archived copy (name,
  branch, made, removed, wall, test minutes and their share, runs full / narrow, passed / failed) and the totals.
  Tests: `COPY-007`–`012`.
- **`py tools/copies.py list`** (also a double-click) — each copy (its own clone, or an older worktree — said), its
  branch and commit, anything uncommitted, and its test stamp (`run_tests.py --stamp` run there: each copy keeps its own
  run records).
- **What works inside a copy** (checked 2026-11-16; for clones 2026-11-19, `COPY-005`): the pre-build gate (above — a
  file is judged by the nearest folder with a `.git`, folder or file); the commit checks — `core.hooksPath git-hooks`
  (the clone's own setting, set by `new`) is relative, so git runs the COPY's `git-hooks/` from the copy's root (seen:
  the version guard refused, the name check and the build check ran, all on the copy's files); serve.py and the test
  runner use the copy's own `dist/`; screenshots go to `%TEMP%\rw-test-artifacts-<name>` (the main folder's stay in
  `rw-test-artifacts`); the private-values check reads the main folder's `.private/` notes, found through the clone's
  `main-folder` remote (a copy has none, and it silently checked credential shapes only). **Every copy's runs share one list of the processes our tools started**
  (`tools/starter.py`, 2026-11-18: `started-processes.json` beside the test slots, changed under the slots' lock): a
  process whose run is still going in another copy is never called a leftover; one whose run has ended is named in a
  banner at the start of the next run anywhere on the PC, with a `NEEDS YOUR ATTENTION:` line (TESTING.md §4).
  `py tools/starter.py` shows it on its own.
- **serve.py's rebuild while another server reads the file:** Windows refuses to swap a new `dist/` copy in over a file
  another program is reading. `tools/build.py` retries for ~2 s; still refused, serve.py serves the copy that's there and
  logs `REBUILD NOT SWAPPED IN` (the next request tries again) — before, the request died. Tests: `BUILD-010`,
  `SERVE-001`.
- **`py tools/merge_branches.py <branch> … [--into <target>] [--no-squash] [--no-test]`** — run in a folder ON the
  target branch (the main folder), clean; first each branch being built in a copy is fetched from it (above); the target
  defaults to the folder's branch — the sprint's, `sprint-N` (made from main when a
  sprint starts; Ron, 2026-11-16 — it replaced the long-lived `main-prime`) — and is never `main`. On a scratch branch
  `merging/<target>`, each branch in turn is squash-merged as one commit (a task's way into the sprint's branch;
  `--no-squash`: a merge commit). Never hand-merged — settled by the script, after every
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
  `--no-test` lands and prints `NOTHING WAS PROVEN`. Tests: `MERGE-001`–`006` (real git in throwaway repositories).

## Backing up Claude's memory and settings (`tools/backup_claude.py`; sprint 9, 2026-11-18)

TODO "Working-process safety net", items 2–3 (decided Ron + UX 2026-10-22). The pieces of the working process that live
OUTSIDE the repository were backed up by hand — and the hand slipped a week (Oct 15 → 22: 56 files of 68, 18
differing). **`py tools/backup_claude.py`** is a **release-checklist step** (not a per-turn hook — a commit per turn is
noise), so the backup is never more than one release behind:

1. **Claude's memory** (`~\.claude\projects\<the project's folder name>\memory\*.md`) → `.private\claude-backup\memory\`
   — a **mirror**: a memory file deleted is deleted in the backup too (git's history keeps it). Only `.md` files; an
   empty or missing memory folder is refused, so the backup is never emptied by mistake.
2. **`.claude\settings.local.json`** → `.private\claude-backup\settings.local.json`.
3. **Claude Code's global settings** (`~\.claude\settings.json` — wires the timestamp hook; no secrets, personal paths)
   → the **Projects repository** (`C:\Users\Ron\Projects`, private, Ron-L/projects-root) as **`claude-settings.json`**,
   beside `stamp.py` and `CLAUDE-TOOLING.md` (the `claude-` name sorts with CLAUDE.md and says whose settings — a bare
   `settings.json` there would read as the folder's own). That repository's `.gitignore` is an allow-list: the first run
   adds `!/claude-settings.json`, or git would never see it. (Ron gave permission for this repository, 2026-11-18.)

Then each repository (`.private` and Projects) **commits ONLY the backup's files** — anything else staged or untracked
there is left as it is — with a message counted from what git staged (with `core.autocrlf` a copy can differ from the
checked-out file in line endings only; git sees no change, so no commit is claimed), and **pushes to `origin`**. Nothing
changed → no commit. A push the remote refuses is said loudly (`PUSH FAILED`), the commit kept — never forced; one
repository failing doesn't stop the other; exit 1 if anything failed. It finds the **main** folder from a working copy
(`copies.main_folder`). Restoring on a new PC: `.private/claude-backup/README.md`. Tests: `CBAK-001`–`007` (throwaway
repositories with local bare stand-ins for GitHub).

## The "open" shortcut (`tools/shortcuts.py`, `serve.py --open`; sprint 9, 2026-11-18)

TODO "The 'open' shortcut: start serve.py if needed and open the app" (decided Ron + Claude 2026-10-31; adapted from the
utilities project's `tools/shortcuts.py`). **`py tools\shortcuts.py`** writes `Start Menu\Programs\ReaderWrangler
(local).lnk` (Windows search: "ReaderWrangler"; "(local)" tells it apart from the site): the py launcher running
`"<main folder>\serve.py" --open`, in the main folder (never a working copy — it is removed when its task is done), with
the app's icon. `--folder <f>` writes it elsewhere (the tests use a temporary folder). Rewriting it is harmless. Ron's
hand-made "ReaderWrangler Server" shortcuts (Start menu + Startup — they start the server without opening the page) are
left alone.

**`serve.py --open`** opens `http://localhost:<port>/readerwrangler.html` in the default browser — a tab, not an app
window (the bookmarklets live on the bookmarks bar) — starting the server first only if nothing is on the port: our
server already there (it answers with the app's page) → just the page, the server left as it is; another program →
says so, opens nothing. The open half only — no restart or shutdown (serve.py only serves files and rarely changes, and
it listens on the home network on purpose: an off switch any device there could press gains nothing). Tests:
`SHORTCUT-001`–`003`, `SERVE-003`–`007` (never a real Start menu, never a browser — the opener is a stand-in).

## Writing a file whole (`tools/whole_file.py`; Law 22, 2026-11-18)

One routine: a scratch copy beside the file, swapped in, retried for ~2 s while Windows refuses the swap (another program
reading the old copy), no scratch copy left on failure. `tools/build.py` (dist/), `tools/browser_level.py`'s `save` (and
through it `tools/test_costs.py`) and `tools/backup_claude.py` all write through it; before, build.py and browser_level.py
each had their own copy of the loop. Tests: `WHOLE-001`–`007`, `BUILD-010`.

## Related
- The gate's checklist content + the debugging law it now carries: `docs/PRINCIPLES.md` (Laws + the
  `GATE-CHECKLIST` block).
- Global (cross-project) tooling: `CLAUDE-TOOLING.md` at the Projects root.
