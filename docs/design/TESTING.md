# Testing — the regression library, and how it grows

_Decided 2026-11-04 (Ron + Claude). The umbrella over every test in ReaderWrangler: what kinds there are, when each
runs, how the library grows task by task, and the rules that keep it trustworthy. Supersedes the "out of scope —
permanently" line of PRELAUNCH-TEST-GATE.md for screens, dialogs, drag-and-drop and menus: the browser driver makes
them testable, and with Claude writing the tests the cost that justified skipping them is gone. That doc's suites stay
the pre-launch data gate (task "All the pre-launch data tests pass")._

---

## 1. The rule

> **"If you don't have a test case, you can't prove you fixed it."** — Ron

The regression library is built **gradually, from the work** — never written up front. Each task adds the tests that
prove it; each bug fix adds the test that would have caught it. Over time the library becomes the guarantee that
nothing that once worked silently stops working.

## 2. Two levels — test at the lowest one that can catch the problem

1. **Function tests** — fast, sturdy, most of the library. For logic: merging, the book-field table, the ownership
   rules, date labels, the key format and its check characters, Auto-Organize, the overlay stack. Plain Node files in
   `test/` (the five that exist today).
2. **Screen tests** — through the browser driver (Playwright for Python, the installed Edge, a throwaway profile).
   Only for what only the screen can show: what the Delete key targets, focus staying inside a window, drag labels,
   two tabs catching up, a menu item disabled rather than missing.

A bug in a function caught by a screen test costs a hundred times the runtime and breaks whenever a button moves. When
a screen test is the only way to catch something, consider first whether the logic should be lifted into a function
that a function test can reach.

**Free with every screen test:** anomaly reporting ("Report our own unexpected errors…") is switched on in the
driver's browser, so **any unexpected error fails the run** — every screen test also checks "nothing went wrong
underneath".

## 3. Tiers — when each runs

| Tier | What | When | Budget |
|---|---|---|---|
| **1** | Function tests + the commit checks (names, parse, versions, private values, TOC…) | **Every commit, automatically** — only the tests covering the staged files | seconds (≤ ~10 s) |
| **2** | Screen tests | **Before every alpha Claude hands Ron** — Ron is never the first to find a regression | a few minutes (≤ ~5 min) |
| **3** | Relay tests (a local relay; dev only as a final check) | When relay code changes; before any worker deploy | ~1 min |
| **all** | Every tier | **Before every release** (release checklist step) | |

Plus a short **manual list per release** (§8) for what can't be automated.

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
  `--tag <area>`, `--id <ID>`, `--changed` (the tests covering what changed). One summary at the end; a screen test's
  failure saves a screenshot and the console to Claude's scratch folder. The commit hook calls it with `--changed`.

## 5. Test data — two kinds

1. **A small, frozen, made-up library** (`test/fixtures/`, committed — no personal data). Built **on purpose to hold
   the awkward cases**: an omnibus at several positions, a sample and a loan of a wishlisted book, books in the Trash,
   deep and pinned folders, a book in no folder, a Book List with repeats, Amazon tags and your own tags, a book with no
   description. **Exact checks run against this.** It grows as tests need new cases.
2. **Ron's real backup, with the Cloud Sync Key removed** — for scale and speed (3,270 books): load time, drag with
   thousands of covers, "does it hold up". **Never committed**; its location is a local setting; the test loader
   strips the key and refuses a file that still carries one. Not used for exact answers (it changes as Ron works).

Screen tests never use Amazon's pages and never the real library's cloud copy: the test app has no Cloud Sync (or a
throwaway test channel on a local relay). Whatever the driver shows Claude goes to Anthropic — so the demo-style
fixture, never anything sensitive on screen.

## 6. The per-task routine

1. **A bug fix starts with a failing test** that reproduces the bug — then the fix makes it pass. (The utilities
   project's Law 18: reproduce with real input before explaining.)
2. **A feature's tests are its acceptance criteria**, written with it — the task's "What you'd get" made checkable.
3. **At the task's end:**
   - **promote** its tests into the library (almost always — a test that passed once costs nothing to keep); a test
     left out says why;
   - **gaps** found next to it (things the task touched that nothing tests) are either filled now, if small, or
     **filed as TODO items**.
4. **The mechanisms (not memory):**
   - each task in work gets a short **Tests** section — the IDs it added, and gaps filed;
   - the **release checklist** asks "every task in this release: tests promoted, gaps filed?";
   - the **post-mortem** asks which bug of the release no test would have caught — and that test is written.

## 7. Trust — the flakiness rules

A test that fails sometimes teaches everyone to ignore failures (Law 12: an alarm on the normal path is noise). So:
- **fixed data** (§5.1) and **a fixed clock** where dates matter (the "today / yesterday" labels);
- **wait for conditions, never fixed sleeps** ("the toast appeared", not "wait 2 seconds");
- **a fresh browser profile** for each run; stop what a test started by its exact process id (Law 5);
- **a flaky test is fixed — or set aside, with a TODO — the same day.** Never tolerated, never "just re-run it".
- **A failing test is read first, not fixed first** (Law 3, 7.25.0): it may be the protection working.

## 8. What stays manual (a short list per release)

- **Amazon's live pages** — the fetchers against the real site (fetcher *logic* can be tested against saved pages kept
  privately; the live run stays a release step).
- **Taste** — how it looks and reads.
- **A real phone** (Android, and an iPhone — Ron has access to one) until device testing is automated.

## 9. Where it starts

- **Today:** five function-test files (bookFields, bookMerge, datePresets, organizeEngine, overlayRegistry — ~80
  checks, each run by hand with `node test/<file>`), and the two relay scripts (`relay/test-phase1.mjs`,
  `relay/test-signed-writes.mjs`). No screen tests, no runner, nothing runs on commit.
- **Step 2 of the order of work** ("Carry over the utilities project's improvements…") builds:
  1. the parse check (tier 1);
  2. `tools/run_tests.py` with tiers, tags, IDs and `--changed`; the existing files get `tags:` / `covers:` headers and
     IDs; the commit hook runs `--changed`;
  3. the browser driver (Playwright for Python + Edge) and the small fixture library's first version;
  4. the first screen tests — from anomaly reporting and the Delete key fix (step 4), each starting from a failing test.
- From then on, every task follows §6.
