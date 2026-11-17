# Screen test: the screen-test driver tells the machine's or the browser's trouble (ENVIRONMENT) from a test failure, with
# its own exit code — 3, which an assertion never gives — so the runner can rerun the one and never the other; and a
# failing test's screenshot is saved and named (2026-11-17, TODO tooling item 9; TESTING.md §4, §7).
# tags: test-runner, environment, tier 2
# covers: test/ui/rw.py, test/ui/harness.py, tools/environment_trouble.py
#
# Each case is a small screen test of its own, run as its own process (as tools/run_tests.py runs a file), so what's
# checked is exactly what the runner sees: its exit code and its printed lines. One browser at a time (this file holds
# one test slot).
import os
import re
import subprocess
import sys
import tempfile

UI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, UI)
from harness import check, done, remove_tree, test   # noqa: E402
import rw                                            # noqa: E402

PRE = f"""import os, sys
sys.path.insert(0, {UI!r})
import rw
from harness import check, done, test
"""
# The app's own script answered with something that isn't the app: the start screen never goes away.
SILENT_APP = PRE + """rw.APP_TIMEOUT_MS = 5000
def app_answered_with(body):
    return lambda ctx: ctx.route(lambda u: "/dist/readerwrangler.js" in u,
                                 lambda r: r.fulfill(status=200, content_type="application/javascript", body=body))
with rw.App(before_load=app_answered_with(BODY)) as app:
    pass
done()
"""
SERVER_GONE = PRE + """with rw.App() as app:
    app._stop_server()       # our web server stops answering (as if the machine had dropped it)
    app.page.evaluate("() => { const i = new Image(); i.src = '/icons/logo-transparent.png?gone=' + Date.now(); "
                      "document.body.appendChild(i); }")
    app.wait_console(r"Failed to load resource: net::ERR_CONNECTION_REFUSED", 20)
    test("ENVX-001", "no unexpected console messages", lambda: check(not app.unexpected_console(), app.unexpected_console()))
done()
"""
FAILS_ON_PURPOSE = PRE + """with rw.App() as app:
    test("ENVX-002", "fails on purpose", lambda: check(False, "failed on purpose (ENV-004)"))
done()
"""

folder = tempfile.mkdtemp(prefix="rw-env-test-")


def run_case(name, source):
    path = os.path.join(folder, name + ".py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(source)
    r = subprocess.run([sys.executable, path], cwd=rw.ROOT, capture_output=True, timeout=240)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    marks = [ln for ln in out.splitlines() if ln.startswith("ENVIRONMENT FAILURE:")]
    return r.returncode, out, marks


def tail(out):
    return "\n".join(out.strip().splitlines()[-10:])


def never_loads():
    code, out, marks = run_case("env_never_loads", SILENT_APP.replace("BODY", repr("// not the app — nothing starts")))
    check(code == 3 and len(marks) == 1 and "never loaded" in marks[0],
          f"exit {code} (3 wanted), marked lines {marks}:\n{tail(out)}")
    shots = [ln.split("screenshot:", 1)[1].strip() for ln in out.splitlines() if "screenshot:" in ln]
    check(shots and all(os.path.exists(p) for p in shots), f"no screenshot of what was on screen: {shots}\n{tail(out)}")


def broken_app():
    code, out, marks = run_case("env_broken_app",
                                SILENT_APP.replace("BODY", repr("throw new Error('broken on purpose (ENV-002)')")))
    check(code == 1 and not marks and "the page reported errors of its own" in out
          and any("broken on purpose (ENV-002)" in ln and "crash" in ln for ln in out.splitlines()),
          f"exit {code} (1 wanted — the page's own error is the app's, not the machine's), marked lines {marks}:\n"
          f"{tail(out)}")


def server_gone():
    code, out, marks = run_case("env_server_gone", SERVER_GONE)
    # (the first request to fail may be refused or cut off — a reset — as the server goes)
    check(code == 3 and len(marks) == 1 and re.search(r"ERR_CONNECTION_(REFUSED|RESET)", marks[0])
          and "our own server" in marks[0],
          f"exit {code} (3 wanted), marked lines {marks}:\n{tail(out)}")


def failure_shot():
    code, out, marks = run_case("env_failure_shot", FAILS_ON_PURPOSE)
    shots = [ln.split("screenshot:", 1)[1].strip() for ln in out.splitlines() if "screenshot:" in ln]
    check(code == 1 and not marks and len(shots) == 1 and shots[0].endswith("ENVX-002.png") and os.path.exists(shots[0]),
          f"exit {code} (1 wanted), screenshots {shots}, marked lines {marks}:\n{tail(out)}")


try:
    test("ENV-001", "the app's start screen never goes away and the page reports no error of its own → the file exits 3 "
         "with 'ENVIRONMENT FAILURE: … never loaded …' and a screenshot of what was on screen", never_loads)
    test("ENV-002", "the start screen never goes away BECAUSE the page failed (its own error) → a test failure: exit 1, "
         "no environment line, the error named", broken_app)
    test("ENV-003", "our own web server stops answering → the browser's requests to it fail (refused, or cut off) and the "
         "console check reports it as the machine's trouble: exit 3, the error named", server_gone)
    test("ENV-004", "a failing test's screenshot is saved and its path printed under the failure (exit 1)", failure_shot)
finally:
    remove_tree(folder)
done()
