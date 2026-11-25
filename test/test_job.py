# Tests for tools/job.py — each test unit runs in a Windows job: measured for its whole process tree, and everything it
# started ended with it (kill-on-close) — when the unit ends, and when the runner itself is stopped hard. Also the
# runner's side (the measures in each run's record) and where the per-PC test state lives.
# tags: test-runner, tier 1
# covers: tools/job.py, tools/run_tests.py, tools/test_slots.py, tools/held_tests.py
# Run: python test/test_job.py
import atexit
import contextlib
import ctypes
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
# Every run of the runner started here keeps its per-PC state in a throwaway folder — never the PC's real one. Read by
# test_slots.slots_folder() at each call, and inherited by every process started from here.
os.environ["RW_TEST_SLOTS_DIR"] = tempfile.mkdtemp(prefix="rw-selftest-slots-")
atexit.register(shutil.rmtree, os.environ["RW_TEST_SLOTS_DIR"], True)
try:
    import job
    missing = None
except Exception as e:      # noqa: BLE001 — every row that needs it fails, naming why
    job, missing = None, f"{type(e).__name__}: {e}"
spec = importlib.util.spec_from_file_location("run_tests", os.path.join(TOOLS, "run_tests.py"))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)
import test_slots   # noqa: E402 — the same module the runner uses (tools/ is on the path)
import held_tests   # noqa: E402

MB = 2 ** 20
MEASURES = ("committed_peak_bytes", "ram_peak_sampled_bytes", "cpu_seconds", "io_read_bytes", "io_written_bytes",
            "processes")
results = []


def row(tid, name, fn, needs_job=True):
    """One check: fn() returns (passed?, detail). An error inside it is a failure, named."""
    try:
        if needs_job and job is None:
            raise RuntimeError(missing)
        ok, detail = fn()
    except Exception as e:      # noqa: BLE001
        ok, detail = False, f"{type(e).__name__}: {e}"
    results.append((tid, ok))
    print(f"  {'✓' if ok else '✗'} {tid} {name}" + ("" if ok else f" — {str(detail)[:1500]}"))


def alive(pid):
    """Is a process with this id running? (Windows: OpenProcess + its exit code; elsewhere a signal 0.)"""
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = ctypes.c_void_p
    h = k32.OpenProcess(0x1000, False, pid)          # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return False
    try:
        code = ctypes.c_ulong()
        return bool(k32.GetExitCodeProcess(ctypes.c_void_p(h), ctypes.byref(code))) and code.value == 259
    finally:
        k32.CloseHandle(ctypes.c_void_p(h))


def gone(pid, limit=10.0):
    """Waited for (up to `limit`): a process its job ended may take a moment to leave."""
    end = time.monotonic() + limit
    while alive(pid):
        if time.monotonic() > end:
            return False
        time.sleep(0.1)
    return True


def stop_exact(pid):
    """This file's own cleanup when a check failed: one process, by its exact id (never /T)."""
    if alive(pid):
        subprocess.run(["taskkill", "/PID", str(pid), "/F"] if os.name == "nt" else ["kill", "-9", str(pid)],
                       capture_output=True)


def read_pid(path, limit=30.0):
    end = time.monotonic() + limit
    while time.monotonic() < end:
        try:
            text = open(path).read().strip()
            if text:
                return int(text)
        except (OSError, ValueError):
            pass
        time.sleep(0.05)
    return None


def quiet_main(argv, **kw):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = rt.main(argv, **kw)
    except SystemExit as e:
        code = f"SystemExit {e.code}"
    return code, buf.getvalue()


# --- 1. one unit, measured -----------------------------------------------------------------------------------------------
def r001():
    real = job._Job
    try:
        def broken():
            raise OSError("making a job object failed (a stand-in)")
        job._Job = broken
        code, out, _, m = job.run([sys.executable, "-c", "print('again')"])
    finally:
        job._Job = real
    ok = (code, out.strip()) == (0, b"again") and all(m[k] is None for k in MEASURES) and "stand-in" in m["missing"]
    return ok, (code, out, m)


row("JOB-001", "no job can be made: the test runs exactly as before, every measure is None, and why is given", r001)

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


def r002():
    with tempfile.TemporaryDirectory() as d:
        script, target = os.path.join(d, "child.py"), os.path.join(d, "written.bin")
        with open(script, "w", encoding="utf-8") as f:
            f.write(CHILD)
        code, out, err, m = job.run([sys.executable, script, target], timeout=120)
    if os.name != "nt":
        return m["cpu_seconds"] is None and m["missing"], m
    ok = code == 0 and m["cpu_seconds"] >= 1.0 and m["committed_peak_bytes"] >= 200 * MB \
        and m.get("ram_kind") == "private" and (m["ram_peak_sampled_bytes"] or 0) >= 200 * MB \
        and (m.get("ram_with_shared_peak_sampled_bytes") or 0) >= m["ram_peak_sampled_bytes"] \
        and m["io_written_bytes"] >= 20 * MB and m["processes"] >= 2 and m.get("left_running") == 0
    return ok, dict(m, code=code, err=err.decode("utf-8", "replace")[-300:])


row("JOB-002", "measured for the WHOLE tree: a child holding 200 MB whose grandchild burns 1 s of CPU and exits first — "
    "the CPU counts the grandchild (≥ 1 s), committed peak ≥ 200 MB, RAM, private (sampled) ≥ the 200 MB it touched "
    "(the shared-included sum at least that), 20 MB written, ≥ 2 processes, none left running", r002)


def r003():
    """The RAM measure is the PRIVATE working set when Windows gives it — else every process's whole working set, and the
    record says which (ram_kind). The call is stubbed: each process reports 100 MB in all, 30 MB of it private."""
    if os.name != "nt":
        return True, "not Windows"
    real = job._process_memory
    child = [sys.executable, "-c", "import time; time.sleep(1.6)"]
    try:
        job._process_memory = lambda pid: (100 * MB, 30 * MB)
        _, _, _, priv = job.run(child)
        job._process_memory = lambda pid: (100 * MB, None)       # this Windows has no private working set
        _, _, _, shared = job.run(child)
    finally:
        job._process_memory = real
    n = priv["ram_with_shared_peak_sampled_bytes"] // (100 * MB) if priv.get("ram_with_shared_peak_sampled_bytes") else 0
    ok = n >= 1 and priv["ram_kind"] == "private" and priv["ram_peak_sampled_bytes"] == n * 30 * MB \
        and shared["ram_kind"] == "shared included" and shared["ram_peak_sampled_bytes"] == n * 100 * MB \
        and shared["ram_with_shared_peak_sampled_bytes"] == n * 100 * MB and "private" in (shared.get("ram_note") or "")
    return ok, (priv, shared)


row("JOB-003", "RAM is each process's PRIVATE working set, added up (what the test adds to the PC's RAM) — where Windows "
    "can't give it, the whole working set instead, and the record says which kind was measured", r003)


# --- 2. ended with it: kill-on-close ---------------------------------------------------------------------------------------
def leaver(d, name, sleep_after=0.0, hold_pipes=False):
    """A stand-in test unit: starts a child that would run for a minute (its id written to <name>.child), writes its own
    id (<name>.unit), prints, sleeps `sleep_after`, and exits. hold_pipes: the child keeps the unit's output pipes."""
    pids = os.path.join(d, name)
    out = "" if hold_pipes else ", stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL"
    p = os.path.join(d, name + ".py")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# sample\n# tags: job-sample, tier 1\n# covers: tools/job.py\n"
                "import os, subprocess, sys, time\n"
                f"open({pids!r} + '.unit', 'w').write(str(os.getpid()))\n"
                # The child runs on the BASE interpreter, so it is one process under a venv too: a venv's
                # python.exe is a launcher that starts the real interpreter as a second process, which made
                # left_running 2 where JOB-005 expects 1 (2026-11-25, the 7.31.1 release run; RUN-057's cousin).
                f"c = subprocess.Popen([getattr(sys, '_base_executable', sys.executable), '-c', "
                f"'import time; time.sleep(60)']{out})\n"
                f"open({pids!r} + '.child', 'w').write(str(c.pid))\n"
                f"print('started a child', flush=True)\ntime.sleep({sleep_after})\n"
                "print('1 passed, 0 failed')\n")
    return p, pids


def r004():
    with tempfile.TemporaryDirectory() as d:
        p, pids = leaver(d, "past", sleep_after=60)
        code, out, _, m = job.run([sys.executable, p], timeout=2)
        child = read_pid(pids + ".child", 1)
        ended = child is not None and gone(child)
        if child and not ended:
            stop_exact(child)
    return code is None and b"started a child" in out and ended, (code, out, child, ended, m)


row("JOB-004", "a unit that runs past its time is stopped WITH everything it started (exit None, what it printed kept)",
    r004)


def r005():
    with tempfile.TemporaryDirectory() as d:
        p, pids = leaver(d, "left")
        t0 = time.monotonic()
        code, out, _, m = job.run([sys.executable, p], timeout=120)
        took = time.monotonic() - t0
        child = read_pid(pids + ".child", 1)
        ended = child is not None and gone(child)
        if child and not ended:
            stop_exact(child)
        p2, pids2 = leaver(d, "pipes", hold_pipes=True)
        t0 = time.monotonic()
        code2, out2, _, m2 = job.run([sys.executable, p2], timeout=120)
        took2 = time.monotonic() - t0
        child2 = read_pid(pids2 + ".child", 1)
        ended2 = child2 is not None and gone(child2)
        if child2 and not ended2:
            stop_exact(child2)
    left = (m.get("left_running"), m2.get("left_running"))
    ok = code == 0 and code2 == 0 and ended and ended2 and took < 30 and took2 < 30 \
        and (left == (1, 1) if os.name == "nt" else True)
    return ok, (code, took, ended, code2, took2, ended2, left, out2[-200:])


row("JOB-005", "a unit whose own process ends while a child it started still runs: the child is ended with its job, "
    "counted in the measures (left_running) — also when the child holds the unit's output pipes (no wait until the time "
    "limit)", r005)


def r006():
    """Through the runner — a sample run, which leaves no record: before, only a run that left a record ran its units in
    a job, so a sample's leftover child lived on."""
    with tempfile.TemporaryDirectory() as d:
        p, pids = leaver(d, "test_leaves_child")
        code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(p)])
        child = read_pid(pids + ".child", 1)
        ended = child is not None and gone(child)
        if child and not ended:
            stop_exact(child)
    return code == 0 and ended, (code, child, ended, out[-400:])


row("JOB-006", "through the runner: a test file that leaves a child running — the child is gone when its file ends",
    r006, needs_job=False)

RUNNER = r'''
import importlib.util, sys
spec = importlib.util.spec_from_file_location("run_tests", sys.argv[1])
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)
sys.exit(rt.main(["--tier", "1"], files=[rt.TestFile(sys.argv[2])]))
'''


def r007():
    """The runner itself stopped hard (its own process ended mid-run — a crash, a closed window): the test it was running
    and the child that test started end with it — nothing is left for anyone to find later."""
    with tempfile.TemporaryDirectory() as d:
        p, pids = leaver(d, "test_runner_dies", sleep_after=120)
        runner = subprocess.Popen([sys.executable, "-c", RUNNER, os.path.join(TOOLS, "run_tests.py"), p],
                                  stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        child, unit = read_pid(pids + ".child"), read_pid(pids + ".unit")
        runner.kill()           # the runner's own process, by its handle — nothing else
        runner.wait(10)
        ended = [pid is not None and gone(pid) for pid in (unit, child)]
        for pid in (unit, child):
            if pid:
                stop_exact(pid)
    return all(ended) and child is not None, (unit, child, ended)


row("JOB-007", "the runner stopped hard mid-run: the test it was running and what that test started are gone with it "
    "(Windows ends a job's processes when its last handle closes)", r007, needs_job=False)


# --- 3. the runner's record ---------------------------------------------------------------------------------------------
def r008():
    with tempfile.TemporaryDirectory() as d:
        def write(name, text):
            path = os.path.join(d, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return path
        ok_py = write("test_cost_ok.py", "# tags: costs, tier 1\n# covers: nothing.js\nprint('1 passed, 0 failed')\n")
        bad_py = write("test_cost_bad.py", "# tags: costs, tier 1\n# covers: nothing.js\n"
                       "print('  ✗ SAMP-002 broken')\nprint('0 passed, 1 failed')\nimport sys; sys.exit(1)\n")
        shard_py = write("test_cost_shards.py", "# tags: costs, tier 1\n# covers: nothing.js\n# shards: 2\n"
                         "import os, sys\nif '--list-cells' in sys.argv:\n    print('SHD-001\\nSHD-002')\n    sys.exit(0)\n"
                         "cells = os.environ.get('RW_CELLS', '').split(',')\nprint(f'{len(cells)} passed, 0 failed')\n")
        rdir = os.path.join(d, "rec")
        code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(p) for p in (ok_py, bad_py, shard_py)], results=rdir,
                               slots=test_slots.Slots(count=2, folder=os.path.join(d, "slots")))
        recs = rt.read_records(rdir)
    by = {os.path.basename(f["file"]): f for f in (recs[-1] if recs else {}).get("files", [])}
    keys = set(MEASURES)
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


row("JOB-008", "a run's record holds the measures beside each file's seconds — and each shard's (a sharded file: CPU "
    "and I/O added up over its shards, the peaks its largest shard's)", r008)


def r009():
    """The per-PC test state (the slots, the held files) lives in %LOCALAPPDATA%\\ReaderWrangler-tests — Windows can clear
    the temp folder, and a held file's record would vanish with it. RW_TEST_SLOTS_DIR still overrides."""
    saved = os.environ.pop("RW_TEST_SLOTS_DIR")
    try:
        default = test_slots.slots_folder()
        own = os.path.join(tempfile.gettempdir(), "rw-own-slots")
        os.environ["RW_TEST_SLOTS_DIR"] = own
        moved = test_slots.slots_folder()
    finally:
        os.environ["RW_TEST_SLOTS_DIR"] = saved
    want = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.join(os.path.expanduser("~"), ".cache"),
                        "ReaderWrangler-tests")
    norm = os.path.normcase
    held = held_tests.path_in(default)
    ok = norm(default) == norm(want) and norm(test_slots.FOLDER) == norm(want) and norm(moved) == norm(own) \
        and norm(os.path.dirname(held)) == norm(want) \
        and not norm(default).startswith(norm(tempfile.gettempdir()))
    return ok, (default, moved, held)


row("JOB-009", "the per-PC test state is kept in %LOCALAPPDATA%\\ReaderWrangler-tests (not the temp folder Windows can "
    "clear) — the slots and the held files; RW_TEST_SLOTS_DIR still chooses another folder", r009, needs_job=False)

failed = [r for r in results if not r[1]]
print(f"{len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
