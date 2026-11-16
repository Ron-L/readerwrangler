# Testing — the regression library, and how it grows

_Decided 2026-11-04 (Ron + Claude). The umbrella over every test in ReaderWrangler: what kinds there are, when each
runs, how the library grows task by task, and the rules that keep it trustworthy. Supersedes the "out of scope —
permanently" line of PRELAUNCH-TEST-GATE.md for screens, dialogs, drag-and-drop and menus: the browser driver makes
them testable, and with Claude writing the tests the cost that justified skipping them is gone. That doc's suites stay
the pre-launch data gate (task "All the pre-launch data tests pass")._

---

## 1. The rule

> **"If you don't have a test case, you can't prove you fixed it."** — Ron

The regression library is built **gradually, from the work** — never written all up front. Each task adds the tests
that prove it; each bug fix adds the test that would have caught it. Over time the library becomes the guarantee that
nothing that once worked silently stops working.

**When a test covers one case of a class** (one ownership kind, one filter), **it covers the whole class if that's
cheap** — one test with a row per case, the rows taken from **the same list the code uses**, so a new case is tested
the day it's added. Each row needs its expected result; **a case with no expected result written fails the test**
(a default "missing — write its expectation" failure), so nobody can add an ownership kind or a filter without saying
how it should behave. (Ron + Claude, 2026-11-04 — the fetcher's hand-kept list once missed library loans and Audible
Plus for exactly want of this.)

## 2. Two levels — test at the lowest one that can catch the problem

1. **Function tests** — fast, sturdy, most of the library. For logic: merging, the book-field table, the ownership
   rules, date labels, the key format and its check characters, Auto-Organize, the overlay stack. Plain Node files in
   `test/` (the five that exist today).
2. **Screen tests** — through the browser driver (Playwright for Python, the installed Chrome — Ron's browser — a throwaway profile, scrollbars shown).
   Only for what only the screen can show: what the Delete key targets, focus staying inside a window, drag labels,
   two tabs catching up, a menu item disabled rather than missing.

A bug in a function caught by a screen test costs a hundred times the runtime and breaks whenever a button moves. When
a screen test is the only way to catch something, consider first whether the logic should be lifted into a function
that a function test can reach.

**Free with every screen test:** the logging module (7.26.0, docs/design/LOGGING.md) is switched on in the
driver's browser, so **any unexpected error fails the run** — every screen test also checks "nothing went wrong
underneath".

## 3. Tiers — when each runs

| Tier | What | When | Budget |
|---|---|---|---|
| **1** | Function tests + the commit checks (names, parse, versions, private values, TOC…) | **Every commit, automatically** — only the tests covering the staged files | seconds (≤ ~10 s) |
| **2** | Screen tests | **Before every alpha Claude hands Ron** — Ron is never the first to find a regression | a few minutes (≤ ~5 min) |
| **3** | Relay tests — against a local relay **the runner starts and stops itself** (dev only as a final check, by `--relay-url`) | When relay code changes; before any worker deploy | ~1½ min |
| **all** | Every tier — `py tools/run_tests.py --tier all --release`: **a skipped or set-aside file fails a release run**, named with why | **Before every release** (release checklist step) | |

Plus a short **manual list per release** (§8) for what can't be automated.

**While building — narrow, then wide** (Ron, 2026-11-13: "that speedup makes perfect sense"): each fix → test round runs
only the tests for what's being built — its own IDs (`--id`; in a file split into shards, `--id CELL-005 --id CELL-019`
runs just those cells, as `RW_CELLS=CELL-005,CELL-019` does — §4), the function tests that cover the file
(`--changed`). Once those pass: the **full tier 1 + tier 2, once, before the alpha is committed** — the regression check.
The full run is never skipped; it just isn't repeated on every try.

**At review, check the stamp instead of rerunning** (TODO "Faster sprints", 2026-11-16): every run leaves a record of the
commit it ran on (§4), so an agent's "it passed" is a claim a machine can check — `py tools/run_tests.py --stamp <commit>`
says PROVEN only for a full tier 1 + tier 2 pass on exactly that commit with nothing uncommitted (tier 3's latest run is
shown beside them, for information — §4). NOT PROVEN means the
run is read (a failure, §7) or done — not taken on trust. **One full run of Claude's own before the sprint's branch
(`sprint-N`) goes to main for release.** `tools/merge_branches.py` makes that run part of the merge (2026-11-16): branches built in
parallel are merged on a scratch branch, tier 1 + tier 2 run on the merged result, and the target moves only when its
stamp is PROVEN — two changes can merge cleanly and break together (docs/design/SESSION-TOOLING.md).

## 4. The library — layout, IDs, tags, the runner

- **Files:** `test/*.test.js` (function, Node), `test/ui/test_*.py` (screen, Playwright for Python), `relay/test-*.mjs`
  (relay). Shared fixtures in `test/fixtures/`.
- **Every test has a stable ID** in its name — `AREA-NNN` (e.g. `MERGE-012`, `DELKEY-003`, `TABS-001`): failures,
  TODO tasks and post-mortems can name a test, and an ID never changes when its wording does.
- **Every test file declares, in its header:**
  - `tags:` — its areas (e.g. `merge, import`) and its tier;
  - `covers:` — the source files it tests (e.g. `bookMerge.js, storage.js`).
  The `covers:` lines are the **one source** for "which tests does this change need?" — tier 1 picks its tests from
  them, and nothing else keeps a separate list.
- **The runner — one command, in Python** (`tools/run_tests.py`; Ron's scripts rule): `--tier 1|2|3|all`,
  `--tag <area>`, `--id <ID>`, `--changed` (the tests covering what changed). With no `--tier`: tier 1 — except `--id`
  and `--tag`, which look in every tier (2026-11-12: a screen test's ID said "No tests match"; RUN-025–029); `--changed`
  stays tier 1. One summary at the end; a screen test's
  failure saves a screenshot and the console to Claude's scratch folder. The commit hook calls it with `--changed`.
- **`--id` picks a file only where it names the ID as a test** (2026-11-16; it picked any file whose text held the ID —
  `--id CELL-005` also ran `test/test_run_tests.py`, ~25 s, where it is sample data, and `--id CELL-001`
  `test/gestureTable.test.js`, where a comment names it). Every file names a test by its ID as a whole quoted string,
  first in what follows: **the first argument of the call that runs it** — `test("ID", …)` / `t('ID', …)` (both
  harnesses), `differs_today("ID", …)`, `add("ID", …)` (test_cells.py), `row("ID", …)` / `check("ID", …)` (files with
  their own helper) — **or the first item of its row in a table**, `("ID", …)` (test_check_parse.py,
  test_message_codes.py, test_layout.py). A comment, a message or data naming it doesn't count. One lookup
  (`test_names` in the runner), used by `--id` and by its narrowing of a sharded file. A new test file keeps to it — a
  table of IDs puts each ID first in its row (test_layout.py, 2026-11-16). Checked against every file: for each tier-1
  file, the IDs found are exactly the IDs it prints (`test_run_tests.py` also names the sample tests it writes); for
  tier 2, exactly the quoted IDs each holds. `py tools/run_tests.py --id CELL-005 --list` → test_cells.py alone. Tests:
  `RUN-063`, `064`.
- **In parallel, under a machine-wide limit** (2026-11-16): tier 1 and tier 2 files run several at once — `--jobs N`
  (default: the limit below; `--jobs 1` = one at a time, as before), the longest first by each file's time in the last
  record. **Every screen-test file holds one of the PC's test slots while it runs** (`tools/test_slots.py`): 4 in total
  for every run on this PC, whatever working copy it's in (`RW_TEST_SLOTS` overrides — every run should use the same
  number). A slot is a file in `%TEMP%\rw-test-slots` held with an OS file lock, so a run that crashes or is stopped
  frees its slot by itself. A run waiting for one prints `· <file> waits for a test slot — all 4 on this PC are in use`
  and who holds each (process id, folder, file, since when). Tier 3 stays one file at a time (its own local relay).
  Output: one line per file as it finishes, with its time; a failing file's details together, never interleaved; the
  same `Tests: N file(s) passed, M failed` line at the end. Before the screen tests start, the runner builds `dist/`
  once — otherwise each test's own serve.py would rebuild the same stale files at the same time.
- **One file split across processes — `shards: N`** (2026-11-16): `test/ui/test_cells.py` alone set tier 2's time
  (~5½ min, the 24 other files finishing alongside it). A file whose header says `shards: N` answers `--list-cells` with
  its cell IDs (one a line, nothing started) and runs only the cells named in `RW_CELLS`; the runner runs it as N
  processes at once — every Nth cell each — **each holding its own test slot**. It is still one file: passed only if
  every shard passed, one line with the counts summed (`… — 3 shards`, and each shard's time), a failing shard's lines
  together under it with its `RW_CELLS=…` to rerun just that shard, one entry in the record (each shard's cells, time and
  result inside it) — so `--stamp` judges it as one file. A file that can't list its cells fails loud; more shards than
  cells → one process per cell; `RW_CELLS` already set (a narrow run) → one process, as asked. **`--id` naming cells of
  a sharded file** (2026-11-16; it ran the whole file before) → one process with `RW_CELLS` = exactly those cells, in the
  file's order — `py tools/run_tests.py --id TOAST-006` runs that one cell (and CELL-058, the console check every
  process of test_cells.py runs); `--list` shows `· only TOAST-006 (--id), one process`. `--id` picks the file as it
  picks every file — where it names the ID as a test (above); a sharded file naming the ID as a test that is no cell of
  it (CELL-058, the console check) is left out, with a line saying so; one naming it only in a comment isn't picked at
  all. With `RW_CELLS` already set, `--id` leaves the file's cells as given.
  A sharded file's cells must not depend on each other (test_cells: each cell restores the fixture). Tests:
  `RUN-054`–`056`, `060`–`062`, `064`.
  Isolation (checked 2026-11-16): each screen-test file has its own serve.py on its own free port — and checks the port
  is served by ITS server (by process id), trying another if a parallel file's server took it in between — its own
  throwaway browser profile, its own local relay (free ports, a throwaway store) when it uses one, and files only in
  folders of its own (`tempfile.mkdtemp`); screenshot names are distinct per file.
- **Working copies** (`tools/copies.py`, 2026-11-16): a git worktree beside the main folder, with `.venv` and the
  `node_modules` folders linked in from the main folder — every tier runs there as here, with the copy's own `dist/`, its
  own run records (so its own stamp), and its own screenshots folder: `%TEMP%\rw-test-artifacts-<copy name>` (or
  `RW_TEST_ARTIFACTS-<copy name>`), so two copies running the same file don't overwrite each other's. The machine-wide
  test slots are shared by every copy. Details: docs/design/SESSION-TOOLING.md.
- **Results stamped with their commit** (2026-11-16): every run except the commit hook's `--changed` (and `--list`)
  leaves a record — the commit it ran on (and again at the end: a commit made during the run is caught), what was
  uncommitted before and after (changed tracked files, and untracked files git doesn't ignore), what ran (tier, `--id`,
  `--tag`, `--release`, jobs), **the environment variables that change a run, each with its value** (`RUN_ENV` in the
  runner — found by searching the tests, their helpers and the runner for `os.environ` / `process.env`; a new one is
  added there), each file's result, counts and time, start and end, the overall result. Kept OUTSIDE the
  working tree, per working copy: `git rev-parse --git-path rw-test-results` (`.git/rw-test-results` here; a git
  worktree gets its own, under `.git/worktrees/<name>/`). The newest 300 are kept.
  `py tools/run_tests.py --stamp [<commit>]` (default HEAD) runs nothing; it prints **PROVEN** (exit 0) only if tier 1
  AND tier 2 each ran in full on exactly that commit (`--tier 1` and `--tier 2`, or `--tier all`; a run narrowed by
  `--id` / `--tag` doesn't count, nor one with a file of that tier set aside — below), every file passed, nothing
  skipped, nothing uncommitted — the LATEST run of each tier counts, so a later failure isn't outvoted by an earlier
  pass. Otherwise **NOT PROVEN**, with why (exit 1). **Tier 3 is shown too** (2026-11-16: after a `--tier all --release`
  run the stamp showed only tiers 1 and 2): one line for tier 3's latest run on that commit — `· tier 3: passed` /
  `failed` (each failing file, or the local relay's problem, under it) / `not run` — **information only**: PROVEN still
  means tiers 1 and 2 (tier 3 needs a relay and isn't part of every review), so a release run's stamp shows all three:

      Test results for 3f2a9c1d7e40 (7.31.0: release stamps …)  — records: …\.git\rw-test-results
        ✓ tier 1: 29 of 29 file(s) passed — run 2026-11-16 14:02:11 → 14:09:40 (--tier all)
        ✓ tier 2: 26 of 26 file(s) passed — run 2026-11-16 14:02:11 → 14:09:40 (--tier all)
        · tier 3: passed — 2 of 2 file(s) passed — run 2026-11-16 14:02:11 → 14:09:40 (--tier all --release) — information only — the stamp proves tiers 1 and 2
      PROVEN — tier 1 and tier 2 passed in full on exactly this commit, with nothing uncommitted.

  The tier 3 line starts with `·`, never `✗` — `tools/copies.py` lists a NOT PROVEN stamp's `✗` lines as its why.
  Tests: `RUN-070`, `071`.
  **A narrowing variable counts like `--id`** (2026-11-16: a run with `RW_CELLS` set ran a few cells and the stamp said
  PROVEN): `RW_CELLS` (test_cells.py runs only the cells it names) makes the whole run narrowed — it counts for neither
  tier, and NOT PROVEN names it with its value; the run itself says so at its end. (`RW_CELLS` the runner sets itself —
  a shard's share, or the cells `--id` named — goes only to that file's process, never in the record's variables: an
  `--id` run is already narrowed by `--id`, RUN-060.) The others are recorded and shown on
  the stamp's line but don't narrow — every test still runs: `RW_HEADED` (the browser shown, slowed), `RW_BROWSER`
  (chrome or msedge), `RW_TEST_ARTIFACTS` (where screenshots go), `RW_TEST_SLOTS` (the PC's limit), `RELAY_URL` (tier 3's
  relay; tier 3 isn't part of the stamp's verdict). Records written before this have no variables and are read as full
  runs.
  Tests: `RUN-035`–`051`, `058`, `059`.
- **Tier 3 brings its own relay** (`tools/local_relay.py`, 2026-11-12): with no `--relay-url`, the runner starts
  relay-worker.js in wrangler's local emulator (`wrangler dev --env dev --local`) on a free port with an empty,
  throwaway store, waits for its "Ready on" line (60 s, else it fails with the end of wrangler's output), runs the relay
  files against it, then stops every process it started **by exact id** (the whole tree) and **checks**: each one gone,
  both its ports no longer listening. Anything left fails the run, named by id — and is left running, since the runner
  can't show it started it. `--relay-url <address>` runs against a relay you started instead (no start, no stop). Never
  the dev or production relay by default. **The screen tests' relay is the same one** (`App(relay=True)`, 2026-11-16 —
  Law 22; rw.py's own copy, which stopped its tree with `taskkill /T`, is gone). **"Ready" is proven against its own
  process:** its ready line must name its port and only its own processes may listen there (by id) — the old screen-test
  relay took any answer on the port, so with files in parallel another run's relay could answer for it. Another process
  on its port that started BEFORE it (proven not its own) is left alone and the relay starts again on new ports, as it
  does when wrangler stops before it's ready (what a taken port does to wrangler); any other fails loud, named by id,
  left running, never retried (it may be one of its own that escaped). Tests: `RUN-016`–`021`, `052`, `053`, `057`.
- **`--release` — skipped is not passed** (2026-11-12; 7.28.0: "31 passed, 2 skipped" read as a pass): with it, any
  file that didn't run fails the run, each named with why. One function decides a skip (`skip_reason` in the runner);
  nothing skips today — tier 3 brings its own relay, and a missing tool fails loud — so this guards any skip added later.
  **And a test still marked "differs today" fails a release run** (7.30.0, sprint 4): `differs_today` (test/ui/harness.py)
  marks a decided behavior that isn't built yet — expected while building, never in a release. The run names each such
  test and its file (`RUN-033`, `034`). **And so does a file set aside** (below).
- **A test file set aside on purpose — `skip: <TODO id> — why`** (2026-11-16; Ron, 2026-11-12: "a good idea, used
  judiciously"): §7 says a flaky test is fixed — or set aside, with a TODO — the same day; this is how the runner
  understands "set aside". A header line beside `tags:` / `covers:` / `shards:`:

      # skip: 20261116-0900 — fails one time in ten (the File menu not found); set aside until fixed

  The runner doesn't run the file and says so plainly at the end of every run — the commit hook's too:
  `Tests: 30 file(s) passed, 0 failed, 1 set aside` then `set aside: test/ui/test_x.py — 20261116-0900 — why`
  (`--list`: `- tier 2  set aside: …`). **The TODO id must be a task in TODO.md** (the id on the line under its header,
  read by tools/backlog_report.py's reader) — the task that fixes it; a `skip:` line naming no task, or without both the
  id and the why, is a header problem: the file fails, loud. **A `--release` run refuses** while any file is set aside,
  naming each with its TODO id — a set-aside test blocks the next release until it's fixed and its `skip:` line is
  gone. **The stamp counts the run as not a full run of that file's tier** — NOT PROVEN, naming the file and its task
  (`its latest tier 2 run … was narrowed by set aside: test/ui/test_x.py (TODO 20261116-0900 — why)`); the other tier
  is judged on its own. Without `--release` the run itself passes. Tests: `RUN-065`–`070`.
- **The project's own Python for screen tests** (Ron, 2026-11-04): Playwright lives in a venv at the repo root
  (`.venv/`, ignored by git), pinned in `requirements-dev.txt` — set up once with `py -m venv .venv` then
  `.venv\Scripts\pip install -r requirements-dev.txt`. The runner starts tier-2 files with that Python and fails loud
  with that command if it's missing; tier 1 and the commit hook need no venv. Playwright drives the **installed Chrome**
  (`channel="chrome"`; Edge until 2026-11-06 — `RW_BROWSER=msedge` still runs it), so no browser download. Scrollbars are
  shown (Playwright hides them in a hidden browser by default, which hid a covered scrollbar); `App(zoom=, size=)`
  emulates browser zoom and window size. Claude's ad-hoc looks use Playwright's command-line tool through
  `npx @playwright/cli@<exact version>` — nothing installed system-wide.

## 5. Test data — three kinds

1. **A small, frozen, made-up library** (`test/fixtures/`, committed — no personal data). Built **on purpose to hold
   the awkward cases**: an omnibus at several positions, a sample and a loan of a wishlisted book, books in the Trash,
   deep and pinned folders, a book in no folder, a Book List with repeats, Amazon tags and your own tags, a book with no
   description. **Exact checks run against this.** It grows as tests need new cases.
2. **The demo library** (`readerwrangler-demo-library-ORGANIZED.json`, 118 books, and its unorganized twin with 119 —
   already public, keys removed by Ron on purpose): real Amazon-shaped data at a realistic small size — for tests that
   need believable books without the awkward cases spelled out.
3. **Ron's real library at scale** — `large-sample-private.json.gz` in the **private** repo's `test/` folder
   (3,270 books, from his 2026-11-04 backup; Cloud Sync Key removed and verified; compressed). For scale and speed —
   load time, drag with thousands of covers, "does it hold up" — not exact answers. **Committed in the private repo so
   it's backed up** (Ron): a test tied to that exact data set can always get it back, and made-up sets holding anything
   personal live there too (its README has the rules). The test loader refuses any file that still carries a key.

**The relay's stored data** (Ron, 2026-11-12 — review queue Q-021): every relay test run starts from a **fresh, empty
store, thrown away afterwards** (tier 3's own local relay, `tools/local_relay.py`), so a test never depends on what an
earlier run left — or it isn't repeatable. A test that NEEDS history (a mailbox with old runs, a channel mid-change) gets
it from a **frozen, labelled snapshot**: built once on purpose, saved as `relay/.wrangler/state-<what it holds>` (a
meaningful label, not a number), with an index listing each snapshot and what it's for; a run COPIES it into place, so
the frozen copy is always there for the next run. None exists yet — the first test that needs one makes it.

Screen tests never use Amazon's pages and never the real library's cloud copy: the test app has no Cloud Sync (or a
throwaway test channel on a local relay). Whatever the driver shows Claude goes to Anthropic — so the demo-style
fixture, never anything sensitive on screen.

## 6. The per-task routine

1. **A bug fix starts with a failing test** that reproduces the bug — then the fix makes it pass. (The utilities
   project's Law 18: reproduce with real input before explaining.)
2. **A feature's tests are its acceptance criteria**, written with it — the task's "What you'd get" made checkable.
   **A test that passes on its very first run is shown it can fail** — feed its check a deliberate problem (a wrong
   expected value, an injected error) and see it refuse — or it may be checking nothing (2026-11-04: APP-001–004's
   detectors were each shown a wrong count, a console error, a relay request and a crash). **For a fix's test, that
   means failing under its own bug** — remove the fix, or make the bug happen — since a wrong expected value proves
   only the assertion. **A test checks its own setup** before the outcome, and asserts after the screen settles, not
   when the call returns (7.26.0: DIAG-008's planted line was overwritten before it was read; IMPORT-004 passed with
   the fix removed; the Import tests checked "no repair" before the second check had run).
3. **At the task's end:**
   - **promote** its tests into the library (almost always — a test that passed once costs nothing to keep); a test
     left out says why;
   - **gaps** found next to it (things the task touched that nothing tests) — **finish the class** while you're in the
     area if it's cheap (the question is "are the remaining rows cheap now?", not a percentage); **file it as a TODO**
     if it's its own project (new fixtures, real time).
4. **The mechanisms (not memory):**
   - each task in work gets a short **Tests** section — the IDs it added, and gaps filed;
   - the **release checklist** asks "every task in this release: tests promoted, gaps filed?";
   - the **post-mortem** asks which bug of the release no test would have caught — and that test is written.

## 7. Trust — the flakiness rules

A test that fails sometimes teaches everyone to ignore failures (Law 12: an alarm on the normal path is noise). So:
- **fixed data** (§5.1) and **a fixed clock** where dates matter (the "today / yesterday" labels);
- **wait for conditions, never fixed sleeps** ("the toast appeared", not "wait 2 seconds");
- **a fresh browser profile** for each run; stop what a test started by its exact process id (Law 5) — **and check it
  stopped** (each process gone, its port free: Law 12, 7.28.0);
- **a flaky test is fixed — or set aside, with a TODO — the same day.** Never tolerated, never "just re-run it". Set
  aside = a `skip: <TODO id> — why` line in the file's header (§4): every run then says so, and the next release is
  blocked until it's fixed.
- **A failing test is read first, not fixed first** (Law 3, 7.25.0): it may be the protection working.

## 8. What stays manual (a short list per release)

- **Amazon's live pages** — the fetchers against the real site (fetcher *logic* can be tested against saved pages kept
  privately; the live run stays a release step).
- **Taste** — how it looks and reads.
- **A real phone** (Android, and an iPhone — Ron has access to one) until device testing is automated.

## 9. Where it starts

- **Before 2026-11-04:** five function-test files (~87 checks), each run by hand with `node test/<file>`, each with its
  own copy of a `test()` helper whose first failure stopped the file; the two relay scripts; nothing ran on commit.
- **Built 2026-11-04 (branch `feature/carry-over`):** the parse check (`PARSE-001`–`010`); **`test/harness.js`** — the one
  shared helper (stable IDs, a failure is counted and the file carries on); the five files moved onto it with headers
  and IDs (`BFIELD-`, `MERGE-`, `DATE-`, `ORG-`, `OVERLAY-`); **`tools/run_tests.py`** (`RUN-001`–`013`); headers on the
  relay scripts (tier 3 — skipped unless `--relay-url` names a relay: `test-phase1.mjs` defaults to the dev relay
  otherwise); **the commit hook runs tier 1 for what changed** (pre-commit step 7). 9 files, ~110 checks.
- **Step 2 of the order of work** ("Carry over the utilities project's improvements…") builds:
  1. ✅ the parse check (tier 1);
  2. ✅ `tools/run_tests.py` with tiers, tags, IDs and `--changed`; the existing files get `tags:` / `covers:` headers and
     IDs; the commit hook runs `--changed`;
  3. ✅ the browser driver (Playwright for Python + Edge) and the small fixture library's first version — `test/ui/rw.py`
     (the shared setup: serve.py on a free port, a fresh Edge profile, Restore through the real menu, console / crash /
     relay-and-Amazon request detectors, GoatCounter answered empty, and `hover()` / `click_reachable()` — the real
     pointer, refusing a covered or zero-size target and naming the cover: PRINCIPLES Law 8), `test/ui/harness.py`, the fixture
     (`test/fixtures/make-small-fixture.js` → `small-fixture.json`: 23 books, every ownership kind), and
     `APP-001`–`004` (the app opens cleanly; the fixture restores; every left-pane count; still clean after) and
     `DRV-001`–`003` (the driver's own reachability checks). ~50 s a
     run today — the in-browser compile; the precompile cuts it;
  4. the first screen tests — from anomaly reporting and the Delete key fix (step 4), each starting from a failing test.
- **Built 2026-11-05 (branch `feature/logging`):** **Cloud Sync in screen tests** — `App(relay=True)` starts a **local
  relay** (since 2026-11-16 the runner's own `tools/local_relay.py` — one launcher, Law 22; it was `rw.LocalRelay`:
  Cloudflare's own emulator, `wrangler dev --local`, running relay-worker.js with an empty
  store made for the run and deleted after; the test page's address allowed for that run only, wrangler.toml untouched;
  stopped by its exact process tree), points the app at it and gives the fresh profile a made-up test channel (planted at
  run time — never in a data file). `app.upload_fetch(items)` sends books as the library fetcher does;
  `app.import_from_relay()` runs File → Import from Relay. First use: `IMPORT-001`–`005`
  (`test/ui/test_import_from_relay.py`), whose `IMPORT-004` reproduces the Import's false "repair" (LOGGING.md F5)
  before its fix. Adds ~5 s to a run. Known noise gained one entry: a new, empty channel's two "not found" answers.
- **Built 2026-11-12 (branch `tooling/relay-tests-own-relay`):** tier 3 starts and stops its own local relay
  (`tools/local_relay.py`; §4) — no more skipping without `--relay-url`, and no more hand-stopped relays: on 2026-11-11
  ending the shell that started one left workerd and three node processes serving its port (7.28.0 post-mortem).
  `RUN-016`–`021` prove it with a stand-in relay: the files get its address; the relay AND its child are gone after and
  the port free; one that never says "ready" fails loud and is stopped; a child that escaped the tree and still holds
  the port is named by id; `--relay-url` still starts nothing; the real command is wrangler's local emulator.
- **Built 2026-11-12 (branch `tooling/release-fails-on-skip`):** `--release` (§4) — a skipped file fails a release
  run; `RUN-022`–`024` (fails it naming file and why; without the flag a skip still passes, as before; with nothing
  skipped the flag passes).
- **Built 2026-11-16 (branch `feature/faster-sprints`, TODO "Faster sprints" items 1–2):** screen tests in parallel under
  a machine-wide limit, and every run's record with its commit (`--stamp`) — §3, §4. Tier 2 went from 594 s (one at a
  time) to ~295 s; it is now as long as its longest file, `test_cells.py` (129 cells, ~250–295 s) — splitting that file's
  cells across processes is the next step. Tier 1: 119 s → ~90 s, likewise its longest file (`test_backlog_report.py`).
- From then on, every task follows §6.
