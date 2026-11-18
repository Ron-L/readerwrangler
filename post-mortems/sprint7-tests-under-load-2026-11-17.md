# Post-mortem — sprint 7 (2026-11-17): tests under load — tools only, no app release

_Merged to main 2026-11-17 as `37a0ea9` (squashed from `sprint-7` at `f7329a6`, whose full run passed: tiers 1, 2 and 3,
59 files, 6 min 25 s). `main` pushed to dev; **not to prod — that waits for Ron's word** (it deploys). No app version, no
tag: nothing a person using ReaderWrangler sees changed. Branches kept (local, dev, prod): `sprint-7`,
`tooling/failed-output-graceful`, `tooling/adaptive-browsers`, `tooling/level-goodput`, `tooling/tier1-load`._

## Why

Ron, 2026-11-16, keeping a dozen or two browser tabs open: "We should probably fail browser issues gracefully. Detect
that is what it is, back off and slow down and repeat." Then 2026-11-17: "I had suggested an algorithm similar to how
TCP works … Use more and more until you hit failures. Kill the failed ones and back off. Occasionally try to increase
again" — and "measure for diminishing returns … conditions change".

## What shipped

1. **A failed file's whole output is kept** beside the run's record (and its screenshot); the summary names the path.
2. **The machine's or the browser's trouble is told from a test failure** (exit 3 + a marked line,
   `tools/environment_trouble.py`) — a page that never loaded, a browser that crashed, our own server refusing, a
   library that failed to download from its site — and **rerun once, alone**, said loudly. A test failure is never rerun.
3. **The runner chooses how many browsers at once by itself** (`tools/browser_level.py`, Ron's design): 1–6, saved per
   PC; halved at once on trouble; one more after a clean full run; back down when one more gained nothing (5% margin,
   held 5 runs) or a clean run took more than twice the best recent at that number; only fully passing runs count.
4. **Heavy tier-1 files** (`heavy: yes — why`) take a test slot inside that number and back it off too.
5. **Waits on conditions, not moments,** in `test_reset.py` (under load: 0 of 2 before, 2 of 2 after) and the toast
   tests (TOAST-001 read a warning's amber mid-fade on a loaded PC).

## The load lab (Ron's idea: "vary the load … confirm the agents pull back. Then drop the load")

The lab squeezed the PC on purpose (memory down to 1.5 GB free, 14 of 16 cores busy) with its own saved number, never
the real one. Lab 3b, 2026-11-17 19:35–20:29:

| # | phase | at | result | next | why |
|---|---|---|---|---|---|
| 1 | quiet | 4 | 27/27, 266 s | 5 | clean |
| 2 | quiet | 5 | 27/27, 232 s | 6 | clean, faster |
| 3 | load | 6 | 27/27, 661 s | 5 | **no failure, but 2.8× slower → back off** |
| 4 | load | 5 | 26/27, 858 s | 2 | trouble (our server refused) → halved; that file rerun alone, passed; TOAST-001 failed (the mid-fade read) |
| 5 | quiet | 2 | 27/27, 371 s | 3 | clean |
| 6 | quiet | 3 | 27/27, 279 s | 4 | clean |
| 7 | quiet | 4 | 27/27, 233 s | 5 | clean |
| 8 | quiet | 5 | 27/27, 205 s | 5 | holds — "6 gained nothing" (judged at run 3, under load) |

It pulls back under load and climbs back one step per clean run. One quirk to watch: the "6 gained nothing" note was
made under load, so it holds 6 off for a few quiet runs after — it expires by itself.

## What went right

1. **The merge script refused twice** (RUN-079, then RUN-057 — timing tests failing under tier 1's parallel heavy
   files) and didn't land. We found the cause — heavy tier-1 files running side by side with no load awareness — instead
   of patching the two tests (Law 4). That became task 3.
2. **The slowness rule caught a run that didn't fail** (lab run 3: everything passed, 2.8× slower) — the case "count
   only failures" would have missed.
3. **The lab found a real test flaw** (TOAST-001) that a quiet PC never shows — a fade read too soon.
4. **Ron's question "it is taking hours — re-running by mistake?" was answered by counting**, not guessing: 29 runs
   recorded, 175 minutes, about 130 of them the labs; no mistaken reruns (`.private/CONVERSATION.md`).

## What went wrong

1. **Lab 1 wasted 40 minutes, and its load outlived it.** I moved the temp folder to give the lab its own saved number —
   which broke the local relay (every run failed). The lab then crashed printing "→" to a cp1252 console and left its
   load running ~30 minutes; its busy helpers outlived "load off" because `os.getppid()` keeps a dead parent's id on
   Windows. Fixed: `RW_TEST_SLOTS_DIR`, a pid file listing every helper, stopped by exact id in `finally`, helpers that
   ask Windows whether their parent lives — proven (they exit within 4 s) before lab 3b. **Lesson: a tool that squeezes
   the machine has its stop proven before it starts.**
2. **The TCP design should have come from Ron's earlier words** — a profile miss (logged in RON-PROFILE's calibration).
3. **A TODO note said "Ron confirmed"** when he'd said "We've discussed it in the past" — corrected to his words.
4. **The sprint idled 16:32 → 17:53** — its tasks were one chain, and a design question sat in the middle. With
   independent tasks, one parks and the others go on.
5. **A working copy's run records are deleted with the copy**, so the agents' own test time can't be counted (filed:
   tooling item 11.6).

## Bugs no test would have caught → the test

- TOAST-001's mid-fade read: caught by the lab, fixed with one shared `amber_look` (TOAST-001 and -003), checked under
  load (TOAST-001–005, two rounds, all passed).
- A heavy tier-1 file that exits with "the machine's trouble": its pieces are tested, the whole path only by hand —
  filed (tooling item 11.2).

## Laws touched (proposed — Ron decides; laws don't change in a sprint)

- **Law 14** ("investigate before estimating"): *count before answering "why is it slow"* — the records answered in
  minutes what memory would have guessed.
- **TESTING.md, not a law:** *a test waits for a condition, never a moment* — 79 fixed waits remain (tooling item 11.1).

## Next (Ron's calls, in `.private/CONVERSATION.md`)

1. `main` to prod (tools only — the site's files are unchanged).
2. Speeding sprints up: settle designs before the sprint, independent tasks; one full check per task instead of per
   alpha (changes his 11-13 rule); no repeated full run at merge when nothing tested changed.
3. His per-test resource budget (tooling item 12) — step 1, measure only, in a later tools sprint.
