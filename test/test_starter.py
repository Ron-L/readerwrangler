# Tests for tools/starter.py — the ONE starter for every process our test tools start, the list of what they started
# (its id, start time, what it is, which run), and leftovers shown loudly; plus a test unit's leftovers stopped by its job
# (tools/test_costs.py) and the relay tests' relay measured (TODO 20261112-1240; sprint 9).
# tags: test-runner, tier 1
# covers: tools/starter.py, tools/local_relay.py, tools/test_costs.py, tools/run_tests.py, tools/test_slots.py, test/ui/rw.py
# Run: python test/test_starter.py
#
# Every process here is a stand-in (a few lines of Python) started in a throwaway folder; the list and the slots live in a
# throwaway folder too (RW_TEST_SLOTS_DIR) — never the PC's real ones. What this file starts itself, it stops itself by
# exact id at the end.
import atexit
import contextlib
import importlib.util
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # print ✓ even when piped (as harness.py)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
SLOTS = tempfile.mkdtemp(prefix="rw-selftest-starter-")
os.environ["RW_TEST_SLOTS_DIR"] = SLOTS                 # the list, the slots, the level and the costs: all throwaway
atexit.register(shutil.rmtree, SLOTS, True)
try:
    import starter
    missing = None
except Exception as e:      # noqa: BLE001 — not built yet: every row fails, naming why
    starter, missing = None, f"{type(e).__name__}: {e}"
import test_costs as tc     # noqa: E402
spec = importlib.util.spec_from_file_location("run_tests", os.path.join(TOOLS, "run_tests.py"))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)

RUN_VAR = "RW_RUN_ID"       # which run a process belongs to — the runner gives it to every file it starts
os.environ[RUN_VAR] = "the START self-test's own run"
DEVNULL = subprocess.DEVNULL
results = []


class Mine:
    """Every process this file started (or caused), with its start time — stopped at the end by exact id if it is STILL
    that process (same start time: an id Windows gave to another process since is never touched)."""

    def __init__(self):
        self.seen = {}

    def add(self, pid):
        if pid and starter is not None and pid not in self.seen:
            self.seen[pid] = starter.started_at(pid)

    def update(self, pids):
        for p in pids:
            self.add(p)

    def stop_left(self):
        for pid, t in sorted(self.seen.items()):
            if t is not None and starter.started_at(pid) == t:
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)    # one process — never /T


mine = Mine()


def row(tid, name, fn):
    """One check: fn() returns (passed?, detail). An error inside it is a failure, named."""
    try:
        if starter is None:
            raise RuntimeError(missing)
        ok, detail = fn()
    except Exception as e:      # noqa: BLE001
        ok, detail = False, f"{type(e).__name__}: {e}"
    results.append((tid, ok))
    print(f"  {'✓' if ok else '✗'} {tid} {name}" + ("" if ok else f" — {str(detail)[:1500]}"))


def until(cond, limit=60.0):
    """Wait for a condition (never a fixed moment — TESTING.md §7); True once it holds, False past the limit."""
    end = time.monotonic() + limit
    while time.monotonic() < end:
        if cond():
            return True
        time.sleep(0.05)
    return bool(cond())


def alive(pid):
    return pid in starter.processes()


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def quiet_main(argv, **kw):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = rt.main(argv, **kw)
    except SystemExit as e:
        code = f"SystemExit {e.code}"
    except TypeError as e:
        code = f"TypeError {e}"
    return code, buf.getvalue()


D = tempfile.mkdtemp(prefix="rw-starter-test-")
atexit.register(shutil.rmtree, D, True)


def write(name, text):
    p = os.path.join(D, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


# A stand-in: "serve" listens on the port; "parent" starts a "serve" child and waits; "relay" does the same and then
# prints wrangler's ready line; "sleep" just waits. Each notes its child's id / that it serves beside `note`.
STANDIN = write("standin.py", r'''import http.server, os, socket, subprocess, sys, time
mode, port, note = sys.argv[1], int(sys.argv[2]), sys.argv[3]
def served():
    for _ in range(1200):
        try:
            socket.create_connection(("127.0.0.1", port), 0.2).close()
            return True
        except OSError:
            time.sleep(0.05)
    return False
if mode == "serve":
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"stand-in")
        def log_message(self, *a):
            pass
    class S(http.server.HTTPServer):
        allow_reuse_address = False
    srv = S(("127.0.0.1", port), H)
    open(note + ".serving", "w").write(str(os.getpid()))
    srv.serve_forever()
elif mode in ("parent", "relay"):
    c = subprocess.Popen([sys.executable, __file__, "serve", str(port), note], stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    open(note + ".child", "w").write(str(c.pid))
    if not served():
        sys.exit("the stand-in's server never came up")
    if mode == "relay":
        print(f"[wrangler:info] Ready on http://127.0.0.1:{port}", flush=True)
    time.sleep(600)
else:
    time.sleep(600)
''')


def stand_in(mode, port, note):
    return [sys.executable, STANDIN, mode, str(port), note]


# ---------------------------------------------------------------------------------------------------------------------
# 1–2. The list: every process started, listed at once — and off the list only when confirmed gone
# ---------------------------------------------------------------------------------------------------------------------
state = {}


def r001():
    port, note = free_port(), os.path.join(D, "s001")
    s = starter.Started("a stand-in web server (START-001)", ports=[port])
    s.start(stand_in("parent", port, note), stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    mine.add(s.proc.pid)
    up = until(lambda: os.path.exists(note + ".serving"))
    child = int(read(note + ".child") or 0)
    mine.add(child)
    s.note_tree()
    state["s001"] = (s, child, port)
    listed = {e["pid"]: e for e in starter.Ledger().entries()}
    root = listed.get(s.proc.pid) or {}
    kid = listed.get(child) or {}
    ok = up and child and root.get("start") == starter.started_at(s.proc.pid) and root.get("start") is not None \
        and root.get("what") == "a stand-in web server (START-001)" and root.get("run") == os.environ[RUN_VAR] \
        and (root.get("owner") or {}).get("pid") == os.getpid() and root.get("ports") == [port] \
        and kid.get("start") == starter.started_at(child) and kid.get("what") == root.get("what") \
        and starter.Ledger().path == os.path.join(SLOTS, starter.FILE_NAME)
    return ok, (up, child, root, kid)


row("START-001", "a process the starter starts is on the list at once — its id, its start time, what it is, which run "
    "started it, the process that started it, its port — and so is its child once the tree is noted", r001)


def r002():
    s, child, port = state["s001"]
    root = s.proc.pid
    left = s.stop()
    gone = until(lambda: not alive(root) and not alive(child), 10)
    listed = {e["pid"] for e in starter.Ledger().entries()}
    return left == [] and gone and root not in listed and child not in listed, (left, gone, listed)


row("START-002", "stopped: each process by its exact id, checked gone, port free — and only then off the list", r002)

RUN_SCRIPT = write("a_run.py", f'''import os, subprocess, sys, time
sys.path.insert(0, {TOOLS!r})
import starter
port, note = int(sys.argv[1]), sys.argv[2]
s = starter.Started("a stand-in web server for a run that crashes (START-003)", ports=[port])
s.start([sys.executable, {STANDIN!r}, "parent", str(port), note], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)
while not os.path.exists(note + ".serving"):
    time.sleep(0.05)
s.note_tree()
open(note + ".listed", "w").write(str(s.proc.pid))
time.sleep(600)
''')


def r003():
    port, note = free_port(), os.path.join(D, "s003")
    run = subprocess.Popen([sys.executable, RUN_SCRIPT, str(port), note], stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL,
                           env=dict(os.environ, **{RUN_VAR: "a run that crashed (START-003)"}))
    mine.add(run.pid)
    listed_up = until(lambda: os.path.exists(note + ".listed"))
    parent, child = int(read(note + ".listed") or 0), int(read(note + ".child") or 0)
    mine.update({parent, child})
    run.kill()              # the run "crashes": stopped hard, by its own handle — it never stops what it started
    run.wait(10)
    state["s003"] = (parent, child, port, run.pid)
    listed = {e["pid"]: e for e in starter.Ledger().entries()}
    ok = listed_up and parent and child and alive(parent) and alive(child) and parent in listed and child in listed \
        and listed[parent].get("run") == "a run that crashed (START-003)"
    return ok, (listed_up, parent, child, alive(parent), alive(child), listed)


row("START-003", "the list outlives a crashed run: the run is stopped hard, what it started keeps running — and stays on "
    "the list", r003)


def r004():
    parent, child, port, run_pid = state["s003"]
    review = starter.Ledger().review()
    banner = starter.banner(review)
    text = "\n".join(banner)
    left = {e["pid"] for e in review["leftovers"]}
    # through the runner: the banner comes at the START of the next run, before any file's result
    ok_py = write("test_ok_sample.py", "# tags: starter, tier 1\n# covers: nothing.js\nprint('1 passed, 0 failed')\n")
    code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(ok_py)])
    first_result = out.find("✓")
    said = out.find(f"taskkill /PID {parent} /F")
    cli = subprocess.run([sys.executable, os.path.join(TOOLS, "starter.py")], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    ok = {parent, child} <= left and f"taskkill /PID {parent} /F" in text and f"taskkill /PID {child} /F" in text \
        and "a stand-in web server for a run that crashes (START-003)" in text and "a run that crashed (START-003)" in text \
        and any(ln.startswith("NEEDS YOUR ATTENTION:") for ln in banner) and alive(parent) and alive(child) \
        and code == 0 and 0 <= said < first_result and "NEEDS YOUR ATTENTION:" in out \
        and f"taskkill /PID {parent} /F" in cli.stdout and "NEEDS YOUR ATTENTION:" in cli.stdout
    return ok, (left, text, code, out[-1500:], cli.stdout[-600:])


row("START-004", "the START of the next run shows a banner naming each leftover — what it is, which run started it, and "
    "the exact command to stop it — plus a 'NEEDS YOUR ATTENTION:' line; the banner stops nothing; the runner prints it "
    "before any result, and `py tools/starter.py` shows the same", r004)


def r005():
    parent, child, port, run_pid = state["s003"]
    for pid in (child, parent):       # Ron's part, done here: the banner's commands, by exact id
        starter.stop_one(pid)
    gone = until(lambda: not alive(parent) and not alive(child), 10)
    review = starter.Ledger().review()
    listed = {e["pid"] for e in starter.Ledger().entries()}
    ok = gone and not review["leftovers"] and parent not in listed and child not in listed \
        and starter.banner(review) == []
    return ok, (gone, review, listed)


row("START-005", "a leftover stopped by its id leaves the list at the next look (confirmed gone) — and the banner is "
    "empty again", r005)


def r006():
    """An id Windows gave to ANOTHER process after ours ended: the list's start time differs — so it isn't ours. It is
    never stopped and never offered as a leftover; holding the port our process had, it is REPORTED (something on our
    port the list doesn't name) — and the old entry leaves the list (ours is confirmed gone)."""
    port, note = free_port(), os.path.join(D, "s006")
    other = subprocess.Popen(stand_in("serve", port, note), stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    mine.add(other.pid)
    up = until(lambda: os.path.exists(note + ".serving"))
    t = starter.started_at(other.pid)
    _, _, _, dead_run = state["s003"]
    planted = {"pid": other.pid, "start": t - 10_000_000, "name": "python.exe", "what": "an old stand-in (START-006)",
               "run": "a run long ended (START-006)", "owner": {"pid": dead_run, "start": 1}, "ports": [port],
               "since": "2026-11-18 00:00:00"}
    starter.Ledger().add([planted])
    review = starter.Ledger().review()
    text = "\n".join(starter.banner(review))
    still = alive(other.pid)
    listed = [e for e in starter.Ledger().entries() if e["pid"] == other.pid]
    named = [u for u in review["unnamed"] if u["pid"] == other.pid]
    ok = up and still and not any(e["pid"] == other.pid for e in review["leftovers"]) and named \
        and named[0].get("port") == port and not listed and f"process {other.pid}" in text \
        and "never stopped" in text
    other.kill()
    other.wait(10)
    return ok, (up, still, review, listed, text)


row("START-006", "a reused id (same id, another start time) is not ours: never stopped, never offered as a leftover — "
    "found on our port, it is reported as not provably ours; the old entry leaves the list", r006)

WORKER = write("worker.py", f'''import os, sys, time
sys.path.insert(0, {TOOLS!r})
import starter
me, go, done, end = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
while not os.path.exists(go):
    time.sleep(0.01)
t = starter.started_at(os.getpid())
for i in range(15):
    starter.Ledger().add([{{"pid": os.getpid(), "start": t, "name": "python.exe", "what": f"{{me}}-{{i}}",
                          "run": "START-007 " + me, "owner": {{"pid": os.getpid(), "start": t}}, "ports": [],
                          "since": "now"}}])
    starter.Ledger().review()          # a run's look at the list, at the same time: it tidies, and must lose nothing
open(done, "w").close()
while not os.path.exists(end):
    time.sleep(0.05)
''')


def r007():
    go, end = os.path.join(D, "go7"), os.path.join(D, "end7")
    procs = [subprocess.Popen([sys.executable, WORKER, f"w{n}", go, os.path.join(D, f"done7-{n}"), end],
                              stdin=DEVNULL, stdout=DEVNULL, stderr=subprocess.PIPE) for n in range(6)]
    mine.update(p.pid for p in procs)
    open(go, "w").close()
    finished = until(lambda: all(os.path.exists(os.path.join(D, f"done7-{n}")) for n in range(6)), 120)
    whats = sorted(e["what"] for e in starter.Ledger().entries() if str(e.get("run", "")).startswith("START-007"))
    open(end, "w").close()
    errs = [p.communicate(timeout=30)[1].decode("utf-8", "replace")[-300:] for p in procs]
    want = sorted(f"w{n}-{i}" for n in range(6) for i in range(15))
    starter.Ledger().review()          # the workers are gone: their entries leave the list
    return finished and whats == want, (finished, len(whats), [e for e in errs if e])


row("START-007", "two runs at once (here six): each adds to the list while others add and tidy — under the slots' own "
    "file lock, nothing is lost (90 of 90 entries)", r007)


def r008():
    """At a stop, something on our port that the list doesn't name: reported, with the command to stop it if it's a
    leftover — never stopped; kept for the next run's start banner, once."""
    port, note = free_port(), os.path.join(D, "s008")
    squatter = subprocess.Popen(stand_in("serve", port, note), stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    mine.add(squatter.pid)
    up = until(lambda: os.path.exists(note + ".serving"))
    s = starter.Started("a stand-in that doesn't listen (START-008)", ports=[port])
    s.start(stand_in("sleep", 0, note), stdin=DEVNULL, stdout=DEVNULL, stderr=DEVNULL)
    mine.add(s.proc.pid)
    left = s.stop(stop_s=1)
    still = alive(squatter.pid)
    first = starter.banner(starter.Ledger().review())
    second = starter.banner(starter.Ledger().review())
    squatter.kill()
    squatter.wait(10)
    text = "\n".join(left)
    ok = up and still and f"process {squatter.pid}" in text and f"taskkill /PID {squatter.pid} /F" in text \
        and "left running" in text and any(f"process {squatter.pid}" in ln for ln in first) \
        and not any(f"process {squatter.pid}" in ln for ln in second)
    return ok, (up, still, left, first, second)


row("START-008", "at a stop, a process on our port that the list doesn't name is reported with its stop command and left "
    "running (not provably ours); the next run's start banner names it once more", r008)

# ---------------------------------------------------------------------------------------------------------------------
# 4. A test unit's leftovers: still running when the unit's own process ended — in its job, so provably its own
# ---------------------------------------------------------------------------------------------------------------------
LEAVER = write("leaver.py", r'''import subprocess, sys
how, note = sys.argv[1], sys.argv[2]
quiet = dict(stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if how != "pipe" else {}
secs = "1" if how == "brief" else "600"
c = subprocess.Popen([sys.executable, "-c", f"import time; time.sleep({secs})"], **quiet)
open(note, "w").write(str(c.pid))
print("left a child", flush=True)
''')


def r009():
    if os.name != "nt":
        return True, "not Windows — no job"
    saved = getattr(tc, "LEFTOVER_GRACE_S", None)
    tc.LEFTOVER_GRACE_S = 2.0
    out = {}
    try:
        for how in ("quiet", "pipe", "brief"):
            note = os.path.join(D, f"leaver-{how}")
            t0 = time.monotonic()
            code, so, _, m = tc.run([sys.executable, LEAVER, how, note], timeout=120)
            pid = int(read(note) or 0)
            mine.add(pid)
            out[how] = (code, round(time.monotonic() - t0, 1), pid, (m or {}).get("leftovers"),
                        until(lambda: not alive(pid), 10))
    finally:
        tc.LEFTOVER_GRACE_S = saved
    ok = True
    for how in ("quiet", "pipe"):
        code, secs, pid, left, gone = out[how]
        ok = ok and code == 0 and secs < 60 and gone and left and [x["pid"] for x in left] == [pid] \
            and left[0].get("name", "").lower().startswith("python") and left[0].get("stopped") is True
    code, secs, pid, left, gone = out["brief"]
    return ok and code == 0 and left == [] and gone, out


row("START-009", "a test unit whose own process ended while a process it started still runs: named (id, name) and "
    "stopped by its job's handle, checked gone — also when that process holds the unit's output pipe (no wait for the "
    "time limit); one that ends within the grace is no leftover", r009)


def r010():
    if os.name != "nt":
        return True, "not Windows — no job"
    note = os.path.join(D, "leaver-runner")
    sample = write("test_leaves_child.py", "# tags: starter, tier 1\n# covers: nothing.js\n"
                   f"import subprocess, sys\nsubprocess.run([sys.executable, {LEAVER!r}, 'quiet', {note!r}])\n"
                   "print('1 passed, 0 failed')\n")
    saved = getattr(tc, "LEFTOVER_GRACE_S", None)
    tc.LEFTOVER_GRACE_S = 2.0
    try:
        code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(sample)], results=os.path.join(D, "rec10"),
                               costs=os.path.join(D, "costs10.json"))
    finally:
        tc.LEFTOVER_GRACE_S = saved
    pid = int(read(note) or 0)
    mine.add(pid)
    gone = until(lambda: not alive(pid), 10)
    tail = out[out.find("Tests:"):] if "Tests:" in out else ""
    ok = code == 0 and gone and f"process {pid}" in tail and "test_leaves_child.py" in tail \
        and "stopped by its job" in tail and "NEEDS YOUR ATTENTION:" in tail
    return ok, (code, pid, gone, out[-1500:])


row("START-010", "through the runner: a file that leaves a process running is named loudly at the run's end — the file, "
    "the process (id, name), 'stopped by its job' — with a 'NEEDS YOUR ATTENTION:' line; the process is gone", r010)


def r011():
    """The end of the run that left them: a run with no record (so no job) whose sample file starts a stand-in through
    the starter and never stops it — the run's end names it, with its stop command."""
    note = os.path.join(D, "forgot")
    sample = write("test_forgets.py", "# tags: starter, tier 1\n# covers: nothing.js\n"
                   f"import subprocess, sys\nsys.path.insert(0, {TOOLS!r})\nimport starter\n"
                   "s = starter.Started('a stand-in its test forgot to stop (START-011)')\n"
                   f"s.start([sys.executable, {STANDIN!r}, 'sleep', '0', {note!r}], stdin=subprocess.DEVNULL, "
                   "stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n"
                   f"open({note!r}, 'w').write(str(s.proc.pid))\nprint('1 passed, 0 failed')\n")
    code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(sample)])
    pid = int(read(note) or 0)
    mine.add(pid)
    tail = out[out.find("Tests:"):] if "Tests:" in out else ""
    still = alive(pid)
    ok = still and f"taskkill /PID {pid} /F" in tail and "a stand-in its test forgot to stop (START-011)" in tail \
        and "NEEDS YOUR ATTENTION:" in tail
    if pid:
        starter.stop_one(pid)
    return ok, (code, pid, still, out[-1500:])


row("START-011", "the END of the run that left them: a process its file started through the starter and never stopped "
    "is named at the run's end — what it is, the exact command to stop it — with a 'NEEDS YOUR ATTENTION:' line", r011)

# ---------------------------------------------------------------------------------------------------------------------
# 5. The relay tests' local relay: measured too, and listed while it runs
# ---------------------------------------------------------------------------------------------------------------------


def r012():
    if os.name != "nt":
        return True, "not Windows — no job"
    note = os.path.join(D, "relay12")
    seen = os.path.join(D, "seen12.json")
    relay_py = write("test-relay-measured.py", "# tags: relay, tier 3\n# covers: relay/relay-worker.js\n"
                     "import json, os, urllib.request\n"
                     "listed = json.load(open(os.path.join(os.environ['RW_TEST_SLOTS_DIR'], 'started-processes.json')))\n"
                     f"json.dump({{'listed': listed, 'run': os.environ.get('RW_RUN_ID')}}, open({seen!r}, 'w'))\n"
                     "print('answer:', urllib.request.urlopen(os.environ['RELAY_URL'], timeout=10).read().decode())\n"
                     "print('1 passed, 0 failed')\n")
    lr = rt.local_relay
    relay = lambda: lr.LocalRelay(command=stand_in("relay", "{port}", note), cwd=D, start_s=60, stop_s=5)  # noqa: E731
    rdir, costs = os.path.join(D, "rec12"), os.path.join(D, "costs12.json")
    code, out = quiet_main(["--tier", "3"], files=[rt.TestFile(relay_py)], relay=relay, results=rdir, costs=costs)
    recs = [json.load(open(os.path.join(rdir, p), encoding="utf-8")) for p in sorted(os.listdir(rdir))
            if p.endswith(".json")] if os.path.isdir(rdir) else []
    r = (recs or [{}])[-1].get("relay") or {}
    m = r.get("measures") or {}
    got = json.load(open(seen, encoding="utf-8")) if os.path.exists(seen) else {}
    relay_listed = [e for e in (got.get("listed") or {}).get("processes", []) if "local relay" in e.get("what", "")]
    saved = json.load(open(costs, encoding="utf-8")) if os.path.exists(costs) else {}
    unit = ((saved.get("files") or {}).get("tools/local_relay.py") or {}).get("units") or {}
    left = [e for e in starter.Ledger().entries() if "local relay" in e.get("what", "")]
    ok = code == 0 and isinstance(m.get("cpu_seconds"), (int, float)) and (m.get("processes") or 0) >= 2 \
        and isinstance(r.get("seconds"), (int, float)) and len(relay_listed) >= 2 \
        and all(e.get("run") == got.get("run") and got.get("run") for e in relay_listed) \
        and (unit.get("the relay for tier 3") or {}).get("count") == 1 and not left and "local relay" in out
    return ok, (code, r, relay_listed, unit, left, out[-1200:])


row("START-012", "the relay tests' local relay runs in a job of its own: what it cost (CPU, memory, processes, time) is in "
    "the run's record and teaches this PC's averages (tools/local_relay.py, 'the relay for tier 3'); while it runs its "
    "processes are on the list under the run that started it; afterwards none is", r012)

# ---------------------------------------------------------------------------------------------------------------------
# 1. One starter: the screen tests' web server and both relays start through it
# ---------------------------------------------------------------------------------------------------------------------


def r013():
    rw_src = open(os.path.join(ROOT, "test", "ui", "rw.py"), encoding="utf-8").read()
    lr_src = open(os.path.join(TOOLS, "local_relay.py"), encoding="utf-8").read()
    ok = "starter.Started(" in rw_src and "subprocess.Popen" not in rw_src and ".terminate()" not in rw_src \
        and "starter.Started(" in lr_src and "subprocess.Popen" not in lr_src and '["taskkill"' not in lr_src \
        and "local_relay.LocalRelay(" in rw_src
    return ok, {"rw.py Started": "starter.Started(" in rw_src, "rw.py Popen": "subprocess.Popen" in rw_src,
                "local_relay Started": "starter.Started(" in lr_src, "local_relay Popen": "subprocess.Popen" in lr_src}


row("START-013", "one starter (Law 22): the screen tests' web server (rw.App) and the local relay (local_relay.py) start "
    "through tools/starter.py — neither starts or stops a process of its own any more", r013)

# --- what this file started, stopped by exact id if still running (a failed row may have left one) ---
if starter is not None:
    mine.stop_left()

failed = [r for r in results if not r[1]]
print(f"{len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
