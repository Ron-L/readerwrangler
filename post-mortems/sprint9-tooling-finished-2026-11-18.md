# Post-mortem — sprint 9 (2026-11-18, evening): tooling and testing finished — tools only, no app release

_Branch `sprint-9` (from main `9b3e6d4`), ready at `f062850`: the closing full run passed all 67 files (tiers 1, 2 and
3, 8 min 24 s), stamp PROVEN, no leftover processes, nothing held. **Not yet on main** — waits for Ron's review. Ran
19:55 → 21:44 while Ron slept on it ("I'd like you to work on this for me to review in the morning")._

## Why

Ron, 2026-11-18: "Which of the TODO tasks have to do with tooling and testing? I'd like to consider those if it is
something we can finish up and be done with and therefore leverage going forward." He chose A + D: the test runner's
leftovers, one starter for every process, the working-process safety net, the "open" shortcut — and the trim of the
always-loaded rules (as a proposal).

## What shipped (into `sprint-9`)

1. **A file that can't be proven is held** (Ron's design, approved that evening): a rerun that meets the machine's
   trouble again is "not proven", never failed; 3 full runs in a row not proven on this PC → held, not run, nothing
   merges past it until Ron releases it, marks it to run alone, or sets it aside.
2. **Every test run is recorded** (Ron: "Absolutely record them. Why would you not???") — the quick ones on their own
   shelf, so they never push out the full runs; the copies' time reports now include them.
3. **No test inherits git's hook variables** — one place in the runner strips them from every test process.
4. **One starter for every process:** the relays and the screen tests' web server; a list of every process started;
   leftovers said loudly at a run's end and the next run's start; a test's leftover processes named and stopped; the
   relay tests' relay measured.
5. **One set of screen-test wait helpers** with one limit (60 s), 175 short limits made generous; the screen-test
   harness ends through the runner's one routine; the joined-line check's two gaps closed (and its scan made linear).
6. **The safety net:** a loud warning when a copy isn't set up for the commit checks (serve.py and session start); a
   backup of Claude's memory and settings into the private notes and the Projects folder — **first real run done**
   (19 memory files added, 14 updated; the last backup was 10-22); one "write a file whole" routine.
7. **The "open" shortcut tool** (`tools/shortcuts.py`, `serve.py --open`) — built and tested without a click.
8. **The rule-trim proposal** (`.private/proposals/rule-trim/`): the three always-loaded files 57.8 K → 27.0 K
   characters, every moved section word for word in its new home — for Ron's yes.

## The incident

At 20:21:56 the shared git settings of the real repository were switched to "bare" (no working files); every git
command in the main folder and all four copies failed until I repaired it at 20:34. **Cause** (found and reproduced
by the safety agent): its first, never-committed test ran `git init` in a temporary folder while the commit check's
git variables still pointed at the real repository — in a working copy git then decides the shared repository is
bare. Nothing else was touched; no branch or commit lost. **Fixed twice:** the agent's tests no longer inherit those
variables (proven byte-for-byte on the real settings), and — the one that matters — the runner now strips them from
every test it starts, so the next new test file can't repeat it.

## The numbers

- **Agents' copies** (`copies.py report`): about 1 h 15 min – 1 h 30 min each; recorded test time 5–18%, except the
  helpers agent's 58% (its proof runs: every screen file, 4 rounds).
- **The commit check's own runs, recorded for the first time:** 3–6 minutes each in the runner agent's copy (the heavy
  tier-1 files that cover run_tests.py run on every commit touching it) — the next speed-up target (filed).
- **Every merge passed its full run first time** (4 merges, tier 1 33–38 files, tier 2 27).

## What went right

1. **Four agents at once, no idle chain**, and the overlapping change (two agents in `run_tests.py`) resolved by the
   later agent merging the earlier one's landed work — no conflict for me to untangle.
2. **The incident was found by its symptom in under 15 minutes** and traced by timestamps (the settings file's change
   time against the agents' commit times), then reproduced on a scratch copy before anything was called fixed.
3. **Agents reported their own slips plainly** (the safety agent's first attempt; the helpers agent re-checked its one
   commit made inside the broken window by hand).
4. **Recording every run paid off within the hour** — it showed the 3–6 minute commit checks nobody could see before.

## What went wrong

1. **A test touched the real repository.** The convention "each test file clears git's variables" (from sprint 5) was
   a promise; a new file forgot it on its first run. The meta-principle in action: only the mechanism (the runner
   clearing them for every test) prevents it.
2. **Working copies share more than files.** The git settings, the slots folder and the real records are shared by
   every copy — damage in one copy reaches all of them at once. Nothing checks that shared state stays healthy.
3. **Ron's settings now always allow `git push`** (approved from prompts that evening) — so a push of main to prod no
   longer stops at a prompt. The rule ("main to prod only on Ron's word") still holds, but its second safety is gone.
   Flagged to Ron; not changed by me.

## Laws touched (proposed — Ron decides)

- **Law 5** (every instance of a class): *what the copies share is a class too* — the git settings, the slots folder,
  the records: a change to any of them needs a mechanism that protects all copies, not a per-file habit. Proposed
  mechanism (filed): the runner checks the shared git settings are healthy before and after each run and says so
  loudly if not.

## Next (Ron's calls)

1. Review `sprint-9` → main → prod on his word.
2. The rule-trim proposal (Q-046) and the release-checklist line for the backup (Q-047).
3. Click the shortcut: `py tools/shortcuts.py`, then "ReaderWrangler (local)" from Windows search.
4. His settings' `git push` allowance — keep, or narrow it to dev.
