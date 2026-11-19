# Tests for tools/test_costs.py — what each test unit costs this PC, measured for its whole process tree (a Windows job
# object), and a running average per PC (TCP's RFC 6298 method); and the runner's part: measures beside each file's and
# shard's seconds in the run's record, only full passing units teaching the average, `--costs` (TODO 20260922-0000c,
# item 12 step 1 — Ron, 2026-11-18: "Measure 1st").
# tags: test-runner, tier 1
# covers: tools/test_costs.py, tools/run_tests.py, tools/test_slots.py, tools/browser_level.py
# Run: python test/test_test_costs.py
import atexit
import contextlib
import glob
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # print ✓ even when piped (as harness.py)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
# Every run of the runner started here uses slot files, a saved level and test costs of its OWN — never the PC's real
# ones (2026-11-18: a self-test's sample files taught the real averages). Read by test_slots.slots_folder() at each
# call, and inherited by any process started from here.
os.environ["RW_TEST_SLOTS_DIR"] = tempfile.mkdtemp(prefix="rw-selftest-slots-")
atexit.register(shutil.rmtree, os.environ["RW_TEST_SLOTS_DIR"], True)     # gone when this file ends (ignore_errors)
try:
    import test_costs as tc
    missing = None
except Exception as e:      # noqa: BLE001 — not built yet: every row fails, naming why
    tc, missing = None, f"{type(e).__name__}: {e}"
spec = importlib.util.spec_from_file_location("run_tests", os.path.join(TOOLS, "run_tests.py"))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)
import test_slots   # noqa: E402 — the same module the runner uses (tools/ is on the path)

MB = 2 ** 20
results = []


def row(tid, name, fn):
    """One check: fn() returns (passed?, detail). An error inside it is a failure, named."""
    try:
        if tc is None:
            raise RuntimeError(missing)
        ok, detail = fn()
    except Exception as e:      # noqa: BLE001
        ok, detail = False, f"{type(e).__name__}: {e}"
    results.append((tid, ok))
    print(f"  {'✓' if ok else '✗'} {tid} {name}" + ("" if ok else f" — {detail}"))


def quiet_main(argv, **kw):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = rt.main(argv, **kw)
    except SystemExit as e:
        code = f"SystemExit {e.code}"
    except TypeError as e:      # main() without the new parameters yet
        code = f"TypeError {e}"
    return code, buf.getvalue()


def records_in(folder):
    out = []
    for p in sorted(glob.glob(os.path.join(folder, "*.json"))):
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def units_in(path):
    """{(file name, unit): its saved entry} from a costs file ({} if none)."""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    return {(os.path.basename(name), key): u for name, e in s.get("files", {}).items() for key, u in e["units"].items()}


def r001():
    a = tc.smooth(None, 8.0)
    b = tc.smooth(a, 16.0)          # spread: 4 + (|16 − 8| − 4)/4 = 5 (the OLD average); average: 8 + (16 − 8)/8 = 9
    c = tc.smooth(b, 9.0)           # spread: 5 + (0 − 5)/4 = 3.75; average stays 9
    got = [(s["avg"], s["spread"], s["count"], s["last"]) for s in (a, b, c)]
    return got == [(8.0, 4.0, 1, 8.0), (9.0, 5.0, 2, 16.0), (9.0, 3.75, 3, 9.0)], got


row("COST-001", "the running average and spread are TCP's (RFC 6298): the first sample → average = it, spread = half; "
    "then the spread moves ¼ of the way to |sample − the old average|, the average ⅛ of the way to the sample", r001)


def r002():
    got = [tc.left_out([], True, False), tc.left_out(["--id SAMP-001"], True, False), tc.left_out([], False, False),
           tc.left_out([], True, True), tc.left_out(["RW_CELLS=CELL-005"], False, True)]
    ok = got[0] is None and "--id SAMP-001" in got[1] and "failed" in got[2] and "rerun" in got[3] \
        and "RW_CELLS" in got[4]
    return ok, got


row("COST-002", "only a unit that ran in full and passed, the first time, may teach the average — a narrowed run, a "
    "failed unit and a rerun alone are left out, each saying why", r002)


def r003():
    s1 = {"file": "t/x.py", "tier": 1, "hash": "aaa", "unit": "whole", "seconds": 10.0,
          "measures": {"cpu_seconds": 2.0, "committed_peak_bytes": None}}
    st = tc.learn(tc.learn(tc.fresh(), [s1], "d1"), [dict(s1, seconds=18.0)], "d2")
    kept = st["files"]["t/x.py"]["units"]["whole"]
    st2 = tc.learn(st, [dict(s1, hash="bbb", seconds=4.0)], "d3")      # the file changed: its history starts over
    again = st2["files"]["t/x.py"]["units"]["whole"]
    ok = kept["count"] == 2 and kept["measures"]["seconds"]["avg"] == 11.0 and kept["when"] == "d2" \
        and "committed_peak_bytes" not in kept["measures"] and kept["measures"]["cpu_seconds"]["count"] == 2 \
        and again["count"] == 1 and again["measures"]["seconds"] == {"avg": 4.0, "spread": 2.0, "count": 1, "last": 4.0} \
        and st2["files"]["t/x.py"]["hash"] == "bbb"
    return ok, (kept, again)


row("COST-003", "a unit's saved history: each sample moves the average (a measure that is None is skipped), with the "
    "count and the date; a test file whose contents changed (another hash) starts its history over", r003)


def r004():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "test-costs.json")
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import test_costs as tc\n"
                "for i in range(10):\n"
                "    err = tc.teach(sys.argv[2], [{'file': 'shared.py', 'tier': 1, 'hash': 'h', 'unit': 'whole',\n"
                "        'seconds': 1.0, 'measures': {}}, {'file': 'p' + sys.argv[3] + '.py', 'tier': 1, 'hash': 'h',\n"
                "        'unit': 'whole', 'seconds': 2.0, 'measures': {}}])\n"
                "    assert err is None, err\n")
        procs = [subprocess.Popen([sys.executable, "-c", code, TOOLS, path, str(n)], stderr=subprocess.PIPE)
                 for n in range(6)]
        errs = [p.communicate(timeout=120)[1].decode("utf-8", "replace") for p in procs]
        got = units_in(path)
        counts = {k[0]: u["count"] for k, u in got.items()}
        want = dict({"shared.py": 60}, **{f"p{n}.py": 10 for n in range(6)})
        return counts == want and not any(p.returncode for p in procs), (counts, [e[-300:] for e in errs if e])


row("COST-004", "six runs saving at the same time (10 saves each, one shared unit) lose nothing: every save is read, "
    "merged and written under the slots' file lock", r004)


def r005():
    real = tc.available
    try:
        tc.available = lambda: (False, "a stand-in reason")
        code, out, err, m = tc.run([sys.executable, "-c", "print('hello')"])
    finally:
        tc.available = real
    real_job = getattr(tc, "_Job", None)
    try:
        def broken():
            raise OSError("making a job object failed (a stand-in)")
        tc._Job = broken
        code2, out2, _, m2 = tc.run([sys.executable, "-c", "print('again')"])
    finally:
        tc._Job = real_job
    values = [m[k] for k in tc.MEASURES[1:]] + [m2[k] for k in tc.MEASURES[1:]]
    ok = (code, out.strip(), code2, out2.strip()) == (0, b"hello", 0, b"again") and all(v is None for v in values) \
        and m["missing"] == "a stand-in reason" and "stand-in" in m2["missing"]
    return ok, (code, out, m, code2, out2, m2)


row("COST-005", "can't measure (not Windows, or making the job fails): the test runs exactly as before, every measure "
    "is None, and why is given", r005)

CHILD = r'''
import os, subprocess, sys, time
held = b"x" * (200 * 2 ** 20)           # 200 MB — committed AND touched (in RAM)
burn = "import time\nt = time.process_time()\nwhile time.process_time() - t < 1.0:\n    pass\n"
g = subprocess.Popen([sys.executable, "-c", burn])      # a grandchild: ~1 s of CPU, then it exits —
g.wait()                                                  # — before the child does
with open(sys.argv[1], "wb") as f:
    f.write(held[:20 * 2 ** 20])                          # 20 MB written
time.sleep(1.5)
print("child done", g.pid)
'''


def r006():
    with tempfile.TemporaryDirectory() as d:
        script, target = os.path.join(d, "child.py"), os.path.join(d, "written.bin")
        with open(script, "w", encoding="utf-8") as f:
            f.write(CHILD)
        code, out, err, m = tc.run([sys.executable, script, target], timeout=120)
    if os.name != "nt":
        return m["cpu_seconds"] is None and m["missing"], m
    ok = code == 0 and m["cpu_seconds"] >= 1.0 and m["committed_peak_bytes"] >= 200 * MB \
        and m.get("ram_kind") == "private" and (m["ram_peak_sampled_bytes"] or 0) >= 200 * MB \
        and (m.get("ram_with_shared_peak_sampled_bytes") or 0) >= m["ram_peak_sampled_bytes"] \
        and m["io_written_bytes"] >= 20 * MB and m["processes"] >= 2
    return ok, dict(m, code=code, err=err.decode("utf-8", "replace")[-300:])


row("COST-006", "measured for the WHOLE tree: a child holding 200 MB whose grandchild burns 1 s of CPU and exits first — "
    "the CPU counts the grandchild (≥ 1 s), committed peak ≥ 200 MB, RAM, private (sampled) ≥ the 200 MB it touched "
    "(the shared-included sum at least that), 20 MB written, ≥ 2 processes", r006)


def r014():
    """The RAM measure is the PRIVATE working set when Windows gives it — else every process's whole working set, and
    the record says which (ram_kind). The API is stubbed: each process reports 100 MB in all, 30 MB of it private."""
    real = tc._process_memory
    child = [sys.executable, "-c", "import time; time.sleep(1.6)"]
    try:
        tc._process_memory = lambda pid: (100 * MB, 30 * MB)
        _, _, _, priv = tc.run(child)
        tc._process_memory = lambda pid: (100 * MB, None)       # this Windows has no private working set
        _, _, _, shared = tc.run(child)
    finally:
        tc._process_memory = real
    n = priv["ram_with_shared_peak_sampled_bytes"] // (100 * MB) if priv.get("ram_with_shared_peak_sampled_bytes") else 0
    ok = n >= 1 and priv["ram_kind"] == "private" and priv["ram_peak_sampled_bytes"] == n * 30 * MB \
        and shared["ram_kind"] == "shared included" and shared["ram_peak_sampled_bytes"] == n * 100 * MB \
        and shared["ram_with_shared_peak_sampled_bytes"] == n * 100 * MB and "private" in (shared.get("ram_note") or "")
    # the averages hold one kind: a sample of the other kind starts the RAM measure over (time keeps its history)
    s = {"file": "t/y.py", "tier": 2, "hash": "h", "unit": "whole", "seconds": 10.0,
         "measures": {"ram_peak_sampled_bytes": 300 * MB, "ram_kind": "private"}}
    st = tc.learn(tc.learn(tc.fresh(), [s], "d1"), [s], "d2")
    s2 = dict(s, measures={"ram_peak_sampled_bytes": 900 * MB, "ram_kind": "shared included"})
    u = tc.learn(st, [s2], "d3")["files"]["t/y.py"]["units"]["whole"]
    ok = ok and u["ram_kind"] == "shared included" and u["measures"]["ram_peak_sampled_bytes"]["count"] == 1 \
        and u["measures"]["ram_peak_sampled_bytes"]["avg"] == 900 * MB and u["measures"]["seconds"]["count"] == 3
    return ok, (priv, shared, u)


row("COST-014", "RAM is each process's PRIVATE working set, added up (what the test adds to the PC's RAM) — where Windows "
    "can't give it, the whole working set instead, and the record says which kind was measured; an average never mixes "
    "the two kinds", r014)


def r007():
    code, out, err, m = tc.run([sys.executable, "-c", "import time, sys\nprint('started', flush=True)\ntime.sleep(30)"],
                               timeout=2)
    return code is None and b"started" in out, (code, out, err, m)


row("COST-007", "a unit that runs past its time is stopped as before (exit None, what it printed kept), measured or not",
    r007)

# --- the runner's part --------------------------------------------------------------------------------------------------
with tempfile.TemporaryDirectory() as d:
    def write(name, text):
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    ok_py = write("test_cost_ok.py", "# tags: costs, tier 1\n# covers: nothing.js\n"
                  "def check(tid, ok): print(('  ✓ ' if ok else '  ✗ ') + tid)\n"
                  "check(\"SAMP-001\", True)\nprint('1 passed, 0 failed')\n")
    bad_py = write("test_cost_bad.py", "# tags: costs, tier 1\n# covers: nothing.js\n"
                   "print('  ✗ SAMP-002 broken')\nprint('0 passed, 1 failed')\nimport sys; sys.exit(1)\n")
    shard_py = write("test_cost_shards.py", "# tags: costs, tier 1\n# covers: nothing.js\n# shards: 2\n"
                     "import os, sys\nif '--list-cells' in sys.argv:\n    print('SHD-001\\nSHD-002')\n    sys.exit(0)\n"
                     "cells = os.environ.get('RW_CELLS', '').split(',')\nprint(f'{len(cells)} passed, 0 failed')\n")
    flag = os.path.join(d, "trouble-once")
    heavy_py = write("test_cost_heavy.py", "# tags: costs, tier 1\n# covers: nothing.js\n# heavy: yes — a stand-in\n"
                     f"import os, sys\nflag = {flag!r}\n"
                     "if not os.path.exists(flag):\n    open(flag, 'w').close()\n"
                     "    print('ENVIRONMENT FAILURE: a stand-in trouble')\n    sys.exit(3)\n"
                     "print('1 passed, 0 failed')\n")
    slots_dir = os.path.join(d, "slots")
    costs = os.path.join(slots_dir, "test-costs.json")

    class Inside(rt.TestFile):
        """A sample file that stands for one INSIDE the repository (test/samples/<name>) — only those teach the averages
        (COST-015); the sample itself lives in a throwaway folder."""

        def rel(self, base=None):
            return "test/samples/" + os.path.basename(self.path)

    def files():
        return [Inside(p) for p in (ok_py, bad_py, shard_py)]

    def r008():
        rdir = os.path.join(d, "rec8")
        code, out = quiet_main(["--tier", "1"], files=files(), results=rdir, costs=costs,
                               slots=test_slots.Slots(count=2, folder=slots_dir))
        rec = (records_in(rdir) or [{}])[0]
        by = {os.path.basename(f["file"]): f for f in rec.get("files", [])}
        keys = set(tc.MEASURES[1:]) | {"processes"}
        ok_m = (by.get("test_cost_ok.py") or {}).get("measures") or {}
        sh = by.get("test_cost_shards.py") or {}
        shard_m = [s.get("measures") or {} for s in sh.get("shards") or []]
        good = code == 1 and keys <= set(ok_m) and len(shard_m) == 2 and all(keys <= set(m) for m in shard_m) \
            and keys <= set(sh.get("measures") or {}) and keys <= set((by.get("test_cost_bad.py") or {}).get("measures") or {})
        if os.name == "nt":
            good = good and ok_m["cpu_seconds"] > 0 and ok_m["processes"] >= 1 and ok_m["committed_peak_bytes"] > MB \
                and all(m["processes"] >= 1 for m in shard_m) \
                and sh["measures"]["cpu_seconds"] == round(sum(m["cpu_seconds"] for m in shard_m), 2)
        return good, (code, ok_m, sh, out[-600:])

    row("COST-008", "a run's record holds the measures beside each file's seconds — and each shard's (a sharded file: CPU "
        "and I/O added up over its shards, the peaks its largest shard's)", r008)

    def r009():
        got = units_in(costs)       # from COST-008's run: a full --tier 1 run
        names = sorted(got)
        want = [("test_cost_ok.py", "whole"), ("test_cost_shards.py", "shard 1 of 2"),
                ("test_cost_shards.py", "shard 2 of 2")]
        return names == want and all(u["count"] == 1 for u in got.values()), names

    row("COST-009", "a full run teaches this PC's averages: each passing unit (a whole file, each shard by itself) — a "
        "failed file doesn't", r009)

    def r010():
        before = units_in(costs)
        code, out = quiet_main(["--tier", "1", "--id", "SAMP-001"], files=files(), results=os.path.join(d, "rec10"),
                               costs=costs, slots=test_slots.Slots(count=2, folder=slots_dir))
        os.environ["RW_CELLS"] = "SHD-001"
        try:
            code2, out2 = quiet_main(["--tier", "1"], files=files(), results=os.path.join(d, "rec10b"), costs=costs,
                                     slots=test_slots.Slots(count=2, folder=slots_dir))
        finally:
            del os.environ["RW_CELLS"]
        # (a narrowed run's record is on the quick shelf since 2026-11-18 — tools/run_tests.py QUICK_SHELF)
        rec = (records_in(os.path.join(d, "rec10", "quick")) or [{}])[0]
        after = units_in(costs)
        return after == before and code == 0 and "--id" in json.dumps(rec.get("costs")), \
            (code, code2, rec.get("costs"), out[-400:])

    row("COST-010", "a run narrowed by --id, or by RW_CELLS, teaches nothing — its record says why", r010)

    def r011():
        rdir = os.path.join(d, "rec11")
        code, out = quiet_main(["--tier", "1"], files=[Inside(heavy_py)], results=rdir, costs=costs, retry_wait=0,
                               slots=test_slots.Slots(count=2, folder=slots_dir))
        rec = (records_in(rdir) or [{}])[0]
        f = (rec.get("files") or [{}])[0]
        tried = (f.get("retried") or [{}])[0]
        taught = ("test_cost_heavy.py", "whole") in units_in(costs)
        return code == 0 and f.get("result") == "passed" and not taught and "first_measures" in tried \
            and "rerun" in json.dumps(rec.get("costs")), (code, f, rec.get("costs"), out[-500:])

    row("COST-011", "a file rerun alone after the machine's trouble passes — but teaches nothing; its record keeps both "
        "runs' measures", r011)

    def r012():
        real = tc.available
        tc.available = lambda: (False, "a stand-in reason")
        try:
            rdir = os.path.join(d, "rec12")
            code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(ok_py)], results=rdir,
                                   costs=os.path.join(d, "c12.json"), slots=test_slots.Slots(count=2, folder=slots_dir))
        finally:
            tc.available = real
        rec = (records_in(rdir) or [{}])[0]
        m = (rec.get("files") or [{}])[0].get("measures") or {}
        said = [ln for ln in out.splitlines() if "a stand-in reason" in ln]
        return code == 0 and m.get("cpu_seconds", 0) is None and len(said) == 1 and said[0].startswith("·"), \
            (code, m, said, out[-400:])

    row("COST-012", "a run that can't measure passes as before: its measures are None, and it says why once, quietly",
        r012)

    def r013():
        state = {"version": 1, "files": {
            "test/ui/test_big.py": {"hash": "a", "tier": 2, "units": {"whole": {"count": 3, "when": "d", "measures": {
                "seconds": {"avg": 40.0, "spread": 4.0, "count": 3, "last": 41.0},
                "ram_peak_sampled_bytes": {"avg": 600 * MB, "spread": 50 * MB, "count": 3, "last": 600 * MB},
                "committed_peak_bytes": {"avg": 900 * MB, "spread": 60 * MB, "count": 3, "last": 900 * MB},
                "cpu_seconds": {"avg": 30.0, "spread": 2.0, "count": 3, "last": 30.0}}}}},
            "test/ui/test_small.py": {"hash": "b", "tier": 2, "units": {"whole": {"count": 2, "when": "d", "measures": {
                "seconds": {"avg": 60.0, "spread": 5.0, "count": 2, "last": 60.0},
                "ram_peak_sampled_bytes": {"avg": 200 * MB, "spread": 10 * MB, "count": 2, "last": 200 * MB}}}}},
            "test/fast.test.js": {"hash": "c", "tier": 1, "units": {"whole": {"count": 5, "when": "d", "measures": {
                "seconds": {"avg": 1.0, "spread": 0.2, "count": 5, "last": 1.0},
                "ram_peak_sampled_bytes": {"avg": 50 * MB, "spread": 1 * MB, "count": 5, "last": 50 * MB}}}}},
            # measured on a Windows without the private figure: starred, and never compared with the private ones
            "test/ui/test_old.py": {"hash": "e", "tier": 2, "units": {"whole": {"count": 1, "when": "d",
                                                                              "ram_kind": "shared included", "measures": {
                "seconds": {"avg": 0.5, "spread": 0.25, "count": 1, "last": 0.5},
                "ram_peak_sampled_bytes": {"avg": 900 * MB, "spread": 450 * MB, "count": 1, "last": 900 * MB}}}}}}}
        path = os.path.join(d, "c13.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f)
        code, out = quiet_main(["--costs"], costs=path)
        lines = out.splitlines()
        order = [i for n in ("test_small.py", "test_big.py", "fast.test.js") for i, ln in enumerate(lines) if n in ln
                 and "differ" not in ln]
        heads = all(h in out for h in ("Test", "Runs", "Time", "Memory committed (peak)", "RAM, private (sampled peak)",
                                       "CPU", "I/O read", "I/O written"))
        ratio = [ln for ln in lines if "differ in RAM by 3.0×" in ln]
        old = [ln for ln in lines if "test_old.py" in ln and "differ" not in ln]
        return code == 0 and heads and order == sorted(order) and len(order) == 3 and "60.0 ± 5.0 s" in out \
            and "600 ± 50 MB" in out and "1.0 ± 0.2 s" in out \
            and any(ln.strip().startswith("Total") and "101.5 s" in ln for ln in lines) \
            and len(ratio) == 1 and "test_big.py" in ratio[0] and "test_small.py" in ratio[0] \
            and "at least twice" in ratio[0] and "private" in ratio[0] \
            and len(old) == 1 and "900 ± 450 MB *" in old[0] and any(ln.strip().startswith("* shared pages included")
                                                                  for ln in lines), out

    row("COST-013", "--costs prints each unit — runs, average ± spread of time, committed, RAM, private (sampled), CPU, "
        "I/O — slowest first, the totals, and how many times the biggest screen test's private RAM is the smallest's (a "
        "unit measured with shared pages included is starred and left out of that comparison)", r013)

    def r015():
        """2026-11-18: the runner's own self-tests (nested runs on throwaway files) taught the PC's REAL averages, under
        names like ../../AppData/Local/Temp/tmp…/a.test.js. A file outside the repository never teaches."""
        c15 = os.path.join(d, "c15.json")
        rdir = os.path.join(d, "rec15")
        code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(ok_py)], results=rdir, costs=c15,
                               slots=test_slots.Slots(count=2, folder=slots_dir))
        rec = (records_in(rdir) or [{}])[0]
        left = (rec.get("costs") or {}).get("left_out") or {}
        pure = [tc.left_out([], True, False, outside=True), tc.left_out([], True, False, outside=False),
                tc.outside("../../AppData/Local/Temp/tmpx/a.test.js"), tc.outside("C:/Temp/a.test.js"),
                tc.outside("test/ui/test_reset.py"), tc.outside("..hidden/x.py")]
        return code == 0 and units_in(c15) == {} and list(left.values()) == ["outside the repository"] \
            and pure == ["outside the repository", None, True, True, False, False], (code, left, pure, out[-300:])

    row("COST-015", "a unit whose file is outside the repository being tested (a self-test's throwaway sample) never "
        "teaches the averages — its record says 'outside the repository'", r015)

    def r016():
        path = os.path.join(d, "c16.json")
        stale = {"hash": "x", "tier": 1, "units": {"whole": {"count": 1, "when": "d", "measures": {
            "seconds": {"avg": 1.0, "spread": 0.5, "count": 1, "last": 1.0}}}}}
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "files": {"../../AppData/Local/Temp/tmph6gy9l87/a.test.js": stale,
                                               "../../../AppData/Local/Temp/tmpo0ukmz_f/a.test.js": stale,
                                               "test/kept.test.js": stale}}, f)
        err = tc.teach(path, [{"file": "test/new.test.js", "tier": 1, "hash": "n", "unit": "whole", "seconds": 2.0,
                               "measures": {}},
                              {"file": "../outside/a.test.js", "tier": 1, "hash": "o", "unit": "whole", "seconds": 2.0,
                               "measures": {}}])
        with open(path, encoding="utf-8") as f:
            names = sorted(json.load(f)["files"])
        return err is None and names == ["test/kept.test.js", "test/new.test.js"], (err, names)

    row("COST-016", "the next save drops every saved entry named outside the repository (the six a self-test left in the "
        "real file clean themselves up) — and never adds one", r016)

    # --- Step 4 (Ron, 2026-11-18): longest first by each unit's average, and a "stuck" limit from it — TCP's own
    # retransmission timer (RFC 6298: average + 4 spreads; a timeout is congestion, and the timer backs off). The stand-ins
    # use tiny numbers: the 120 s floor, 4 times the average and the flat 600 s are made 1 s, twice and 10 s for these rows
    # (stuck_hooks), so a limit is a second and a hang ten.
    def fake_costs(path, units):
        """A costs file whose time averages are made up — units: {(sample path, unit key): (average, spread, runs)}, each
        under the sample's name inside the repository and its real contents' hash (hash: 'other' — other contents)."""
        files = {}
        for (p, key), (avg, spread, runs, *other) in units.items():
            tf = Inside(p)
            e = files.setdefault(tf.rel(), {"hash": "other" if other else tc.file_hash(p), "tier": tf.tier, "units": {}})
            e["units"][key] = {"count": runs, "when": "d", "measures": {
                "seconds": {"avg": avg, "spread": spread, "count": runs, "last": avg}}}
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"version": 1, "files": files}, f)
        return path

    @contextlib.contextmanager
    def stuck_hooks(floor=1.0, flat=10.0, times=2):
        """The limit's floor (120 s, and 4 times the average) and the flat limit (600 s) made small for a row — and put
        back."""
        saved = tc.STUCK_FLOOR_S, tc.STUCK_FLAT_S, tc.STUCK_FLOOR_TIMES
        tc.STUCK_FLOOR_S, tc.STUCK_FLAT_S, tc.STUCK_FLOOR_TIMES = floor, flat, times
        try:
            yield
        finally:
            tc.STUCK_FLOOR_S, tc.STUCK_FLAT_S, tc.STUCK_FLOOR_TIMES = saved

    def stat(avg, spread, runs):
        return {"avg": avg, "spread": spread, "count": runs, "last": avg}

    def r017():
        """The floor was twice the average or 60 s until the 2026-11-18 lab (12 of 16 CPUs kept busy by other programs):
        five healthy heavy files passed twice their average and were stopped — test_merge_branches.py at 110 s (average
        55), test_backlog_report.py at 282 s (average 141) — and healthy tests ran 2–5× slower when other programs took
        the CPU. Now 4 times the average or 120 s."""
        got = [tc.stuck_limit(stat(10.0, 1.0, 5)),       # 14 s, under the floor of 120 s → 120 (was 60)
               tc.stuck_limit(stat(100.0, 10.0, 7)),     # 140 s, under 4 times the average (400) → 400 (was 200)
               tc.stuck_limit(stat(100.0, 80.0, 5)),     # 420 s, between the floor (400) and the ceiling → 420
               tc.stuck_limit(stat(55.0, 3.0, 9)),       # the lab's test_merge_branches.py: 220 s (stopped at 110 before)
               tc.stuck_limit(stat(141.0, 5.0, 9)),      # the lab's test_backlog_report.py: 564 s (was 282)
               tc.stuck_limit(stat(400.0, 100.0, 9)),    # 800 s → the ceiling, 600
               tc.stuck_limit(stat(160.0, 10.0, 5)),     # 4 times the average (640) is over the ceiling too → 600
               tc.stuck_limit(stat(100.0, 30.0, 4)),     # 4 runs: too few → the flat 600, no average
               tc.stuck_limit(None)]
        want = [(120.0, 10.0), (400.0, 100.0), (420.0, 100.0), (220.0, 55.0), (564.0, 141.0), (600.0, 400.0),
                (600.0, 160.0), (600.0, None), (600.0, None)]
        consts = (tc.STUCK_FLAT_S, tc.STUCK_FLOOR_S, tc.STUCK_FLOOR_TIMES, tc.STUCK_MIN_RUNS, tc.STUCK_SPREADS)
        return got == want and consts == (600.0, 120.0, 4, 5, 4), (got, consts)

    row("COST-017", "the stuck limit — average + 4 spreads, never under 4 times the average or 120 s (the 2026-11-18 lab: "
        "twice stopped five healthy files), never over the flat 600 s: at its floor (120 s, and 4 times the average — the "
        "lab's two files), in its middle, at its ceiling; fewer than 5 runs, or none → the flat 600 s", r017)

    def r018():
        state = json.load(open(fake_costs(os.path.join(d, "c18-pure.json"), {
            (ok_py, "whole"): (8.0, 1.0, 5), (bad_py, "whole"): (9.0, 1.0, 5, "other")})))
        hashes = {Inside(p).path: tc.file_hash(p) for p in (ok_py, bad_py)}
        same = tc.time_stat(state, Inside(ok_py).rel(), "whole", hashes[Inside(ok_py).path])
        changed = tc.time_stat(state, Inside(bad_py).rel(), "whole", hashes[Inside(bad_py).path])
        none = tc.time_stat(state, "test/samples/never.py", "whole", "h")
        shard = Inside(shard_py)
        last = {Inside(bad_py).rel(): (30.0, False), shard.rel(): (12.0, True)}
        est = [rt.estimate((Inside(ok_py), None, None, None), state, last, hashes),         # its average
               rt.estimate((Inside(bad_py), None, None, None), state, last, hashes),        # changed → the record
               rt.estimate((shard, 2, 2, ["SHD-002"]), state, last, hashes),                # the record's longest shard
               rt.estimate((shard, 2, 2, ["SHD-002"]), state, {shard.rel(): (12.0, False)}, hashes),  # split 2 ways
               rt.estimate((Inside(heavy_py), None, None, None), state, last, hashes)]      # neither → 5 s (tier 1)
        pure = same == stat(8.0, 1.0, 5) and changed is None and none is None and est == [8.0, 30.0, 12.0, 6.0, 5.0]

        # Through the runner, one at a time: the order follows each file's AVERAGE — not this copy's latest record.
        marks = os.path.join(d, "order-marks")
        os.makedirs(marks, exist_ok=True)
        names = ["test_order_a.py", "test_order_b.py", "test_order_c.py", "test_order_d.py"]
        paths = [write(n, "# tags: costs, order, tier 1\n# covers: nothing.js\nimport os, time\n"
                          f"open(os.path.join({marks!r}, {n!r}), 'w').write(repr(time.time()))\n"
                          "print('1 passed, 0 failed')\n") for n in names]
        a, b, c, dd = paths
        costs18 = fake_costs(os.path.join(d, "c18.json"),
                             {(a, "whole"): (50.0, 5.0, 5), (dd, "whole"): (40.0, 4.0, 5, "other")})
        rdir = os.path.join(d, "rec18")
        os.makedirs(rdir)
        with open(os.path.join(rdir, "0000-earlier.json"), "w", encoding="utf-8") as f:     # this copy's latest record
            json.dump({"ended": "2026-11-18T00:00:00", "files": [
                {"file": Inside(a).rel(), "seconds": 1.0}, {"file": Inside(b).rel(), "seconds": 20.0},
                {"file": Inside(dd).rel(), "seconds": 30.0}]}, f)
        code, out = quiet_main(["--tier", "1", "--jobs", "1"], files=[Inside(p) for p in paths], results=rdir,
                               costs=costs18, slots=test_slots.Slots(count=2, folder=slots_dir))
        when = {n: float(open(os.path.join(marks, n)).read()) for n in names if os.path.exists(os.path.join(marks, n))}
        order = sorted(when, key=when.get)
        want = ["test_order_a.py", "test_order_d.py", "test_order_b.py", "test_order_c.py"]
        return pure and code == 0 and order == want, (same, changed, none, est, code, order, out[-400:])

    row("COST-018", "longest first by each unit's AVERAGE on this PC (its contents unchanged), else its time in this copy's "
        "latest record (a shard: its file's longest shard, or its time split), else 60 s / 5 s — through the runner, one "
        "at a time: the average's order, not the record's", r018)

    stuck_flag, child_pid, stuck_runs = (os.path.join(d, n) for n in ("stuck-once", "stuck-child.pid", "stuck-runs"))
    stuck_py = write("test_cost_stuck.py", "# tags: costs, stuck, tier 1\n# covers: nothing.js\n"
                     "# heavy: yes — a stand-in that runs past its usual time once\n"
                     f"import os, subprocess, sys, time\nopen({stuck_runs!r}, 'a').write('run\\n')\n"
                     f"if not os.path.exists({stuck_flag!r}):\n"
                     f"    open({stuck_flag!r}, 'w').close()\n"
                     "    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'],\n"
                     "                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, "
                     "stderr=subprocess.DEVNULL)\n"
                     f"    open({child_pid!r}, 'w').write(str(child.pid))\n"
                     "    print('started a child', flush=True)\n"
                     "    time.sleep(20)\n"
                     "time.sleep(2.0)     # its rerun: longer than its stuck limit (1 s), well within the flat one\n"
                     "print('1 passed, 0 failed')\n")
    lr = rt.local_relay      # its process list, read raw (local_relay.processes) — and stop_one, by exact id

    def gone(pid, limit=10.0):
        """Is the process gone? Waited for (up to `limit`) — a process the job ended may take a moment to leave."""
        end = time.monotonic() + limit
        while pid in lr.processes():
            if time.monotonic() > end:
                return False
            time.sleep(0.1)
        return True

    def r019():
        lvl_dir = os.path.join(d, "slots-stuck")
        costs19 = fake_costs(os.path.join(d, "c19.json"), {(stuck_py, "whole"): (0.5, 0.05, 5)})
        rdir = os.path.join(d, "rec19")
        with stuck_hooks():
            code, out = quiet_main(["--tier", "1"], files=[Inside(stuck_py)], results=rdir, costs=costs19, retry_wait=0,
                                   slots=test_slots.Slots(count=2, folder=lvl_dir))
        pid = int(open(child_pid).read()) if os.path.exists(child_pid) else None
        ended = pid is not None and gone(pid)
        if pid is not None and not ended:
            lr.stop_one(pid)        # left running by the runner: stopped here, by its exact id
        rec = (records_in(rdir) or [{}])[0]
        f = (rec.get("files") or [{}])[0]
        tried = (f.get("retried") or [{}])[0]
        level, _ = rt.browser_level.load(os.path.join(lvl_dir, rt.browser_level.FILE_NAME))
        runs = len(open(stuck_runs).read().split()) if os.path.exists(stuck_runs) else 0
        said = "ran past its usual time: 1.0 s, its average 0.5 s"
        first = open(tried["first_output"], encoding="utf-8").read() if tried.get("first_output") else ""
        ok = code == 0 and ended and runs == 2 and f.get("result") == "passed" \
            and "· stuck limits from this PC's averages (1 unit)" in out \
            and f"test/samples/test_cost_stuck.py: {said} — stopped, with every process it started: the machine's " \
                "trouble, not a test failure — it will be rerun once, alone, with the flat 10 s" in out \
            and "! browsers at once: 4 → 2 for the rest of this run" in out and level["level"] == 2 \
            and f"; rerun alone after {said})" in out and tried.get("reason") == said \
            and tried.get("rerun") == "passed" and tried.get("limit") == 1.0 and tried.get("average") == 0.5 \
            and "started a child" in first and f"1 file retried after {said}" in out
        return ok, (code, pid, ended, runs, f, level, out[-900:])

    row("COST-019", "a unit that runs past its stuck limit (its average's) is the machine's trouble, not a failure: stopped "
        "with its whole process tree (its child gone too), said plainly with its limit and average, the browsers' level "
        "halved, rerun alone with the flat limit — longer than the stuck one — and passes; the run's opening line says "
        "how many units have limits from the averages", r019)

    def r022():
        """TCP keeps its backed-off timer until a sample it can trust (Karn): a unit stopped at its limit is marked, and
        its next run gets the flat limit; passing then, the first time, teaches its average and clears the mark. (A rerun
        alone never teaches — without the mark, a test that truly got slower would be stopped every run, forever.)"""
        costs19 = os.path.join(d, "c19.json")       # COST-019's: the stand-in was stopped at its limit there
        unit = lambda: units_in(costs19).get(("test_cost_stuck.py", "whole")) or {}      # noqa: E731
        marked = unit().get("backed_off")
        with stuck_hooks():
            code, out = quiet_main(["--tier", "1"], files=[Inside(stuck_py)], results=os.path.join(d, "rec22"),
                                   costs=costs19, retry_wait=0, slots=test_slots.Slots(count=2, folder=slots_dir))
        after = unit()
        ok = bool(marked) and code == 0 and "ran past its usual time" not in out and "stuck limits from" not in out \
            and "backed_off" not in after and after.get("count") == 6 and after["measures"]["seconds"]["last"] >= 2.0
        return ok, (marked, code, after, out[-500:])

    row("COST-022", "a unit stopped at its limit is marked in this PC's averages: its next run gets the flat limit (its "
        "2 s run passes) — and that pass, the first time, teaches its average and clears the mark", r022)

    hang_runs = os.path.join(d, "hang-runs")
    hang_py = write("test_cost_hang.py", "# tags: costs, hang, tier 1\n# covers: nothing.js\nimport time\n"
                    f"open({hang_runs!r}, 'a').write('run\\n')\nprint('hanging', flush=True)\ntime.sleep(60)\n"
                    "print('1 passed, 0 failed')\n")

    def r020():
        costs20 = fake_costs(os.path.join(d, "c20.json"), {(hang_py, "whole"): (0.5, 0.05, 6)})
        rdir = os.path.join(d, "rec20")
        with stuck_hooks(flat=5.0):         # a hang: past the stuck 1 s, and past the flat limit of its rerun too
            code, out = quiet_main(["--tier", "1"], files=[Inside(hang_py)], results=rdir, costs=costs20, retry_wait=0,
                                   slots=test_slots.Slots(count=2, folder=slots_dir))
        rec = (records_in(rdir) or [{}])[0]
        f = (rec.get("files") or [{}])[0]
        tried = (f.get("retried") or [{}])[0]
        rerun = open(tried["rerun_output"], encoding="utf-8").read() if tried.get("rerun_output") else ""
        runs = len(open(hang_runs).read().split()) if os.path.exists(hang_runs) else 0
        ok = code == 1 and runs == 2 and f.get("result") == "failed" and tried.get("rerun") == "failed" \
            and "✗ timed out after 5 s" in rerun and "✗ timed out after 5 s" in out \
            and "Tests: 0 file(s) passed, 1 failed" in out and "browsers at once" not in out
        return ok, (code, runs, f, out[-700:])

    row("COST-020", "a unit that hangs past its stuck limit AND the flat limit of its rerun alone is a real failure, "
        "reported as today ('timed out after …'); a light tier-1 file in a run with no level in play halves nothing",
        r020)

    cap_runs = os.path.join(d, "cap-runs")
    cap_py = write("test_cost_cap.py", "# tags: costs, cap, tier 1\n# covers: nothing.js\nimport time\n"
                   f"open({cap_runs!r}, 'a').write('run\\n')\nprint('slow but healthy', flush=True)\ntime.sleep(20)\n"
                   "print('1 passed, 0 failed')\n")

    def r023():
        """The 2026-11-18 lab: test_backlog_report.py ran past its limit after MAX_RETRIES files of the run were already
        taken for a rerun — and was reported 'timed out', a FAILURE: a slow-but-healthy test called broken. Past the
        rerun cap, the machine's trouble is NOT PROVEN — never a failure (here the cap is made 0)."""
        costs23 = fake_costs(os.path.join(d, "c23.json"), {(cap_py, "whole"): (0.5, 0.05, 5)})
        rdir = os.path.join(d, "rec23")
        saved = rt.MAX_RETRIES
        rt.MAX_RETRIES = 0
        try:
            with stuck_hooks():
                code, out = quiet_main(["--tier", "1"], files=[Inside(cap_py)], results=rdir, costs=costs23, retry_wait=0,
                                       slots=test_slots.Slots(count=2, folder=slots_dir))
        finally:
            rt.MAX_RETRIES = saved
        rec = (records_in(rdir) or [{}])[0]
        f = (rec.get("files") or [{}])[0]
        runs = len(open(cap_runs).read().split()) if os.path.exists(cap_runs) else 0
        kept = open(f["output"], encoding="utf-8").read() if f.get("output") and os.path.exists(f["output"]) else ""
        left = (rec.get("costs") or {}).get("left_out") or {}
        backed = (rec.get("costs") or {}).get("backed_off") or []
        ok = code == 3 and runs == 1 and f.get("result") == "not proven" \
            and "ran past its usual time: 1.0 s" in str(f.get("not_proven")) and "slow but healthy" in kept \
            and rec.get("result") == "not proven" and "test/samples/test_cost_cap.py" in backed \
            and left.get("test/samples/test_cost_cap.py") == "the machine's trouble — not proven" \
            and "Tests: 0 file(s) passed, 0 failed, 1 not proven (the machine's trouble)" in out \
            and "not proven — the machine was too busy (1 file met its trouble this run; only 0 are rerun)" in out \
            and "✗ test/samples/test_cost_cap.py" not in out and "timed out" not in out \
            and tc.left_out([], False, False, trouble=True) == "the machine's trouble — not proven"
        return ok, (code, runs, f, rec.get("result"), left, out[-900:])

    row("COST-023", "a unit past its stuck limit after the rerun cap is already taken is NOT PROVEN — never a failure: "
        "stopped once, not rerun, counted apart ('1 not proven (the machine's trouble)'), its output kept, the run's exit "
        "3, the record marking it (and its backed-off limit), its sample left out as the machine's trouble", r023)

    slow_py = write("test_cost_slow.py", "# tags: costs, slow, tier 1\n# covers: nothing.js\nimport time\n"
                    "def check(tid, ok): print(('  ✓ ' if ok else '  ✗ ') + tid)\ntime.sleep(2.0)\n"
                    "check(\"SLOW-001\", True)\nprint('1 passed, 0 failed')\n")
    few_py = write("test_cost_few.py", "# tags: costs, few, tier 1\n# covers: nothing.js\nimport time\ntime.sleep(2.0)\n"
                   "print('1 passed, 0 failed')\n")

    def r021():
        costs21 = os.path.join(d, "c21.json")
        cases = {}
        with stuck_hooks():
            for name, argv, env in (("full, too few runs", ["--tier", "1"], {}),
                                    ("--id", ["--tier", "1", "--id", "SLOW-001"], {}),
                                    ("--tag", ["--tier", "1", "--tag", "slow"], {}),
                                    ("RW_CELLS", ["--tier", "1"], {"RW_CELLS": "SLOW-001"})):
                fake_costs(costs21, {(slow_py, "whole"): (0.5, 0.05, 5), (few_py, "whole"): (0.5, 0.05, 4)})
                os.environ.update(env)
                try:
                    picked = [few_py] if name.startswith("full") else [slow_py, few_py]
                    cases[name] = quiet_main(argv, files=[Inside(p) for p in picked], costs=costs21, retry_wait=0,
                                             results=os.path.join(d, f"rec21-{len(cases)}"),
                                             slots=test_slots.Slots(count=2, folder=slots_dir))
                finally:
                    for k in env:
                        del os.environ[k]
        ok = all(c == 0 and "ran past its usual time" not in o and "stuck limits from" not in o
                 for c, o in cases.values())
        return ok, {k: (c, o[-300:]) for k, (c, o) in cases.items()}

    row("COST-021", "the flat limit where an average doesn't apply: a unit with fewer than 5 runs measured, and every unit "
        "of a narrowed run (--id, --tag, RW_CELLS) — a 2 s unit whose stuck limit would be 1 s passes", r021)

    screen_py = write("test_cost_screen.py", "# tags: costs, screen, tier 2\n# covers: nothing.js\n"
                      "def check(tid, ok): print(('  ✓ ' if ok else '  ✗ ') + tid)\n"
                      "check(\"SCRN-001\", True)\nprint('1 passed, 0 failed')\n")

    def r024():
        """A narrowed run with a SCREEN test in it taught the averages until 2026-11-18: the browsers-at-once part of the
        runner reassigned the run's `narrowing` to its narrowing variables only, so an --id run read as full below it."""
        costs24 = os.path.join(d, "c24.json")
        own = test_slots.Slots(count=2, folder=os.path.join(d, "slots-24"))
        code, out = quiet_main(["--tier", "2", "--id", "SCRN-001"], files=[Inside(screen_py)], costs=costs24,
                               results=os.path.join(d, "rec24"), retry_wait=0, slots=own)
        narrowed_taught = units_in(costs24)
        code2, out2 = quiet_main(["--tier", "2"], files=[Inside(screen_py)], costs=costs24,
                                 results=os.path.join(d, "rec24"), retry_wait=0, slots=own)
        full_taught = units_in(costs24)
        return code == 0 and code2 == 0 and narrowed_taught == {} \
            and list(full_taught) == [("test_cost_screen.py", "whole")], \
            (code, narrowed_taught, code2, list(full_taught), out[-400:], out2[-300:])

    row("COST-024", "a narrowed run (--id) of a SCREEN test teaches nothing — a full one does (the browsers-at-once part "
        "once reassigned what narrowed the run)", r024)

failed = [r for r in results if not r[1]]
print(f"{len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
