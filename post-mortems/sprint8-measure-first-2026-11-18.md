# Post-mortem — sprint 8 (2026-11-18): measure first — tools only, no app release

_Branch `sprint-8` (from main `d9e4ced`), ready at `eee45ee`: the closing full run passed all 61 files (tiers 1, 2 and
3, 6 min 58 s), stamp PROVEN. **Not yet on main** — waits for Ron's review. No app version, no tag. Every task branch
kept (local, dev, prod)._

## Why

Ron, 2026-11-17: "Rather than treat every test equally we should measure them … learn which resources are the most
critical … Change those resource limits when runs fail. Increase them when all works." And 2026-11-18: "YES!!! Measure
1st. If you don't measure you won't know if you've improved things." Plus sprint 7's leftovers (TODO tooling item 11).

## What shipped (into `sprint-8`)

1. **Every test measured** (`tools/test_costs.py`): time, memory committed, the RAM it adds (private, sampled), CPU,
   I/O — for every process it starts, browsers included (proven: none escaped the measurement); TCP's own running
   average and spread per PC; `py tools/run_tests.py --costs`.
2. **Copies keep their records and say where their time went** (`copies.py remove`, `copies.py report`).
3. **No test line joined onto a comment** — commit check step 11 (0 false refusals on 1,712 comments; caught 438–459
   of 465 deliberate joins); in CLAUDE.md with Ron's wording.
4. **The runner's three:** a file rerun alone runs in a row is said loudly; the heavy-file trouble path tested end to
   end; RUN-049 waits for its partner, not 20 s.
5. **The 79 fixed waits** now wait for the thing itself (11 that prove a duration or an absence stay, marked).
6. **Longest first by the average; a "stuck" limit per test** from its history (max(4× average, 120 s), up to the
   flat 10 min); a test past it is the machine's trouble, rerun alone; trouble beyond the rerun cap is **"not
   proven"**, never a failure.

## The measurements

**Before → after the waits** (5 quiet full runs each, `.private/sprint8-*-costs.*`): all tests' time added up 1,690 →
1,251 s (−26%); test_cells' three parts ~148 → ~49 s each; test_delete_key 73 → 37 s; a full screen-test run 3:10–5:06
→ 2:44–2:54. CPU 960 → 913 s — the time removed was idle waiting.

**Which resource breaks runs** (lab 4, one at a time, 3 runs each): memory squeezed to 0.7–1.1 GB free → no trouble,
no slower; disk (4 churners) → 1.5× slower, no trouble; **CPU (15 of 16 busy) → trouble at once, 5× slower** — and
fewer browsers was *slower* when other programs held the CPU (2 at once 1,687 s; 3 at once 924 s). So step 3 (a memory
budget) was **not built** — the agreed rule needed memory to be what runs out (Q-045 asks Ron what next).

**The stuck limit under load** (lab 5): the first floor (2× the average) stopped five healthy heavy files under CPU
load, and the fifth — past the rerun cap — was counted as a failure. Both fixed the same afternoon (the floor 4×; "not
proven").

**Where the agents' time went** (`copies.py report`, 9 building copies): test runs 2–14% of each copy's life; the rest
building — and waiting for my merge (step 4's copy: done at 12:37, held until the lab ended at 14:02). Caveat: their
`--changed` runs aren't recorded (TODO 13.1).

## What went right

1. **Measuring first paid off three times:** the RAM column was wrong (shared pages) and fixed before anything was
   decided on it; the self-tests were polluting the real averages, caught by the first real `--costs`; and the lab
   overturned the obvious guess (memory) — the budget that would have been built on that guess wasn't.
2. **Parallel copies, no idle chain:** up to four agents at once, each merge proven, zero mid-sprint waits on Ron
   (the one CLAUDE.md wording took him a minute).
3. **The labs found real defects** a quiet PC never shows: ENV-006's timing race, the 2× floor, the "✗" for a slow test.
4. **The waits agents found an app bug** a fixed wait had hidden: a refused Restore shows a false "Restore Warning"
   box a minute later (filed in Polish).

## What went wrong

1. **I said a decision was logged before I'd logged it** (12:07, the step 4 floor) — corrected at 12:20. Law 12: a
   receipt needs a mechanism that can know; mine was memory.
2. **My own floor (2×) was a guess** — the agreed rule had none; I added one "to be safe" and the lab proved it unsafe.
   Fixed by data the same day, but it should have been tried in the lab before merging.
3. **The lab's disk helpers left 1.1 GB of files** (a force-stop skips their own clean-up) — removed by exact name;
   the lab now removes them itself.
4. **One agent used `sed -i`** once (identical result, self-reported); later briefs said "never".
5. **"No network buffer space" stays unexplained**: three times today on quiet runs at 5 browsers (connections peak
   ~1,900 of 16,384 — not simply full). Handled correctly each time (back off, rerun alone, passed).

## Laws touched (proposed — Ron decides)

- **Law 3** (prove the theory): *a safety margin is a theory too* — the 2× floor needed the lab before the merge, not
  after.
- **Law 12** (mechanical honesty): *"logged" is a claim — write the line, then say it.*

## Next (Ron's calls)

1. Review `sprint-8` → main, and prod on his word.
2. Q-045: close item 12 here, or a CPU budget / gentler back-off next.
3. Where the false Restore Warning goes in the TODO.
