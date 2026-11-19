#!/usr/bin/env python3
"""
held_tests.py — a test file that can't be proven is HELD (TODO tooling 13.13; Ron, 2026-11-18: "I think not proven. But
we don't want to go into an infinite try loop if a file is never going to run under current resources and loading … Give
up after say 3 failures of same file and report it and await instruction from me?" — the proposal approved the same day).

Per PC, beside the test slots (test_slots.slots_folder(): RW_TEST_SLOTS_DIR, else %TEMP%\\rw-test-slots), in
`held-tests.json` — so the runs of every working copy and of every merge on this PC add up (TODO tooling 13.10: the
count read only one folder's records until then). For each test file (its name in the repository, the same in every
copy), the FULL runs in a row in which it met the machine's or the browser's trouble (docs/design/TESTING.md §4):

    rerun alone   it met the trouble, was rerun alone, and passed — proven, but worth knowing
    not proven    its rerun alone met the trouble again, or no rerun was left for it (more files met it than are rerun)

A full run that passed it the first time — or failed it (a test failure: a definite answer) — ends its streak. Only full
runs count (run_tests.py: a run narrowed by --changed, --id, --tag or RW_CELLS is passed over — it leaves its record on
the quick shelf, never read here). Then:

    SAID_AFTER (2) in a row        said loudly: it may truly need to run alone (TODO tooling 11.7)
    HOLD_AFTER (3) in a row NOT PROVEN   HELD: "couldn't be proven in 3 runs in a row on this PC — held for Ron's
                                   decision". Later runs don't run it: "held — not run", counted as not proven — so no
                                   stamp is PROVEN and nothing merges past it. That block IS the "await instruction".

Ron's ways out: `py tools/run_tests.py --release-held <file>` (try again — the hold and the streak cleared); an
`alone: yes — <why>` line in its header (it then runs only while it holds every test slot on the PC — a hold taken while
it ran beside others is lifted by it); or `skip: <TODO id> — <why>` (set aside, the existing way).

Saved as tools/test_costs.py saves its averages: read, merged and written under the slots' own OS file lock
(test_slots.locked), written whole (browser_level.save). Tested by test/test_run_tests.py (RUN-076, 092, 098–101).
"""
import contextlib
import datetime
import json
import os
import sys

if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import browser_level   # noqa: E402 — the one way a file is written whole (save)
import test_slots      # noqa: E402 — the one way a file is locked on this PC (locked)

FILE_NAME = "held-tests.json"
SAID_AFTER = 2          # full runs in a row met by the machine's trouble → said loudly (TODO tooling 11.7)
HOLD_AFTER = 3          # full runs in a row NOT PROVEN → held (Ron, 2026-11-18: "say 3")
HOLD_ON = ("not proven",)   # the outcomes that count toward a hold — a rerun alone that passed proved the file
KEEP = 10               # runs kept in a file's streak
LOCK_LIMIT_S = 30.0
TROUBLED = ("rerun alone", "not proven")


def path_in(folder):
    return os.path.join(folder, FILE_NAME)


def fresh():
    return {"version": 1, "files": {}}


def load(path):
    """(state, note) — note None when read; missing → fresh (no note); damaged → fresh, and the note says so."""
    try:
        with open(path, encoding="utf-8") as f:
            s = json.load(f)
    except FileNotFoundError:
        return fresh(), None
    except (OSError, ValueError) as e:
        return fresh(), f"the held tests' file couldn't be read ({type(e).__name__}: {path}) — starting again"
    if not isinstance(s, dict) or not isinstance(s.get("files"), dict):
        return fresh(), f"the held tests' file couldn't be read (damaged: {path}) — starting again"
    return s, None


@contextlib.contextmanager
def _held_lock(path):
    with test_slots.locked(path + ".lock", limit_s=LOCK_LIMIT_S) as got:
        yield got


def read(path):
    """(state, note) — load(), under the lock (a save may be putting the file in place right now)."""
    try:
        with _held_lock(path):
            return load(path)
    except OSError as e:
        return fresh(), f"the held tests' file couldn't be read ({e})"


def holds(state):
    """{file: its hold} — every file held on this PC."""
    return {k: v["held"] for k, v in (state.get("files") or {}).items() if isinstance(v, dict) and v.get("held")}


def apply(state, outcomes, when):
    """The state after one FULL run — pure: a new state. outcomes: {file: {outcome, why, …, alone}} — outcome one of
    'passed' (the first time), 'failed', 'rerun alone' (passed on its rerun), 'not proven'. Returns (state, {file: its
    streak, newest last — for every file troubled this run}, [files held by this run])."""
    files = json.loads(json.dumps(state.get("files") or {}))
    troubled, newly = {}, []
    for name, o in outcomes.items():
        entry = files.setdefault(name, {"streak": []})
        if entry.get("held"):
            continue            # held: it wasn't run (or its hold was lifted before the run — release() cleared it)
        if o.get("outcome") not in TROUBLED:
            entry["streak"] = []        # a definite answer ends the streak — passed the first time, or a test failure
        else:
            run = {"when": when, **{k: v for k, v in o.items() if k != "alone" and v is not None}}
            entry["streak"] = (list(entry.get("streak") or []) + [run])[-KEEP:]
            troubled[name] = entry["streak"]
            last = entry["streak"][-HOLD_AFTER:]
            if len(last) == HOLD_AFTER and all(r.get("outcome") in HOLD_ON for r in last):
                entry["held"] = {"since": when, "alone": bool(o.get("alone")), "runs": last}
                newly.append(name)
        if not entry.get("streak") and not entry.get("held"):
            files.pop(name, None)       # nothing to remember
    return {"version": 1, "files": files}, troubled, newly


def note_run(path, outcomes, when=None):
    """Add one full run's outcomes to this PC's file, under the lock (runs finishing together each add theirs).
    Returns (troubled streaks, newly held, None) — or ({}, [], why it couldn't be saved): a run never fails on it."""
    if not outcomes:
        return {}, [], None
    when = when or datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    try:
        with _held_lock(path) as got:
            if not got:
                return {}, [], f"another run held {path}'s lock for {LOCK_LIMIT_S:g} s — this run wasn't counted there"
            state, _ = load(path)
            state, troubled, newly = apply(state, outcomes, when)
            err = browser_level.save(path, state)
            return ({}, [], err) if err else (troubled, newly, None)
    except OSError as e:
        return {}, [], f"the held tests couldn't be saved to {path}: {e}"


def release(path, name):
    """Clear the file's hold AND its streak (Ron's "try again", or its header now saying alone: yes). Returns (its hold —
    None if it wasn't held, every file held on this PC, None) — or (None, {}, why it couldn't be saved)."""
    try:
        with _held_lock(path) as got:
            if not got:
                return None, {}, f"another run held {path}'s lock for {LOCK_LIMIT_S:g} s — try again"
            state, _ = load(path)
            entry = (state.get("files") or {}).get(name)
            if not entry or not entry.get("held"):
                return None, holds(state), None
            hold = entry["held"]
            state["files"].pop(name)
            err = browser_level.save(path, state)
            return (None, {}, err) if err else (hold, holds(state), None)
    except OSError as e:
        return None, {}, f"the held tests couldn't be saved to {path}: {e}"


# --- the words -----------------------------------------------------------------------------------------------------------
def _when(text):
    return str(text or "?")[:16].replace("T", " ")


def run_line(r):
    """One run of a streak, on a line: when, where (which folder's run), why, how its rerun went, its kept outputs."""
    return (f"    {_when(r.get('when'))}" + (f" in {r['where']}" if r.get("where") else "")
            + (f" (shard {r['shard']})" if r.get("shard") else "") + f" — {r.get('why') or '?'} — "
            + (r.get("outcome") if r.get("outcome") == "not proven" else "rerun alone: passed")
            + (f" ({r['rerun']})" if r.get("outcome") == "not proven" and r.get("rerun") else "")
            + f" — first output: {r.get('first_output') or '(not kept)'}"
            + (f" — the rerun's: {r['rerun_output']}" if r.get("rerun_output") else ""))


def ways_out(name):
    return (f"Ron's ways out: py tools/run_tests.py --release-held {name}  (try again — the hold and its streak "
            "cleared) · an 'alone: yes — <why>' line in its header (it then runs only while it holds every test slot on "
            "the PC; that lifts the hold too) · a 'skip: <TODO id> — <why>' line (set aside)")


def streak_lines(name, streak):
    """The loud lines for a file met by the machine's trouble in `len(streak)` full runs in a row on this PC."""
    return ([f"! {name} met the machine's or the browser's trouble {len(streak)} full runs in a row on this PC — it may "
             f"truly need to run alone (TESTING.md §7); not proven {HOLD_AFTER} runs in a row would hold it; its runs, "
             "newest first:"] + [run_line(r) for r in reversed(streak)])


def held_lines(name, hold):
    """The loud lines for a file held by this run."""
    return ([f"! {name} couldn't be proven in {HOLD_AFTER} runs in a row on this PC — held for Ron's decision: later runs "
             "won't run it (each says 'held — not run', so none can be proven and nothing merges past it). " + ways_out(name)
             + ". Its runs, newest first:"] + [run_line(r) for r in reversed(hold.get("runs") or [])])


def not_run_reason(hold):
    """The record's `not_proven` for a held file — and its line's words."""
    return (f"held — not run: it couldn't be proven in {HOLD_AFTER} runs in a row on this PC (held since "
            f"{_when(hold.get('since'))}) — held for Ron's decision")
