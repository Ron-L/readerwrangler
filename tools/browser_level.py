"""
browser_level.py — how many screen-test browsers a run may use at once, chosen by the runner itself (Ron, 2026-11-17:
"similar to how TCP works" — use more until failures, back off, occasionally try more; measure diminishing returns;
conditions change). Replaces the fixed low-memory rule (under 4 GB free → 2 browsers…) of the day before.

The LEVEL (1 to TOP = 6) is saved per PC, in a small file beside the test slots (%TEMP%\\rw-test-slots\\
browsers-at-once.json — FILE_NAME): the level, why, and a short history of runs. Every run can move it:

  - Back off hard: the machine's or the browser's trouble (a screen test's exit 3, tools/environment_trouble.py) halves
    the level AT ONCE for the rest of the run (Gate, below — files already running go on, new ones start only while
    fewer than the level are running); the halved level is saved. Never below 1.
  - Grow gently: after a FULL screen-test run (not narrowed by --id, --tag, RW_CELLS or a file set aside) with no such
    trouble, the next run may use one more, up to TOP —
  - — unless it gained nothing: a run at one more is compared with the BEST recent full run at the level below (the same
    suite, about the same number of files, no trouble); not faster by more than NOISE (5 %) → back to the level below,
    and no try at the higher one for the next HOLD_RUNS full runs. Then it tries again: conditions change.
  - Only fully passing runs count (Ron, 2026-11-17 — Karn's algorithm: an ambiguous sample is dropped, not risked): a
    full run with a failed file (or one that couldn't run) is saved, marked `failed`, but moves nothing — it is no
    reason to grow, never a yardstick (no "best recent time", no "no faster" judgment, no "twice as slow" bar), and no
    full run toward the wait after a try that gained nothing. A try at one more whose run failed is judged by the next
    clean run at that level. Machine trouble still backs off, failed or not.
  - Sustained slowness steps down by one (Ron, 2026-11-17): a clean full run at L that took more than SLOW (twice) the
    best recent clean full run at the same L (the same suite, about the same size) → the next run at L−1 — not halved,
    never below 1 — and it says why. No wait afterwards: the next clean run at normal speed may grow again.
  - A narrowed run without trouble moves nothing and isn't saved. A forced number (--jobs, RW_TEST_SLOTS) never reaches
    here: the runner leaves the saved level alone. The file lives in RW_TEST_SLOTS_DIR instead, when that's set
    (tools/test_slots.py — a folder of its own without moving TEMP).

The level governs HEAVY tier-1 files too (Ron, 2026-11-17: "Yes. Also back off"): a tier-1 file whose header says
`heavy: yes` holds a test slot within the same level while it runs, and its machine trouble halves the level like a
browser's. A run with no screen tests is no measure of browsers: only its trouble moves the level (never up).

decide() is the rule — a pure function (history + the run just done → the next level, why, and what kind of move);
record() applies it to the saved state; load() / save() read and write the file (a missing or damaged file → START, 4,
said so); describe() is the run's line; Gate is the level inside one run. Two runs at once each save their own result —
the last one written wins (the slots, not this file, keep the PC within its limit).

Tested by test/test_browser_level.py (LEVEL-001–021) and test/test_run_tests.py (RUN-083–086).
"""
import json
import os
import threading

START = 4           # a PC with no saved level (or a damaged file) starts here — the old fixed number
TOP = 6             # the most browsers at once — the PC's slot count (tools/test_slots.py) matches it
NOISE = 0.05        # one more at once must be faster by more than this share of the time, or it gained nothing
HOLD_RUNS = 5       # after a try that gained nothing: this many full runs before trying again
RECENT = 10         # the yardstick is the best of the last this-many saved runs (older ones: conditions changed)
KEEP = 30           # saved runs kept
SAME_SIZE = 0.10    # suites within this share of each other's file count compare; further apart they don't
SLOW = 2.0          # a clean run at L taking more than this many times the best recent one at L → one fewer next run
FILE_NAME = "browsers-at-once.json"


def minsec(seconds):
    """'3 min 24 s' (or '48 s')."""
    s = int(round(seconds or 0))
    return f"{s // 60} min {s % 60} s" if s >= 60 else f"{s} s"


def _clean(h):
    """A run that can be a yardstick: full, no trouble, every file passed, a time."""
    return bool(h.get("full") and not h.get("trouble") and not h.get("failed")
                and isinstance(h.get("seconds"), (int, float)))


def _best(history, level, run):
    """The best (shortest) time of the recent clean runs at `level` comparable with `run` — None if there's none."""
    times = [h["seconds"] for h in history[-RECENT:] if _clean(h) and h.get("level") == level and _comparable(h, run)]
    return min(times) if times else None


def _comparable(a, b):
    """The same suite (tier 2, or every tier) and about the same number of screen-test files."""
    fa, fb = a.get("files") or 0, b.get("files") or 0
    return a.get("suite") == b.get("suite") and abs(fa - fb) <= max(1, round(SAME_SIZE * max(fa, fb)))


def decide(history, run):
    """The next level — (level, why in words, outcome) — from the saved history (oldest first; each run with the
    `outcome` and `next` decided after it) and the run just done: {level it started at, end (the level it ended at — lower
    if it was halved), seconds, files, suite, full, trouble (how many times), failed (how many files failed or couldn't
    run), free_gb, when}. Outcomes: 'backed off', 'failed', 'slow', 'grew', 'no gain', 'held', 'top', 'baseline',
    'ignored' (a narrowed run with no trouble — not saved). Pure: changes neither argument."""
    level = max(1, min(TOP, int(run.get("level") or START)))
    if run.get("trouble"):
        n = max(1, min(int(run.get("end") or level), level // 2))
        return n, (f"the machine's or the browser's trouble in the last run at {level} at once — backed off to {n}"), \
            "backed off"
    if not run.get("full"):
        return level, "a narrowed run (only full runs move the level)", "ignored"
    if run.get("failed"):       # an ambiguous sample: dropped, not risked (Karn's algorithm)
        n = int(run["failed"])
        return level, (f"{n} file{'s' if n > 1 else ''} failed in the last run at {level} at once — only a run where "
                       f"every file passed moves the level or is compared — staying at {level}"), "failed"
    same = _best(history, level, run)
    if same is not None and run["seconds"] > SLOW * same:
        n = max(1, level - 1)
        return n, (f"{level} at once took {minsec(run['seconds'])} — more than twice the best recent run at {level} "
                   f"({minsec(same)}) — " + (f"one fewer: {n}" if n < level else f"staying at {n}, the fewest")), "slow"
    prev = next((h for h in reversed(history) if h.get("outcome") != "failed"), None)   # a dropped run is skipped over
    probe = bool(prev) and prev.get("outcome") == "grew" and prev.get("next") == level and level > 1
    if probe:
        below = level - 1
        at_below = [h for h in history[-RECENT:] if _clean(h) and h.get("level") == below]
        best = _best(history, below, run)
        if best is not None:
            if run["seconds"] > best * (1 - NOISE):
                return below, (f"{level} at once took {minsec(run['seconds'])} — no faster than {below} at once "
                               f"({minsec(best)}, the best recent run) — back to {below}, and no try at {level} for the "
                               f"next {HOLD_RUNS} full runs"), "no gain"
        else:
            seen = ", ".join(sorted({f"{h.get('suite')}, {h.get('files')} files" for h in at_below}))
            return level, (f"nothing to compare {level} at once with — "
                           + (f"the recent runs at {below} ran another suite ({seen}; this run: {run.get('suite')}, "
                              f"{run.get('files')} files)" if at_below else f"no recent full run at {below}")
                           + f" — staying at {level} to measure it"), "baseline"
    if level >= TOP:
        return TOP, f"{TOP} at once is the most", "top"
    gave_up = next((i for i in range(len(history) - 1, -1, -1) if history[i].get("outcome") == "no gain"), None)
    if gave_up is not None and level + 1 >= int(history[gave_up].get("level") or TOP + 1):
        since = sum(1 for h in history[gave_up + 1:] if h.get("full") and not h.get("failed")) + 1
        if since < HOLD_RUNS:
            tried = history[gave_up]
            return level, (f"{tried.get('level')} at once gained nothing ({str(tried.get('when', ''))[:10]}) — staying at "
                           f"{level} for {HOLD_RUNS - since} more full run{'s' if HOLD_RUNS - since > 1 else ''}, "
                           "then trying again"), "held"
    return level + 1, (f"a full run with no machine trouble at {level} at once — trying {level + 1}"
                       + (" (it was faster)" if probe else "")), "grew"


def record(state, run):
    """(new state, level, why, outcome) — decide() applied to the saved state. A narrowed run with no trouble changes
    nothing (the same state back). Pure: changes neither argument."""
    level, why, outcome = decide(state.get("history") or [], run)
    if outcome == "ignored":
        return state, level, why, outcome
    history = (list(state.get("history") or []) + [dict(run, outcome=outcome, next=level)])[-KEEP:]
    return {"level": level, "why": why, "history": history}, level, why, outcome


def fresh():
    return {"level": START, "why": "", "history": []}


def load(path):
    """(state, note) — the saved level and history; note None when read. A missing file or a damaged one (not JSON, the
    wrong shape, a level outside 1–TOP) → a fresh state at START, and the note says so."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        return fresh(), f"no saved level yet — starting at {START}"
    except OSError as e:
        return fresh(), f"the saved level couldn't be read ({e}) — starting at {START}"
    try:
        s = json.loads(text)
        ok = isinstance(s, dict) and type(s.get("level")) is int and 1 <= s["level"] <= TOP \
            and isinstance(s.get("history", []), list) and all(isinstance(h, dict) for h in s.get("history", []))
    except ValueError:
        ok = False
    if not ok:
        return fresh(), f"the saved level couldn't be read (damaged: {path}) — starting at {START}"
    return {"level": s["level"], "why": str(s.get("why") or ""), "history": s.get("history", [])}, None


def save(path, state):
    """Write the state: a temporary file beside it, then put in place (a reader never sees half a file). None, or why it
    couldn't be saved, in words."""
    tmp = f"{path}.{os.getpid()}.{threading.get_ident()}.tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=1)
        os.replace(tmp, path)
        return None
    except OSError as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return f"the level couldn't be saved to {path}: {e}"


def describe(state, note):
    """The words after 'browsers at once: ' — the level, where it came from and why, the last full runs."""
    full = [h for h in state.get("history") or [] if h.get("full") and isinstance(h.get("seconds"), (int, float))][-3:]
    runs = ", ".join(f"{h.get('level')} → {minsec(h['seconds'])}" + (" (trouble)" if h.get("trouble") else "")
                     + (" (failed)" if h.get("failed") else "") for h in full)
    where = note or ("saved" + (f" — {state['why']}" if state.get("why") else ""))
    return f"{state['level']} ({where}" + (f"; last {len(full)} full run{'s' if len(full) > 1 else ''}: {runs}"
                                          if full else "") + ")"


class Gate:
    """The level inside one run: a screen test starts only while fewer than `level` are running (enter waits);
    trouble() halves it at once — the files already running go on. One halving per burst: trouble from a file that
    started before the last halving doesn't halve again (the halving already answered it). Never below 1."""

    def __init__(self, level):
        self.level, self.running, self.peak, self.gen = max(1, level), 0, 0, 0
        self.changes = []           # (from, to) — each halving, in order
        self._cond = threading.Condition()

    def enter(self):
        """Wait for room, take it; returns the generation it started in (for trouble())."""
        with self._cond:
            while self.running >= self.level:
                self._cond.wait()
            self.running += 1
            self.peak = max(self.peak, self.running)
            return self.gen

    def try_enter(self):
        """Take room if there is some, without waiting: the generation it started in — or None, the run already has its
        level running (tools/run_tests.py takes the next unit that may start, never sitting on one that can't)."""
        with self._cond:
            if self.running >= self.level:
                return None
            self.running += 1
            self.peak = max(self.peak, self.running)
            return self.gen

    def leave(self):
        with self._cond:
            self.running -= 1
            self._cond.notify_all()

    def trouble(self, gen):
        """A file that started in generation `gen` met the machine's trouble: (old level, new level) if it halved now,
        else None (it already halved for this burst, or it's at 1)."""
        with self._cond:
            if gen != self.gen or self.level <= 1:
                return None
            old, self.level = self.level, max(1, self.level // 2)
            self.gen += 1
            self.changes.append((old, self.level))
            return old, self.level
