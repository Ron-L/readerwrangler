"""
test/ui/harness.py — the Python twin of test/harness.js for screen tests: stable IDs (AREA-NNN), a failure is counted
and the file carries on, done() prints the summary and exits 1 if anything failed (tools/run_tests.py reads both).
differs_today() — a test of decided behavior the app doesn't have yet, with what it does today (2026-11-13, CELL-…).

The machine's or the browser's trouble (2026-11-17, TODO tooling item 9; tools/environment_trouble.py): the screen-test
driver (rw.py) raises EnvironmentTrouble — or calls environment(reason) for trouble it only sees go by, such as a
request to our own server that failed. If nothing failed before the first such trouble, the file exits 3 (never an
assertion's code) with a line "ENVIRONMENT FAILURE: <reason>", and the runner reruns it once, alone; a failure BEFORE the
trouble is a test failure (exit 1) — it happened while the machine was fine. Trouble that failed nothing exits 0.
on_failure(fn): fn(label) saves a screenshot for a failing test and returns its path, printed under the failure (rw.App
registers one for its page).
"""
import os
import re
import sys
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
import environment_trouble   # noqa: E402 — tools/environment_trouble.py: the exit code and the marked line, one place

# Print UTF-8 whatever the output is (2026-11-12): run piped or redirected on Windows, Python used the old code page and
# crashed on the first "✓" — every test had to be run with PYTHONIOENCODING=utf-8 set by hand. Here for every test that
# prints through the harness; the three that print on their own (test_check_parse, test_message_codes, test_run_tests)
# set it the same way.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

_passed = 0
_failures = []
_seen = set()
_events = []        # ("fail", what) / ("env", reason), in the order they happened — decides the exit code
_troubled = []      # tests the machine's or the browser's trouble stopped (not counted as failed)
_on_failure = []    # fn(label) -> a screenshot's path or None


class EnvironmentTrouble(Exception):
    """The machine or the browser failed, not the app (the page never loaded, the browser closed, our own server didn't
    come up…) — raised by the screen-test driver (rw.py). Never raised for what a test asserts. Noted the moment it's
    made (environment()), so whatever the clean-up on its way out reports comes AFTER it — not before."""

    def __init__(self, reason):
        super().__init__(reason)
        environment(reason)


def environment(reason):
    """Trouble of the machine's or the browser's, seen now (rw.App: a request to our own server failed, the browser
    disconnected). Failures after it count as the machine's; on its own it fails nothing."""
    _events.append(("env", reason))
    if sum(1 for k, _ in _events if k == "env") <= 10:
        print(f"  ! machine or browser trouble: {reason}", flush=True)


def on_failure(fn):
    """fn(label) is called when a test fails and returns where it saved a screenshot (or None); the path is printed under
    the failure. Returns a function that takes fn off again."""
    _on_failure.append(fn)
    return lambda: _on_failure.remove(fn) if fn in _on_failure else None


def _failed(label):
    _events.append(("fail", label))
    for fn in list(_on_failure):
        try:
            p = fn(label)
        except Exception:   # noqa: BLE001 — a screenshot is a help, never a second failure
            p = None
        if p:
            print(f"      screenshot: {p}", flush=True)


def _trouble(tid, name, e):
    _troubled.append(tid)       # (the trouble itself was noted when it was raised — EnvironmentTrouble)
    print(f"  ! {tid} {name}\n      stopped by the machine's or the browser's trouble, not a test failure: {e}", flush=True)
    for fn in list(_on_failure):
        try:
            p = fn(tid)
        except Exception:   # noqa: BLE001
            p = None
        if p:
            print(f"      screenshot: {p}", flush=True)


def test(tid, name, fn):
    global _passed
    if not re.fullmatch(r"[A-Z][A-Z0-9]*-\d{3}", tid) or tid in _seen:
        _failures.append(tid)
        _events.append(("fail", tid))
        print(f"  ✗ {tid} {name}\n      bad or repeated test ID — use AREA-NNN", flush=True)
        return
    _seen.add(tid)
    try:
        fn()
        _passed += 1
        print(f"  ✓ {tid} {name}", flush=True)
    except EnvironmentTrouble as e:
        _trouble(tid, name, e)
    except Exception as e:   # noqa: BLE001 — every failure is reported, then the file carries on
        _failures.append(tid)
        msg = str(e) or traceback.format_exc(limit=1)
        print(f"  ✗ {tid} {name}\n      " + "\n      ".join(msg.splitlines()[:6]), flush=True)
        _failed(tid)


_differ = []


def differs_today(tid, name, fn, today):
    """A test that asserts the DECIDED behavior where the app is known to differ today (test-first, before the build —
    sprint 4 of docs/design/ONE-TABLE.md). `today` is what was measured: text (or a list of texts) that the failure's
    words must contain. Three outcomes, so a mark can't hide a new problem or outlive its fix:
      - it fails AND its words hold every `today` text → the known difference: reported, not counted as a failure;
      - it fails with other words → a FAILURE (the app changed, or the test broke — read it);
      - it passes → a FAILURE: the app now does what was decided — drop the mark (call test() instead)."""
    if not re.fullmatch(r"[A-Z][A-Z0-9]*-\d{3}", tid) or tid in _seen:
        _failures.append(tid)
        print(f"  ✗ {tid} {name}\n      bad or repeated test ID — use AREA-NNN", flush=True)
        return
    _seen.add(tid)
    marks = [today] if isinstance(today, str) else list(today)
    try:
        fn()
    except EnvironmentTrouble as e:
        _trouble(tid, name, e)
        return
    except Exception as e:   # noqa: BLE001
        msg = str(e) or traceback.format_exc(limit=1)
        if isinstance(e, AssertionError) and all(m in msg for m in marks):
            _differ.append(tid)
            print(f"  ~ {tid} {name}\n      differs today, as measured:\n      "
                  + "\n      ".join(msg.splitlines()[:8]), flush=True)
            return
        _failures.append(tid)
        print(f"  ✗ {tid} {name}\n      not the difference measured (expected words: {marks}):\n      "
              + "\n      ".join(msg.splitlines()[:8]), flush=True)
        _failed(tid)
        return
    _failures.append(tid)
    _events.append(("fail", tid))
    print(f"  ✗ {tid} {name}\n      now does what was decided — drop its 'differs today' mark", flush=True)


def check(cond, msg):
    if not cond:
        raise AssertionError(msg)


def fail_after(label, msg):
    """A failure found after the tests ran (the driver's end-of-session log check — LOGGING.md §5 step 6): counted like
    any failed test, printed under `label` (not a test ID — it belongs to the whole file)."""
    _failures.append(label)
    print(f"  ✗ {label}\n      " + "\n      ".join(str(msg).splitlines()[:12]), flush=True)
    _failed(label)


def remove_tree(top):
    """Delete a throwaway test folder completely (2026-11-16). shutil.rmtree(ignore_errors=True) quietly left every
    throwaway git repository behind — git's object files are read-only on Windows — so 45 piled up in %TEMP%. Here: every
    link is removed by itself first, never followed (a link may point at a folder that must survive — tools/copies.py),
    a read-only file is made writable and deleted. Returns what couldn't be deleted ([] = all gone)."""
    import os
    import stat
    left = []

    def is_link(p):
        return os.path.islink(p) or (hasattr(os.path, "isjunction") and os.path.isjunction(p))

    def walk(d):
        for e in list(os.scandir(d)):
            try:
                if is_link(e.path):
                    os.rmdir(e.path) if os.path.isjunction(e.path) else os.unlink(e.path)
                elif e.is_dir(follow_symlinks=False):
                    walk(e.path)
                    os.rmdir(e.path)
                else:
                    os.chmod(e.path, stat.S_IWRITE)
                    os.remove(e.path)
            except OSError as err:
                left.append(f"{e.path}: {err}")
    if os.path.lexists(top):
        try:
            walk(top)
            os.rmdir(top)
        except OSError as err:
            left.append(f"{top}: {err}")
    return left


def _exit_code():
    """0 nothing failed; EXIT_CODE (3) the machine's or the browser's trouble came first — no test had failed before it;
    1 a test failure (one before any trouble, or no trouble at all)."""
    kinds = [k for k, _ in _events]
    if not _failures and not _troubled and "fail" not in kinds:
        return 0
    if "env" in kinds and ("fail" not in kinds or kinds.index("env") < kinds.index("fail")):
        return environment_trouble.EXIT_CODE
    return 1


def _finish():
    """Print the summary (and, for the machine's trouble, the marked line the runner reads); return the exit code."""
    code = _exit_code()
    print(f"{_passed} passed, {len(_failures)} failed" + (f", {len(_differ)} differ today (as measured)" if _differ else "")
          + (f", {len(_troubled)} stopped by the machine's or the browser's trouble" if _troubled else ""), flush=True)
    if code == environment_trouble.EXIT_CODE:
        first = next(r for k, r in _events if k == "env")
        print(f"{environment_trouble.MARK} {first}", flush=True)
        print(f"  (exit {code}: the machine or the browser failed, not a test — tools/run_tests.py reruns this file once, "
              "alone)", flush=True)
    return code


def _uncaught(kind, exc, tb):
    """An error no test caught (e.g. the App's start, outside any test): Python's own report, then — if the machine's or
    the browser's trouble came first — the summary, the marked line and exit 3. Otherwise Python exits 1, as always."""
    _default_hook(kind, exc, tb)
    if issubclass(kind, KeyboardInterrupt):
        return
    if isinstance(exc, EnvironmentTrouble):         # (noted when it was raised) — it stopped the file
        _troubled.append("(outside any test)")
    else:
        _events.append(("fail", f"(outside any test) {kind.__name__}"))
    if _exit_code() == environment_trouble.EXIT_CODE:
        _finish()
        sys.stderr.flush()
        os._exit(environment_trouble.EXIT_CODE)   # (an excepthook can't choose the exit code any other way)


_default_hook = sys.excepthook
sys.excepthook = _uncaught


def done():
    sys.exit(_finish())
