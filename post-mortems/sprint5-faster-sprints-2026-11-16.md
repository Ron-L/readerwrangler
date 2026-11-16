# Post-mortem — sprint 5 (2026-11-16): faster sprints — tools only, no app release

_Merged to main 2026-11-16 as `4470dd1` (squashed from main-prime), pushed to prod and dev at Ron's word ("yes to
all"). No app version, no tag: nothing a person using ReaderWrangler sees changed. Branches kept: feature/faster-sprints,
feature/faster-sprints-cells._

## Why

Sprint 4 took ~11 hours for one big task; about half was full test runs — ~10 minutes each, ~3 per round, one after
another in one shared folder (Ron, 2026-11-15: "Testing is GOOD. But if we can do anything to speed it up, that would
be VERY GOOD").

## What shipped

1. **Screen tests in parallel** under a machine-wide limit (4 OS-locked slots); a file can split itself (`shards: 3`
   for the 129 cells). **Tier 2: 594 s → ~3 min; tier 1: ~2 min.**
2. **Results stamped with their commit:** review checks `--stamp` (PROVEN only for full tier 1 + 2 on a clean tree of
   exactly that commit; `--id`, `--tag` or `RW_CELLS` don't count) instead of rerunning.
3. **Working copies** (`tools/copies.py`) — Ron's idea — and **branches merged by a script**
   (`tools/merge_branches.py`) that regenerates what's generated and lands only a proven merged result.
4. CLAUDE.md's agent workflow (Ron's wording, Q-043).

## What went right

1. **Isolation was proven before parallelizing** — and found two real races (a test's server answered by another
   file's server; two servers rebuilding `dist/` at once).
2. **A hazard caught before it bit:** `git worktree remove` deletes THROUGH a directory junction into what it points
   at. The removal script unlinks first, refuses a folder it can't scan, and checks the main folder lost nothing.
3. **The merge script earned its keep on its first job:** the full run on the merged result found a test that lost
   evidence under load (three processes appending to one file) — and refused to land until it was fixed.
4. **The first real working copy** let an agent build while the main folder stayed free — the wait it was built to end.
5. Agents found a hole in their own tool (a run narrowed by `RW_CELLS` would have counted as full) before it was ever
   relied on.

## What went wrong

1. **The gate didn't work in a copy, and the private-values check quietly checked less there** — both found by testing
   inside a copy, both fixed with tests. A tool moved somewhere new is a new place for every check.
2. I wrote "worktrees were ruled out" into the TODO from memory; CLAUDE.md actually said "a worktree each" — corrected
   before commit by reading it (Law 2).
3. "Keep as is" read two ways; asked rather than guessed (a CLAUDE.md change).

## Laws touched

- **Law 5** (class of sites): moving work into a copy is a class change — every check must be shown working there.
- **Law 22:** two local-relay launchers became one.

## Next

Ron, before the next sprint: is `main-prime` still needed? Then TODO's order: "Messages never block a click", "A book
left in no folder…".
