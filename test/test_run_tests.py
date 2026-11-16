# Tests for tools/run_tests.py — the one test runner (docs/design/TESTING.md §4).
# tags: test-runner, tier 1
# covers: tools/run_tests.py, tools/local_relay.py, test/harness.js, test/ui/rw.py
# Run: python test/test_run_tests.py
#
# Sample test files are written to a temporary folder; each row checks one thing the runner must do.
import contextlib
import importlib.util
import io
import os
import socket
import subprocess
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # print ✓ even when piped (2026-11-12; as harness.py)
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("run_tests", os.path.join(ROOT, "tools", "run_tests.py"))
rt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rt)

HARNESS = os.path.join(ROOT, "test", "harness.js").replace("\\", "/")
results = []


def row(tid, name, ok, detail=""):
    results.append((tid, name, ok, detail))
    print(f"  {'✓' if ok else '✗'} {tid} {name}" + ("" if ok else f" — {detail}"))


with tempfile.TemporaryDirectory() as d:
    def write(name, text):
        p = os.path.join(d, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    js_ok = write("a.test.js", f"""// sample
// tags: merge, import, tier 1
// covers: bookMerge.js, storage.js
const {{ test, done }} = require('{HARNESS}');
test('SAMPLE-001', 'passes', () => {{}});
done();
""")
    js_bad = write("b.test.js", f"""// sample
// tags: dates, tier 1
// covers: uiHelpers.js
const {{ test, done }} = require('{HARNESS}');
test('SAMPLE-002', 'fails', () => {{ throw new Error('boom'); }});
test('SAMPLE-003', 'still runs after a failure', () => {{}});
done();
""")
    py_ok = write("test_c.py", """# sample
# tags: commit-checks, tier 1
# covers: git-hooks/check-parse.py
print("1 passed, 0 failed")
""")
    no_header = write("d.test.js", "// no header at all\nconsole.log('hi');\n")
    ui = write("test_e.py", "# sample\n# tags: delete-key, tier 2\n# covers: readerwrangler.js\n")

    h = rt.read_header(js_ok)
    row("RUN-001", "reads tags, tier and covers from a // header",
        h["tags"] == ["merge", "import"] and h["tier"] == 1 and h["covers"] == ["bookMerge.js", "storage.js"], str(h))
    h = rt.read_header(py_ok)
    row("RUN-002", "reads a # header (Python files)",
        h["tags"] == ["commit-checks"] and h["tier"] == 1 and h["covers"] == ["git-hooks/check-parse.py"], str(h))
    h = rt.read_header(no_header)
    row("RUN-003", "a file with no header is reported as missing one (headers are required)",
        h["problem"] is not None, str(h))

    files = [rt.TestFile(p) for p in (js_ok, js_bad, py_ok, ui)]
    def pick(**kw):
        return sorted(os.path.basename(f.path) for f in rt.select(files, **kw))
    row("RUN-004", "--changed picks the tests that cover a changed file",
        pick(changed=["bookMerge.js"]) == ["a.test.js"], str(pick(changed=["bookMerge.js"])))
    row("RUN-005", "--changed picks nothing for a file no test covers",
        pick(changed=["readme.txt"]) == [], str(pick(changed=["readme.txt"])))
    own = [os.path.relpath(js_bad, d)]
    row("RUN-006", "--changed picks a test file that itself changed",
        pick(changed=own, base=d) == ["b.test.js"], str(pick(changed=own, base=d)))
    row("RUN-007", "--tag picks by area", pick(tags=["dates"]) == ["b.test.js"], str(pick(tags=["dates"])))
    row("RUN-008", "--tier 1 leaves out tier 2", pick(tier=1) == ["a.test.js", "b.test.js", "test_c.py"], str(pick(tier=1)))
    row("RUN-009", "--tier all keeps every tier", pick(tier="all") == ["a.test.js", "b.test.js", "test_c.py", "test_e.py"],
        str(pick(tier="all")))

    ok, out = rt.run_file(rt.TestFile(js_ok))
    row("RUN-010", "a passing JS file reports success", ok and "1 passed, 0 failed" in out, out[-200:])
    ok, out = rt.run_file(rt.TestFile(js_bad))
    row("RUN-011", "a failing JS file reports failure", not ok and "SAMPLE-002" in out, out[-200:])
    row("RUN-012", "a failure doesn't stop the file — the next test still ran", "SAMPLE-003" in out, out[-200:])
    ok, out = rt.run_file(rt.TestFile(py_ok))
    row("RUN-013", "a passing Python file reports success", ok, out[-200:])

    # 7.29.1 (TODO 20261112-1755): the copy routine answers later (a promise), so a test may return one — the harness waits
    # for it. Before, a test's promise was ignored: it "passed" at once, and its later failure never reached the count.
    js_async = write("g.test.js", f"""// sample
// tags: dates, tier 1
// covers: uiHelpers.js
const {{ test, done }} = require('{HARNESS}');
test('SAMPLE-004', 'passes later', () => new Promise(r => setTimeout(r, 20)));
test('SAMPLE-005', 'fails later', () => new Promise((_, no) => setTimeout(() => no(new Error('late boom')), 20)));
test('SAMPLE-006', 'a plain test after them', () => {{}});
done();
""")
    ok, out = rt.run_file(rt.TestFile(js_async))
    row("RUN-030", "a test that returns a promise is waited for: its later failure is counted (2 passed, 1 failed)",
        not ok and "late boom" in out and "2 passed, 1 failed" in out, out[-300:])
    lines = [ln for ln in out.strip().splitlines() if ln.strip()]
    row("RUN-031", "the summary is the last line — printed after every test has finished",
        bool(lines) and lines[-1].strip() == "2 passed, 1 failed", out[-300:])
    js_hang = write("h.test.js", f"""// sample
// tags: dates, tier 1
// covers: uiHelpers.js
const {{ test, done }} = require('{HARNESS}');
test('SAMPLE-007', 'never finishes', () => new Promise(() => {{}}));
done();
""")
    ok, out = rt.run_file(rt.TestFile(js_hang))
    row("RUN-032", "a test whose promise never settles fails the file, by name — never a pass by not finishing",
        not ok and "SAMPLE-007" in out, out[-300:])

    ui_py = write("test_f.py", "# sample\n# tags: screen, tier 2\n# covers: readerwrangler.js\n"
                               "import sys\nprint('ran with', sys.executable)\n")
    ok, out = rt.run_file(rt.TestFile(ui_py))
    row("RUN-014", "a screen test (tier 2) runs with the project's venv Python",
        ok and ".venv" in out.replace("\\", "/"), out[-200:])
    saved, rt.VENV_PY = rt.VENV_PY, os.path.join(d, "no-such-venv", "python.exe")
    ok, out = rt.run_file(rt.TestFile(ui_py))
    rt.VENV_PY = saved
    row("RUN-015", "no venv → the screen test fails loud with the setup command (never skipped quietly)",
        not ok and "py -m venv .venv" in out, out[-200:])

    # --- Tier 3: the runner starts and stops its own local relay (TODO "Turn more of our working rules into automatic
    # checks", item 3; 7.28.0 post-mortem: stopping a relay by hand left four processes serving its port). No real
    # wrangler here (tier 1): a stand-in "relay" — a Python script that starts a CHILD which serves the port (as wrangler's
    # workerd does), then prints wrangler's ready line. Every process it starts writes "<role> <id>" to a list, so the
    # test can check each one is gone afterwards — by its own look (tasklist), not the runner's.
    standin = write("standin_relay.py", r'''import http.server, os, socket, subprocess, sys, time
mode, port, pids = sys.argv[1], int(sys.argv[2]), sys.argv[3]
def note(role):
    with open(pids, "a") as f:
        f.write(f"{role} {os.getpid()}\n")
def me(m):
    return [sys.executable, __file__, m, str(port), pids]
def child(m):
    return subprocess.Popen(me(m), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
def wait_served():
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", port), 0.2).close()
            return
        except OSError:
            time.sleep(0.1)
    sys.exit("the stand-in's server never came up")
if mode in ("serve", "serve-strict"):
    note("server")
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"stand-in relay")
        def log_message(self, *a):
            pass
    class Strict(http.server.HTTPServer):
        allow_reuse_address = False   # a taken port is refused, as wrangler's runtime refuses it
    srv = (Strict if mode == "serve-strict" else http.server.HTTPServer)(("127.0.0.1", port), H)
    open(pids + ".bound-" + str(os.getpid()), "w").close()
    srv.serve_forever()
elif mode == "strict":                # like wrangler on a taken port: its server can't start, so it stops, never ready
    note("relay")
    srv = child("serve-strict")
    while not os.path.exists(pids + ".bound-" + str(srv.pid)):
        if srv.poll() is not None:
            sys.exit("the stand-in's server couldn't take the port — stopping, as wrangler does")
        time.sleep(0.05)
    print(f"[wrangler:info] Ready on http://127.0.0.1:{port}", flush=True)
    time.sleep(600)
elif mode == "middle":
    note("middle")
    child("serve")
    wait_served()                     # then exit: the server is left with no parent — it has escaped the tree
else:
    note("relay")
    if mode == "orphan":
        subprocess.run(me("middle"), stdin=subprocess.DEVNULL)
    else:
        child("serve")
    wait_served()
    if mode != "never":
        print(f"[wrangler:info] Ready on http://127.0.0.1:{port}", flush=True)
    time.sleep(600)
''')
    relay_test = write("test-relay-sample.py", "# sample\n# tags: relay, tier 3\n# covers: relay/relay-worker.js\n"
                       "import os, sys, urllib.request\nurl = os.environ.get('RELAY_URL', '')\n"
                       f"open({os.path.join(d, 'seen-url.txt')!r}, 'w').write(url)\n"
                       "print('answer:', urllib.request.urlopen(url, timeout=5).read().decode())\n")
    lr = rt.local_relay      # the runner's own copy (tools/local_relay.py), so its errors are the ones it catches

    def running():
        """The ids running now — the whole process list, read raw (not the runner's stop-and-check code). It must hold
        this test's own id, or the list is broken and "nothing left running" would prove nothing (setup check)."""
        now = set(lr.processes())
        if os.getpid() not in now:
            raise AssertionError(f"the process list doesn't show this test's own id {os.getpid()} — can't check")
        return now

    def run_main(argv, mode=None, start_s=20):
        """main() on the sample tier-3 file, with the stand-in relay in `mode`. (exit code, printed text, {role: id})"""
        pids = os.path.join(d, f"pids-{mode}.txt")
        for p in (pids, os.path.join(d, "seen-url.txt")):
            if os.path.exists(p):
                os.remove(p)
        relay = (lambda: lr.LocalRelay(command=[sys.executable, standin, mode, "{port}", pids], cwd=d, start_s=start_s,
                                       stop_s=1)) if mode else None
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = rt.main(argv, files=[rt.TestFile(relay_test)], relay=relay)
        started = {}
        if os.path.exists(pids):
            for ln in open(pids).read().split("\n"):
                if ln.strip():
                    role, pid = ln.split()
                    started[role] = int(pid)
        seen = open(os.path.join(d, "seen-url.txt")).read() if os.path.exists(os.path.join(d, "seen-url.txt")) else None
        return code, buf.getvalue(), started, seen

    code, out, started, seen = run_main(["--tier", "3"], mode="ok")
    row("RUN-016", "with no --relay-url, tier 3 runs against a local relay the runner started — the file gets its "
        "address and the relay answers there",
        code == 0 and seen is not None and seen.startswith("http://127.0.0.1:") and "relay" in started
        and "server" in started,     # the sample file passes only when the address it was given answered
        f"exit {code}, url seen {seen!r}, started {started}: {out[-400:]}")
    port = int(seen.rsplit(":", 1)[1]) if seen and seen.startswith("http://127.0.0.1:") else None
    with socket.socket() as s:
        s.settimeout(0.5)
        port_free = port is not None and s.connect_ex(("127.0.0.1", port)) != 0
    now = running()
    left = [f"{role} {pid}" for role, pid in started.items() if pid in now]
    row("RUN-017", "afterwards every process the relay started is gone — the relay AND its child — and the port is free",
        set(started) == {"relay", "server"} and not left and port_free,
        f"started {started}; still running {left}; port {port} free: {port_free}")

    code, out, started, _ = run_main(["--tier", "3"], mode="never", start_s=1.5)
    now = running()
    left = [f"{role} {pid}" for role, pid in started.items() if pid in now]
    row("RUN-018", "a relay that never says it's ready fails the run loud — and what it started is stopped",
        code == 1 and "didn't say it was ready within 1.5 s" in out and set(started) == {"relay", "server"} and not left,
        f"exit {code}, started {started}, still running {left}: {out[-400:]}")

    code, out, started, _ = run_main(["--tier", "3"], mode="orphan")
    escaped = started.get("server")
    now = running()
    row("RUN-019", "a child that escaped the tree and still serves the port fails the run, named by its id — and the "
        "runner leaves it running (not provably its own)",
        code == 1 and escaped is not None and f"process {escaped}" in out and "left running" in out
        and escaped in now       # (since 2026-11-16 caught at the start — not alone on its port — rather than at the stop)
        and open(os.path.join(d, "pids-orphan.txt")).read().count("relay ") == 1,   # …and never tried again

        f"exit {code}, started {started}: {out[-600:]}")
    for pid in started.values():      # the test's own cleanup — by exact id, processes this test started
        if pid in now:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)   # one process each — never /T

    def no_relay():
        raise AssertionError("a relay was started although --relay-url named one")
    if os.path.exists(os.path.join(d, "seen-url.txt")):
        os.remove(os.path.join(d, "seen-url.txt"))      # never read the previous test's address
    given_port = lr.free_port()
    given = f"http://127.0.0.1:{given_port}"
    srv = subprocess.Popen([sys.executable, standin, "serve", str(given_port), os.path.join(d, "pids-given.txt")],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", given_port), 0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code = rt.main(["--tier", "3", "--relay-url", given], files=[rt.TestFile(relay_test)], relay=no_relay)
        except AssertionError as e:
            code = str(e)
        seen = open(os.path.join(d, "seen-url.txt")).read() if os.path.exists(os.path.join(d, "seen-url.txt")) else None
        row("RUN-020", "--relay-url given → no relay is started, and the file gets that address (as before)",
            code == 0 and seen == given, f"exit {code}, url seen {seen!r}, given {given}: {buf.getvalue()[-300:]}")
    finally:
        srv.kill()      # the one process this test started (no children here)
        srv.wait(10)

    a = lr.WRANGLER_ARGS
    row("RUN-021", "the real relay is wrangler's LOCAL emulator on 127.0.0.1 — never the dev or production relay",
        "--local" in a and a[a.index("--ip") + 1] == "127.0.0.1" and "--remote" not in a and "{port}" in a, str(a))

    # --- "Ready" is proven against the relay's OWN process (2026-11-16, TODO "Faster sprints"): the free port is chosen,
    # then taken a moment later — and with screen tests in parallel, another run's relay can take it in between. The
    # screen tests' old relay took ANY answer on the port as "up" (the same race as the app server's — rw.py
    # App._server_is_ours). Here this test squats the first port the relay is given (this process listens there).
    def all_started(pids_file):
        """Every id the stand-in wrote — all tries — as [(role, id)]."""
        return ([tuple(ln.split()) for ln in open(pids_file).read().splitlines() if ln.strip()]
                if os.path.exists(pids_file) else [])

    def squatted_relay(mode, name):
        """Start the stand-in relay in `mode` with its FIRST port already taken by this process; (url or error, its
        LocalRelay, what served the url, the answer there, what stop() left, every (role, id) it started, the port)."""
        squat = socket.socket()
        squat.bind(("127.0.0.1", 0))
        squat.listen(16)
        squatted = squat.getsockname()[1]
        real_free_port, handed = lr.free_port, []

        def squatted_first():
            handed.append(1)
            return squatted if len(handed) == 1 else real_free_port()
        pids = os.path.join(d, f"pids-{name}.txt")
        url, served, answer, left, relay = None, set(), None, ["(not stopped)"], None
        lr.free_port = squatted_first
        try:
            relay = lr.LocalRelay(command=[sys.executable, standin, mode, "{port}", pids], cwd=d, start_s=20,
                                  stop_s=1, extra_args=["--var", "ALLOWED_ORIGINS:http://localhost:1"])
            url = relay.start()
            served = lr.port_owners(int(url.rsplit(":", 1)[1]))
            import urllib.request
            answer = urllib.request.urlopen(url, timeout=5).read()
        except Exception as e:      # noqa: BLE001 — a refusal (or, before the build, a TypeError): reported in the row
            url = f"{type(e).__name__}: {e}"
        finally:
            lr.free_port = real_free_port
            if relay is not None:
                left = relay.stop()
            still_squatting = os.getpid() in lr.port_owners(squatted)
            squat.close()
        return url, relay, served, answer, left, all_started(pids), squatted, still_squatting

    url, relay, served, answer, left, started, squatted, untouched = squatted_relay("ok", "squat")
    now = running()
    ours_left = [f"{role} {pid}" for role, pid in started if int(pid) in now]
    row("RUN-052", "the local relay's ready line isn't taken on trust: it printed 'Ready' on its port while another "
        "process (here: this test, older than the relay — so proven not one of its own) listened there → not accepted; "
        "that process left alone; started again on new ports — the address it gives is served by processes it started "
        "and nothing else; nothing it started is left running",
        url.startswith("http://127.0.0.1:") and not url.endswith(f":{squatted}") and served and relay is not None
        and served <= set(relay.ours) and answer == b"stand-in relay" and not left
        and sum(1 for r, _ in started if r == "relay") == 2 and not ours_left and untouched,
        f"url {url[:400]}, served by {served}, ours {sorted(relay.ours) if relay else None}, answer {answer!r}, left "
        f"{left}, started {started}, still running {ours_left}, squatter untouched {untouched}")
    url, relay2, served, answer, left, started, squatted, _ = squatted_relay("strict", "strict")
    now = running()
    ours_left = [f"{role} {pid}" for role, pid in started if int(pid) in now]
    row("RUN-057", "a relay that stops before it's ready (wrangler on a taken port: 'The Workers runtime failed to start') "
        "is started again on new ports — the address it gives is served by processes it started and nothing else; "
        "every try's processes are gone afterwards",
        url.startswith("http://127.0.0.1:") and not url.endswith(f":{squatted}") and served and relay2 is not None
        and served <= set(relay2.ours) and answer == b"stand-in relay" and not left
        and sum(1 for r, _ in started if r == "relay") == 2 and not ours_left,
        f"url {url[:300]}, served by {served}, ours {sorted(relay2.ours) if relay2 else None}, answer {answer!r}, "
        f"left {left}, started {started}, still running {ours_left}")
    rw_src = open(os.path.join(ROOT, "test", "ui", "rw.py"), encoding="utf-8").read()
    row("RUN-053", "one relay launcher (Law 22): extra arguments reach the relay after its own (the screen tests' "
        "ALLOWED_ORIGINS), and the screen tests start theirs through tools/local_relay.py — rw.py has no copy of its own "
        "(no relay class, no taskkill)",
        relay is not None and getattr(relay, "args", [])[-2:] == ["--var", "ALLOWED_ORIGINS:http://localhost:1"]
        and "class LocalRelay" not in rw_src and "taskkill" not in rw_src and "local_relay.LocalRelay(" in rw_src,
        f"args {getattr(relay, 'args', None)}; rw.py has a relay class: {'class LocalRelay' in rw_src}, taskkill: "
        f"{'taskkill' in rw_src}")

    # --- A release run counts "skipped" as failed (TODO "Turn more of our working rules…", item 4; 7.28.0 post-mortem:
    # "31 passed, 2 skipped" read as a pass). Nothing skips today, so the test plants a reason through the runner's one
    # place that decides a skip (skip_reason) — keeping the original to put back.
    def run_with_skip(argv):
        saved = getattr(rt, "skip_reason", None)
        rt.skip_reason = lambda f: "SAMPLE-SKIP: the sample says it can't run here" if f.path == py_ok else None
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code = rt.main(argv, files=[rt.TestFile(js_ok), rt.TestFile(py_ok)])
        except SystemExit as e:          # an unknown flag: argparse exits
            code = f"SystemExit {e.code}"
        finally:
            if saved is None:
                del rt.skip_reason
            else:
                rt.skip_reason = saved
        return code, buf.getvalue()

    code, out = run_with_skip(["--tier", "1", "--release"])
    row("RUN-022", "--release: a skipped file fails the run, naming the file and why",
        code == 1 and "test_c.py" in out and "SAMPLE-SKIP: the sample says it can't run here" in out
        and "a.test.js" in out, f"exit {code}: {out[-400:]}")
    code, out = run_with_skip(["--tier", "1"])
    row("RUN-023", "without --release a skip is reported as skipped and the run still passes (as before)",
        code == 0 and "1 skipped" in out and "test_c.py: skipped" in out, f"exit {code}: {out[-400:]}")
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            code = rt.main(["--tier", "1", "--release"], files=[rt.TestFile(js_ok), rt.TestFile(py_ok)])
    except SystemExit as e:
        code = f"SystemExit {e.code}"
    row("RUN-024", "--release with nothing skipped passes (the flag isn't a blanket failure)",
        code == 0 and "2 file(s) passed" in buf.getvalue(), f"exit {code}: {buf.getvalue()[-300:]}")

    # --- With no --tier: --id and --tag look in EVERY tier (2026-11-12, sprint 2: a screen test's ID said "No tests
    # match" because the default tier 1 was applied first); --changed stays tier 1 (the commit hook's budget is seconds);
    # nothing at all stays tier 1 (the default).
    ui_id = write("test_g.py", "# sample\n# tags: screen-sample, tier 2\n# covers: readerwrangler.js\n"
                               "test(\"SCREENSAMPLE-001\", \"this file's test\", lambda: None)\n")   # named as a test (RUN-063)
    tier3 = write("test-h.mjs", "// sample\n// tags: screen-sample, tier 3\n// covers: relay/relay-worker.js\n")
    pool = [rt.TestFile(p) for p in (js_ok, py_ok, ui_id, tier3)]

    def listed(argv, changed=None):
        saved_changed = rt.changed_files
        if changed is not None:
            rt.changed_files = lambda: changed
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rt.main(argv + ["--list"], files=pool)
        finally:
            rt.changed_files = saved_changed
        return sorted(os.path.basename(ln.split()[2]) for ln in buf.getvalue().splitlines()
                      if ln.strip().startswith("tier "))

    got = listed(["--id", "SCREENSAMPLE-001"])
    row("RUN-025", "--id with no --tier finds a screen test's ID (it said \"No tests match\")",
        got == ["test_g.py"], str(got))
    got = listed(["--tag", "screen-sample"])
    row("RUN-026", "--tag with no --tier looks in every tier", got == ["test-h.mjs", "test_g.py"], str(got))
    got = listed(["--id", "SCREENSAMPLE-001", "--tier", "1"])
    row("RUN-027", "--id with --tier 1 still looks in tier 1 only", got == [], str(got))
    got = listed(["--changed"], changed=["readerwrangler.js", "bookMerge.js"])
    row("RUN-028", "--changed with no --tier stays tier 1 (the commit hook's budget is seconds)",
        got == ["a.test.js"], str(got))
    got = listed([])
    row("RUN-029", "no flags at all still means tier 1", got == ["a.test.js", "test_c.py"], str(got))

    # --- --release refuses while any test still "differs today" (7.30.0, sprint 4): a differs_today mark (test/ui/
    # harness.py) is a decided behavior not built yet — fine while building, never in a release. The sample uses the REAL
    # harness, so the runner reads the very lines a screen test prints.
    ui_harness = os.path.join(ROOT, "test", "ui").replace("\\", "/")
    differs = write("test_i.py", f"""# sample
# tags: cells-sample, tier 1
# covers: readerwrangler.js
import sys
sys.path.insert(0, r"{ui_harness}")
from harness import differs_today, done, test
test("SAMPLE-010", "built", lambda: None)
def today():
    raise AssertionError("today it says the old words")
differs_today("SAMPLE-011", "decided, not built yet", today, "the old words")
differs_today("SAMPLE-012", "decided, not built yet either", today, "the old words")
done()
""")

    def run_differs(argv):
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                code = rt.main(argv, files=[rt.TestFile(js_ok), rt.TestFile(differs)])
        except SystemExit as e:
            code = f"SystemExit {e.code}"
        return code, buf.getvalue()

    code, out = run_differs(["--tier", "1", "--release"])
    row("RUN-033", "--release: a test that still differs from what was decided fails the run, naming each test and its file",
        code == 1 and "SAMPLE-011" in out and "SAMPLE-012" in out and "test_i.py" in out and "SAMPLE-010" not in out.split("release run")[-1],
        f"exit {code}: {out[-500:]}")
    code, out = run_differs(["--tier", "1"])
    row("RUN-034", "without --release the same run passes (while building, a 'differs today' mark is expected)",
        code == 0 and "2 differ today" in out, f"exit {code}: {out[-400:]}")

    # --- Results stamped with their commit (TODO "Faster sprints", item 2; 2026-11-16): every --tier run leaves a
    # record — the commit, anything uncommitted, what ran, each file's result — and --stamp says PROVEN only for a commit
    # whose tier 1 AND tier 2 passed in full, nothing skipped, on a clean tree. At review that check replaces a rerun.
    # Made-up records first (the judging alone), then the runner writing and reading real ones.
    A, B = "a" * 40, "b" * 40

    def rec(commit=A, tier="all", files=None, dirty=(), after=None, tags=(), ids=(), ended="2026-11-16T10:00:00",
            env=None):
        files = files if files is not None else [
            {"file": "test/x.test.js", "tier": 1, "result": "passed", "counts": "3 passed, 0 failed"},
            {"file": "test/ui/test_y.py", "tier": 2, "result": "passed", "counts": "5 passed, 0 failed"}]
        ok = all(f["result"] == "passed" for f in files)
        return {"commit": commit, "commit_after": after or commit, "uncommitted": {"before": list(dirty), "after": []},
                "ran": {"tier": tier, "tags": list(tags), "ids": list(ids), "release": False, "jobs": 4},
                "files": files, "problems": [], "started": "2026-11-16T09:55:00", "ended": ended,
                "result": "passed" if ok else "failed", **({"env": env} if env is not None else {})}

    def judged(records, commit=A):
        try:
            proven, lines = rt.judge(records, commit)
            return proven, "\n".join(lines)
        except Exception as e:      # noqa: BLE001 — not built yet: the row fails, naming why
            return None, f"{type(e).__name__}: {e}"

    t1 = [{"file": "test/x.test.js", "tier": 1, "result": "passed", "counts": "3 passed, 0 failed"}]
    t2 = [{"file": "test/ui/test_y.py", "tier": 2, "result": "passed", "counts": "5 passed, 0 failed"}]
    p, why = judged([rec()])
    p2, why2 = judged([rec(tier="1", files=t1), rec(tier="2", files=t2)])
    row("RUN-035", "--stamp: tiers 1 and 2 passed in full on exactly this commit, tree clean → PROVEN (one 'all' run, "
        "or a tier 1 run and a tier 2 run)", p is True and p2 is True, f"{p}: {why} | {p2}: {why2}")
    p, why = judged([rec(dirty=["M readerwrangler.js"])])
    p2, why2 = judged([rec(after=B)])
    row("RUN-036", "--stamp: anything uncommitted while it ran → NOT PROVEN, naming it (and so is a commit made "
        "during the run)", p is False and "readerwrangler.js" in why and p2 is False, f"{p}: {why} | {p2}: {why2}")
    p, why = judged([rec(commit=B)])
    row("RUN-037", "--stamp: a run on another commit proves nothing for this one → NOT PROVEN",
        p is False and "tier 1" in why, f"{p}: {why}")
    p, why = judged([rec(tier="2", files=t2)])
    p2, why2 = judged([rec(tier="1", files=t1), rec(tier="2", files=t2, ids=["CELL-005"])])
    row("RUN-038", "--stamp: tier 2 alone → NOT PROVEN (tier 1 never ran); a run narrowed by --id / --tag doesn't count "
        "as its tier", p is False and "tier 1" in why and p2 is False and "tier 2" in why2, f"{p}: {why} | {p2}: {why2}")
    bad = [dict(t1[0]), {"file": "test/ui/test_y.py", "tier": 2, "result": "failed", "counts": "4 passed, 1 failed"}]
    p, why = judged([rec(files=bad)])
    p2, why2 = judged([rec(ended="2026-11-16T09:00:00"), rec(files=bad, ended="2026-11-16T11:00:00")])
    row("RUN-039", "--stamp: a failed file → NOT PROVEN, naming it — and a later failure on the same commit beats an "
        "earlier pass (a one-time failure is read, not rerun away)",
        p is False and "test_y.py" in why and p2 is False, f"{p}: {why} | {p2}: {why2}")
    sk = [dict(t1[0]), {"file": "test/ui/test_y.py", "tier": 2, "result": "skipped", "why": "no browser"}]
    p, why = judged([rec(files=sk)])
    row("RUN-040", "--stamp: a skipped file → NOT PROVEN, naming it", p is False and "test_y.py" in why, f"{p}: {why}")
    # A run with RW_CELLS set ran only some cells (2026-11-16): its record looked like a full run and the stamp said
    # PROVEN. The record notes the variables that change a run; a narrowing one makes it narrowed, like --id / --tag.
    p, why = judged([rec(env={"RW_CELLS": "CELL-005,CELL-019"})])
    p2, why2 = judged([rec(env={"RW_HEADED": "1", "RW_BROWSER": "msedge", "RW_TEST_SLOTS": "2"})])
    p3, why3 = judged([rec(), rec(env={"RW_CELLS": "CELL-005"}, ended="2026-11-16T11:00:00")])
    row("RUN-058", "--stamp: a run with RW_CELLS set (only some cells ran) doesn't count as its tier's full run → NOT "
        "PROVEN, naming the variable and its value; a run with only variables that don't narrow (RW_HEADED, RW_BROWSER, "
        "RW_TEST_SLOTS) is still PROVEN and shows them; a full run on the same commit still counts",
        p is False and "tier 2" in why and "RW_CELLS=CELL-005,CELL-019" in why
        and p2 is True and "RW_BROWSER=msedge" in why2 and p3 is True,
        f"{p}: {why} | {p2}: {why2} | {p3}: {why3}")

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    rdir = os.path.join(d, "results")
    os.makedirs(rdir)

    def records_in(folder):
        try:
            return rt.read_records(folder)
        except Exception as e:      # noqa: BLE001
            return f"{type(e).__name__}: {e}"

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

    code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(js_ok), rt.TestFile(js_bad)], results=rdir)
    got = records_in(rdir)
    r0 = got[0] if isinstance(got, list) and len(got) == 1 else {}
    res = {f.get("file", "").rsplit("/", 1)[-1]: f.get("result") for f in r0.get("files", [])}
    row("RUN-041", "a --tier run leaves one record: the commit it ran on, what was uncommitted, what ran, each file's "
        "result, start and end, the overall result",
        r0.get("commit") == head and isinstance(r0.get("uncommitted", {}).get("before"), list)
        and r0.get("ran", {}).get("tier") == "1" and res == {"a.test.js": "passed", "b.test.js": "failed"}
        and r0.get("result") == "failed" and r0.get("started") and r0.get("ended"),
        f"exit {code}; records: {str(got)[:500]}")
    # The same through the path a real run takes — files discovered, the record in this copy's folder (results_dir) —
    # with both swapped for the test (originals kept): the first build checked "were files given?" AFTER discovery had
    # filled them in, so a real run left no record while the sample runs above did.
    real_dir = os.path.join(d, "real-results")
    saved_discover, saved_results_dir = rt.discover, rt.results_dir
    rt.discover, rt.results_dir = (lambda root=None: [rt.TestFile(js_ok)]), (lambda root=None: real_dir)
    try:
        code, out = quiet_main(["--tier", "1"])
    finally:
        rt.discover, rt.results_dir = saved_discover, saved_results_dir
    got = records_in(real_dir)
    row("RUN-051", "a real run (its files found by the runner, no folder given) leaves its record in this working copy's "
        "folder and says so", isinstance(got, list) and len(got) == 1 and "· recorded for" in out,
        f"exit {code}; {str(got)[:200]}: {out[-300:]}")
    saved_changed = rt.changed_files
    rt.changed_files = lambda: ["bookMerge.js"]
    try:
        quiet_main(["--changed"], files=[rt.TestFile(js_ok)], results=rdir)
        quiet_main(["--tier", "1", "--list"], files=[rt.TestFile(js_ok)], results=rdir)
    finally:
        rt.changed_files = saved_changed
    got2 = records_in(rdir)
    row("RUN-042", "the commit hook's --changed runs, and --list, leave no record",
        isinstance(got2, list) and len(got2) == 1, str(got2)[:300])
    # The record notes every variable that changes a run, with its value (RUN-058 judges them) — and says at once that a
    # narrowed run proves nothing. One set (RW_CELLS) and one that doesn't narrow (RW_BROWSER); both put back after.
    edir = os.path.join(d, "env-results")
    saved_env = {k: os.environ.get(k) for k in ("RW_CELLS", "RW_BROWSER")}
    os.environ.update({"RW_CELLS": "CELL-005", "RW_BROWSER": "msedge"})
    try:
        code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(js_ok)], results=edir)
    finally:
        for k, v in saved_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    got3 = records_in(edir)
    env3 = got3[0].get("env") if isinstance(got3, list) and len(got3) == 1 else None
    row("RUN-059", "a run's record notes the variables that change a run, with their values (RW_CELLS=CELL-005, "
        "RW_BROWSER=msedge), and the run says it was narrowed",
        env3 == {"RW_CELLS": "CELL-005", "RW_BROWSER": "msedge"} and "RW_CELLS=CELL-005" in out,
        f"exit {code}; env {env3}; {out[-300:]}")

    sdir = os.path.join(d, "stamp-results")
    os.makedirs(sdir)

    def stamp_with(records):
        for name in os.listdir(sdir):
            os.remove(os.path.join(sdir, name))
        for i, r in enumerate(records):
            with open(os.path.join(sdir, f"made-up-{i}.json"), "w", encoding="utf-8") as f:
                f.write(__import__("json").dumps(r))
        return quiet_main(["--stamp"], results=sdir)

    code, out = stamp_with([rec(commit=head)])
    code2, out2 = stamp_with([rec(commit=head, dirty=["?? scratch.txt"])])
    row("RUN-043", "py tools/run_tests.py --stamp (HEAD by default): PROVEN and exit 0 — or NOT PROVEN, why, and exit 1",
        code == 0 and "PROVEN" in out and "NOT PROVEN" not in out
        and code2 == 1 and "NOT PROVEN" in out2 and "scratch.txt" in out2,
        f"exit {code}: {out[-300:]} | exit {code2}: {out2[-300:]}")

    # Per working copy, outside the working tree: git's own folder for that copy (a worktree has its own).
    repo, wt = os.path.join(d, "repo"), os.path.join(d, "wt")
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", "-c", "core.hooksPath=" + os.path.join(d, "no-hooks")]
    os.makedirs(repo)
    # Run from the commit hook, git's own variables (GIT_DIR, GIT_INDEX_FILE…) would point every git command here at
    # THIS project's repository — so the throwaway repo's commands run without them (found 2026-11-16, first commit).
    git_vars = {k: v for k, v in os.environ.items() if k.startswith("GIT_")}
    for k in git_vars:
        del os.environ[k]
    try:
        for args in (["init", "-q"], ["commit", "-q", "--allow-empty", "-m", "one"], ["worktree", "add", "-q", wt]):
            subprocess.run(git + args, cwd=repo, capture_output=True)
        dm, dw = rt.results_dir(repo), rt.results_dir(wt)
    except Exception as e:      # noqa: BLE001
        dm, dw = None, f"{type(e).__name__}: {e}"
    finally:
        os.environ.update(git_vars)
    norm = lambda p: os.path.normcase(os.path.abspath(p)) if isinstance(p, str) else ""   # noqa: E731
    in_git = lambda p: os.sep + ".git" + os.sep in norm(p) + os.sep                        # noqa: E731
    row("RUN-044", "the records live in git's folder for each working copy — one for the main folder, another for a "
        "worktree — never in the working tree",
        dm and dw and norm(dm) != norm(dw) and in_git(dm) and in_git(dw) and not norm(dw).startswith(norm(wt) + os.sep),
        f"main: {dm} | worktree: {dw}")

    # --- Screen tests in parallel, under a machine-wide limit (item 1). The slots: an OS file lock per slot, so a run
    # that dies frees its slot; a run waiting for one says so, naming the holders.
    import importlib
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    ts = importlib.import_module("test_slots")
    sl = ts.Slots(count=1, folder=os.path.join(d, "slots"))
    first = sl.acquire("first-holder")
    waits = []
    second = sl.try_acquire("second")
    holder = subprocess.Popen([sys.executable, "-c", "import sys,time; sys.path.insert(0, sys.argv[1]); import test_slots as t; "
                               "s = t.Slots(count=1, folder=sys.argv[2]).acquire('crash-holder'); print('held', flush=True); "
                               "time.sleep(600)", os.path.join(ROOT, "tools"), os.path.join(d, "slots2")],
                              stdout=subprocess.PIPE, text=True)
    first.release()
    third = sl.acquire("third", on_wait=waits.append, poll_s=0.05)
    row("RUN-045", "a slot is held: with 1 slot a second run can't take it; released, it's free again",
        second is None and third is not None, f"second {second}, third {third}")
    third.release()
    import threading
    t_hold = sl.acquire("holder-A")
    threading.Timer(0.5, t_hold.release).start()
    sl.acquire("waiter", on_wait=waits.append, poll_s=0.05).release()
    row("RUN-046", "a run waiting for a slot says so once, naming who holds it",
        len(waits) == 1 and "waits for a test slot" in waits[0] and "holder-A" in waits[0], str(waits))
    held = holder.stdout.readline().strip() == "held"
    sl2 = ts.Slots(count=1, folder=os.path.join(d, "slots2"))
    taken = sl2.try_acquire("while-held")
    holder.kill()           # the one process this test started, by its exact id (no children)
    holder.wait(10)
    freed = sl2.try_acquire("after-crash")
    row("RUN-047", "a holder that dies frees its slot by itself — nothing stale to clean up",
        held and taken is None and freed is not None, f"held {held}, taken while held {taken}, after {freed}")
    for s in (freed,):
        if s:
            s.release()
    saved_env = os.environ.get("RW_TEST_SLOTS")
    os.environ["RW_TEST_SLOTS"] = "7"
    n7 = ts.slot_count()
    os.environ["RW_TEST_SLOTS"] = "nonsense"
    nbad = ts.slot_count()
    if saved_env is None:
        del os.environ["RW_TEST_SLOTS"]
    else:
        os.environ["RW_TEST_SLOTS"] = saved_env
    row("RUN-048", "4 slots on the PC by default; RW_TEST_SLOTS overrides", n7 == 7 and nbad == 4, f"{n7}, {nbad}")

    # Two files that can only pass TOGETHER: each waits (up to 20 s) for the other's mark — run one after the other, the
    # first gives up. The failing one prints several detail lines, which must come out together, never interleaved.
    def pair_file(name, me, other, fail=False):
        return write(name, f"""# sample
# tags: parallel-sample, tier 1
# covers: tools/run_tests.py
import os, sys, time
open(os.path.join({d!r}, {me!r}), "w").close()
end = time.time() + 20
while not os.path.exists(os.path.join({d!r}, {other!r})):
    if time.time() > end:
        print("  ✗ PAIR-001 the other file never ran at the same time"); print("0 passed, 1 failed"); sys.exit(1)
    time.sleep(0.05)
for i in range(5):
    print("  {'✗' if fail else '✓'} {me}-line", i, flush=True)
    time.sleep(0.05)
print("{'0 passed, 1 failed' if fail else '1 passed, 0 failed'}")
sys.exit({1 if fail else 0})
""")
    pa, pb = pair_file("pa.test_pair.py", "PA", "PB"), pair_file("pb.test_pair.py", "PB", "PA", fail=True)
    code, out = quiet_main(["--tier", "1", "--jobs", "2"], files=[rt.TestFile(pa), rt.TestFile(pb)])
    pb_lines = [i for i, ln in enumerate(out.splitlines()) if "PB-line" in ln]
    row("RUN-049", "--jobs 2 runs two files at the same time; the failing one's lines come out together; the summary line "
        "is the same as ever",
        "Tests: 1 file(s) passed, 1 failed" in out and code == 1 and len(pb_lines) == 5
        and pb_lines == list(range(pb_lines[0], pb_lines[0] + 5)) and "PAIR-001" not in out, f"exit {code}: {out[-700:]}")

    # Screen tests (tier 2) each hold a slot: with 1 slot on the PC, two tier-2 files never overlap — even with --jobs 2.
    def timed_file(name):
        return write(name, f"""# sample
# tags: slot-sample, tier 2
# covers: tools/run_tests.py
import os, time
with open(os.path.join({d!r}, "times.txt"), "a") as f:
    f.write(f"{name} start {{time.time()}}\\n")
time.sleep(0.6)
with open(os.path.join({d!r}, "times.txt"), "a") as f:
    f.write(f"{name} end {{time.time()}}\\n")
print("1 passed, 0 failed")
""")
    ta, tb = timed_file("test_ta.py"), timed_file("test_tb.py")
    one = ts.Slots(count=1, folder=os.path.join(d, "slots3"))
    code, out = quiet_main(["--tier", "2", "--jobs", "2"], files=[rt.TestFile(ta), rt.TestFile(tb)], slots=one)
    spans = {}
    if os.path.exists(os.path.join(d, "times.txt")):
        for ln in open(os.path.join(d, "times.txt")).read().split("\n"):
            if ln.strip():
                n, what, t = ln.split()
                spans.setdefault(n, {})[what] = float(t)
    s = sorted(spans.values(), key=lambda x: x.get("start", 0))
    apart = len(s) == 2 and all("start" in x and "end" in x for x in s) and s[0]["end"] <= s[1]["start"]
    row("RUN-050", "screen-test files each hold a slot: with 1 slot two tier-2 files run one after the other, and the "
        "waiting one says so", code == 0 and apart and "waits for a test slot" in out, f"exit {code}, spans {spans}: {out[-400:]}")

    # --- One file split across processes (2026-11-16, TODO "Faster sprints"): test_cells.py alone set tier 2's time. A
    # file whose header says `shards: N` lists its cells (--list-cells, running nothing) and runs as N processes, each
    # with RW_CELLS set to its share and each holding a test slot; the file's result is the sum, its lines together.
    def shard_file(name, fail_cell=None, n=3, cells=7, lists=True):
        # Its cell IDs written out in the file as test names, as test_cells.py's add(<its ID>, …) calls are — --id finds a
        # file where it names the ID as a test (RUN-063). Each sample also names SHARD-099 as a test that is no cell (as
        # test_cells.py's CELL-058, the console check every process runs), and SHARD-098 only in a comment.
        cell_rows = "".join(f'    ("SHARD-{i:03d}", "a cell"),\n' for i in range(1, cells + 1))
        return write(name, f"""# sample
# tags: shard-sample, tier 2
# covers: tools/run_tests.py
# shards: {n}
# SHARD-098 is named here, in a comment only — it is no test of this file
import os, sys, time
ROWS = [
{cell_rows}]
NOT_A_CELL = ("SHARD-099", "a test every process runs — not one of the cells")
CELLS = [r[0] for r in ROWS]
if "--list-cells" in sys.argv:
    {'print(chr(10).join(CELLS))' if lists else 'print("no list here"); sys.exit(1)'}
    sys.exit(0)
only = [x for x in os.environ.get("RW_CELLS", "").split(",") if x]
mine = [c for c in CELLS if not only or c in only]
# one note per process (2026-11-16: three processes appending to ONE file lost a line under load — on Windows an
# append from separate processes can overwrite another's), its start time now and its end time after the work
note = os.path.join({d!r}, {name!r} + ".%d.log" % os.getpid())
with open(note, "w") as f:
    f.write(f"{{os.getpid()}} {{','.join(mine)}} {{time.time()}}")
time.sleep(0.4)
with open(note, "a") as f:
    f.write(f" {{time.time()}}\\n")
bad = [c for c in mine if c == {fail_cell!r}]
for c in mine:
    print(("  ✗ " if c in bad else "  ✓ ") + c + " a cell")
    if c in bad:
        print("      the detail of " + c)
print(f"{{len(mine) - len(bad)}} passed, {{len(bad)}} failed")
sys.exit(1 if bad else 0)
""")

    def shard_runs(name):
        notes = [os.path.join(d, f) for f in os.listdir(d) if f.startswith(name + ".") and f.endswith(".log")]
        return [open(p).read().split() for p in sorted(notes)]

    def all_at_once(runs):
        """Every shard started before any shard finished — they overlapped (no fixed time limit, so load can't break it)."""
        return len(runs) > 1 and all(len(r) == 4 for r in runs) and max(float(r[2]) for r in runs) < min(float(r[3]) for r in runs)

    sh_ok = shard_file("test_shards_ok.py")
    four = ts.Slots(count=4, folder=os.path.join(d, "slots4"))
    shard_rec = os.path.join(d, "shard-results")
    code, out = quiet_main(["--tier", "2", "--jobs", "4"], files=[rt.TestFile(sh_ok)], slots=four, results=shard_rec)
    runs = shard_runs("test_shards_ok.py")
    shares_seen = sorted(r[1] for r in runs)
    every = sorted(c for r in runs for c in r[1].split(","))
    starts = sorted(float(r[2]) for r in runs)
    got = records_in(shard_rec)
    entries = [f for r in got for f in r.get("files", [])] if isinstance(got, list) else []
    row("RUN-054", "a file with 'shards: 3' runs as 3 processes at once, each with its share of the cells in RW_CELLS (all "
        "of them, none twice); one line for the file with the summed counts; one entry in the record",
        code == 0 and len(runs) == 3 and every == [f"SHARD-{i:03d}" for i in range(1, 8)] and len(set(every)) == 7
        and all_at_once(runs) and out.count("test_shards_ok.py") == 1 and "7 passed, 0 failed" in out
        and len(entries) == 1 and entries[0].get("result") == "passed" and len(entries[0].get("shards") or []) == 3,
        f"exit {code}, shares {shares_seen}, starts {starts}, entries {str(entries)[:300]}: {out[-500:]}")

    sh_bad = shard_file("test_shards_bad.py", fail_cell="SHARD-005")
    code, out = quiet_main(["--tier", "2", "--jobs", "4"], files=[rt.TestFile(sh_bad), rt.TestFile(sh_ok)], slots=four,
                           results=shard_rec)
    lines = out.splitlines()
    head = next((i for i, ln in enumerate(lines) if "test_shards_bad.py" in ln), None)
    block = lines[head:head + 4] if head is not None else []
    got = records_in(shard_rec)
    last = got[-1] if isinstance(got, list) and got else {}
    res = {f.get("file", "").rsplit("/", 1)[-1]: f.get("result") for f in last.get("files", [])}
    row("RUN-055", "a failing shard fails its file: the file's line shows the sum (6 passed, 1 failed), the failing "
        "shard's lines come right under it, together, naming the shard; the record and the stamp see one failed file",
        code == 1 and head is not None and "6 passed, 1 failed" in lines[head] and any(" of 3" in ln for ln in block)
        and any("SHARD-005" in ln for ln in block) and any("the detail of SHARD-005" in ln for ln in block)
        and "Tests: 1 file(s) passed, 1 failed" in out
        and res == {"test_shards_bad.py": "failed", "test_shards_ok.py": "passed"},
        f"exit {code}, record {res}: {out[-700:]}")

    sh_nolist = shard_file("test_shards_nolist.py", lists=False)
    code, out = quiet_main(["--tier", "2"], files=[rt.TestFile(sh_nolist)], slots=four)
    nolist_runs = shard_runs("test_shards_nolist.py")
    sh_small = shard_file("test_shards_small.py", n=5, cells=2)
    code2, out2 = quiet_main(["--tier", "2"], files=[rt.TestFile(sh_small)], slots=four)
    small_runs = shard_runs("test_shards_small.py")
    saved_cells = os.environ.get("RW_CELLS")
    os.environ["RW_CELLS"] = "SHARD-002"
    try:
        code3, out3 = quiet_main(["--tier", "2"], files=[rt.TestFile(shard_file("test_shards_narrow.py"))], slots=four)
    finally:
        if saved_cells is None:
            del os.environ["RW_CELLS"]
        else:
            os.environ["RW_CELLS"] = saved_cells
    narrow_runs = shard_runs("test_shards_narrow.py")
    bad_header = write("test_shards_header.py", "# sample\n# tags: shard-sample, tier 2\n# covers: tools/run_tests.py\n"
                                                "# shards: many\nprint('1 passed, 0 failed')\n")
    row("RUN-056", "shards, the edges: a file that can't list its cells fails loud (never run whole, quietly); more shards "
        "than cells → one process per cell; RW_CELLS already set (a narrow run) → one process, as asked; a shards: line "
        "that isn't a number is a header problem",
        code == 1 and "list" in out and not nolist_runs and code2 == 0 and len(small_runs) == 2
        and code3 == 0 and len(narrow_runs) == 1 and narrow_runs[0][1] == "SHARD-002"
        and rt.TestFile(bad_header).problem and "shards" in rt.TestFile(bad_header).problem,
        f"no list: exit {code}, runs {nolist_runs}: {out[-200:]} | small: exit {code2}, runs {small_runs} | narrow: exit "
        f"{code3}, runs {narrow_runs} | header problem: {rt.TestFile(bad_header).problem}")

    # --- --id narrows a sharded file to the cells it names (2026-11-16, TODO tooling item 6): an --id naming one cell ran
    # all of test_cells.py (3 shards, ~132 cells) — only RW_CELLS narrowed it. (No real test ID is written here: --id
    # picks every file whose text names it, this one included.) Now an --id naming cells of a sharded file runs
    # that file as ONE process with RW_CELLS = exactly those cells; the run is narrowed by --id (its record says so — and
    # notes no RW_CELLS of its own: the runner set it for that one process, not in its environment).
    id_rec = os.path.join(d, "id-results")
    sh_id1 = shard_file("test_shards_id1.py")
    code, out = quiet_main(["--id", "SHARD-005"], files=[rt.TestFile(sh_id1), rt.TestFile(js_ok)], slots=four,
                           results=id_rec)
    id1_runs = shard_runs("test_shards_id1.py")
    got = records_in(id_rec)
    r1 = got[-1] if isinstance(got, list) and got else {}
    row("RUN-060", "--id naming one cell of a sharded file: ONE process, RW_CELLS = that cell, only it ran; the record "
        "says narrowed by --id (no RW_CELLS of its own in the environment noted) — so it proves nothing for its tier",
        code == 0 and len(id1_runs) == 1 and id1_runs[0][1] == "SHARD-005" and "1 passed, 0 failed" in out
        and "a.test.js" not in out and (r1.get("ran") or {}).get("ids") == ["SHARD-005"]
        and "RW_CELLS" not in (r1.get("env") or {}) and rt.narrowed_by(r1) == ["--id SHARD-005"]
        and "narrowed by --id SHARD-005" in out and "RW_CELLS" not in os.environ,
        f"exit {code}, runs {id1_runs}, record ran {r1.get('ran')} env {r1.get('env')}: {out[-500:]}")

    sh_id2 = shard_file("test_shards_id2.py")
    code, out = quiet_main(["--id", "SHARD-006", "--id", "SHARD-002"], files=[rt.TestFile(sh_id2)], slots=four)
    id2_runs = shard_runs("test_shards_id2.py")
    row("RUN-061", "--id naming two cells of a sharded file: both, in the file's order, in ONE process",
        code == 0 and len(id2_runs) == 1 and id2_runs[0][1] == "SHARD-002,SHARD-006" and "2 passed, 0 failed" in out,
        f"exit {code}, runs {id2_runs}: {out[-400:]}")

    sh_id3 = shard_file("test_shards_id3.py")
    code, out = quiet_main(["--id", "NOPE-001"], files=[rt.TestFile(sh_id3), rt.TestFile(js_ok)], slots=four)
    code2, out2 = quiet_main(["--id", "SHARD-099"], files=[rt.TestFile(sh_id3)], slots=four)
    id3_runs = shard_runs("test_shards_id3.py")
    row("RUN-062", "--id naming no test anywhere: nothing runs and it says so (as before); an --id naming a test of a "
        "sharded file that is no cell of it (SHARD-099, as CELL-058 in test_cells.py) leaves the file out, saying why — "
        "never runs it whole",
        code == 0 and "No tests match." in out and code2 == 0 and "No tests match." in out2 and "SHARD-099" in out2
        and not id3_runs,
        f"exit {code}: {out[-200:]} | exit {code2}: {out2[-300:]} | runs {id3_runs}")

    # --- --id picks a file only where it names the ID as a TEST (2026-11-16, TODO tooling item 7): --id picked any file
    # whose text held the ID — `--id CELL-001` also ran test/gestureTable.test.js (a comment names it), `--id CELL-005`
    # also this file (~25 s; CELL-005 is sample data here). A test is named as the first argument of the call that runs
    # it — test("ID", …) / t('ID', …) (test/harness.js, test/ui/harness.py), add("ID", …) (test_cells.py),
    # differs_today("ID", …), row("ID", …) / check("ID", …) (files with their own helper) — or as the first item of its
    # row in a table: ("ID", …). Not in a comment, a message, or as data.
    def idrule_file(name, body, js=False):
        c = "//" if js else "#"
        return write(name, f"{c} sample\n{c} tags: idrule-sample, tier 1\n{c} covers: tools/run_tests.py\n" + body)
    by_comment = idrule_file("test_idrule_comment.py",
                             "# IDRULE-001 is tested in test_idrule_call.py — here a comment names it: test(\"IDRULE-001\", …)\n"
                             "ids = [\"IDRULE-001\"]                 # as data\n"
                             "settings = {\"RW_CELLS\": \"IDRULE-001\"}  # as data\n"
                             "print(\"IDRULE-001\" in \"a message naming IDRULE-001\")\n")
    by_call = idrule_file("test_idrule_call.py", "test(\"IDRULE-001\", \"its test\", lambda: None)\n")
    by_row = idrule_file("test_idrule_row.py", "CASES = [\n    (\"IDRULE-002\", \"a row in a table\", True),\n]\n")
    by_alias = idrule_file("idrule.test.js", "// IDRULE-001 in a comment\nt(\n    'IDRULE-003', 'the harness under another "
                           "name, its ID on the next line', () => {});\n", js=True)
    rule_files = [rt.TestFile(p) for p in (by_comment, by_call, by_row, by_alias)]

    def picked(*ids):
        return sorted(os.path.basename(f.path) for f in rt.select(rule_files, ids=list(ids)))
    got = (picked("IDRULE-001"), picked("IDRULE-002"), picked("IDRULE-003"))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rt.main(["--id", "IDRULE-001", "--list"], files=rule_files)
    row("RUN-063", "--id picks a file only where it names the ID as a test — the first argument of a test call "
        "(test(\"ID\", …), t('ID', …) on the next line too) or the first item of a table row ((\"ID\", …)) — never a "
        "file that names it only in a comment, a message or as data",
        got == (["test_idrule_call.py"], ["test_idrule_row.py"], ["idrule.test.js"])
        and "test_idrule_comment.py" not in buf.getvalue() and "1 file(s) would run" in buf.getvalue(),
        f"picked {got}; --list: {buf.getvalue()[-300:]}")

    sh_id4 = shard_file("test_shards_id4.py")
    code, out = quiet_main(["--id", "SHARD-098"], files=[rt.TestFile(sh_id4)], slots=four)
    code2, out2 = quiet_main(["--id", "SHARD-003"], files=[rt.TestFile(sh_id4)], slots=four)
    id4_runs = shard_runs("test_shards_id4.py")
    row("RUN-064", "the same rule for a sharded file: an ID only in its comments (SHARD-098) doesn't pick it at all — no "
        "process, no 'left out' line; one of its cells still runs alone (SHARD-003, one process)",
        code == 0 and "No tests match." in out and "SHARD-098" not in out and code2 == 0 and len(id4_runs) == 1
        and id4_runs[0][1] == "SHARD-003" and "1 passed, 0 failed" in out2,
        f"exit {code}: {out[-300:]} | exit {code2}, runs {id4_runs}: {out2[-300:]}")

    # --- A test file set aside on purpose: a `skip: <TODO id> — why` header line (2026-11-16, TODO tooling item 5;
    # TESTING.md §7: a flaky test is fixed — or set aside, with a TODO — the same day). The runner doesn't run it and says
    # so plainly; the TODO id must be a task in TODO.md (here a sample TODO file); a release run refuses; the stamp
    # counts the run as not a full run of that file's tier.
    todo_sample = write("TODO-sample.md", "# TODO\n\n## Up next\n\n#### A sample test that fails one time in ten\n"
                        "<!-- id 20261116-0900 -->\n\n_Why it matters:_ a sample.\n")
    aside_ran = os.path.join(d, "aside-ran.txt")

    def aside_file(name, skip_line, tier=1):
        return write(name, f"# sample\n# tags: aside-sample, tier {tier}\n# covers: tools/run_tests.py\n{skip_line}"
                           f"import sys\nopen({aside_ran!r}, 'w').write('ran')\nprint('0 passed, 1 failed')\nsys.exit(1)\n")
    aside = aside_file("test_aside.py", "# skip: 20261116-0900 — fails one time in ten; set aside until fixed\n")
    h = rt.read_header(aside)
    bad_lines = [rt.read_header(aside_file(f"test_aside_bad{i}.py", ln)).get("problem") for i, ln in enumerate(
        ["# skip: soon\n", "# skip: 20261116-0900\n", "# skip: someday — no task named\n"])]
    row("RUN-065", "a 'skip: <TODO id> — why' header line is read (the task's id and why); a skip: line without both is "
        "a header problem",
        h.get("skip") == {"todo": "20261116-0900", "why": "fails one time in ten; set aside until fixed"}
        and h.get("problem") is None and all(p and "skip:" in p for p in bad_lines),
        f"{h} | problems {bad_lines}")

    aside_rec = os.path.join(d, "aside-results")
    code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(js_ok), rt.TestFile(aside)], results=aside_rec,
                           todo=todo_sample)
    got = records_in(aside_rec)
    entry = next((f for r in got for f in r.get("files", []) if "test_aside.py" in f.get("file", "")), {}) \
        if isinstance(got, list) else {}
    said = [ln for ln in out.splitlines() if ln.startswith("set aside: ")]
    row("RUN-066", "a set-aside file isn't run; the run still passes and its summary says, plainly, "
        "'set aside: <file> — <TODO id> — why' (and '1 set aside'); the record notes it as set aside",
        code == 0 and not os.path.exists(aside_ran) and len(said) == 1 and "test_aside.py — 20261116-0900 — fails one "
        "time in ten; set aside until fixed" in said[0] and "1 file(s) passed, 0 failed, 1 set aside" in out
        and entry.get("result") == "set aside" and entry.get("todo") == "20261116-0900",
        f"exit {code}, ran {os.path.exists(aside_ran)}, entry {entry}: {out[-500:]}")

    unknown = aside_file("test_aside_unknown.py", "# skip: 20261116-0999 — names a task TODO.md doesn't have\n")
    if os.path.exists(aside_ran):
        os.remove(aside_ran)        # each row sees only its own run
    code, out = quiet_main(["--tier", "1"], files=[rt.TestFile(js_ok), rt.TestFile(unknown)], todo=todo_sample)
    row("RUN-067", "a skip: line naming a TODO id that TODO.md doesn't have is a header problem: the file fails, loud, "
        "naming the id — never set aside quietly",
        code == 1 and any(ln.startswith("✗") and "test_aside_unknown.py" in ln and "20261116-0999" in ln
                          for ln in out.splitlines()) and not os.path.exists(aside_ran),
        f"exit {code}: {out[-400:]}")

    if os.path.exists(aside_ran):
        os.remove(aside_ran)
    code, out = quiet_main(["--tier", "1", "--release"], files=[rt.TestFile(js_ok), rt.TestFile(aside)], todo=todo_sample)
    refusal = out.split("✗ release run", 1)[-1] if "✗ release run" in out else ""
    row("RUN-068", "--release refuses while a file is set aside, naming it with its TODO id (a set-aside test blocks the "
        "next release until it's fixed)",
        code == 1 and "set aside" in refusal and "test_aside.py" in refusal and "20261116-0900" in refusal
        and not os.path.exists(aside_ran), f"exit {code}: {out[-500:]}")

    code, out = quiet_main(["--tier", "1", "--list"], files=[rt.TestFile(js_ok), rt.TestFile(aside)], todo=todo_sample)
    row("RUN-069", "--list shows a set-aside file as set aside, with its TODO id, and doesn't count it as would-run",
        code == 0 and "1 file(s) would run" in out
        and any("test_aside.py" in ln and "set aside" in ln and "20261116-0900" in ln for ln in out.splitlines()),
        f"exit {code}: {out[-400:]}")

    aside2 = {"file": "test/ui/test_z.py", "tier": 2, "result": "set aside", "todo": "20261116-0900", "why": "flaky"}
    # (a run with a file set aside passes without --release, so its record says "passed")
    p, why = judged([dict(rec(files=t1 + t2 + [aside2]), result="passed")])
    p2, why2 = judged([dict(rec(files=t1 + t2 + [dict(aside2, file="test/x2.test.js", tier=1)]), result="passed")])
    row("RUN-070", "--stamp: a run with a set-aside file isn't a full run of that file's tier → NOT PROVEN, naming the "
        "file and its TODO id; the other tier is judged on its own (tier 2 set aside: tier 1 still ✓)",
        p is False and "tier 2" in why and "test_z.py" in why and "20261116-0900" in why and "✓ tier 1" in why
        and p2 is False and "x2.test.js" in why2 and "✓ tier 2" in why2,
        f"{p}: {why} | {p2}: {why2}")

    # --- The stamp shows tier 3 too (2026-11-16): after a --tier all --release run that passed tier 3, the stamp showed
    # only tiers 1 and 2. Tier 3's latest run on the commit is a line — passed / failed / not run — information only:
    # PROVEN still means tiers 1 and 2 (tier 3 needs a relay and isn't part of every review).
    here = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    t3 = {"file": "relay/test-x.mjs", "tier": 3, "result": "passed", "counts": "9 passed, 0 failed"}
    t3bad = dict(t3, result="failed", counts="8 passed, 1 failed")
    code, out = stamp_with([rec(commit=here, files=t1 + t2 + [t3])])
    code2, out2 = stamp_with([rec(commit=here, files=t1 + t2 + [t3]),
                              rec(commit=here, tier="3", files=[t3bad], ended="2026-11-16T11:00:00")])
    code3, out3 = stamp_with([rec(commit=here, tier="1", files=t1), rec(commit=here, tier="2", files=t2)])

    def t3_line(o):
        return next((ln for ln in o.splitlines() if "tier 3" in ln and "PROVEN" not in ln), "")
    row("RUN-071", "--stamp shows tier 3's latest run on the commit as a line — passed / failed (naming the file) / not "
        "run — information only: PROVEN is still tiers 1 and 2",
        code == 0 and "passed" in t3_line(out) and "1 of 1" in t3_line(out)
        and code2 == 0 and "failed" in t3_line(out2) and "test-x.mjs" in out2
        and code3 == 0 and "not run" in t3_line(out3) and all("PROVEN —" in o for o in (out, out2, out3)),
        f"exit {code}: {t3_line(out)!r} | exit {code2}: {t3_line(out2)!r} {out2[-300:]} | exit {code3}: {t3_line(out3)!r}")

failed = [r for r in results if not r[2]]
print(f"{len(results) - len(failed)} passed, {len(failed)} failed")
sys.exit(1 if failed else 0)
