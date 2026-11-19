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
| **2** | Screen tests | **Before anything reaches Ron to test** — Ron is never the first to find a regression. While building: only the tests for the change; the full run once per task, at its merge (below) | a few minutes (≤ ~5 min) |
| **3** | Relay tests — against a local relay **the runner starts and stops itself** (dev only as a final check, by `--relay-url`) | When relay code changes; before any worker deploy | ~1½ min |
| **all** | Every tier — `py tools/run_tests.py --tier all --release`: **a skipped or set-aside file fails a release run**, named with why | **Before every release** (release checklist step) | |

Plus a short **manual list per release** (§8) for what can't be automated.

**While building — only the tests for the change** (Ron, 2026-11-13: "that speedup makes perfect sense"; narrowed
2026-11-18: "a full regression only at the end makes sense … normal procedure with human test teams"): each fix → test
round, and each alpha, runs only the tests for what's being built — its own IDs (`--id`; in a file split into shards,
`--id CELL-005 --id CELL-019` runs just those cells, as `RW_CELLS=CELL-005,CELL-019` does — §4), the function tests that
cover the files it changed (`--changed`). **An agent runs no full run. The full tier 1 + tier 2 runs once per task, at
its merge into the sprint's branch** (Ron, 2026-11-18: "1 full regression after each task") — so a break points at one
task. One more full run before the sprint's branch (`sprint-N`) goes to main, only if something was committed after the
last merge.

**A test waits for a condition, never a moment** (2026-11-18, sprint 7's post-mortem): a fixed sleep is a guess about how
fast this PC is today — too short on a loaded PC (a fail), too long on a quiet one (wasted time). Wait for the thing
itself: the element, the text, the color settled (`app.amber_look`), the file written — with a generous upper limit
that only a real failure reaches (the waits, one set in `rw.App`, and their one limit `rw.LIMIT_MS`: §4).

**At review, the proof is the merge's stamp** (TODO "Faster sprints", 2026-11-16; 2026-11-18): every run leaves a record
of the commit it ran on (§4) — `py tools/run_tests.py --stamp <commit>` says PROVEN only for a full tier 1 + tier 2 pass
on exactly that commit with nothing uncommitted (tier 3's latest run is shown beside them, for information — §4). NOT
PROVEN means the run is read (a failure, §7) or done — not taken on trust. `tools/merge_branches.py` makes the full run
part of the merge (2026-11-16): branches built in parallel are merged on a scratch branch, tier 1 + tier 2 run on the
merged result, and the target moves only when its stamp is PROVEN — two changes can merge cleanly and break together
(docs/design/SESSION-TOOLING.md). An agent's own report is its narrow tests' output; review reads it with the diff.

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
  stays tier 1. One summary at the end; a failing screen test saves a screenshot of its page (the harness asks `rw.App`,
  2026-11-17 — the path printed under the failure: `screenshot: <path>`, in `%TEMP%\rw-test-artifacts[-<copy name>]`),
  and a failed file's whole output is kept (below). The commit hook calls it with `--changed`.
- **A failed file's WHOLE output is kept** (2026-11-17, TODO tooling item 9 — five one-time failures in one week, the
  last two unreadable: the runner printed only a failing file's filtered lines). Every failed file's output — stdout and
  stderr, every line — is saved beside the run's record, in a folder named as the record
  (`<git-path rw-test-results>\<record name>\<file>.txt`); its failure lines end with `full output: <path>`, the end of
  the run lists each again, and the record holds the path (`output`) and the screenshots the output named
  (`screenshots`). A failed file on the stamp's NOT PROVEN line names it too. Old outputs go with their old records (the
  newest 300 kept). Every run leaves a record since 2026-11-18 — a narrowed one on the quick shelf, its kept outputs beside it
  there (below). Tests: `RUN-072`, `073`.
- **The machine's or the browser's trouble (ENVIRONMENT) is told from a TEST failure — by the screen-test driver, where
  it's known** (2026-11-17; Ron: "Detect that is what it is, back off and slow down and repeat"). `test/ui/rw.py` raises
  `harness.EnvironmentTrouble` — or notes it with `harness.environment()` — when: our web server (serve.py) or our local
  relay didn't start; the browser didn't start; **the page never loaded** (the start screen still up after 180 s, or the
  page's load never finished) **and the page reported no error of its own** — with one, it's a test failure naming the
  error (ENV-002); the browser disconnected or a tab crashed; **a request to our own server failed for the machine's
  reasons** — short of network buffers or memory (`net::ERR_NO_BUFFER_SPACE`, `ERR_INSUFFICIENT_RESOURCES`,
  `ERR_OUT_OF_MEMORY`) on the way to our web server or local relay, or a refused / reset / empty connection to our web
  server (only to it: to the relay that may be the relay code under test). A request a test refuses on purpose
  (`ERR_FAILED`), one a page change cut short (`ERR_ABORTED`) and one to anywhere else never count. **And a library the
  page loads that failed to DOWNLOAD** (2026-11-17 — a lab run's start-up failed on "ReactDOM is not defined"): a script
  or stylesheet from a library host (`LIBRARY_HOSTS` — unpkg.com, cdnjs.cloudflare.com, cdn.jsdelivr.net,
  fonts.googleapis.com) whose request failed or timed out (any `net::` error but `ERR_ABORTED`, `ERR_FAILED`,
  `ERR_BLOCKED_BY_CLIENT`), whose host answered 5xx, or that came back **empty** (the only loss that reproduced the lab's
  case exactly: no failed request in the console at all) — and a start-up whose **only** errors are "`<Name>` is not
  defined" for a library whose script didn't arrive (`LIBRARY_GLOBALS`: React, ReactDOM, QRCode). One that downloaded and
  then threw is the app's (a test failure, its error named — and the start-up failure lists what each library download
  did). A 4xx is never the network's (a wrong address is ours). **The console check
  (`app.unexpected_console()`) reports such a network error as the machine's trouble, never as a test failure** (RENAME-006,
  2026-11-15). The harness (`test/ui/harness.py`) then decides the file's exit code: **3 — with a line
  `ENVIRONMENT FAILURE: <reason>` — when the trouble came before any test failed** (a failure after it counts as the
  trouble's); **1 when a test failed first** (it failed while the machine was fine) or there was no trouble; 0 when
  nothing failed (trouble that failed nothing is only noted: `! machine or browser trouble: …`). An assertion can never
  give 3. The code, the line and that rule (`exit_code`) live in one place, `tools/environment_trouble.py`, read by both
  sides. Tests: `ENV-001`–`007` (a real browser: a page that never loads → 3; one that never loads because it failed → 1;
  our server stopped mid-session → 3; a failure's screenshot; ReactDOM's script cut off → 3, answered empty → 3, loaded
  and threw → 1), `RUN-080`–`082`, `090`, `091`.
- **A test's own fixed wait running out is NOT the machine's trouble** (Ron, 2026-11-17 — it could hide a real hang).
  Waits are conditions with generous limits instead (§7). test_reset.py's Tools click gave up after Playwright's 30 s
  seven times in a day, always right after opening a second tab: **Chrome slows the tabs behind the one in front** —
  measured under a lab load, the tab behind took 8-44 s to answer anything and the click 122-222 s; brought to the front
  first, 0.1 s. So `rw.App`'s `menu()` and `reload()` bring the app's tab to the front first, as a person switches to
  it, and a test acting on another tab brings that one forward (`page.bring_to_front()`). test_reset.py waits for
  conditions only (the reset's own last line, the tab having drawn what it was given, the Welcome screen — shown only
  once the load is done), each under one limit (`LIMIT_MS` = the driver's 180 s); proven both ways under the same lab
  load (before: 2 of 2 failed at that click; after: passed), and RESET-003 still caught the bug's effect planted on
  purpose. **The waits — one set, in `rw.App`, under one limit** (sprint 8 replaced the screen tests' fixed sleeps;
  sprint 9, 2026-11-18, gathered the helpers it grew in three files into one place — Law 22): `app.wait_loaded()` — the
  library's load has finished after a reload (its folders set, or the critical box up; the start screen leaving means
  only that the app is drawn); `app.wait_console(pattern, since=n0)` — a console line came (`AFTER_CHECK`: the check
  after an Import or Restore has run, that operation's last step); `app.heard(pattern, n0)` — the same, but False
  instead of raising, so the checks after it still say what went wrong; `app.until(cond)` — any condition Python can
  ask, polled; `app.caught_up()` — the page has run every task it queued (a task-queue flush, NOT idle callbacks: after
  an Escape Chrome gave no idle time for 3–5 s); `app.settled(read_js)` — a reading that stays the same with the page
  caught up between; `app.toast(*words)` — a toast holding those words; `app.amber_look(words)` — a warning toast's
  look once it has reached amber; `app.held(text, words, ms)` — a toast still where it appeared `ms` after it was shown
  (a duration, timed on purpose, on the page's clock). **One limit for a step: `rw.LIMIT_MS`, 60 s** — every screen
  test's (it was 30 s in test_cells.py, 60 s in the two key files, 3–10 s at ~120 waits elsewhere). Generous: a step
  answers in well under a second, 2–5× slower on a loaded PC. And under the runner's 120 s floor for "ran past its usual
  time" (below), so a wait that runs out is reported as the test failure it is, not stopped as the machine's trouble.
  The app opening or a load (a reload, a reset) has its own: `rw.APP_TIMEOUT_MS`, 180 s (test_reset.py, test_boot.py
  and three files' relay / restore / reset waits use it). A sleep that stays proves something does NOT happen (a
  window, measured from the right moment) and says so: `# timed on purpose: …`.
- **Heavy tier-1 files** (Ron, 2026-11-17: "Yes. Also back off"; the merge's full run failed a different timing test of
  test_run_tests.py twice — RUN-079, then RUN-057 — under 4 tier-1 files at once). A tier-1 file whose header says
  **`heavy: yes`** (optionally `— why`; `heavy: no` or no line = light; anything else is a header problem) starts many
  processes of its own. It **holds one of the PC's test slots while it runs, within the same browsers-at-once level** —
  so the level governs heavy work of both tiers — and `--list` marks it. Counted 2026-11-17 (each run alone, every process
  it started): `test_backlog_report.py` ~1,200 git processes one after another for ~2 min; `test_copies.py` ~400, up to
  9 at once; `test_merge_branches.py` ~350; `test_run_tests.py` ~300, up to 8 at once (sample runs in parallel, stand-in
  relays); `test_sync_remotes.py` ~220, up to 5 at once — the five marked. The next, `test_gate_check.py`, ~75 (2 at
  once); every other tier-1 file under 15. **Light tier-1 files run beside them, outside the slots, as before**: each of
  the `--jobs` workers takes the first file in order that may start now — a light one always, a slotted one only with
  room — so a light file never waits behind a slotted one. **Its machine trouble backs the level off as a browser's
  does** (halved at once, saved) and it is **rerun once, alone**, said loudly — only when the file itself says so (exit 3
  and the marked line), never guessed. What a heavy file can tell reliably: **test_run_tests.py's stand-in relay wasn't
  ready within its time** — only when the stand-in's last try never reached its own ready line (each try leaves a note)
  AND the runner waited its whole time; if the stand-in said "Ready", whatever followed is the runner's — a failure
  (`standin_late`; RUN-016–020, 052, 057). The others have no time limits of their own: they only get slower. A run with
  no screen tests is no measure of browsers — only its trouble moves the level, never up. A light tier-1 file's exit 3 is
  a failure like any other. test_run_tests.py ends through `environment_trouble.tally` (its summary — a check the
  machine's trouble stopped counted apart, `N passed, M failed, K stopped by the machine's trouble` — the exit rule and
  the marked line), and `RUN-093` runs a stand-in that ends the same way through the real runner, the whole path end to
  end (2026-11-18, TODO tooling 11.2): exit 3 → 4 → 2 at once, saved → rerun alone, passed → the summary's counts and
  the record. Tests: `RUN-077`, `087`–`090`, `093`, `LEVEL-022`.
- **Rerun once, ALONE — never silently** (2026-11-17): a screen-test file — or a heavy tier-1 file (above) — that exits 3
  with that line (both needed; a light tier-1 file and tier 3 never) is not reported yet; when every other file of the
  run is done, the runner waits 10 s, takes **every**
  test slot on the PC (in order — two runs doing it can't deadlock; no other run's screen test beside it either) and
  reruns it once. A file split into shards reruns only the shard that met the trouble. The summary says so loudly,
  every time:

      ! 1 file retried after the page never loaded — … — its first output: <path>
          test/ui/test_x.py — rerun alone: passed — the rerun's output: <path>

  and the file's own line ends `; rerun alone after <reason>`. The record notes it (`retried`: the reason, both outputs,
  how the rerun went). **Passed on its rerun, it counts as passed** — and the stamp says so under its tier, on a `·` line
  (`· test/ui/test_x.py was rerun alone after … — passed — its first output: <path>`), still PROVEN. **Its rerun meeting
  the machine's trouble AGAIN is NOT PROVEN — never a failure** (2026-11-18, TODO tooling 13.13 — Ron: "I think not
  proven"; it was a failure until then): `? test/ui/test_x.py  not proven — the machine was too busy (it met its trouble
  again on its rerun alone — one rerun a run) — <why>`, both outputs kept, the rerun's note `not proven — the machine's
  trouble again: <why>`. **One run never retries more than once**; across runs, a file that keeps being not proven is held
  (below). Any other failure of the rerun is a failure. **A test failure is never rerun.** More than 4 files meeting the trouble in one run
  aren't rerun (`MAX_RETRIES`: that many points at something broken) — **and each one past the 4 is NOT PROVEN, never a
  failure** (2026-11-18 lab, 12 of 16 CPUs kept busy by other programs: the fifth file past its limit,
  test_backlog_report.py, was reported `✗ … timed out after 281.747 s` — a slow-but-healthy test called broken). Its
  line starts `?`:

      ? test/x.py  not proven — the machine was too busy (5 files met its trouble this run; only 4 are rerun) — <why>
          full output: <path>

  its whole output is kept, the summary counts it apart — `Tests: 58 file(s) passed, 0 failed, 1 not proven (the
  machine's trouble)` — and says loudly, right under it, `! 5 files met the machine's or the browser's trouble this run
  — only 4 are rerun alone; that many points at something broken, not a passing hiccup — look at what else the PC is
  doing`, naming them. The record marks the file (`result: "not proven"`, `not_proven`: why) and the run (`result:
  "not proven"`); its cost sample teaches nothing (`the machine's trouble — not proven`). **The run's exit is 3** (the
  machine's trouble, `environment_trouble.EXIT_CODE`) when nothing failed — **a real failure still wins: 1**. Nothing
  treats it as a pass: the stamp is NOT PROVEN (the file named under its tier: `<file> not proven — the machine was
  too busy: <why> — 5 files met its trouble this run; only 4 are rerun — full output: <path>`), so the merge script
  doesn't land on it (and says `tier 1 not proven — the machine was too busy`, never "failed"); the commit hook's
  `--changed` refuses the commit (any exit but 0); the browsers-at-once level backs off for the trouble and learns
  nothing from the run. A sharded file is failed if a shard failed, else not proven if a shard was. Tests: `RUN-095`–`097`,
  `COST-023`, `MERGE-005`.
- **A file that can't be proven is HELD** (2026-11-18, TODO tooling 13.13 — Ron: "we don't want to go into an infinite
  try loop if a file is never going to run under current resources and loading … Give up after say 3 failures of same file
  and report it and await instruction from me"; the proposal approved the same day; `tools/held_tests.py`). Counted **per
  PC**, in the slots folder (`%TEMP%\rw-test-slots\held-tests.json`, or `RW_TEST_SLOTS_DIR`'s) — so the runs of every
  working copy and of every merge on this PC add up (it read one folder's records until then, TODO tooling 13.10) — over
  **full runs only**: a run narrowed by `--changed`, `--id`, `--tag` or `RW_CELLS` is passed over. For each file, the full
  runs in a row in which it met the machine's or the browser's trouble — `rerun alone` (passed on its rerun) or `not
  proven`; a full run that passed it the first time, or failed it (a test failure — a definite answer), ends its streak.
  - **2 in a row → said loudly** (TODO tooling 11.7; Ron: "it may truly need to run alone"), at the end of the run:

        ! test/ui/test_x.py met the machine's or the browser's trouble 2 full runs in a row on this PC — it may truly need
        to run alone (TESTING.md §7); not proven 3 runs in a row would hold it; its runs, newest first:
            2026-11-18 11:00 in s9-runner — the page never loaded — rerun alone: passed — first output: <path> — the rerun's: <path>
            2026-11-18 10:59 in ReaderWrangler — the page never loaded — rerun alone: passed — first output: <path> — …

  - **3 in a row NOT PROVEN → held** (a rerun alone that passed proved the file: it never counts toward a hold —
    `HOLD_ON`), said loudly with Ron's ways out and the 3 runs:

        ! test/ui/test_x.py couldn't be proven in 3 runs in a row on this PC — held for Ron's decision: later runs won't
        run it (each says 'held — not run', so none can be proven and nothing merges past it). Ron's ways out: py
        tools/run_tests.py --release-held test/ui/test_x.py  (try again — the hold and its streak cleared) · an 'alone:
        yes — <why>' line in its header (…; that lifts the hold too) · a 'skip: <TODO id> — <why>' line (set aside). Its
        runs, newest first: …

  - **Later runs don't run a held file** — every run, narrowed ones and the commit hook's too: `? test/ui/test_x.py  held —
    not run: it couldn't be proven in 3 runs in a row on this PC (held since …) — held for Ron's decision`, counted as not
    proven (`Tests: 25 file(s) passed, 0 failed, 1 not proven (the machine's trouble — 1 held, not run)`, exit 3), a loud
    `! held — not run: …` line with the ways out at the end, and in the record `result: "not proven"` with the hold — so
    the stamp is NOT PROVEN and the merge script lands nothing past it. That block IS the "await instruction"; in a
    sprint it goes to the review queue and its task parks. (A held file covering staged files also refuses the commit,
    as any not-proven file does.) `--list` shows it held.
  - **Ron's ways out:** `py tools/run_tests.py --release-held <file>` — try again: the hold and its streak cleared, runs
    nothing (a file that isn't held: said, with what is, exit 1); **`alone: yes — <why>`** in its header — run it alone
    every time: the file runs only while it holds EVERY test slot on the PC, after the others (its machine trouble then
    handled as anywhere: rerun once, alone; again → not proven); the why is required (`alone: no` or no line = beside the
    others; anything else is a header problem); a hold taken while it ran beside others is lifted by it, said (`the hold
    is lifted and its streak starts over`); or **`skip: <TODO id> — <why>`** (set aside, below).
  Tests: `RUN-074`–`078`, `092`, `098`–`101`.
- **How many browsers at once — the runner finds it itself** (2026-11-17; Ron: "similar to how TCP works" — use more
  until failures, back off, occasionally try more; measure diminishing returns; conditions change). It replaced, the
  same day, a fixed rule (under 4 GB free → 2 browsers, under 2 GB → 1). `tools/browser_level.py`:
  - **The level** — how many screen-test browsers a run may run at once, **1 to 6** (the PC's slots are 6 to match).
    It is **saved per PC**, beside the slot files: `%TEMP%\rw-test-slots\browsers-at-once.json` — the level, why, and
    the last 30 runs (`{level, end, wall seconds, files, suite, full, trouble, failed, free GB, when}` + what was
    decided after each). Written to a temporary file, then put in place. **Missing or damaged → start at 4, and the run
    says so.** **To reset it: delete that file** (the next run starts at 4).
    **A folder of its own — `RW_TEST_SLOTS_DIR`** (2026-11-17): set, it holds the slot files AND this file instead of
    `%TEMP%\rw-test-slots` — TEMP itself stays where it is (a lab that moved TEMP broke the local relay emulator:
    wrangler keeps its storage in TEMP). Every run that should share the PC's limit must use the same folder. Recorded
    with the run; it doesn't narrow it. Unset → `%TEMP%\rw-test-slots`, as before. Test: `RUN-085`.
  - **Back off hard:** a screen test meeting the machine's or the browser's trouble (exit 3, above) **halves the level
    at once** for the rest of the run (`! browsers at once: 4 → 2 for the rest of this run — <file> met …`): the files
    already running go on; new ones start only while fewer than the level are running. One halving per burst (trouble
    from a file that started before the last halving doesn't halve again); never below 1. The file is rerun alone as
    before, and **the halved level is saved** — whether or not the run was narrowed.
  - **Grow gently:** after a **full** screen-test run (`--tier 2` or `--tier all`, not narrowed by `--id`, `--tag`,
    `--changed`, `RW_CELLS` or a set-aside tier-2 file) with no such trouble **and every file passing**, the next run
    gets **one more** (up to 6).
  - **Only fully passing runs count** (Ron, 2026-11-17 — Karn's algorithm: an ambiguous sample is dropped, not risked):
    a full run where **any** file failed — or couldn't run, or the build failed (tiers 1 and 2 and their reruns; tier 3
    runs after, outside the timed part) — is **saved, marked `failed`** (how many), shown `(failed)` on the level line,
    and **moves nothing**: `· browsers at once next run: 4 — 1 file failed in the last run at 4 at once — only a run
    where every file passed moves the level or is compared — staying at 4`. It is never a yardstick (not the best recent
    time, not the bar for "twice as slow"), and doesn't count toward the 5-run wait below. A try at one more whose run
    failed isn't judged: the next clean run at that level is. **The machine's trouble still backs off**, failed or not.
  - **Diminishing returns:** the run right after a step up is judged — its wall time (the parallel part: not the build,
    reruns or tier 3) against **the best recent full run at the level below** (the last 10 saved runs; the same suite —
    tier 2 or all — and about the same number of screen-test files, within 10 %; never a run with trouble or a failed
    file). **Not faster by more than 5 % → back to the level below, and no try at the higher one for the next 5 full
    runs** — then it tries again (conditions change). A suite that changed size a lot isn't compared: the run stays at
    its level to measure it.
  - **Sustained slowness steps down by one** (Ron, 2026-11-17): a clean full run (every file passed, no trouble) at
    level L that took **more than twice** the best recent clean full run at the same L (the same suite and size, as
    above) → the next run at **L−1** — not halved; never below 1 — saying both times (`4 at once took 6 min 50 s — more
    than twice the best recent run at 4 (3 min 20 s) — one fewer: 3`). No wait afterwards: the next clean run at normal
    speed may grow again by the rules above.
  - **Said and recorded:** each screen-test run starts with a line like
    `· browsers at once: 4 (saved — 5 at once took 3 min 40 s — no faster than 4 at once (3 min 24 s, the best recent
    run) — back to 4, and no try at 5 for the next 5 full runs; last 3 full runs: 4 → 3 min 24 s, 5 → 3 min 40 s, 4 →
    3 min 22 s) · 18.2 GB of memory free` and ends with `· browsers at once next run: 4 — <why>`. The record holds
    `browsers` (the level it started at, where from, each change, the end, the most at once, troubles, the wall time,
    the next level and why) and `memory` (free GB — evidence, no longer a rule).
  - **Forcing a number:** `--jobs N` or `RW_TEST_SLOTS=N` runs N at once (the slots still cap it) — **the saved level is
    left alone**, and trouble doesn't move N within that run. `--jobs` also sets how many files at once overall; by
    default that's 4, or the level when higher (tier-1 files beside the browsers in a `--tier all` run aren't held to
    the browsers' level).
  - Two runs at once (two working copies) each save their own result; the last one written wins. A run at level L takes
    only the first L of the PC's slots, so runs at the same level together stay within it.
  - Measured 2026-11-17 for scale: one screen-test file's Chrome takes 0.15 GB of RAM typically, 0.57 GB at most; our
    servers and relays up to 0.27 GB together (tools/test_slots.py).

  Tests: `LEVEL-001`–`021` (test/test_browser_level.py — the rule, a pure function: history in → next level and why
  out; `017`–`019` a failed run, `020`–`021` slowness), `RUN-079`, `083`–`086`.
- **What each test costs this PC — measured, averaged, shown** (2026-11-18, TODO tooling item 12 step 1; Ron: "Measure
  1st. If you don't measure you won't know if you've improved things"). **Step 1 measured only; step 4 puts the time
  averages to work — the order and a "stuck" limit (the next bullet).** `tools/test_costs.py`:
  - **What is measured** — per **unit** (one process the runner starts: a whole file, or one shard of a `shards: N`
    file), per run, for its **whole process tree, exited processes included** (git, node, Chrome's helpers): the unit is
    started suspended, put in a Windows **job object** of its own, then let go — a job counts every process started
    inside it, and nothing can leave it (breakaway is never allowed; Chrome's own nested jobs still count in ours).
    Checked 2026-11-18 on three real screen-test files: every process under the test was asked "are you in the job?"
    every half second — 8–12 chrome.exe each, none outside. In the run's record, beside each file's `seconds` (and each
    shard's), `measures`:
    - `committed_peak_bytes` — **memory committed, at its peak**: the most private memory the tree held at once (what
      the processes asked Windows to guarantee them — RAM or the page file). **It is NOT RAM in use** (Law 2: 7.31.0
      quoted committed memory as RAM);
    - `ram_peak_sampled_bytes` — **RAM, private (sampled peak)**: what the test adds to the PC's RAM — each process's
      **private** working set (RAM only it uses; the pages it shares with others — Chrome's and Python's DLLs — left
      out; `PROCESS_MEMORY_COUNTERS_EX2`), added up about once a second (first at ¼ s), the highest sum seen. A peak
      between two samples is missed; a unit shorter than ¼ s has none (`None`). `ram_kind` says which kind was measured:
      `private`, or — on a Windows without the private figure (before Windows 10 1709) — `shared included` (the whole
      working sets, shared pages counted in each process; `ram_note` says why; `--costs` stars it and leaves it out of
      the comparison below; an average never mixes the two kinds). Why private (2026-11-18, the first version summed
      whole working sets): the same shared base — about 0.45 GB a screen test — was added to every test, squeezing the
      ratio between tests toward 1 (1.2× whole, 1.5× private on the same three files). Checked against Windows' own
      figure for one process: 203.9 MB from both (WMI's `WorkingSetPrivate`, by process id). The whole-working-set sum
      is kept beside it, `ram_with_shared_peak_sampled_bytes` — the same call gives it, so it costs nothing, and it shows
      the shared base — but it is never averaged or shown: nothing is decided on it;
    - `cpu_seconds` — user + kernel time of every process in the tree;
    - `io_read_bytes`, `io_written_bytes` — **I/O, every kind**: Windows counts files, pipes AND network here — not the
      disk alone;
    - `processes` — how many the tree started in all.
    A sharded file's own entry adds CPU, I/O and processes over its shards and takes the largest shard's peaks (they
    ran side by side — their sum would claim they all peaked at once). A file rerun alone keeps its first run's
    measures too (`retried` → `first_measures`). Measured on 2026-11-18, one screen-test file at a time
    (test_app_loads, test_reset, test_delete_key): 41–51 processes, 0.66–0.82 GB committed, 0.39–0.59 GB RAM private
    (0.83–1.09 GB with shared pages counted in each), 10–20 s of CPU, 27–40 MB read, 8–19 MB written.
    **Not on Windows, or anything about measuring fails: every measure is `None`, the test runs exactly as before, and
    the run says why once** (`· measures missing for …`). Only a run that leaves a record measures — every run of the
    repository's files since 2026-11-18, the commit hook's `--changed` included (on the quick shelf; a narrowed run's
    measures stay in its record and teach nothing).
  - **Where the averages live** — per PC, beside the browsers-at-once level: `%TEMP%\rw-test-slots\test-costs.json`
    (or `RW_TEST_SLOTS_DIR`'s folder). For each unit and each measure (time included), **a running average and
    spread — TCP's own method for round-trip times (RFC 6298)**: the spread moves ¼ of the way to |sample − the old
    average|, then the average ⅛ of the way to the sample; the first sample sets average = sample, spread = half of it
    (so a unit measured once shows a wide ± — by design). Each with its count, last value and date.
    - **Only a unit that ran in full and passed, the first time, teaches it** (Karn's rule, as the browsers-at-once
      level): never a unit of a run narrowed by `--id`, `--tag`, `--changed` or `RW_CELLS`, never a failed one, never a
      rerun alone after the machine's trouble. Those stay in the run's record, marked: `costs` → `taught` (how many),
      `left_out` (each unit and why).
    - **Only the repository's own test files teach it** (2026-11-18 — the runner's self-tests run it on throwaway sample
      files, and one of them, RUN-051, takes a real run's path: it taught the PC's real averages under names like
      `../../AppData/Local/Temp/tmp…/a.test.js`): a unit whose file is outside the repository being tested is left out
      (`outside the repository`), and every save drops any saved entry named outside it — so such entries clean
      themselves up. And **the runner's self-tests use slot files, a level and test costs of their own**: a test file
      that runs the runner (test/test_run_tests.py, test/test_test_costs.py) sets its own temporary `RW_TEST_SLOTS_DIR`
      at its top (removed when it ends) — never the PC's real `browsers-at-once.json`, `test-costs.json` or slots.
      (test_merge_branches.py and test_copies.py drive stand-in runners, which touch none of them.)
    - **A test file whose contents changed starts its history over** (its hash, taken as the run starts, is kept).
    - **Runs finishing together lose nothing**: each save reads, merges and writes under an OS file lock (the slots' own
      lock, `test_slots.locked`) and is written whole (`browser_level.save` — a temporary file put in place, a refused
      swap retried for ~2 s). Six runs saving 10 times each at once: 60 of 60 kept (3 without the lock).
    - To start again: delete the file.
  - **`py tools/run_tests.py --costs`** runs nothing; it prints each unit — how many runs taught it, average ± spread of
    time, memory committed, RAM private (sampled), CPU, I/O read and written — slowest first; the totals (time, CPU
    and I/O for one run of each, one after another); and how much the screen tests differ in RAM: `Screen tests differ
    in RAM by 1.5× — the biggest average private RAM peak (sampled) is …, the smallest … — less than twice` (the next
    step's question: is the biggest at least twice the smallest?).

  Tests: `COST-001`–`016` (test/test_test_costs.py — `015`–`016` a file outside the repository: never taught, cleaned
  up on the next save — `006` a real child holding 200 MB whose grandchild burns 1 s of CPU
  and exits first: the job counts it, and its private RAM is ≥ the 200 MB; `014` private vs whole working set, the API
  stubbed).
- **The averages at work — longest first, and a "stuck" limit per unit** (2026-11-18, TODO tooling item 12 step 4;
  Ron: "longest first by each file's average, and a 'stuck' limit of average + 4 spreads (never above today's 10
  minutes): act once every file has at least 5 runs measured"). Both read this PC's averages (above), and only for a
  unit whose file still has the contents they were measured on (its hash — a changed file starts over):
  - **Longest first by the average** — the units of tiers 1 and 2 start in order of their average time on this PC;
    a unit with none: its time in this copy's latest record (a shard: its file's longest shard then, or its file's
    time split N ways); with neither, 60 s for a screen test, 5 s for any other. One place decides (`estimate` in the
    runner).
  - **The stuck limit — TCP's own retransmission timer** (RFC 6298: average + 4 spreads; `test_costs.stuck_limit`).
    A unit with **at least 5 runs measured** gets **average + 4 spreads, never under 4 times its average or 120 s,
    never over 600 s** (the flat 10 minutes every unit had before — the ceiling wins when 4 times the average is over
    it). **Why the floor:** healthy tests ran 2–5× slower when other programs took the CPU — 2× stopped five healthy
    files (the 2026-11-18 lab, 12 of 16 CPUs kept busy by other programs: test_merge_branches.py stopped at 110 s,
    average 55; test_environment.py 170 s, average 85; test_copies.py 171 s, average 86; test_run_tests.py 207 s,
    average 103; test_backlog_report.py 282 s, average 141 — the first four passed rerun alone, in about their normal
    time; the fifth found the reruns taken and was reported as a failure, which is now NOT PROVEN, above). The floor
    was twice the average or 60 s until then (an earlier lab, the CPU alone squeezed, had seen 2.8×). **The flat 600 s stays** for a unit with fewer than 5
    runs, for **every unit of a narrowed run** (`--id`, `--tag`, `--changed`, `RW_CELLS` — a narrowed unit's
    average doesn't apply), for tier 3 (one file at a time, its own relay) and for every rerun alone. The run's opening
    lines say it once: `· stuck limits from this PC's averages (59 units; the other 2: the flat 600 s — fewer than 5
    runs measured on their contents, or stopped at their limit last time)`.
  - **Past its limit, a unit is the machine's trouble, not a test failure** (TCP: a timeout is congestion, not a lost
    connection): it is **stopped with every process it started** — the unit runs in a Windows job of its own (above),
    and the job is ended by its handle (never by a name, never `taskkill /T`; before, only the unit's own process was
    killed and its children ran on); **said plainly** — `! test/x.py: ran past its usual time: 196 s, its average 98 s
    — stopped, with every process it started: the machine's trouble, not a test failure — it will be rerun once,
    alone, with the flat 600 s, when the others are done`; **the browsers-at-once level halved** as for other machine
    trouble (a light tier-1 unit, which holds no place in the level, halves it where it stands; a run with no screen
    test or heavy file has no level to halve); and **rerun once, alone, with the flat 600 s** (TCP doubles its timer
    on a retransmit) — the same rerun as for any machine trouble (above: after the others, holding every slot; said at
    the end; the record's `retried` holds the reason, `limit` and `average`; a rerun teaches no average). Its line
    ends `; rerun alone after ran past its usual time: N s, its average M s`. **Past the flat 600 s too, it's a hang
    — a failure**, reported as before (`✗ timed out after 600 s`, both outputs kept). **Stopped when the run's 4
    reruns are already taken, it is NOT PROVEN** — never a failure (the rerun bullet above; `COST-023`).
  - **The backed-off limit is kept until a pass it can trust** (TCP keeps its backed-off timer until a sample that
    wasn't a retransmit — Karn): a unit stopped at its limit is marked `backed_off` in `test-costs.json` (the run's
    `· test costs:` line says so, the record's `costs` → `backed_off` names it), and **its next runs get the flat 600
    s** until one passes the first time — that pass teaches its average, as any, and clears the mark. Why: a rerun alone
    never teaches, so without it a test that truly got slower — the app it drives slower, its own file unchanged (so
    its history doesn't start over) — would be stopped at the old limit every run, forever, halving the level each time.
  - What the PC's averages gave on 2026-11-18 (61 units, 59 with 5+ runs), with the first floor (2× / 60 s):
    `test_backlog_report.py` first — average 141 s, limit 283 s; then `test_run_tests.py` 98 s → 196 s,
    `test_environment.py` 88 s → 176 s, `test_copies.py` 88 s → 175 s, `test_merge_branches.py` 58 s → 115 s, the three
    `test_cells.py` shards ~46–51 s → 104–110 s, `test_delete_key.py` 37 s → 94 s (average + 4 spreads, its times vary
    more). With the floor at 4× / 120 s (the same day, after the lab), 4 times the average sets every one of those:
    564 s, 392 s, 352 s, 352 s, 232 s, ~184–204 s, 148 s.

  Tests: `COST-017` (the limit at its floor — 120 s, and 4 times the average: the lab's two files — its middle and its
  ceiling; fewer than 5 runs → flat), `018` (the order:
  average, then the record, then the defaults; a changed file's average unused — through the runner, one at a time),
  `019` (a stand-in past its limit: its child gone too, said, the level halved 4 → 2, rerun alone with the flat limit —
  longer than the stuck one — and passing), `020` (past both: a failure, as before), `021` (fewer than 5 runs, `--id`,
  `--tag`, `RW_CELLS` → the flat limit), `022` (stopped once → marked; its next run gets the flat limit, passes, teaches,
  and the mark is gone), `023` (past its limit with the reruns already taken — the cap made 0: not proven, exit 3, never
  a failure). The 120 s floor, 4 times the average and the flat 600 s are made 1 s, twice and 10 s (5 s) inside those
  rows.
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
  (default: 4, or the browsers-at-once level above when higher; `--jobs 1` = one at a time, as before), the longest
  first by each unit's average on this PC (step 4, above — else its time in the last record). **Every screen-test file — and every heavy tier-1 file (above) — holds
  one of the PC's test slots while it runs** (`tools/test_slots.py`): 6 in total for every run on this PC (4 until 2026-11-17, when the runner began choosing
  its own level, 1–6, above), whatever working copy it's in (`RW_TEST_SLOTS` overrides — every run should use the same
  number). A slot is a file in `%TEMP%\rw-test-slots` (or `RW_TEST_SLOTS_DIR`, above) held with an OS file lock, so a
  run that crashes or is stopped frees its slot by itself. A run waiting for one prints `· <file> waits for a test slot — all 6 on this PC are in use`
  (or `— the first 4 of the 6 on this PC (browsers at once: 4) are in use`) and who holds each (process id, folder,
  file, since when). Tier 3 stays one file at a time (its own local relay).
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
  Isolation (checked 2026-11-16): each screen-test file has its own serve.py on its own free port (started through
  `tools/starter.py` since 2026-11-18, below) — and checks the port
  is served by ITS server (by process id), trying another if a parallel file's server took it in between — its own
  throwaway browser profile, its own local relay (free ports, a throwaway store) when it uses one, and files only in
  folders of its own (`tempfile.mkdtemp`); screenshot names are distinct per file. **No test process sees git's own
  variables** (2026-11-18): every process the runner starts for a test file — the file and its `--list-cells` — gets the
  runner's environment WITHOUT any `GIT_*` variable (`test_env` in the runner). Under the commit hook git sets
  `GIT_DIR`, `GIT_INDEX_FILE`… to the REAL repository; that day a test run there set `core.bare = true` in the shared
  `.git/config`, and every working copy failed "must be run in a work tree" for 13 minutes. RUN-044 had left it to each
  test file; the runner is the chokepoint now. Test: `RUN-103`.
- **Working copies** (`tools/copies.py`, 2026-11-16): a git worktree beside the main folder, with `.venv` and the
  `node_modules` folders linked in from the main folder — every tier runs there as here, with the copy's own `dist/`, its
  own run records (so its own stamp), and its own screenshots folder: `%TEMP%\rw-test-artifacts-<copy name>` (or
  `RW_TEST_ARTIFACTS-<copy name>`), so two copies running the same file don't overwrite each other's. The machine-wide
  test slots are shared by every copy. Details: docs/design/SESSION-TOOLING.md.
- **Results stamped with their commit** (2026-11-16): every run except `--list` leaves a record (the commit hook's
  `--changed` too, since 2026-11-18 — below) — the commit it ran on (and again at the end: a commit made during the run is caught), what was
  uncommitted before and after (changed tracked files, and untracked files git doesn't ignore), what ran (tier, `--id`,
  `--tag`, `--release`, jobs), **the environment variables that change a run, each with its value** (`RUN_ENV` in the
  runner — found by searching the tests, their helpers and the runner for `os.environ` / `process.env`; a new one is
  added there), each file's result, counts and time, start and end, the overall result. Kept OUTSIDE the
  working tree, per working copy: `git rev-parse --git-path rw-test-results` (`.git/rw-test-results` here; a git
  worktree gets its own, under `.git/worktrees/<name>/`). The newest 300 are kept.
  **Every run is recorded — a narrowed one on the quick shelf** (2026-11-18; Ron: "Absolutely record them. Why would you
  not???" — the commit hook's `--changed` runs left none, so an agent's own test time landed in "everything else" in a
  copy's time report, TODO tooling 13.1): a run narrowed by `--changed`, `--id`, `--tag` or a narrowing variable writes its
  record (and its failed files' outputs) in **`rw-test-results\quick\`** (`QUICK_SHELF`), which keeps its own newest 300
  (`KEEP_QUICK`) — so quick runs never push the full runs' records out. **The full-run logic never reads it**:
  `read_records` reads only its folder's own `.json` files — the stamp and the longest-first estimates (`latest_times`)
  see the full runs alone, and the held streak isn't read from records at all (per PC, full runs only — above). A
  `--changed` record also says `ran.changed: true`, and `narrowed_by` names it (`--changed`), so it could never count as a
  full run wherever it's read. A narrowed run's NOT PROVEN line on the stamp ("its latest tier 2 run … was narrowed by
  --id …") is gone with it: the stamp now says only `no full tier 2 run recorded on this commit`. It costs the commit hook
  about 0.3 s (the commit and git status, before and after). `tools/copies.py` counts the shelf in a copy's time report,
  labelled `quick` (COPY-010). Tests: `RUN-042`, `059`, `060`, `102`, `COST-010`.
  `py tools/run_tests.py --stamp [<commit>]` (default HEAD) runs nothing; it prints **PROVEN** (exit 0) only if tier 1
  AND tier 2 each ran in full on exactly that commit (`--tier 1` and `--tier 2`, or `--tier all`; a run narrowed by
  `--id` / `--tag` doesn't count, nor one with a file of that tier set aside — below), every file passed (a file NOT
  PROVEN — the machine's trouble past the reruns, above — never did), nothing
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
  (chrome or msedge), `RW_TEST_ARTIFACTS` (where screenshots go), `RW_TEST_SLOTS` (the PC's limit, and
  the browsers at once forced to it), `RW_TEST_SLOTS_DIR` (the folder of the slots and the saved level),
  `RELAY_URL` (tier 3's relay; tier 3 isn't part of the stamp's verdict). Records written before this have no variables and are read as full
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
  **Measured too** (2026-11-18, sprint 9 — TODO tooling 13.3: it ran outside every relay test's measurement): in a run
  that leaves a record, tier 3's relay runs in a Windows job of its own (as each test unit does, below), so its CPU,
  memory, I/O and processes are in the run's record (`relay`), said after the stop (`· the local relay cost: …`), and —
  a full tier 3 where every relay file passed and the relay stopped clean — teach this PC's averages as their own row,
  `tools/local_relay.py (the relay for tier 3)`, in `--costs`. Test: `START-012`.
- **One starter for every process our tools start — a list of their ids, leftovers shown loudly** (`tools/starter.py`,
  2026-11-18, sprint 9; TODO 20261112-1240 — Ron: "keep a list of IDs as you create them, delete from list when
  confirmed dead"; "draw my attention to it"). Grown from `tools/local_relay.py` (its process code moved there): the
  relay tests' relay and the screen tests' relay (both through `local_relay.py`) and **the screen tests' web server**
  (`rw.App` — it had its own `Popen` and `terminate()`; it keeps its check that the server answering is its own, by
  process id) all start through it (Law 22).
  - **The list** — `started-processes.json` beside the test slots (`%TEMP%\rw-test-slots`, or `RW_TEST_SLOTS_DIR`, so
    every working copy's runs share it): every process started — and each process of its tree as it's seen — with its
    **id, its start time** (an id Windows later gives another process is never taken for ours), its program, **what it
    is** ("the screen tests' web server (serve.py) for test_x.py"), **which run** started it (the runner gives its label
    to every file it starts as `RW_RUN_ID`; else "<script> run directly"), the process that started it and its ports. An
    entry leaves the list **only when its process is confirmed gone** (that id with that start time no longer running).
    The file outlives a crashed run. Every change is read, merged and written whole under the slots' own OS file lock
    (no second lock). A list that can't be updated is said loudly on the error output, never a test failure.
  - **Stopping** — unchanged in kind: every process of the tree by its exact id (start time checked; never `/T`, never by
    name), the one started by its own handle, then checked gone and its ports free; a gone process leaves the list, one
    still running stays on it and is reported with its stop command. **Something on our port the list doesn't name is
    reported, never stopped** — and kept on the list's "unnamed" side so the next run's start banner names it once more.
  - **Leftovers, loudly** — **at the START of every run that runs tests** (the commit hook's too, quiet or not): a banner
    naming each listed process still running whose run has ENDED (its owner gone — a process of a run still going in
    another working copy is none), what it is, which run, since when, and the exact command to stop it; plus anything
    unnamed found on such a process's port. **At the END of the run that left them:** every process that run started
    still running. Both end with one line starting **`NEEDS YOUR ATTENTION:`** — the line Claude reads into its "needs
    your attention" list when reporting to Ron. The banner stops nothing. `py tools/starter.py` prints the same banner
    on its own. A sample:

        !! ══════════════════════════════════════════════════════…
        !! LEFTOVER PROCESSES — 2 started by an earlier test run on this PC and still running:
        !!   process 63000 (python.exe) — the screen tests' web server (serve.py) for test_paste.py, port 60043
        !!       started 2026-11-18 20:20:34 by the test run of 2026-11-18 20:20:01 in C:\…\ReaderWrangler (process 1111) — that run has ended
        !!       stop it:  taskkill /PID 63000 /F
        !!   …
        !! ══════════════════════════════════════════════════════…
        NEEDS YOUR ATTENTION: 2 leftover process(es) from an earlier test run — process 63000 (python.exe): taskkill /PID 63000 /F; …

  - **What a test unit leaves running** (TODO tooling 13.4): each unit already runs in a Windows job of its own
    (`test_costs.py`, below). When the unit's own process ends, the job is asked what is still running in it; after a
    short grace (5 s — a browser's helpers may be on their way out) each one left is named (id, program) and, being in the
    unit's job and so provably its own, **stopped by the job's handle** and checked gone — also when one of them holds
    the unit's output pipes (the runner used to wait for it until the unit's time limit, and call the unit stuck). Said
    at the end of the file's output and loudly at the run's end (`!! LEFT RUNNING AFTER ITS TEST ENDED …` and a
    `NEEDS YOUR ATTENTION:` line — a leak in the test or a tool it uses), kept in the record (`left_running`, and the
    unit's measures' `leftovers`). It doesn't fail the file. Only in runs that measure (those that leave a record) —
    the commit hook's `--changed` run has no jobs.
  Tests: `START-001`–`013` (`test/test_starter.py`: stand-ins in a throwaway folder and list — a run "crashed" keeps its
  entries; the next run's banner names them with the stop command; a reused id with another start time is not ours,
  reported on our port, never stopped; six runs adding and tidying at once lose nothing; a unit's leftover — and one
  holding its pipe — named and stopped by its job; the relay measured).
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
- **wait for conditions, never fixed sleeps** ("the toast appeared", not "wait 2 seconds") — **under generous limits**:
  a limit only matters when something's wrong, and a busy machine is no hang (2026-11-17, test_reset.py; §4). A test's
  own wait running out is a test failure, never the machine's trouble — it could hide a real hang. **Act on the tab in
  front**: with two tabs open, Chrome slows the one behind (§4) — bring a tab forward before acting on it, as a person
  switches tabs. The one exception is a wait the test can prove was the machine's: test_run_tests.py's stand-in relay
  (`standin_late`, §4) and its pair of files that must run together (RUN-049, 2026-11-18 — it waited a fixed 20 s for
  its partner; now each waits for the other's mark, up to 180 s): a partner the runner started with it that never
  reached its mark in that time is the machine's (`partner_late` — the check is stopped, the file exits 3 and is rerun
  alone); a pair the runner ran one after the other is a failure (RUN-094);
- **a fresh browser profile** for each run; stop what a test started by its exact process id (Law 5) — **and check it
  stopped** (each process gone, its port free: Law 12, 7.28.0);
- **a flaky test is fixed — or set aside, with a TODO — the same day.** Never tolerated, never "just re-run it". Set
  aside = a `skip: <TODO id> — why` line in the file's header (§4): every run then says so, and the next release is
  blocked until it's fixed.
- **A failing test is read first, not fixed first** (Law 3, 7.25.0): it may be the protection working.
- **A one-time failure — how it's handled now** (2026-11-17, TODO tooling item 9; §4): it is **kept** (the failed file's
  whole output beside the run's record, and its screenshot — `full output: <path>`), **read** before anything else, and
  **rerun only if it is the machine's or the browser's trouble** — which the screen-test driver itself recognizes and
  (or a heavy tier-1 file, for its own stand-ins — §4) says with exit 3, never a guess at the output afterwards: once,
  alone, after a wait, said loudly in the summary and
  noted in the record and on the stamp (`1 file retried after <reason> — its first output: <path>`). That rerun is the
  machine's hiccup being waited out, not "just re-run it": a TEST failure is never rerun — it is read, and fixed or set
  aside the same day. **Its rerun meeting the trouble again is NOT PROVEN, not a failure** — one run never retries more
  than once (2026-11-18). A file rerun after the trouble that keeps coming back is a flaky environment to look into — the
  first outputs say what happened — or a file that truly needs to run alone: **2 full runs in a row on this PC and the
  run says so, loudly**, with each run's kept outputs; **not proven 3 full runs in a row on this PC and it is HELD** —
  later runs don't run it ("held — not run", not proven) until Ron decides: `--release-held` (try again), `alone: yes —
  <why>` (run it alone every time) or `skip:` (§4). The run also slows down by itself: that trouble halves the browsers at once, at once,
  and the next runs start from the halved level, climbing back one at a time only after full runs without it (§4).
- **"Ran past its usual time" is the machine's trouble, not a failure** (2026-11-18, TODO tooling item 12 step 4; §4):
  a unit that runs past its stuck limit — from its average on this PC: average + 4 spreads, at least 4 times the average
  or 2 minutes (healthy tests ran 2–5× slower when other programs took the CPU — 2× stopped five healthy files, the
  2026-11-18 lab), at most 10 minutes — is stopped with every process it started, said plainly (`ran past its usual time:
  N s, its average M s`), the browsers at once halved, and rerun once, alone, with the flat 10 minutes. Read it as a
  busy PC, as any rerun after the machine's trouble: passed on its rerun, it counts as passed (the summary and the stamp
  say so). **Past the 10 minutes on its rerun too, it is a hang — a failure** (`✗ timed out after 600 s`), read as any
  failure: both outputs are kept. Its next run gets the full 10 minutes, so a test that truly grew slower relearns its
  average from that pass (§4) — a file that keeps being stopped at its limit is worth a look at what changed in it.
- **"Not proven" is the machine's trouble, not a failure — and not a pass** (2026-11-18 lab; §4): when more files meet
  the machine's or the browser's trouble in one run than are rerun (4), each one past that is reported `? <file>  not
  proven — the machine was too busy (N files met its trouble this run; only 4 are rerun) — <why>`, counted apart in
  the summary (`…, 0 failed, 2 not proven (the machine's trouble)`), its whole output kept; the run exits 3 (1 if a test
  also failed). Read it as the PC, not the test: look at what else the PC was doing (the loud `! N files met …` line
  says that many points at something broken), then run again when it's quieter — a not-proven file is never fixed as
  a failing test, and never counted as passed: the stamp stays NOT PROVEN and the merge script won't land on it. The
  same holds for a file whose rerun alone met the trouble again (`… (it met its trouble again on its rerun alone — one
  rerun a run) …`) — and for a HELD file (`held — not run`): not proven 3 full runs in a row on this PC, it waits for
  Ron's decision (§4).
- **A failed run is no measure of speed** (2026-11-17, §4): the browsers-at-once level learns only from runs where every
  file passed — a run with a failure is kept in its history, marked, but neither grows the level nor sets a time to
  beat, so a failure can't be mistaken for "faster" or "slower". A clean run more than twice as slow as usual at its
  level steps down by one — the PC busy with something else, answered gently, not halved.
- **A test can't vanish into a comment** (2026-11-18, sprint 8; TODO tooling item 11.3): an edit that swallows a line
  break joins the next line onto the comment above it — a `check(…)`, a table row, a `test(…)` stops running and the file
  still passes. The commit check `git-hooks/check-joined.py` (pre-commit step 11) refuses a staged test file whose
  comment ends in a complete line of code, read by each language's own parser. A comment that truly ends in code says
  why: `# not-joined: <why>` (`//` in JavaScript). `py git-hooks/check-joined.py --all` checks every test file; what it
  catches and what it doesn't is in its header. Since sprint 9 also a line joined with one space after a line of dashes
  (a separator comment) and JavaScript's `'use strict';`. Tests: `JOIN-001`–`054`.

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
- **Built 2026-11-17 (branch `tooling/failed-output-graceful`, TODO tooling item 9):** a failed file's whole output kept;
  the machine's or the browser's trouble told from a test failure by the driver (exit 3) and rerun once, alone; fewer
  browsers when memory is low — §4, §7. `tools/environment_trouble.py`; `test/ui/test_environment.py` (ENV-001–004);
  RUN-072–082.
- **Built 2026-11-17 (branch `tooling/adaptive-browsers`, sprint 7):** the runner chooses how many browsers to run at
  once by itself, 1 to 6, saved per PC — halved at once on the machine's trouble, one more after a clean full run, back
  down when one more gained nothing (§4); the fixed low-memory rule removed; the PC's slots 4 → 6.
  `tools/browser_level.py`; `test/test_browser_level.py` (LEVEL-001–016); RUN-079 (reworded), 083, 084.
- **Built 2026-11-17 (branch `tooling/tier1-load`, sprint 7):** heavy tier-1 files hold a test slot within the browsers'
  level and back it off on their machine trouble (`heavy: yes`; five files marked); a light tier-1 file never waits
  behind a slotted one; test_run_tests.py tells a late stand-in relay (the machine's) from the runner's failure; a
  library script that failed to download is the network's trouble; test_reset.py's waits are conditions, on the tab in
  front — §4, §7. RUN-087–091, ENV-005–007, LEVEL-022.
- **Built 2026-11-18 (branch `tooling/measure-tests`, sprint 8):** what each test costs, measured per unit for its whole
  process tree (a Windows job object) — memory committed, RAM private (sampled), CPU, I/O — in each run's record, averaged per PC
  (RFC 6298) by full passing runs only, and shown by `--costs` — §4. `tools/test_costs.py`; `test/test_test_costs.py`
  (COST-001–013). Measuring only; scheduling unchanged.
- **Built 2026-11-18 (branch `tooling/one-starter`, sprint 9):** one starter for every process our tools start
  (`tools/starter.py` — the screen tests' web server moved onto it), a list of every process it started kept until each
  is confirmed gone, leftovers shown loudly at a run's start and end with a `NEEDS YOUR ATTENTION:` line; what a test unit
  leaves running stopped by its job; the relay tests' relay measured — §4. `test/test_starter.py` (START-001–013);
  COST-024 (a run narrowed by `--id` with a screen test no longer teaches the averages).
- From then on, every task follows §6.
