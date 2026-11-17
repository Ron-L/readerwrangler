# Tests for tools/browser_level.py — how many screen-test browsers a run may use at once, chosen by the runner itself
# (Ron, 2026-11-17: "similar to how TCP works" — use more until failures, back off, occasionally try more; measure
# diminishing returns; conditions change). The decision is one pure function: what happened before + the run just done
# in → the next level, why, and what kind of move it was out.
# tags: test-runner, tier 1
# covers: tools/browser_level.py
# Run: python test/test_browser_level.py
import json
import os
import sys
import tempfile
import threading
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # print ✓ even when piped (2026-11-12; as harness.py)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    import browser_level as bl
except Exception as e:      # noqa: BLE001 — not built yet: every row fails, naming why
    bl, missing = None, f"{type(e).__name__}: {e}"

results = []


def row(tid, name, fn):
    """One check: fn() returns (passed?, detail). An error inside it is a failure, named."""
    try:
        if bl is None:
            raise RuntimeError(missing)
        ok, detail = fn()
    except Exception as e:      # noqa: BLE001
        ok, detail = False, f"{type(e).__name__}: {e}"
    results.append((tid, ok))
    print(f"  {'✓' if ok else '✗'} {tid} {name}" + ("" if ok else f" — {detail}"))


def run(level, seconds=200.0, files=26, suite="tier 2", full=True, trouble=0, end=None, when="2026-11-17T10:00:00"):
    """A run just done, as the runner reports it."""
    return {"level": level, "end": level if end is None else end, "seconds": seconds, "files": files, "suite": suite,
            "full": full, "trouble": trouble, "free_gb": 3.0, "when": when}


def past(level, outcome, nxt, **kw):
    """A run in the saved history: the run, plus what was decided after it."""
    return dict(run(level, **kw), outcome=outcome, next=nxt)


def grown_from(level, seconds=200.0, **kw):
    """History where the last run at `level` was clean and full, so the level grew to level + 1 — the next run probes."""
    return [past(level, "grew", level + 1, seconds=seconds, **kw)]


def r001():
    lv, why, how = bl.decide([], run(4))
    lv2, _, how2 = bl.decide([past(3, "backed off", 3, trouble=1, end=3)], run(3))
    return (lv, how, lv2, how2) == (5, "grew", 4, "grew") and "5" in why, (lv, why, how, lv2, how2)


row("LEVEL-001", "a full run with no machine trouble → one more next time (4 → 5; after a back-off, 3 → 4)", r001)


def r002():
    got = [bl.decide([], run(4, trouble=1, end=2))[:1], bl.decide([], run(5, trouble=1, end=2))[:1],
           bl.decide([], run(1, trouble=1, end=1))[:1], bl.decide([], run(4, trouble=2, end=1))[:1],
           bl.decide([], run(6, trouble=1))[:1]]
    lv, why, how = bl.decide([], run(4, trouble=1, end=2))
    return got == [(2,), (2,), (1,), (1,), (3,)] and how == "backed off" and "trouble" in why, (got, why, how)


row("LEVEL-002", "machine trouble → halve at once (4 → 2, 5 → 2, 6 → 3); halved twice in the run → what it ended at "
    "(4 → 1); never below 1", r002)


def r003():
    lv, why, how = bl.decide(grown_from(5, seconds=200), run(6, seconds=150))
    lv2, _, _ = bl.decide([past(6, "top", 6)], run(6))
    return (lv, lv2) == (6, 6) and how != "grew", (lv, why, how, lv2)


row("LEVEL-003", "the cap: a clean full run at 6 stays at 6 (never 7)", r003)


def r004():
    lv, why, how = bl.decide(grown_from(4, seconds=200), run(5, seconds=205))
    return lv == 4 and how == "no gain" and "3 min 25 s" in why and "3 min 20 s" in why, (lv, why, how)


row("LEVEL-004", "a try at one more that was no faster than the best recent run at the level below → back down, saying "
    "both times (5 took 3 min 25 s, 4 took 3 min 20 s → 4)", r004)


def r005():
    barely = bl.decide(grown_from(4, seconds=200), run(5, seconds=192))     # 4 % faster: within the noise
    clearly = bl.decide(grown_from(4, seconds=200), run(5, seconds=180))    # 10 % faster
    return (barely[0], barely[2], clearly[0], clearly[2]) == (4, "no gain", 6, "grew"), (barely, clearly)


row("LEVEL-005", "the noise margin: 4 % faster is no gain (back to 4); 10 % faster is a gain (on to 6)", r005)


def r006():
    hist = [past(4, "held", 4, seconds=230, when="2026-11-17T08:00:00"),
            past(4, "grew", 5, seconds=220, when="2026-11-17T09:00:00")]
    lv, why, how = bl.decide([past(4, "held", 4, seconds=190, when="2026-11-17T07:00:00")] + hist, run(5, seconds=200))
    # the BEST recent run at 4 (190 s), not the last (220 s): 200 is no gain on 190 (it would be on 220)
    trouble_base = [past(4, "backed off", 2, seconds=100, trouble=1, end=2), past(2, "grew", 3, seconds=260),
                    past(3, "grew", 4, seconds=240), past(4, "grew", 5, seconds=200)]
    lv2, _, how2 = bl.decide(trouble_base, run(5, seconds=170))
    # a run with trouble is no yardstick (its 100 s would make 170 s look slow)
    old = [past(4, "held", 4, seconds=100)] + [past(4, "held", 4, seconds=220) for _ in range(bl.RECENT)] \
        + [past(4, "grew", 5, seconds=210)]
    lv3, _, how3 = bl.decide(old, run(5, seconds=180))
    # only RECENT runs count: an old 100 s run at 4 no longer sets the bar (conditions change)
    return (lv, how, lv2, how2, lv3, how3) == (4, "no gain", 6, "grew", 6, "grew"), (lv, why, how, lv2, how2, lv3, how3)


row("LEVEL-006", "the yardstick: the BEST recent full run at the level below — never a run with trouble, never one older "
    "than the recent runs", r006)


def r007():
    hist = grown_from(4, seconds=200)
    lv, why, how = bl.decide(hist, run(5, seconds=210, when="2026-11-17T11:00:00"))
    hist.append(dict(run(5, seconds=210), outcome=how, next=lv))
    seen = []
    for i in range(bl.HOLD_RUNS):
        cur = lv
        lv, why, how = bl.decide(hist, run(cur, seconds=200))
        seen.append((lv, how, why))
        hist.append(dict(run(cur, seconds=200), outcome=how, next=lv))
    held = seen[:-1]
    ok = all(s[0] == 4 and s[1] == "held" for s in held) and (seen[-1][0], seen[-1][1]) == (5, "grew") \
        and f"{bl.HOLD_RUNS - 1} more" in held[0][2] and "1 more" in held[-1][2]
    return ok, seen


row("LEVEL-007", "after a try that gained nothing: no try again for the next few full runs (each says how many more), "
    "then it tries again — conditions change", r007)


def r008():
    hist = grown_from(4, seconds=200) + [past(5, "no gain", 4, seconds=210), past(4, "backed off", 2, trouble=1, end=2),
                                         past(2, "grew", 3, seconds=260)]
    lv, why, how = bl.decide(hist, run(3, seconds=230))     # 3 → 4: below the level that gained nothing — fine
    hist2 = hist + [past(3, "grew", 4, seconds=230)]
    lv2, why2, how2 = bl.decide(hist2, run(4, seconds=200))  # 4 → 5 is the try that gained nothing, still within the hold
    return (lv, how, lv2, how2) == (4, "grew", 4, "held"), (lv, why, how, lv2, why2, how2)


row("LEVEL-008", "climbing back after a back-off, the hold still stops at the level that gained nothing", r008)


def r009():
    state = {"level": 4, "why": "saved", "history": grown_from(3)}
    lv, why, how = bl.decide(state["history"], run(4, full=False))
    new, lv2, _, how2 = bl.record(state, run(4, full=False))
    return (lv, how, lv2, how2) == (4, "ignored", 4, "ignored") and new == state, (lv, why, how, new)


row("LEVEL-009", "a narrowed run (--id, --tag, RW_CELLS, a file set aside) moves nothing — and isn't saved", r009)


def r010():
    state = {"level": 4, "why": "saved", "history": []}
    new, lv, why, how = bl.record(state, run(4, full=False, trouble=1, end=2))
    return (lv, how, new["level"]) == (2, "backed off", 2) and new["history"][-1]["outcome"] == "backed off", (new, why)


row("LEVEL-010", "…but machine trouble in a narrowed run still backs off — and the halved level is saved", r010)


def r011():
    bigger = bl.decide(grown_from(4, seconds=200, files=26), run(5, seconds=260, files=40))
    other = bl.decide(grown_from(4, seconds=100, suite="tier 2"), run(5, seconds=300, suite="tier all"))
    near = bl.decide(grown_from(4, seconds=200, files=26), run(5, seconds=230, files=27))
    return (bigger[0], bigger[2], other[0], other[2], near[0], near[2]) == (5, "baseline", 5, "baseline", 4, "no gain") \
        and "26" in bigger[1] and "40" in bigger[1], (bigger, other, near)


row("LEVEL-011", "like with like: a suite that changed size a lot (26 files → 40), or another suite (tier 2 vs all), is "
    "not compared — it stays to measure; one file more still compares", r011)


def r012():
    d = tempfile.mkdtemp()
    p = os.path.join(d, bl.FILE_NAME)
    out = {}
    out["missing"] = bl.load(p)
    for name, text in [("garbage", "{not json"), ("too high", json.dumps({"level": 9, "history": []})),
                       ("zero", json.dumps({"level": 0, "history": []})), ("not a number", '{"level": "x"}'),
                       ("a list", "[4]"), ("history not a list", '{"level": 5, "history": 3}')]:
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        out[name] = bl.load(p)
    ok = all(s["level"] == 4 and s["history"] == [] for s, _ in out.values()) \
        and "no saved level" in out["missing"][1] and "starting at 4" in out["missing"][1] \
        and all("couldn't be read" in n and "starting at 4" in n for k, (s, n) in out.items() if k != "missing")
    return ok, out


row("LEVEL-012", "a damaged or missing saved file → start at 4, and say so (garbage, a level of 9 or 0, not a number, "
    "the wrong shape)", r012)


def r013():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "sub", bl.FILE_NAME)
    state = {"level": 5, "why": "a full run with no machine trouble", "history": grown_from(4)}
    err = bl.save(p, state)
    back, note = bl.load(p)
    left = sorted(os.listdir(os.path.dirname(p)))
    return err is None and back == state and note is None and left == [bl.FILE_NAME], (err, back, note, left)


row("LEVEL-013", "saved and read back the same; written to a temporary file then put in place (nothing left beside it)",
    r013)


def r014():
    state = {"level": 4, "why": "", "history": [past(4, "held", 4) for _ in range(bl.KEEP)]}
    before = json.dumps(state)
    r = run(4, seconds=123)
    new, lv, why, how = bl.record(state, r)
    last = new["history"][-1]
    return len(new["history"]) == bl.KEEP and last["seconds"] == 123 and last["outcome"] == how \
        and last["next"] == lv == new["level"] and new["why"] == why and json.dumps(state) == before \
        and "outcome" not in r, (len(new["history"]), last)


row("LEVEL-014", "each decision is saved with its run (outcome, next level, why); the history is bounded; the inputs "
    "are never changed (a pure function)", r014)


def r015():
    g = bl.Gate(4)
    gens = [g.enter() for _ in range(4)]
    fifth = threading.Event()

    def later():
        g.enter()
        fifth.set()
    threading.Thread(target=later, daemon=True).start()
    waited = not fifth.wait(0.3)                        # all 4 running: a 5th waits
    first = g.trouble(gens[0])                          # 4 → 2
    again = g.trouble(gens[1])                          # started before the halving: no second halving for the same burst
    g.leave()
    g.leave()                                           # 2 still running, and the waiting 5th: fewer than 2? no
    still = not fifth.wait(0.3)
    g.leave()                                           # 1 running → the 5th may start
    went = fifth.wait(2)
    g.leave()
    g.leave()
    gen = g.enter()
    one = g.trouble(gen)                                # 2 → 1
    g.leave()
    floor = g.trouble(g.enter())                        # never below 1
    g.leave()
    return (waited, first, again, still, went, one, floor, g.level, g.peak) == \
        (True, (4, 2), None, True, True, (2, 1), None, 1, 4), (waited, first, again, still, went, one, floor, g.level)


row("LEVEL-015", "in a run: new screen tests start only while fewer than the level are running; trouble halves it at "
    "once (files already running go on); one halving per burst; never below 1", r015)


def r016():
    state = {"level": 4, "why": "5 at once was no faster than 4 — back to 4",
             "history": [past(4, "grew", 5, seconds=204), past(5, "no gain", 4, seconds=220),
                         past(4, "held", 4, seconds=201, full=False), past(4, "held", 4, seconds=199)]}
    words = bl.describe(state, None)
    fresh = bl.describe({"level": 4, "why": "", "history": []}, "no saved level yet — starting at 4")
    return words.startswith("4 (saved") and "no faster" in words and "4 → 3 min 24 s" in words \
        and "5 → 3 min 40 s" in words and "3 min 21 s" not in words and fresh.startswith("4 (no saved level yet"), \
        (words, fresh)


row("LEVEL-016", "the run's line says the level, where it came from and why, and the last full runs' levels and times",
    r016)

failed = [r for r in results if not r[1]]
print(f"{len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
