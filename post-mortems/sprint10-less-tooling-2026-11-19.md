# Post-mortem — sprint 10 (2026-11-19): separate clones, remove what didn't pay, the compaction hooks — tools only

_Branch `sprint-10` (from main), ready at `ebbb474`: the closing full run passed all 65 files (tiers 1, 2 and 3, 6 min
59 s), stamp PROVEN. Not yet on main — waits for Ron's word. No app version. The last tooling sprint: the remaining
tooling ideas are parked in the TODO's "Watching"; a cold review of the TODO runs before app work resumes._

## Why

An outside review (2026-11-19, `.private/OUTSIDE-REVIEW-2026-11-19-REPORT.md`) found the tooling had passed the point
of diminishing returns at sprint 7, that the tooling's own tests caused both real outages, and that two safeguards had
holes. Ron accepted it: "If nothing else we learned from it… don't over-engineer it" — and gave up his own design, the
adaptive browser count ("my baby, but I'm willing to give it up").

## What shipped (into `sprint-10`)

1. **Working copies are separate clones** — their own git settings and history; a test proves a copy marked "bare"
   leaves the main folder untouched. Plus a check, before and after each run, on the main repository's shared settings.
2. **Removed:** the adaptive browser count (now a fixed 4), the limits learned from averages (now a flat 10 minutes),
   the running averages (each run's own measurements kept — "never throw away information"), the process list
   (`tools/starter.py` — Windows now ends everything a test started), the joined-line check. **~5,700 lines deleted,
   ~2,700 added** across the sprint; the runner's header 144 → 43 lines; the per-PC test state out of the temp folder.
3. **The prod guard:** while the autonomy switch is on, a push of main to prod is refused unless Ron's newest message
   says "push to prod".
4. **The compaction hooks** (global, `C:\Users\Ron\Projects\compaction_carry.py`): before a compaction, the summary
   gets a rule to carry every open topic with Ron's words and the argument; after it, Ron's latest messages come back
   word for word — by size, not a fixed count (Ron's "smart decision").

## What went right

1. **Subtraction worked first time:** three agents in parallel, each merge proven on the first try (one doc collision,
   settled by hand), 65 files passing at the end with three test files fewer.
2. **The clones agent found a real blind spot** the old setup hid: inside a clone the private-values commit check would
   have checked nothing — fixed with a test before it could matter.
3. **Building the compaction hook against the real transcript** caught two bugs before wiring (a queued message stored
   as a list; my reply picked from mid-task narration) — and confirmed the conversation's real size (about 2,000 of
   Ron's messages over three weeks).

## What went wrong

1. **I wrote invented labels to Ron** ("subtraction pass", "the shrink") — the third such slip in two days. Ron: "Why
   didn't you just say it plainly?" Saved as a standing rule in memory with his own example sentence.
2. **Ron's "always allow" answers widened the push permission twice** (back to `git push *`) — prompts for harmless
   reads made "always" a habit. Fixed at the source: seven read-only text tools are now allowed, so those prompts stop.
3. **The first prod-guard idea would have refused Ron's own release pushes** (the switch is on for days) — caught in
   design, not in use: the guard reads his newest message for "push to prod".

## The numbers

- Copies: 20–56 minutes each; recorded test time 14–19%.
- The test library: 65 files (68 before), all passing; tier 1 now 36 files.

## Laws touched

- **Law 23** ("A mechanism has a cost") was written this morning and applied the same day — this sprint is its first
  use: three mechanisms removed, none added beyond the two that close real holes (the prod guard, the shared-settings
  check) and the one Ron asked for (the compaction hooks).

## Next (Ron's calls)

1. Review `sprint-10` → main → prod: say **"push to prod"** (the new guard needs those words).
2. The cold review of the TODO (running) → its findings with my verdicts → then app work.
