# Tests for test/ui/harness.py's end — the summary, the marked line and the exit code every screen-test file gives (the
# runner reads them: tools/run_tests.py) — and that they come from ONE implementation, tools/environment_trouble.py's
# tally (Law 22; TODO tooling 13.9, 2026-11-18, sprint 9: done() repeated it).
# tags: test-runner, environment, tier 1
# covers: test/ui/harness.py, tools/environment_trouble.py
# Run: python test/test_ui_harness.py
#
# Each case is a small stand-in screen-test file run as its own process — no browser: the harness alone — so what's
# checked is exactly what the runner sees. Its printed lines (stdout) are compared WHOLE with what the harness printed on
# 2026-11-18 before done() was moved onto tally (captured then, kept here): the move must change nothing a runner reads.
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UI = os.path.join(ROOT, "test", "ui")
sys.path.insert(0, UI)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from harness import check, done, remove_tree, test   # noqa: E402
import environment_trouble                           # noqa: E402

PRE = (f"import sys\nsys.path.insert(0, {UI!r})\n"
       "from harness import EnvironmentTrouble, check, differs_today, done, environment, fail_after, test\n")
TROUBLE = 'def trouble():\n    raise EnvironmentTrouble("the page never loaded (a sample)")\n'
EXIT3 = "  (exit 3: the machine or the browser failed, not a test — tools/run_tests.py reruns this file once, alone)"
STOPPED = "stopped by the machine's or the browser's trouble"

# (id, what, the stand-in's body, its exit code, its whole stdout) — the stdout as the harness printed it before the move
CASES = [
    ("HARNESS-001", "every test passed → exit 0, 'N passed, 0 failed'",
     'test("HX-001", "a", lambda: None)\ntest("HX-002", "b", lambda: None)\ndone()\n', 0,
     ["  ✓ HX-001 a", "  ✓ HX-002 b", "2 passed, 0 failed"]),
    ("HARNESS-002", "a pass, a failure, a difference as measured, then trouble → exit 1; each counted in the summary, the "
     "differences and the stopped ones apart", TROUBLE + 'test("HX-001", "a", lambda: None)\n'
     'test("HX-002", "b", lambda: check(False, "x"))\n'
     'differs_today("HX-003", "c", lambda: check(False, "as today"), "as today")\ntest("HX-004", "d", trouble)\ndone()\n', 1,
     ["  ✓ HX-001 a", "  ✗ HX-002 b", "      x", "  ~ HX-003 c", "      differs today, as measured:", "      as today",
      "  ! machine or browser trouble: the page never loaded (a sample)", "  ! HX-004 d",
      f"      {STOPPED}, not a test failure: the page never loaded (a sample)",
      f"1 passed, 1 failed, 1 differ today (as measured), 1 {STOPPED}"]),
    ("HARNESS-003", "trouble before any failure → exit 3, the summary, the marked line, and the line that explains it",
     TROUBLE + 'test("HX-001", "a", trouble)\ntest("HX-002", "b", lambda: None)\n'
     'test("HX-003", "c", lambda: check(False, "x"))\ndone()\n', 3,
     ["  ! machine or browser trouble: the page never loaded (a sample)", "  ! HX-001 a",
      f"      {STOPPED}, not a test failure: the page never loaded (a sample)", "  ✓ HX-002 b", "  ✗ HX-003 c", "      x",
      f"1 passed, 1 failed, 1 {STOPPED}", "ENVIRONMENT FAILURE: the page never loaded (a sample)", EXIT3]),
    ("HARNESS-004", "trouble outside any test (the App's start) → exit 3, through the same summary",
     'test("HX-001", "a", lambda: None)\nraise EnvironmentTrouble("our web server didn\'t start (a sample)")\n', 3,
     ["  ✓ HX-001 a", "  ! machine or browser trouble: our web server didn't start (a sample)",
      f"1 passed, 0 failed, 1 {STOPPED}", "ENVIRONMENT FAILURE: our web server didn't start (a sample)", EXIT3]),
    ("HARNESS-005", "a failure found after the tests (fail_after) counts as failed → exit 1",
     'test("HX-001", "a", lambda: None)\nfail_after("the session\'s log", "an error the tests didn\'t expect")\ndone()\n', 1,
     ["  ✓ HX-001 a", "  ✗ the session's log", "      an error the tests didn't expect", "1 passed, 1 failed"]),
    ("HARNESS-006", "trouble that failed nothing is only noted → exit 0",
     'environment("a request to our own server failed (a sample)")\ntest("HX-001", "a", lambda: None)\ndone()\n', 0,
     ["  ! machine or browser trouble: a request to our own server failed (a sample)", "  ✓ HX-001 a",
      "1 passed, 0 failed"]),
]

folder = tempfile.mkdtemp(prefix="rw-harness-test-")


def run_case(name, body):
    path = os.path.join(folder, name + ".py")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(PRE + body)
    r = subprocess.run([sys.executable, path], capture_output=True, timeout=60)
    return r.returncode, r.stdout.decode("utf-8", "replace").splitlines(), r.stderr.decode("utf-8", "replace")


def case(name, body, code, lines):
    def run():
        got_code, got, err = run_case(name, body)
        check(got_code == code and got == lines,
              f"exit {got_code} ({code} wanted); stdout differs from what the harness printed before:\n"
              + "\n".join(f"  {'=' if i < len(lines) and g == lines[i] else '≠'} {g}" for i, g in enumerate(got))
              + f"\nwanted:\n" + "\n".join(f"    {x}" for x in lines) + (f"\nstderr: {err[-300:]}" if err else ""))
    return run


def ends_through_tally():
    # The stand-in wraps tally to say each call; the harness's end must go through it — once — for both ways it ends
    # (done(), and an uncaught trouble outside any test).
    spy = ("import environment_trouble\n_real = environment_trouble.tally\n"
           "def _spy(*a, **k):\n    print('[tally called]')\n    return _real(*a, **k)\n"
           "environment_trouble.tally = _spy\n")
    _, by_done, _ = run_case("spy_done", spy + 'test("HX-001", "a", lambda: None)\ndone()\n')
    _, by_hook, _ = run_case("spy_hook", spy + 'raise EnvironmentTrouble("a sample")\n')
    check(by_done.count("[tally called]") == 1 and by_hook.count("[tally called]") == 1,
          f"done() and the uncaught trouble should each end through environment_trouble.tally, once: "
          f"{by_done} | {by_hook}")


def tally_also():
    lines, code = environment_trouble.tally([("A", "a", True, ""), ("B", "b", None, "")], [("env", "why")],
                                            trouble="the machine's or the browser's trouble",
                                            also=["2 differ today (as measured)"])
    check(lines == ["1 passed, 0 failed, 2 differ today (as measured), 1 stopped by the machine's or the browser's "
                    "trouble", "ENVIRONMENT FAILURE: why"] and code == 3, f"{lines} exit {code}")
    plain, code2 = environment_trouble.tally([("A", "a", True, "")], [])
    check(plain == ["1 passed, 0 failed"] and code2 == 0, f"without it, as before: {plain} exit {code2}")


try:
    for tid, what, body, code, lines in CASES:
        test(tid, what, case(tid.lower().replace("-", "_"), body, code, lines))
    test("HARNESS-007", "the harness ends through tools/environment_trouble.py's tally — one implementation (done() and an "
         "uncaught trouble outside any test both)", ends_through_tally)
    test("HARNESS-008", "tally's summary holds other counts where they're asked for (also=…: the harness's 'differ today'), "
         "between the failed and the stopped — and without them, as before", tally_also)
finally:
    remove_tree(folder)
done()
